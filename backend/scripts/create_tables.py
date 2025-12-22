"""
Create all database tables.

Run this script to create all tables defined in models.py.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.neon import engine, Base
from app.db.models import User, ChatMessage, PersonalizationCache, TranslationCache


def create_all_tables():
    """Create all database tables."""
    print("Creating database tables...")
    print(f"Database URL: {engine.url}")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("\n✓ All tables created successfully!")
    print("\nTables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


if __name__ == "__main__":
    create_all_tables()
