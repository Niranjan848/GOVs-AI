"""
GOVs-AI Database Models
SQLAlchemy ORM models for all entities in the system.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, JSON,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database.connection import Base


class User(Base):
    """Registered user (citizen or admin)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="citizen", nullable=False)  # citizen | admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    memory = relationship("ConversationMemory", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="uploaded_by_user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    """User profile with demographic and socioeconomic data for eligibility matching."""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), default="")
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)  # male | female | other
    state = Column(String(50), nullable=True)
    district = Column(String(100), nullable=True)
    occupation = Column(String(100), nullable=True)
    annual_income = Column(Float, nullable=True)
    category = Column(String(30), nullable=True)  # general | obc | sc | st | ews
    education = Column(String(50), nullable=True)
    land_area_acres = Column(Float, nullable=True)
    has_disability = Column(Boolean, default=False)
    family_size = Column(Integer, nullable=True)
    marital_status = Column(String(20), nullable=True)
    has_bank_account = Column(Boolean, default=True)
    has_aadhaar = Column(Boolean, default=True)
    bpl_card = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="profile")

    @property
    def completion_percentage(self) -> int:
        """Calculate profile completion as a percentage."""
        fields = [
            self.name, self.age, self.gender, self.state, self.occupation,
            self.annual_income, self.category, self.education, self.family_size,
            self.marital_status
        ]
        filled = sum(1 for f in fields if f is not None and f != "")
        return int((filled / len(fields)) * 100)


class Chat(Base):
    """Chat conversation session."""
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), default="New Conversation")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    """Individual message within a chat."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)  # Stores schemes, checklists, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    chat = relationship("Chat", back_populates="messages")


class ConversationMemory(Base):
    """Persistent memory store per user for the AI agent."""
    __tablename__ = "conversation_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    memory_data = Column(JSON, default=dict)  # Extracted profile fields, summaries, interests
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="memory")


class GovernmentScheme(Base):
    """Government welfare scheme with eligibility criteria."""
    __tablename__ = "government_schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    short_name = Column(String(50), nullable=True)
    category = Column(String(50), nullable=False)  # agriculture | education | health | business | women | pension | housing | skill
    description = Column(Text, nullable=False)
    eligibility = Column(JSON, nullable=False)  # Structured eligibility criteria
    benefits = Column(Text, nullable=False)
    benefits_amount = Column(String(100), nullable=True)  # e.g., "₹6,000/year"
    documents_required = Column(JSON, nullable=False)
    application_process = Column(Text, nullable=True)
    website_url = Column(String(500), nullable=True)
    ministry = Column(String(200), nullable=True)
    state = Column(String(50), default="Central")  # Central or state name
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    recommendations = relationship("Recommendation", back_populates="scheme")
    bookmarks = relationship("Bookmark", back_populates="scheme")


class Recommendation(Base):
    """AI-generated scheme recommendation for a user."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)  # 0.0 to 1.0 eligibility confidence
    reasoning = Column(Text, nullable=True)
    checklist = Column(JSON, nullable=True)  # Document checklist items
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="recommendations")
    scheme = relationship("GovernmentScheme", back_populates="recommendations")

    __table_args__ = (
        UniqueConstraint("user_id", "scheme_id", name="uq_user_scheme"),
    )


class Bookmark(Base):
    """User's bookmarked schemes."""
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    scheme = relationship("GovernmentScheme", back_populates="bookmarks")

    __table_args__ = (
        UniqueConstraint("user_id", "scheme_id", name="uq_user_bookmark"),
    )


class Document(Base):
    """Uploaded PDF document for RAG ingestion."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    upload_path = Column(String(500), nullable=False)
    processed = Column(Boolean, default=False)
    chunks_count = Column(Integer, default=0)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    uploaded_by_user = relationship("User", back_populates="documents")


class Notification(Base):
    """User notifications for scheme updates, recommendations, etc."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    notification_type = Column(String(50), default="info")  # info | recommendation | update | alert
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="notifications")
