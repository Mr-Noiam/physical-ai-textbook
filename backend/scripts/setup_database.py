"""
Database setup script for Physical AI textbook backend.

This script creates all database tables and initializes the Qdrant collection.

Usage:
    python scripts/setup_database.py
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.db.neon import engine, Base
from app.db.models import User, ChatMessage, PersonalizationCache, TranslationCache
from app.db.qdrant import qdrant_service


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def setup_qdrant():
    """Initialize Qdrant collection."""
    print("\nSetting up Qdrant collection...")

    if qdrant_service.collection_exists():
        print(f"✓ Collection '{qdrant_service.collection_name}' already exists")
    else:
        qdrant_service.create_collection(vector_size=1536)
        print(f"✓ Created collection '{qdrant_service.collection_name}'")


def main():
    """Main setup function."""
    print("=" * 60)
    print("Physical AI & Humanoid Robotics - Database Setup")
    print("=" * 60)

    try:
        # Create PostgreSQL tables
        create_tables()

        # Setup Qdrant collection
        setup_qdrant()

        print("\n" + "=" * 60)
        print("✓ Database setup completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during setup: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
