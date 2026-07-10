"""
GOVs-AI Profile Routes
GET/PUT /api/profile — user profile management
GET /api/profile/completion — completion percentage
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User, Profile
from api.auth import get_current_user
from utils.validators import ProfileUpdate, ProfileResponse

router = APIRouter(prefix="/api", tags=["Profile"])


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current user's profile."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse.model_validate(profile)


@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    updates: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user profile fields."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(profile, field):
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return ProfileResponse.model_validate(profile)


@router.get("/profile/completion")
def get_profile_completion(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get profile completion percentage."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        return {"completion": 0, "missing_fields": []}

    fields_map = {
        "name": profile.name,
        "age": profile.age,
        "gender": profile.gender,
        "state": profile.state,
        "occupation": profile.occupation,
        "annual_income": profile.annual_income,
        "category": profile.category,
        "education": profile.education,
        "family_size": profile.family_size,
        "marital_status": profile.marital_status,
    }

    missing = [k for k, v in fields_map.items() if v is None or v == ""]

    return {
        "completion": profile.completion_percentage,
        "missing_fields": missing,
        "total_fields": len(fields_map),
        "filled_fields": len(fields_map) - len(missing),
    }
