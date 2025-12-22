"""
Authentication API endpoints.

Provides user signup, login, logout, and profile management.
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.db.neon import get_db
from app.db.models import User
from app.auth.jwt import (
    create_access_token,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/auth")


# Request/Response Models
class SignupRequest(BaseModel):
    """User signup request."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    software_background: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    hardware_background: Optional[str] = Field(None, pattern="^(no_experience|hobbyist|professional)$")


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds


class UserResponse(BaseModel):
    """User profile response."""

    id: str
    email: str
    software_background: Optional[str]
    hardware_background: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# Endpoints
@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        request: Signup request with email, password, and optional background
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        software_background=request.software_background,
        hardware_background=request.hardware_background,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.

    Args:
        request: Login request with email and password
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.

    Args:
        current_user: Authenticated user from dependency

    Returns:
        User profile information
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        software_background=current_user.software_background,
        hardware_background=current_user.hardware_background,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
    )


@router.post("/logout")
def logout():
    """
    Logout user (client should delete token).

    Note: JWT tokens are stateless, so logout is handled client-side
    by deleting the token from storage.

    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
