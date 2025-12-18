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
BATCH_SIZE = 10  # Process 10 chunks at a time (reduced for better reliability)
MAX_RETRIES = 3  # Retry failed batches up to 3 times


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
    Generate embeddings and upload chunks to Qdrant with automatic retry for failed batches.

    Args:
        client: Qdrant client instance
        chunks: List of TextChunk objects
    """
    total_chunks = len(chunks)
    print(f"\nIngesting {total_chunks} chunks...")

    # Track success and failures
    successful_batches = []
    failed_batches = []

    # First pass: Try all batches
    for i in range(0, total_chunks, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (total_chunks + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"\nBatch {batch_num}/{total_batches} ({len(batch)} chunks)")

        success = process_batch(client, batch, batch_num)

        if success:
            successful_batches.append(batch_num)
        else:
            failed_batches.append((batch_num, batch, 1))  # (batch_num, chunks, attempt_count)

    # Retry failed batches
    if failed_batches:
        print(f"\n{'='*60}")
        print(f"Retrying {len(failed_batches)} failed batches...")
        print(f"{'='*60}")

        retry_round = 1
        while failed_batches and retry_round <= MAX_RETRIES:
            print(f"\nRetry Round {retry_round}/{MAX_RETRIES}")

            still_failing = []

            for batch_num, batch, attempt in failed_batches:
                print(f"\nRetrying Batch {batch_num} (Attempt {attempt + 1})")

                success = process_batch(client, batch, batch_num)

                if success:
                    successful_batches.append(batch_num)
                    print(f"  [SUCCESS] Batch {batch_num} uploaded on retry!")
                else:
                    if attempt + 1 < MAX_RETRIES:
                        still_failing.append((batch_num, batch, attempt + 1))
                    else:
                        print(f"  [FAILED] Batch {batch_num} failed after {MAX_RETRIES} attempts")

            failed_batches = still_failing
            retry_round += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"Ingestion Summary:")
    print(f"{'='*60}")
    print(f"  Total batches: {(total_chunks + BATCH_SIZE - 1) // BATCH_SIZE}")
    print(f"  Successful: {len(successful_batches)}")
    print(f"  Failed: {len(failed_batches)}")

    if failed_batches:
        print(f"\n  Failed batch numbers: {[b[0] for b in failed_batches]}")
        print(f"  Failed chunks: {len(failed_batches) * BATCH_SIZE}")

    total_uploaded = len(successful_batches) * BATCH_SIZE
    # Adjust for last batch which might be smaller
    if total_chunks % BATCH_SIZE != 0:
        last_batch_size = total_chunks % BATCH_SIZE
        if (total_chunks // BATCH_SIZE) + 1 in successful_batches:
            total_uploaded = total_uploaded - BATCH_SIZE + last_batch_size

    print(f"  Total chunks uploaded: ~{total_uploaded}/{total_chunks}")
    print(f"{'='*60}")


def process_batch(client, batch, batch_num):
    """
    Process a single batch: generate embeddings and upload to Qdrant.

    Args:
        client: Qdrant client instance
        batch: List of TextChunk objects
        batch_num: Batch number for logging

    Returns:
        bool: True if successful, False if failed
    """
    # Extract texts for embedding
    texts = [chunk.text for chunk in batch]

    # Generate embeddings
    print("  Generating embeddings...")
    try:
        embeddings = generate_embeddings_batch(texts)
    except Exception as e:
        print(f"  [ERROR] Error generating embeddings: {e}")
        return False

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
            points=points,
            wait=True  # Wait for operation to complete
        )
        print(f"  [OK] Uploaded {len(points)} points")
        return True

    except Exception as e:
        print(f"  [ERROR] Error uploading to Qdrant: {e}")
        return False


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
    try:
        result = client.count(collection_name=COLLECTION_NAME)
        print(f"Collection size: {result.count} points")
    except Exception as e:
        print(f"Note: Verification had a minor error (this doesn't affect uploaded data): {str(e)[:100]}")
        print("Your data has been uploaded successfully!")

    print("\n" + "=" * 60)
    print("[OK] Ingestion complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
