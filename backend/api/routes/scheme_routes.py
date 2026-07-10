"""
GOVs-AI Scheme & Recommendation Routes
GET /api/schemes — browse schemes
GET /api/recommendations — personalized recommendations
POST /api/bookmark — save a scheme
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.connection import get_db
from database.models import User, GovernmentScheme, Recommendation, Bookmark
from api.auth import get_current_user
from utils.validators import (
    SchemeResponse, RecommendationResponse, BookmarkRequest, BookmarkResponse,
)

router = APIRouter(prefix="/api", tags=["Schemes"])


@router.get("/schemes", response_model=List[SchemeResponse])
def list_schemes(
    category: Optional[str] = None,
    state: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List all active government schemes with optional filters."""
    query = db.query(GovernmentScheme).filter(GovernmentScheme.is_active == True)

    if category:
        query = query.filter(GovernmentScheme.category.ilike(f"%{category}%"))
    if state:
        query = query.filter(
            (GovernmentScheme.state.ilike(f"%{state}%")) | (GovernmentScheme.state == "Central")
        )
    if search:
        query = query.filter(
            (GovernmentScheme.name.ilike(f"%{search}%")) |
            (GovernmentScheme.description.ilike(f"%{search}%"))
        )

    schemes = query.offset(skip).limit(limit).all()
    return [SchemeResponse.model_validate(s) for s in schemes]


@router.get("/schemes/{scheme_id}", response_model=SchemeResponse)
def get_scheme(scheme_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific scheme."""
    scheme = db.query(GovernmentScheme).filter(GovernmentScheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return SchemeResponse.model_validate(scheme)


@router.get("/recommendations", response_model=List[RecommendationResponse])
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get personalized scheme recommendations for the current user."""
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == current_user.id)
        .order_by(Recommendation.score.desc())
        .limit(10)
        .all()
    )

    result = []
    for rec in recs:
        scheme = db.query(GovernmentScheme).filter(GovernmentScheme.id == rec.scheme_id).first()
        if scheme:
            result.append(RecommendationResponse(
                id=rec.id,
                scheme=SchemeResponse.model_validate(scheme),
                score=rec.score,
                reasoning=rec.reasoning,
                checklist=rec.checklist,
                created_at=rec.created_at,
            ))

    return result


@router.post("/bookmark", response_model=BookmarkResponse)
def create_bookmark(
    request: BookmarkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bookmark a government scheme."""
    # Check scheme exists
    scheme = db.query(GovernmentScheme).filter(GovernmentScheme.id == request.scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Check if already bookmarked
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.scheme_id == request.scheme_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Scheme already bookmarked")

    bookmark = Bookmark(user_id=current_user.id, scheme_id=request.scheme_id)
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse(
        id=bookmark.id,
        scheme=SchemeResponse.model_validate(scheme),
        created_at=bookmark.created_at,
    )


@router.get("/bookmarks", response_model=List[BookmarkResponse])
def get_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's bookmarked schemes."""
    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id)
        .order_by(Bookmark.created_at.desc())
        .all()
    )

    result = []
    for bm in bookmarks:
        scheme = db.query(GovernmentScheme).filter(GovernmentScheme.id == bm.scheme_id).first()
        if scheme:
            result.append(BookmarkResponse(
                id=bm.id,
                scheme=SchemeResponse.model_validate(scheme),
                created_at=bm.created_at,
            ))
    return result


@router.delete("/bookmark/{scheme_id}")
def delete_bookmark(
    scheme_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a bookmarked scheme."""
    bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.scheme_id == scheme_id,
    ).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()
    return {"message": "Bookmark removed"}
