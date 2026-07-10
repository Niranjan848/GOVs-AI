"""
GOVs-AI Agent Tools
LangChain tool definitions for the AI agent to use during reasoning.
"""

import json
import logging
from typing import Optional
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import GovernmentScheme, Profile, User

logger = logging.getLogger(__name__)


def search_schemes_by_query(query: str, top_k: int = 5) -> list:
    """Semantic search over the FAISS vector store for relevant schemes."""
    from rag.embeddings import embed_query
    from rag.retriever import retrieve

    query_embedding = embed_query(query)
    results = retrieve(query_embedding, k=top_k)
    return results


def get_all_schemes() -> list:
    """Get all active government schemes from the database."""
    db = SessionLocal()
    try:
        schemes = db.query(GovernmentScheme).filter(GovernmentScheme.is_active == True).all()
        return [
            {
                "id": s.id,
                "name": s.name,
                "short_name": s.short_name,
                "category": s.category,
                "description": s.description,
                "eligibility": s.eligibility,
                "benefits": s.benefits,
                "benefits_amount": s.benefits_amount,
                "documents_required": s.documents_required,
                "application_process": s.application_process,
                "website_url": s.website_url,
                "ministry": s.ministry,
                "state": s.state,
            }
            for s in schemes
        ]
    finally:
        db.close()


def get_scheme_by_name(name: str) -> Optional[dict]:
    """Look up a specific scheme by name (fuzzy match)."""
    db = SessionLocal()
    try:
        scheme = db.query(GovernmentScheme).filter(
            GovernmentScheme.name.ilike(f"%{name}%")
        ).first()
        if scheme:
            return {
                "id": scheme.id,
                "name": scheme.name,
                "short_name": scheme.short_name,
                "category": scheme.category,
                "description": scheme.description,
                "eligibility": scheme.eligibility,
                "benefits": scheme.benefits,
                "benefits_amount": scheme.benefits_amount,
                "documents_required": scheme.documents_required,
                "application_process": scheme.application_process,
                "website_url": scheme.website_url,
                "ministry": scheme.ministry,
                "state": scheme.state,
            }
        return None
    finally:
        db.close()


