"""
GOVs-AI Input Validators
Pydantic schemas for request/response validation across all API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime
import re


# ── Auth Schemas ─────────────────────────────────────────────────
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(default="", max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


# ── User Schemas ─────────────────────────────────────────────────
class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Profile Schemas ──────────────────────────────────────────────
class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None
    education: Optional[str] = None
    land_area_acres: Optional[float] = Field(None, ge=0)
    has_disability: Optional[bool] = None
    family_size: Optional[int] = Field(None, ge=1, le=50)
    marital_status: Optional[str] = None
    has_bank_account: Optional[bool] = None
    has_aadhaar: Optional[bool] = None
    bpl_card: Optional[bool] = None

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() not in ("male", "female", "other"):
            raise ValueError("Gender must be male, female, or other")
        return v.lower() if v else None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        valid = ("general", "obc", "sc", "st", "ews")
        if v and v.lower() not in valid:
            raise ValueError(f"Category must be one of: {', '.join(valid)}")
        return v.lower() if v else None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    age: Optional[int]
    gender: Optional[str]
    state: Optional[str]
    district: Optional[str]
    occupation: Optional[str]
    annual_income: Optional[float]
    category: Optional[str]
    education: Optional[str]
    land_area_acres: Optional[float]
    has_disability: bool
    family_size: Optional[int]
    marital_status: Optional[str]
    has_bank_account: bool
    has_aadhaar: bool
    bpl_card: bool
    completion_percentage: int

    class Config:
        from_attributes = True


# ── Chat Schemas ─────────────────────────────────────────────────
class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    chat_id: Optional[int] = None  # None = start new chat

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Basic prompt injection protection."""
        # Strip common injection patterns
        dangerous_patterns = [
            r"ignore\s+(previous|above|all)\s+instructions",
            r"system\s*:\s*",
            r"<\|im_start\|>",
            r"\[INST\]",
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Invalid message content")
        return v.strip()


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    metadata_json: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ChatListItem(BaseModel):
    id: int
    title: str
    created_at: datetime
    message_count: int = 0
    last_message_preview: str = ""

    class Config:
        from_attributes = True


# ── Scheme Schemas ───────────────────────────────────────────────
class SchemeResponse(BaseModel):
    id: int
    name: str
    short_name: Optional[str]
    category: str
    description: str
    eligibility: Any
    benefits: str
    benefits_amount: Optional[str]
    documents_required: Any
    application_process: Optional[str]
    website_url: Optional[str]
    ministry: Optional[str]
    state: str
    is_active: bool

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    id: int
    scheme: SchemeResponse
    score: float
    reasoning: Optional[str]
    checklist: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Bookmark Schemas ─────────────────────────────────────────────
class BookmarkRequest(BaseModel):
    scheme_id: int


class BookmarkResponse(BaseModel):
    id: int
    scheme: SchemeResponse
    created_at: datetime

    class Config:
        from_attributes = True


# ── Notification Schemas ─────────────────────────────────────────
class NotificationResponse(BaseModel):
    id: int
    title: str
    body: str
    notification_type: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Admin Schemas ────────────────────────────────────────────────
class AdminStatsResponse(BaseModel):
    total_users: int
    total_chats: int
    total_schemes: int
    total_documents: int
    total_recommendations: int
    popular_schemes: List[dict]
    popular_states: List[dict]
    recent_signups: int
