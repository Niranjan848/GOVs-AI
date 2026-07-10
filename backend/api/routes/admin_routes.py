"""
GOVs-AI Admin Routes
Admin-only endpoints for dashboard analytics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.connection import get_db
from database.models import (
    User, Chat, Message, GovernmentScheme, Recommendation,
    Document, Profile, Bookmark,
)
from api.auth import require_admin
from utils.validators import AdminStatsResponse
from rag.retriever import get_index_stats

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get admin dashboard statistics."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_chats = db.query(func.count(Chat.id)).scalar() or 0
    total_schemes = db.query(func.count(GovernmentScheme.id)).scalar() or 0
    total_documents = db.query(func.count(Document.id)).scalar() or 0
    total_recommendations = db.query(func.count(Recommendation.id)).scalar() or 0

    # Recent signups (last 7 days)
    from datetime import datetime, timedelta, timezone
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_signups = db.query(func.count(User.id)).filter(User.created_at >= week_ago).scalar() or 0

    # Popular schemes (by recommendation count)
    popular_schemes_q = (
        db.query(
            GovernmentScheme.name,
            func.count(Recommendation.id).label("count"),
        )
        .join(Recommendation, Recommendation.scheme_id == GovernmentScheme.id)
        .group_by(GovernmentScheme.name)
        .order_by(func.count(Recommendation.id).desc())
        .limit(5)
        .all()
    )
    popular_schemes = [{"name": name, "count": count} for name, count in popular_schemes_q]

    # If no recommendations yet, show bookmarked schemes
    if not popular_schemes:
        bookmarked_q = (
            db.query(
                GovernmentScheme.name,
                func.count(Bookmark.id).label("count"),
            )
            .join(Bookmark, Bookmark.scheme_id == GovernmentScheme.id)
            .group_by(GovernmentScheme.name)
            .order_by(func.count(Bookmark.id).desc())
            .limit(5)
            .all()
        )
        popular_schemes = [{"name": name, "count": count} for name, count in bookmarked_q]

    # Popular states
    popular_states_q = (
        db.query(
            Profile.state,
            func.count(Profile.id).label("count"),
        )
        .filter(Profile.state.isnot(None), Profile.state != "")
        .group_by(Profile.state)
        .order_by(func.count(Profile.id).desc())
        .limit(5)
        .all()
    )
    popular_states = [{"state": state, "count": count} for state, count in popular_states_q]

    return AdminStatsResponse(
        total_users=total_users,
        total_chats=total_chats,
        total_schemes=total_schemes,
        total_documents=total_documents,
        total_recommendations=total_recommendations,
        popular_schemes=popular_schemes,
        popular_states=popular_states,
        recent_signups=recent_signups,
    )


@router.get("/users")
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all registered users."""
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get chat analytics data."""
    # Messages per day (last 7 days)
    from datetime import datetime, timedelta, timezone
    daily_stats = []
    for i in range(7):
        day = datetime.now(timezone.utc) - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        count = db.query(func.count(Message.id)).filter(
            Message.created_at >= start,
            Message.created_at < end,
        ).scalar() or 0
        daily_stats.append({
            "date": start.strftime("%Y-%m-%d"),
            "messages": count,
        })

    # Vector DB stats
    vector_stats = get_index_stats()

    return {
        "daily_messages": list(reversed(daily_stats)),
        "vector_db": vector_stats,
    }
