"""
RAG Retrieval Module

Performs semantic search over the textbook content using Qdrant vector database.
Returns the most relevant chunks for a given question.
"""

from typing import List, Dict
from app.db.qdrant import get_qdrant_client, qdrant_service
from app.rag.embeddings import generate_embedding


# Use collection name from settings instead of hardcoded value
def get_collection_name():
    """Get the configured Qdrant collection name."""
    return qdrant_service.collection_name

DEFAULT_TOP_K = 3  # Return top 3 most relevant chunks (faster, still accurate)


class SearchResult:
    """Represents a search result from vector similarity search."""

    def __init__(self, text: str, source_file: str, section_title: str, score: float):
        self.text = text
        self.source_file = source_file
        self.section_title = section_title
        self.score = score  # Similarity score (0-1, higher is better)

    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses."""
        return {
            "text": self.text,
            "source": self.source_file,
            "section": self.section_title,
            "relevance_score": round(self.score, 3)
        }

    def __repr__(self):
        return f"SearchResult(source={self.source_file}, score={self.score:.3f})"


def search_similar_chunks(query: str, top_k: int = DEFAULT_TOP_K) -> List[SearchResult]:
    """
    Search for chunks semantically similar to the query.

    Args:
        query: User's question or search query
        top_k: Number of results to return (default 5)

    Returns:
        List of SearchResult objects, sorted by relevance (highest first)

    Raises:
        Exception: If search fails
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    try:
        # 1. Generate embedding for query
        query_embedding = generate_embedding(query)

        # 2. Connect to Qdrant
        client = get_qdrant_client()

        # 3. Search for similar vectors
        collection_name = get_collection_name()
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=0.6  # Only return results with >60% similarity (lowered for better recall)
        )

        # 4. Convert to SearchResult objects
        results = []
        for hit in search_results:
            result = SearchResult(
                text=hit.payload["text"],
                source_file=hit.payload["source_file"],
                section_title=hit.payload["section_title"],
                score=hit.score
            )
            results.append(result)

        return results

    except Exception as e:
        print(f"Error during search: {e}")
        raise


def format_context_for_prompt(search_results: List[SearchResult]) -> str:
    """
    Format search results into a context string for the LLM prompt.

    Args:
        search_results: List of SearchResult objects

    Returns:
        Formatted context string with sources
    """
    if not search_results:
        return "No relevant information found in the textbook."

    context_parts = []

    for i, result in enumerate(search_results, 1):
        context_parts.append(
            f"[Source {i}: {result.section_title}]\n{result.text}\n"
        )

    return "\n".join(context_parts)


def get_unique_sources(search_results: List[SearchResult]) -> List[Dict]:
    """
    Extract unique source files from search results.

    Args:
        search_results: List of SearchResult objects

    Returns:
        List of dicts with source file and section title
    """
    sources = []
    seen = set()

    for result in search_results:
        key = (result.source_file, result.section_title)
        if key not in seen:
            sources.append({
                "file": result.source_file,
                "section": result.section_title,
                "url": f"/docs/{result.source_file.replace('.md', '')}"
            })
            seen.add(key)

    return sources


# Example usage
if __name__ == "__main__":
    # Test search
    test_queries = [
        "What is a ROS 2 node?",
        "How do I create a URDF file?",
        "Explain Isaac Sim synthetic data generation"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)

        try:
            results = search_similar_chunks(query, top_k=3)

            if results:
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.section_title} (score: {result.score:.3f})")
                    print(f"   Source: {result.source_file}")
                    print(f"   Preview: {result.text[:150]}...")
            else:
                print("No results found")

        except Exception as e:
            print(f"Search failed: {e}")