def check_eligibility(profile: dict, scheme: dict) -> dict:
    """
    Rule-based eligibility check against structured scheme criteria.
    Returns eligibility result with score and reasoning.
    """
    eligibility = scheme.get("eligibility", {})
    if isinstance(eligibility, str):
        try:
            eligibility = json.loads(eligibility)
        except json.JSONDecodeError:
            return {"eligible": True, "score": 0.5, "reasoning": "Could not parse eligibility criteria."}

    score = 1.0
    reasons = []
    blockers = []

    # Age check
    if "min_age" in eligibility and profile.get("age"):
        if profile["age"] < eligibility["min_age"]:
            blockers.append(f"Minimum age is {eligibility['min_age']}, you are {profile['age']}")
            score -= 0.3
    if "max_age" in eligibility and profile.get("age"):
        if profile["age"] > eligibility["max_age"]:
            blockers.append(f"Maximum age is {eligibility['max_age']}, you are {profile['age']}")
            score -= 0.3

    # Income check
    if "max_income" in eligibility and profile.get("annual_income"):
        if profile["annual_income"] > eligibility["max_income"]:
            blockers.append(f"Maximum income is ₹{eligibility['max_income']:,}, yours is ₹{profile['annual_income']:,}")
            score -= 0.4
        else:
            reasons.append(f"Your income of ₹{profile['annual_income']:,} is within the limit")

    # Gender check
    if "gender" in eligibility and profile.get("gender"):
        required_gender = eligibility["gender"].lower()
        if required_gender != "all" and profile["gender"].lower() != required_gender:
            blockers.append(f"This scheme is for {required_gender} applicants only")
            score -= 0.5

    # Occupation check
    if "occupation" in eligibility and profile.get("occupation"):
        required_occ = eligibility["occupation"]
        if isinstance(required_occ, list):
            if profile["occupation"].lower() not in [o.lower() for o in required_occ]:
                blockers.append(f"Required occupation: {', '.join(required_occ)}")
                score -= 0.3
            else:
                reasons.append(f"Your occupation '{profile['occupation']}' matches the criteria")
        elif isinstance(required_occ, str) and required_occ.lower() != "all":
            if required_occ.lower() not in profile["occupation"].lower():
                blockers.append(f"This scheme targets {required_occ} occupation")
                score -= 0.3

    # Category check (SC/ST/OBC/General/EWS)
    if "category" in eligibility and profile.get("category"):
        required_cats = eligibility["category"]
        if isinstance(required_cats, list):
            if profile["category"].lower() not in [c.lower() for c in required_cats]:
                blockers.append(f"Required category: {', '.join(required_cats)}")
                score -= 0.2
            else:
                reasons.append(f"Your category '{profile['category']}' qualifies")
        elif isinstance(required_cats, str) and required_cats.lower() != "all":
            if required_cats.lower() != profile["category"].lower():
                blockers.append(f"Required category: {required_cats}")
                score -= 0.2

    # State check
    if "state" in eligibility and profile.get("state"):
        required_state = eligibility["state"]
        if isinstance(required_state, str) and required_state.lower() not in ("all", "central"):
            if required_state.lower() != profile["state"].lower():
                blockers.append(f"This scheme is for {required_state} residents")
                score -= 0.4

    # Land check (for farmer schemes)
    if "min_land_acres" in eligibility and profile.get("land_area_acres") is not None:
        if profile["land_area_acres"] < eligibility["min_land_acres"]:
            blockers.append(f"Minimum land required: {eligibility['min_land_acres']} acres")
            score -= 0.3
    if "max_land_acres" in eligibility and profile.get("land_area_acres") is not None:
        if profile["land_area_acres"] > eligibility["max_land_acres"]:
            blockers.append(f"Maximum land allowed: {eligibility['max_land_acres']} acres")
            score -= 0.3

    # BPL check
    if eligibility.get("bpl_required") and not profile.get("bpl_card"):
        blockers.append("BPL card is required for this scheme")
        score -= 0.4

    score = max(0.0, min(1.0, score))
    eligible = len(blockers) == 0 and score >= 0.5

    return {
        "scheme_name": scheme["name"],
        "eligible": eligible,
        "score": round(score, 2),
        "reasons_for": reasons,
        "blockers": blockers,
        "reasoning": (
            f"You {'likely qualify' if eligible else 'may not qualify'} for {scheme['name']}. "
            + (f"Positives: {'; '.join(reasons)}. " if reasons else "")
            + (f"Issues: {'; '.join(blockers)}." if blockers else "All criteria appear to be met.")
        ),
    }


def get_user_profile_dict(user_id: int) -> dict:
    """Get user profile as a dictionary for agent consumption."""
    db = SessionLocal()
    try:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            return {}
        return {
            "name": profile.name,
            "age": profile.age,
            "gender": profile.gender,
            "state": profile.state,
            "district": profile.district,
            "occupation": profile.occupation,
            "annual_income": profile.annual_income,
            "category": profile.category,
            "education": profile.education,
            "land_area_acres": profile.land_area_acres,
            "has_disability": profile.has_disability,
            "family_size": profile.family_size,
            "marital_status": profile.marital_status,
            "has_bank_account": profile.has_bank_account,
            "has_aadhaar": profile.has_aadhaar,
            "bpl_card": profile.bpl_card,
        }
    finally:
        db.close()


def generate_checklist_for_scheme(scheme: dict, profile: dict) -> dict:
    """Generate a document checklist for a specific scheme application."""
    docs = scheme.get("documents_required", [])
    if isinstance(docs, str):
        try:
            docs = json.loads(docs)
        except json.JSONDecodeError:
            docs = [docs]

    items = []
    for doc in docs:
        doc_name = doc if isinstance(doc, str) else doc.get("name", str(doc))
        # Infer if user likely has the document
        likely_has = False
        if "aadhaar" in doc_name.lower() and profile.get("has_aadhaar"):
            likely_has = True
        elif "bank" in doc_name.lower() and profile.get("has_bank_account"):
            likely_has = True
        elif "bpl" in doc_name.lower() and profile.get("bpl_card"):
            likely_has = True

        items.append({
            "document": doc_name,
            "mandatory": True,
            "user_likely_has": likely_has,
            "tips": "",
        })

    return {
        "scheme_name": scheme["name"],
        "total_documents": len(items),
        "items": items,
        "application_process": scheme.get("application_process", "Visit the official scheme website or nearest CSC center."),
        "website_url": scheme.get("website_url", ""),
    }
