"""
Qdrant Cloud vector database client for RAG implementation.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import settings


class QdrantService:
    """Qdrant vector database service."""

    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection_name

    def create_collection(self, vector_size: int = 1536):
        """
        Create Qdrant collection for storing text embeddings.

        Args:
            vector_size: Dimension of embedding vectors (1536 for text-embedding-3-small)
        """
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,  # Cosine similarity for semantic search
            ),
        )

    def collection_exists(self) -> bool:
        """Check if collection exists."""
        try:
            self.client.get_collection(self.collection_name)
            return True
        except Exception:
            return False


# Global Qdrant service instance
qdrant_service = QdrantService()


def get_qdrant_client():
    """Get the Qdrant client instance."""
    return qdrant_service.client


# DATA STRUCTURES - Complete Content List
