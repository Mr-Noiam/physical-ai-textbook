"""
Content Ingestion Script

Batch-processes all Docusaurus markdown files:
1. Reads and chunks all content
2. Generates embeddings for each chunk
3. Stores in Qdrant vector database

Run this script after updating textbook content to refresh the RAG knowledge base.

Usage:
    python scripts/ingest_content.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.ingestion import read_all_markdown_files
from app.rag.embeddings import generate_embeddings_batch, EMBEDDING_DIMENSIONS
from app.db.qdrant import get_qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid


COLLECTION_NAME = "book_content"
BATCH_SIZE = 20  # Process 20 chunks at a time (smaller for free tier)


def create_collection_if_not_exists(client):
    """
    Create Qdrant collection for book content if it doesn't exist.

    Args:
        client: Qdrant client instance
    """
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if COLLECTION_NAME in collection_names:
        print(f"Collection '{COLLECTION_NAME}' already exists")

        # Optionally delete and recreate for fresh ingestion
        response = input("Delete and recreate collection? (y/n): ")
        if response.lower() == 'y':
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted collection '{COLLECTION_NAME}'")
        else:
            print("Using existing collection")
            return

    # Create collection
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=EMBEDDING_DIMENSIONS,
            distance=Distance.COSINE  # Cosine similarity for semantic search
        )
    )
    print(f"Created collection '{COLLECTION_NAME}' with {EMBEDDING_DIMENSIONS} dimensions")


def ingest_chunks(client, chunks):
    """
    Generate embeddings and upload chunks to Qdrant.

    Args:
        client: Qdrant client instance
        chunks: List of TextChunk objects
    """
    total_chunks = len(chunks)
    print(f"\nIngesting {total_chunks} chunks...")

    for i in range(0, total_chunks, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (total_chunks + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"\nBatch {batch_num}/{total_batches} ({len(batch)} chunks)")

        # Extract texts for embedding
        texts = [chunk.text for chunk in batch]

        # Generate embeddings
        print("  Generating embeddings...")
        try:
            embeddings = generate_embeddings_batch(texts)
        except Exception as e:
            print(f"  [ERROR] Error generating embeddings: {e}")
            continue

        # Prepare points for Qdrant
        points = []
        for chunk, embedding in zip(batch, embeddings):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=chunk.to_dict()
            )
            points.append(point)

        # Upload to Qdrant
        print("  Uploading to Qdrant...")
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"  [OK] Uploaded {len(points)} points")

        except Exception as e:
            print(f"  [ERROR] Error uploading to Qdrant: {e}")

    print(f"\n[OK] Ingestion complete! {total_chunks} chunks processed")


def main():
    """Main ingestion workflow."""
    print("=" * 60)
    print("Docusaurus Content Ingestion Script")
    print("=" * 60)

    # 1. Read markdown files
    docs_path = Path(__file__).parent.parent.parent / "docusaurus" / "docs"

    if not docs_path.exists():
        print(f"[ERROR] Docs directory not found at {docs_path}")
        sys.exit(1)

    print(f"\nReading markdown files from: {docs_path}")
    chunks = read_all_markdown_files(docs_path)

    if not chunks:
        print("[ERROR] No chunks created. Check markdown files.")
        sys.exit(1)

    # Show statistics
    total_words = sum(chunk.word_count for chunk in chunks)
    avg_words = total_words / len(chunks)

    print(f"\nStatistics:")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Total words: {total_words:,}")
    print(f"  Avg words per chunk: {avg_words:.1f}")

    # 2. Connect to Qdrant
    print("\nConnecting to Qdrant...")
    try:
        client = get_qdrant_client()
        print("[OK] Connected to Qdrant")
    except Exception as e:
        print(f"[ERROR] Error connecting to Qdrant: {e}")
        print("\nMake sure:")
        print("  1. Qdrant is running (or Qdrant Cloud URL is set)")
        print("  2. QDRANT_URL and QDRANT_API_KEY are in .env")
        sys.exit(1)

    # 3. Create collection
    create_collection_if_not_exists(client)

    # 4. Ingest chunks
    ingest_chunks(client, chunks)

    # 5. Verify
    print("\nVerifying ingestion...")
    collection_info = client.get_collection(COLLECTION_NAME)
    print(f"Collection size: {collection_info.points_count} points")

    print("\n" + "=" * 60)
    print("[OK] Ingestion complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
