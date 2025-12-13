"""
Functions for generating text embeddings using OpenAI.
"""
import logging
from openai import OpenAI, APIError
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
# The client automatically picks up the OPENAI_API_KEY from the environment,
# which is loaded by the Settings class.
client = OpenAI(api_key=settings.openai_api_key)

def generate_embedding(text: str) -> list[float] | None:
    """
    Generates an embedding for the given text using the configured OpenAI model.

    Args:
        text: The input string to embed.

    Returns:
        A list of floats representing the embedding, or None if an error occurs.
    """
    if not text or not isinstance(text, str):
        logger.warning("generate_embedding called with invalid input.")
        return None

    try:
        response = client.embeddings.create(
            input=[text.replace("\n", " ")],  # OpenAI recommends replacing newlines
            model=settings.openai_embedding_model
        )
        embedding = response.data[0].embedding
        logger.info(f"Successfully generated embedding for text snippet: '{text[:50]}...'")
        return embedding
    except APIError as e:
        logger.error(f"OpenAI API error while generating embedding: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during embedding generation: {e}")
        return None