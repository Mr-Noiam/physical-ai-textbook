"""
Authentication API Endpoints

Provides signup and signin endpoints compatible with Better Auth session format.
"""
from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import bcrypt
import secrets
import uuid

from app.db.models import User, Session as SessionModel, Account
from app.db.neon import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Truncate to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    # Truncate to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.checkpw(password_bytes, hashed.encode('utf-8'))


class SignupRequest(BaseModel):
    """Request body for user signup."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)
    software_background: str = Field(default="intermediate")
    hardware_background: str = Field(default="hobbyist")


class SigninRequest(BaseModel):
    """Request body for user signin."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Response from auth endpoints."""
    user: dict
    session: dict


def create_session(user_id: uuid.UUID, db: Session) -> SessionModel:
    """Create a new session for the user."""
    session_id = secrets.token_urlsafe(32)
    session_token = secrets.token_urlsafe(32)

    session = SessionModel(
        id=session_id,
        token=session_token,
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return session


@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Create a new user account.

    Args:
        request: Signup request with email, password, name, and background info
        response: FastAPI response object (to set cookies)
        db: Database session

    Returns:
        User and session information

    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    password_hash = hash_password(request.password)

    # Create user
    user = User(
        email=request.email,
        password_hash=password_hash,
        name=request.name,
        software_background=request.software_background,
        hardware_background=request.hardware_background,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create account entry (for Better Auth compatibility)
    account = Account(
        user_id=user.id,
        account_id=str(user.id),
        provider_id="credential",  # Email/password provider
        password=password_hash,
    )
    db.add(account)
    db.commit()

    # Create session
    session = create_session(user.id, db)

    # Set session cookie
    response.set_cookie(
        key="better-auth.session_token",
        value=session.token,
        httponly=True,
        secure=True,  # Required for cross-origin cookies with HTTPS
        samesite="none",  # Required for cross-origin requests
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return AuthResponse(
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "software_background": user.software_background,
            "hardware_background": user.hardware_background,
        },
        session={
            "id": session.id,
            "expires_at": session.expires_at.isoformat(),
        }
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    request: SigninRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Sign in an existing user.

    Args:
        request: Signin request with email and password
        response: FastAPI response object (to set cookies)
        db: Database session

    Returns:
        User and session information

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create session
    session = create_session(user.id, db)

    # Set session cookie
    response.set_cookie(
        key="better-auth.session_token",
        value=session.token,
        httponly=True,
        secure=True,  # Required for cross-origin cookies with HTTPS
        samesite="none",  # Required for cross-origin requests
        max_age=60 * 60 * 24 * 7,  # 7 days
    )

    return AuthResponse(
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "software_background": user.software_background,
            "hardware_background": user.hardware_background,
        },
        session={
            "id": session.id,
            "expires_at": session.expires_at.isoformat(),
        }
    )


@router.post("/signout")
async def signout(
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Sign out the current user.

    Args:
        response: FastAPI response object (to clear cookies)
        db: Database session

    Returns:
        Success message
    """
    # Clear session cookie
    response.delete_cookie(key="better-auth.session_token")

    return {"message": "Signed out successfully"}


@router.get("/session")
async def get_session(
    session_token: str = None,
    db: Session = Depends(get_db)
):
    """
    Get current session information.

    Args:
        session_token: Session token from cookie
        db: Database session

    Returns:
        Session and user information or null
    """
    if not session_token:
        return {"session": None, "user": None}

    # Find session
    session = db.query(SessionModel).filter(
        SessionModel.token == session_token,
        SessionModel.expires_at > datetime.utcnow()
    ).first()

    if not session:
        return {"session": None, "user": None}

    # Get user
    user = db.query(User).filter(User.id == session.user_id).first()

    if not user:
        return {"session": None, "user": None}

    return {
        "session": {
            "id": session.id,
            "expires_at": session.expires_at.isoformat(),
        },
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "software_background": user.software_background,
            "hardware_background": user.hardware_background,
        }
    }
