import os
from pathlib import Path
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Explicitly load environment variables from the .env file located in the backend directory
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from app.db.neon import get_db
from app.db.models import TranslationCache

def clear_translation_cache_db():
    """Clears all entries from the TranslationCache table in the database."""
    print("Attempting to clear TranslationCache table...")
    db_session: Session = next(get_db())
    try:
        num_deleted = db_session.query(TranslationCache).delete()
        db_session.commit()
        print(f"Successfully deleted {num_deleted} entries from TranslationCache.")
    except Exception as e:
        db_session.rollback()
        print(f"Error clearing TranslationCache: {e}")
    finally:
        db_session.close()
    print("Database session closed.")

if __name__ == "__main__":
    clear_translation_cache_db()
