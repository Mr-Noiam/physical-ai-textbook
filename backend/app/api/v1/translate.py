"""
Translation API Endpoint

Provides HTTP API for translating textbook content to multiple languages.
Includes caching support to minimize API costs and improve response times.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.services.translation import (
    translate_content,
    translate_multiple,
    SUPPORTED_LANGUAGES
)
from app.db.models import User
from app.db.neon import get_db
from app.auth.dependencies import get_current_user_optional
from sqlalchemy.orm import Session


# Create API router
router = APIRouter(prefix="/api/v1/translate", tags=["translate"])


# Request/Response models
class TranslateRequest(BaseModel):
    """Request body for translating content."""
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Content to translate"
    )
    target_language: str = Field(
        default="ur",
        description="Target language code (e.g., 'ur' for Urdu)"
    )
    source_language: str = Field(
        default="en",
        description="Source language code (default: 'en')"
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use caching (default: True)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "# ROS 2 Fundamentals\n\nROS 2 is a flexible framework for robot software...",
                "target_language": "ur",
                "source_language": "en",
                "use_cache": True
            }
        }


class TranslateMultipleRequest(BaseModel):
    """Request body for translating multiple content items."""
    contents: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of content items to translate"
    )
    target_language: str = Field(
        default="ur",
        description="Target language code"
    )
    source_language: str = Field(
        default="en",
        description="Source language code"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "contents": [
                    "ROS 2 is a robotics framework",
                    "Nodes are independent processes",
                    "Topics enable message passing"
                ],
                "target_language": "ur",
                "source_language": "en"
            }
        }


class TranslateResponse(BaseModel):
    """Response from translation API."""
    original_content: str
    translated_content: str
    source_language: str
    target_language: str
    cached: bool = Field(
        ...,
        description="Whether the translation was retrieved from cache"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "original_content": "ROS 2 is a robotics framework",
                "translated_content": "ROS 2 روبوٹکس فریم ورک ہے",
                "source_language": "en",
                "target_language": "ur",
                "cached": False,
                "timestamp": "2025-01-10T12:00:00"
            }
        }


class TranslateMultipleResponse(BaseModel):
    """Response from multiple translations."""
    translations: List[TranslateResponse]
    total: int
    cached_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LanguagesResponse(BaseModel):
    """Response listing supported languages."""
    languages: dict[str, str]
    total: int


@router.post("/", response_model=TranslateResponse)
async def translate_text(
    request: TranslateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Translate content to target language.

    This endpoint:
    1. Checks cache for existing translation (if use_cache=True)
    2. Calls OpenAI API if not cached
    3. Saves translation to cache
    4. Returns translated content with metadata

    Args:
        request: Translation request with content and language codes
        db: Database session (injected)
        current_user: Optional authenticated user (injected)

    Returns:
        Translated content with source/target languages and cache status

    Raises:
        HTTPException: If translation fails or language is unsupported
    """
    try:
        # Get user_id if authenticated
        user_id = str(current_user.id) if current_user else None

        # Translate content
        translation_response = translate_content(
            content=request.content,
            target_language=request.target_language,
            source_language=request.source_language,
            db=db,
            user_id=user_id,
            use_cache=request.use_cache
        )

        # Return response
        return TranslateResponse(
            original_content=translation_response.original_content,
            translated_content=translation_response.translated_content,
            source_language=translation_response.source_language,
            target_language=translation_response.target_language,
            cached=translation_response.cached
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print(f"Error in translate endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/multiple", response_model=TranslateMultipleResponse)
async def translate_multiple_texts(
    request: TranslateMultipleRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Translate multiple content items in a single request.

    Useful for translating multiple sections or paragraphs efficiently.
    Each item is cached separately for reuse.

    Args:
        request: Multiple translation request
        db: Database session (injected)
        current_user: Optional authenticated user (injected)

    Returns:
        List of translations with aggregate statistics

    Raises:
        HTTPException: If translation fails
    """
    try:
        # Get user_id if authenticated
        user_id = str(current_user.id) if current_user else None

        # Translate all contents
        translation_responses = translate_multiple(
            contents=request.contents,
            target_language=request.target_language,
            source_language=request.source_language,
            db=db,
            user_id=user_id
        )

        # Convert to response models
        translations = [
            TranslateResponse(
                original_content=resp.original_content,
                translated_content=resp.translated_content,
                source_language=resp.source_language,
                target_language=resp.target_language,
                cached=resp.cached
            )
            for resp in translation_responses
        ]

        # Calculate statistics
        cached_count = sum(1 for t in translations if t.cached)

        return TranslateMultipleResponse(
            translations=translations,
            total=len(translations),
            cached_count=cached_count
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print(f"Error in translate_multiple endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@router.get("/languages", response_model=LanguagesResponse)
async def get_supported_languages():
    """
    Get list of supported languages.

    Returns:
        Dictionary of language codes to language names

    Example response:
    {
        "languages": {
            "ur": "Urdu",
            "ar": "Arabic",
            "hi": "Hindi",
            ...
        },
        "total": 15
    }
    """
    return LanguagesResponse(
        languages=SUPPORTED_LANGUAGES,
        total=len(SUPPORTED_LANGUAGES)
    )


@router.get("/health")
async def health_check():
    """Check if translation API is running."""
    return {
        "status": "healthy",
        "service": "translation",
        "version": "1.0.0",
        "supported_languages": len(SUPPORTED_LANGUAGES)
    }
