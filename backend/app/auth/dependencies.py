"""Authentication dependencies for FastAPI endpoints."""
from typing import Optional
from datetime import datetime
from fastapi import Header, Cookie, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.models import User, Session as SessionModel
from app.db.neon import get_db


async def get_current_user_optional(
    session_token: Optional[str] = Cookie(None, alias="better-auth.session_token"),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from Better Auth session token (optional - returns None if not authenticated).

    This verifies the session by checking the session table in the database.
    Better Auth manages the session creation/deletion on the frontend.

    Args:
        session_token: Session token from Better Auth cookie
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if not session_token:
        return None

    try:
        # Query session from database
        session = db.query(SessionModel).filter(
            SessionModel.token == session_token,
            SessionModel.expires_at > datetime.utcnow()
        ).first()

        if not session:
            return None

        # Get user from session
        user = db.query(User).filter(User.id == session.user_id).first()
        return user

    except Exception as e:
        print(f"Error verifying session: {e}")
        return None


async def get_current_user_required(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """
    Get current user (required - raises 401 if not authenticated).

    Args:
        user: User from get_current_user_optional dependency

    Returns:
        User object

    Raises:
        HTTPException: 401 if not authenticated
    """
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please sign in."
        )
    return user
