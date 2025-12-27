"""
Translation Service

Provides text translation functionality using Gemini (free) or OpenAI API with caching support.
Supports translation to multiple languages with a focus on Urdu for accessibility.

Provider Comparison:
- Gemini (default): FREE - 1,500 requests/day, 15 RPM, 1M tokens/month
- OpenAI: PAID - $0.15-0.60 per 1M tokens (fast but costs money)
"""

from typing import Optional
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import TranslationCache

# Initialize API clients
openai_client = None
gemini_client = None
gemini_model = None

# Always initialize OpenAI client (for fallback even when using Gemini)
try:
    openai_client = OpenAI(api_key=settings.openai_api_key)
except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")

# Initialize Gemini client if using Gemini provider
if settings.translation_provider == "gemini" and settings.gemini_api_key:
    try:
        from google import genai
        from google.genai import types

        # Initialize with new SDK
        gemini_client = genai.Client(api_key=settings.gemini_api_key)
        # Use stable model: gemini-1.5-flash (reliable, fast, free tier compatible)
        gemini_model = "gemini-1.5-flash"
        print(f"Gemini API initialized with model: {gemini_model}")
    except Exception as e:
        print(f"Warning: Could not initialize Gemini client: {e}")
        print("Will use OpenAI as primary provider...")
        settings.translation_provider = "openai"
        gemini_client = None
        gemini_model = None

# Model configuration
OPENAI_MODEL = "gpt-4o-mini"  # Fast and cost-effective for translations
MAX_TOKENS = 2000  # Allow for longer translated content
TEMPERATURE = 0.3  # Lower temperature for more consistent translations


class TranslationResponse:
    """Represents a translation response with metadata."""

    def __init__(
        self,
        original_content: str,
        translated_content: str,
        source_language: str,
        target_language: str,
        cached: bool = False
    ):
        self.original_content = original_content
        self.translated_content = translated_content
        self.source_language = source_language
        self.target_language = target_language
        self.cached = cached

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "original_content": self.original_content,
            "translated_content": self.translated_content,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "cached": self.cached
        }


# Language configuration
SUPPORTED_LANGUAGES = {
    "ur": "Urdu",
    "ar": "Arabic",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ru": "Russian",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
}


def get_language_name(code: str) -> str:
    """Get full language name from language code."""
    return SUPPORTED_LANGUAGES.get(code, code.upper())


def check_translation_cache(
    db: Session,
    original_content: str,
    source_language: str,
    target_language: str,
    user_id: Optional[str] = None
) -> Optional[TranslationCache]:
    """
    Check if translation exists in cache.

    Args:
        db: Database session
        original_content: Original text to translate
        source_language: Source language code (e.g., "en")
        target_language: Target language code (e.g., "ur")
        user_id: Optional user ID for user-specific cache

    Returns:
        TranslationCache object if found, None otherwise
    """
    try:
        query = db.query(TranslationCache).filter(
            TranslationCache.original_content == original_content,
            TranslationCache.source_language == source_language,
            TranslationCache.target_language == target_language
        )

        # Optionally filter by user_id if provided
        if user_id:
            query = query.filter(TranslationCache.user_id == user_id)

        return query.first()

    except Exception as e:
        print(f"Error checking translation cache: {e}")
        return None


def save_translation_to_cache(
    db: Session,
    original_content: str,
    translated_content: str,
    source_language: str,
    target_language: str,
    user_id: Optional[str] = None
) -> bool:
    """
    Save translation to cache.

    Args:
        db: Database session
        original_content: Original text
        translated_content: Translated text
        source_language: Source language code
        target_language: Target language code
        user_id: Optional user ID

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        cache_entry = TranslationCache(
            user_id=user_id,
            original_content=original_content,
            translated_content=translated_content,
            source_language=source_language,
            target_language=target_language
        )
        db.add(cache_entry)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        print(f"Error saving translation to cache: {e}")
        return False


def translate_content(
    content: str,
    target_language: str = "ur",
    source_language: str = "en",
    db: Optional[Session] = None,
    user_id: Optional[str] = None,
    use_cache: bool = True
) -> TranslationResponse:
    """
    Translate content to target language using Gemini (free) or OpenAI API.

    Provider is configured via TRANSLATION_PROVIDER env variable:
    - "gemini" (default): FREE - 1,500 requests/day, 15 RPM
    - "openai": PAID - $0.15-0.60 per 1M tokens

    Workflow:
    1. Check cache if enabled
    2. If not cached, call Gemini/OpenAI API for translation
    3. Save to cache for future use
    4. Return translation response

    Args:
        content: Text content to translate
        target_language: Target language code (default: "ur" for Urdu)
        source_language: Source language code (default: "en" for English)
        db: Optional database session for caching
        user_id: Optional user ID for user-specific cache
        use_cache: Whether to use caching (default: True)

    Returns:
        TranslationResponse with translated content and metadata

    Raises:
        ValueError: If content is empty or languages are invalid
        Exception: If translation fails
    """
    # Validation
    if not content or not content.strip():
        raise ValueError("Content cannot be empty")

    if target_language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported target language: {target_language}. "
            f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}"
        )

    # Check cache if enabled and db session provided
    if use_cache and db:
        cached_translation = check_translation_cache(
            db, content, source_language, target_language, user_id
        )

        if cached_translation:
            return TranslationResponse(
                original_content=content,
                translated_content=cached_translation.translated_content,
                source_language=source_language,
                target_language=target_language,
                cached=True
            )

    try:
        # Build translation prompt
        target_lang_name = get_language_name(target_language)
        source_lang_name = get_language_name(source_language)

        # Build system prompt with language-specific instructions
        base_system_prompt = f"""You are a professional translator specializing in technical and educational content.

