"""Test script to check Qdrant collections and their contents."""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.qdrant import get_qdrant_client, qdrant_service
from app.config import settings

def main():
    print("=" * 60)
    print("Qdrant Collections Check")
    print("=" * 60)

    # Get client
    client = get_qdrant_client()

    # Get all collections
    print("\n1. Fetching all collections...")
    try:
        collections = client.get_collections()
        print(f"   Found {len(collections.collections)} collection(s):")
        for col in collections.collections:
            print(f"     - {col.name}")

            # Get collection info
            try:
                info = client.get_collection(col.name)
                count = client.count(collection_name=col.name)
                print(f"       Points: {count.count}")
                print(f"       Vector size: {info.config.params.vectors.size}")
            except Exception as e:
                print(f"       Error getting info: {e}")
    except Exception as e:
        print(f"   [ERROR] {e}")
        return

    # Check configured collection
    print(f"\n2. Checking configured collection: '{qdrant_service.collection_name}'")
    print(f"   (from env: QDRANT_COLLECTION_NAME or default: 'physical_ai_textbook')")

    exists = qdrant_service.collection_exists()
    print(f"   Exists: {exists}")

    if not exists:
        print("\n   [ISSUE] Configured collection does not exist!")
        print("   The chatbot is looking for a collection that doesn't exist.")

        if collections.collections:
            print("\n   Possible solutions:")
            print("   1. Update QDRANT_COLLECTION_NAME in .env to match an existing collection")
            print("   2. Run the ingestion script to create the collection")
            for col in collections.collections:
                print(f"      - To use '{col.name}', set: QDRANT_COLLECTION_NAME={col.name}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
