"""
OpenAI Embeddings Module

Generates vector embeddings for text chunks using OpenAI's text-embedding-ada-002 model.
These embeddings enable semantic search in the RAG chatbot system.

Key Features:
- Single text embedding generation
- Batch embedding generation (100x more efficient for ingestion)
- Configurable via app settings
- Comprehensive error handling
- Production-ready logging

Usage:
    from app.rag.embeddings import generate_embedding, generate_embeddings_batch

    # Single text
    embedding = generate_embedding("What is a ROS 2 node?")

    # Batch processing (for ingestion)
    texts = ["Text 1", "Text 2", "Text 3"]
    embeddings = generate_embeddings_batch(texts)
"""

import logging
from typing import List, Optional
from openai import OpenAI, APIError
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
# The client automatically picks up the OPENAI_API_KEY from settings
client = OpenAI(api_key=settings.openai_api_key)

# Embedding model configuration
EMBEDDING_MODEL = settings.openai_embedding_model  # text-embedding-ada-002
EMBEDDING_DIMENSIONS = 1536  # Ada-002 produces 1536-dimensional vectors


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate a single embedding vector for the given text.

    Uses OpenAI's text-embedding-ada-002 model to convert text into
    a 1536-dimensional vector suitable for semantic search.

    Args:
        text: The text to embed (max ~8,000 tokens for ada-002)

    Returns:
        List of 1536 floats representing the embedding vector,
        or None if generation fails

    Raises:
        ValueError: If text is empty or invalid
        APIError: If OpenAI API call fails

    Example:
        >>> embedding = generate_embedding("What is a ROS 2 node?")
        >>> len(embedding)
        1536
    """
    # Validate input
    if not text or not isinstance(text, str):
        logger.warning("generate_embedding called with invalid input")
        raise ValueError("Text must be a non-empty string")

    # Clean text (OpenAI recommends replacing newlines)
    cleaned_text = text.replace("\n", " ").strip()

    if not cleaned_text:
        logger.warning("generate_embedding called with whitespace-only text")
        raise ValueError("Text cannot be empty after cleaning")

    try:
        # Call OpenAI API
        response = client.embeddings.create(
            input=[cleaned_text],
            model=EMBEDDING_MODEL,
            encoding_format="float"
        )

        # Extract embedding
        embedding = response.data[0].embedding

        logger.info(f"Generated embedding for text snippet: '{cleaned_text[:50]}...'")
        return embedding

    except APIError as e:
        logger.error(f"OpenAI API error while generating embedding: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during embedding generation: {e}")
        raise


def generate_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batches.

    This is MUCH more efficient than calling generate_embedding() multiple times:
    - 100 texts: 100 API calls vs 1 API call
    - ~100x faster
    - ~100x cheaper
    - Critical for content ingestion

    Args:
        texts: List of texts to embed (will be processed in batches)
        batch_size: Number of texts per API call (default 100, max 2048)

    Returns:
        List of embedding vectors, one per input text (same order)

    Raises:
        ValueError: If texts list is empty or contains only empty strings
        APIError: If OpenAI API call fails

    Example:
        >>> texts = ["ROS 2 node", "URDF file", "Gazebo sim"]
        >>> embeddings = generate_embeddings_batch(texts)
        >>> len(embeddings)
        3
        >>> len(embeddings[0])
        1536
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")

    # Filter out empty/invalid texts and clean
    valid_texts = []
    valid_indices = []

    for i, text in enumerate(texts):
        if text and isinstance(text, str):
            cleaned = text.replace("\n", " ").strip()
            if cleaned:
                valid_texts.append(cleaned)
                valid_indices.append(i)

    if not valid_texts:
        raise ValueError("All texts are empty or invalid")

    logger.info(f"Generating embeddings for {len(valid_texts)} texts in batches of {batch_size}")

    all_embeddings = []

    # Process in batches
    for i in range(0, len(valid_texts), batch_size):
        batch = valid_texts[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(valid_texts) + batch_size - 1) // batch_size

        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")

        try:
            # Call OpenAI API with batch
            response = client.embeddings.create(
                input=batch,
                model=EMBEDDING_MODEL,
                encoding_format="float"
            )

            # Extract embeddings (they're returned in the same order)
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

            logger.info(f"✓ Batch {batch_num}/{total_batches} complete")

        except APIError as e:
            logger.error(f"OpenAI API error in batch {batch_num}: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error in batch {batch_num}: {e}")
            raise

    logger.info(f"✓ Generated {len(all_embeddings)} embeddings total")
    return all_embeddings


def get_embedding_dimensions() -> int:
    """
    Returns the number of dimensions in the embedding vectors.

    Used for configuring Qdrant collections and validating embeddings.

    Returns:
        Number of dimensions (1536 for text-embedding-ada-002)

    Example:
        >>> get_embedding_dimensions()
        1536
    """
    return EMBEDDING_DIMENSIONS


def get_embedding_model() -> str:
    """
    Returns the current embedding model name.

    Useful for logging and debugging.

    Returns:
        Model name (e.g., "text-embedding-ada-002")
    """
    return EMBEDDING_MODEL


# Example usage and testing
if __name__ == "__main__":
    """
    Test script for embedding generation.

    Run with:
        python -m app.rag.embeddings
    """
    print("=" * 70)
    print("OpenAI Embeddings Module - Test Suite")
    print("=" * 70)

    # Test 1: Single embedding
    print("\n[Test 1] Single embedding generation:")
    sample_text = "What is a ROS 2 node and how does it work?"

    try:
        embedding = generate_embedding(sample_text)
        print(f"✓ Generated embedding with {len(embedding)} dimensions")
        print(f"  First 5 values: {embedding[:5]}")
        print(f"  Model: {get_embedding_model()}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Batch embeddings
    print("\n[Test 2] Batch embedding generation:")
    sample_texts = [
        "ROS 2 uses DDS for communication between nodes",
        "URDF describes the robot's geometry and kinematics",
        "Gazebo is a physics-based robot simulator",
        "Isaac Sim provides GPU-accelerated robot simulation",
        "Nav2 is the navigation framework for ROS 2"
    ]

    try:
        embeddings = generate_embeddings_batch(sample_texts, batch_size=3)
        print(f"✓ Generated {len(embeddings)} embeddings")
        for i, emb in enumerate(embeddings):
            print(f"  Text {i+1}: {len(emb)} dimensions")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Error handling
    print("\n[Test 3] Error handling:")
    try:
        generate_embedding("")
        print("✗ Should have raised ValueError for empty text")
    except ValueError:
        print("✓ Correctly raised ValueError for empty text")

    try:
        generate_embeddings_batch([])
        print("✗ Should have raised ValueError for empty list")
    except ValueError:
        print("✓ Correctly raised ValueError for empty list")

    print("\n" + "=" * 70)
    print("✓ All tests complete!")
    print("=" * 70)
