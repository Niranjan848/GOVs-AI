"""
GOVs-AI Auth Routes
POST /api/signup and POST /api/login endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User, Profile, ConversationMemory
from api.auth import hash_password, verify_password, create_access_token
from utils.validators import SignupRequest, LoginRequest, AuthResponse, UserResponse

router = APIRouter(prefix="/api", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role="citizen",
    )
    db.add(user)
    db.flush()  # Get user.id

    # Create empty profile
    profile = Profile(user_id=user.id, name=request.name)
    db.add(profile)

    # Create empty memory
    memory = ConversationMemory(user_id=user.id, memory_data={})
    db.add(memory)

    db.commit()
    db.refresh(user)

    # Generate JWT token
    token = create_access_token({"sub": user.id, "role": user.role})

    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token = create_access_token({"sub": user.id, "role": user.role})

    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )
