"""
Translation API Endpoints

Provides Urdu translation for authenticated users.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from app.db.models import User
from app.db.neon import get_db
from app.services.translation import translate_to_urdu, translate_multiple
from app.auth.dependencies import get_current_user_required

router = APIRouter(prefix="/api/v1/translate", tags=["translation"])


class TranslateRequest(BaseModel):
    """Request body for translation."""
    content: str = Field(..., description="English content to translate")
    chapter_path: str = Field(..., description="Path to chapter (for caching)")


class TranslateResponse(BaseModel):
    """Response from translation endpoint."""
    original_content: str
    translated_content: str
    cached: bool
    chapter_path: str


class TranslateMultipleRequest(BaseModel):
    """Request body for batch translation."""
    contents: list[str] = Field(..., description="List of English contents to translate")
    chapter_paths: list[str] = Field(..., description="List of chapter paths (must match contents length)")


class TranslateMultipleResponse(BaseModel):
    """Response from batch translation endpoint."""
    results: list[dict]
    total: int
    cached_count: int


@router.post("/", response_model=TranslateResponse)
async def translate(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Translate English content to Urdu.

    Requires authentication. Uses GPT-4 for translation with caching.

    Args:
        request: Translation request with content and chapter path
        current_user: Authenticated user (from session)
        db: Database session

    Returns:
        Original and translated content with cache status

    Raises:
        HTTPException: 401 if not authenticated, 500 if translation fails
    """
    try:
        translated_content, cached = await translate_to_urdu(
            content=request.content,
            chapter_path=request.chapter_path,
            db=db
        )

        return TranslateResponse(
            original_content=request.content,
            translated_content=translated_content,
            cached=cached,
            chapter_path=request.chapter_path
        )

    except Exception as e:
        print(f"Translation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/multiple", response_model=TranslateMultipleResponse)
async def translate_batch(
    request: TranslateMultipleRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Translate multiple content blocks to Urdu in batch.

    Requires authentication. More efficient than multiple single requests.

    Args:
        request: Batch translation request with contents and chapter paths
        current_user: Authenticated user (from session)
        db: Database session

    Returns:
        Translation results with cache statistics

    Raises:
        HTTPException: 401 if not authenticated, 400 if lengths don't match, 500 if translation fails
    """
    if len(request.contents) != len(request.chapter_paths):
        raise HTTPException(
            status_code=400,
            detail="Contents and chapter_paths must have the same length"
        )

    try:
        results = await translate_multiple(
            contents=request.contents,
            chapter_paths=request.chapter_paths,
            db=db
        )

        cached_count = sum(1 for r in results if r["cached"])

        return TranslateMultipleResponse(
            results=results,
            total=len(results),
            cached_count=cached_count
        )

    except Exception as e:
        print(f"Batch translation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch translation failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for translation service.

    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "translation",
        "supported_languages": ["ur"],  # Urdu only
    }