Your task is to translate text from {source_lang_name} to {target_lang_name} while:
1. Maintaining technical accuracy and terminology
2. Preserving the original meaning and tone
3. Keeping code snippets, URLs, and technical terms unchanged
4. Adapting idioms and cultural references appropriately
5. Ensuring the translation is natural and readable in {target_lang_name}

Special instructions for technical content:
- Keep programming keywords, function names, and code syntax in English
- Translate comments and documentation strings
- Preserve markdown formatting
- Keep technical terms that don't have common translations

Return ONLY the translated text without explanations or notes."""

        # Add Urdu-specific instructions for better quality
        if target_language == "ur":
            urdu_instructions = """

IMPORTANT URDU-SPECIFIC GUIDELINES:
1. Use proper Urdu/Arabic words instead of English transliterations where possible:
   - "Hello" → "السلام علیکم" or "نمستے" (not "ہیلو")
   - "Welcome" → "خوش آمدید" ✓ (this is correct)
   - "Course" → "نصاب" or "کورس" (both acceptable)
   - "Robotics" → "روبوٹکس" (acceptable as technical term)

2. Use formal/standard Urdu (فصیح اردو) suitable for educational content
3. For technical terms without Urdu equivalents, use English or transliteration
4. Maintain right-to-left text direction properly
5. Use appropriate honorifics and formal tone for educational material

EXAMPLES OF GOOD URDU TRANSLATION:
- "Hello, welcome!" → "السلام علیکم، خوش آمدید!"
- "Introduction to..." → "...کا تعارف"
- "Please note..." → "براہ کرم نوٹ کریں..."
- "Click here" → "یہاں کلک کریں"
"""
            system_prompt = base_system_prompt + urdu_instructions
        else:
            system_prompt = base_system_prompt

        user_prompt = f"""Translate the following {source_lang_name} text to {target_lang_name}:

{content}"""

        # Call translation API based on configured provider
        if settings.translation_provider == "gemini" and gemini_client and gemini_model:
            try:
                # Use Gemini API (FREE) with new SDK
                full_prompt = f"{system_prompt}\n\n{user_prompt}"

                response = gemini_client.models.generate_content(
                    model=gemini_model,
                    contents=full_prompt
                )

                translated_content = response.text.strip()

            except Exception as gemini_error:
                # If Gemini fails (quota, rate limit, etc.), fallback to OpenAI
                error_msg = str(gemini_error)
                print(f"Gemini API error: {error_msg[:200]}...")

                # Check if it's a quota/rate limit error
                if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    print("WARNING: Gemini quota/rate limit exceeded. Falling back to OpenAI...")
                else:
                    print("WARNING: Gemini API error. Falling back to OpenAI...")

                # Fallback to OpenAI
                if not openai_client:
                    raise Exception("Both Gemini and OpenAI failed. Please check API keys.")

                response = openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE
                )
                translated_content = response.choices[0].message.content.strip()
                print("SUCCESS: Used OpenAI fallback successfully")

        else:
            # Use OpenAI API (PAID - fallback)
            if not openai_client:
                raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY.")

            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            translated_content = response.choices[0].message.content.strip()

        # Save to cache if db session provided
        if db:
            save_translation_to_cache(
                db,
                content,
                translated_content,
                source_language,
                target_language,
                user_id
            )

        return TranslationResponse(
            original_content=content,
            translated_content=translated_content,
            source_language=source_language,
            target_language=target_language,
            cached=False
        )

    except Exception as e:
        print(f"Error translating content: {e}")
        raise Exception(f"Translation failed: {str(e)}")


def translate_multiple(
    contents: list[str],
    target_language: str = "ur",
    source_language: str = "en",
    db: Optional[Session] = None,
    user_id: Optional[str] = None
) -> list[TranslationResponse]:
    """
    Translate multiple content items.

    Args:
        contents: List of text contents to translate
        target_language: Target language code (default: "ur")
        source_language: Source language code (default: "en")
        db: Optional database session for caching
        user_id: Optional user ID

    Returns:
        List of TranslationResponse objects
    """
    results = []

    for content in contents:
        try:
            result = translate_content(
                content,
                target_language=target_language,
                source_language=source_language,
                db=db,
                user_id=user_id
            )
            results.append(result)
        except Exception as e:
            print(f"Error translating content: {e}")
            # Add error response
            results.append(
                TranslationResponse(
                    original_content=content,
                    translated_content=f"[Translation error: {str(e)}]",
                    source_language=source_language,
                    target_language=target_language,
                    cached=False
                )
            )

    return results


# Example usage
if __name__ == "__main__":
    # Test translation
    test_content = """
# ROS 2 Fundamentals

ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software.
It is a collection of tools, libraries, and conventions that aim to simplify the task
of creating complex and robust robot behavior across a wide variety of robotic platforms.

## Key Concepts

1. **Nodes**: Independent processes that perform computation
2. **Topics**: Named buses for message passing between nodes
3. **Services**: Request/response communication pattern
"""

    try:
        # Translate to Urdu
        print("Translating to Urdu...")
        response = translate_content(test_content, target_language="ur")

        print("\n" + "=" * 70)
        print(f"Translation: {response.source_language} → {response.target_language}")
        print("=" * 70)
        print(response.translated_content)
        print("\n" + "=" * 70)
        print(f"Cached: {response.cached}")

    except Exception as e:
        print(f"Error: {e}")
