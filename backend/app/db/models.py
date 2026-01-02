"""
SQLAlchemy database models for Physical AI textbook backend.

Models:
- User: User accounts with authentication
- ChatMessage: Chat history between users and RAG chatbot
- PersonalizationCache: Cached personalized content
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.neon import Base


class User(Base):
    """User model for authentication and personalization."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Better Auth manages this
    name = Column(String(255), nullable=True)
    email_verified = Column(DateTime(timezone=True), nullable=True)
    image = Column(String(500), nullable=True)
    software_background = Column(
        Enum("beginner", "intermediate", "advanced", name="software_level"),
        nullable=True,
    )
    hardware_background = Column(
        Enum("no_experience", "hobbyist", "professional", name="hardware_level"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    chat_messages = relationship("ChatMessage", back_populates="user")
    personalizations = relationship("PersonalizationCache", back_populates="user")
    sessions = relationship("Session", back_populates="user")


class ChatMessage(Base):
    """Chat message model for storing conversation history."""

    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    context = Column(Text, nullable=True)  # Retrieved context from RAG
    selected_text = Column(Text, nullable=True)  # User-highlighted text
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_messages")


class PersonalizationCache(Base):
    """Cache for personalized content to avoid redundant API calls."""

    __tablename__ = "personalization_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    original_content = Column(Text, nullable=False)
    personalized_content = Column(Text, nullable=False)
    software_level = Column(String(50), nullable=False)
    hardware_level = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="personalizations")


class Session(Base):
    """Better Auth session model."""

    __tablename__ = "sessions"

    id = Column(String(255), primary_key=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    token = Column(String(500), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")


class TranslationCache(Base):
    """Cache for Urdu translations to avoid redundant API calls."""

    __tablename__ = "translation_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_path = Column(String(255), nullable=False)
    language_code = Column(String(10), nullable=False, default="ur")  # Only Urdu for now
    original_content = Column(Text, nullable=False)
    translated_content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Composite unique constraint: same content shouldn't be translated twice
    __table_args__ = (
        {"schema": None},
    )


class Account(Base):
    """Better Auth account model for OAuth providers."""

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(String(255), nullable=False)
    provider_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    id_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    scope = Column(String(500), nullable=True)
    password = Column(String(255), nullable=True)  # For email/password provider
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
