"""
Clear translation cache to test new improved translations.
"""

from app.db.neon import SessionLocal
from app.db.models import TranslationCache

def clear_cache():
    """Clear all translation cache entries."""
    db = SessionLocal()
    try:
        # Count existing entries
        count = db.query(TranslationCache).count()
        print(f"Found {count} cached translations")

        if count > 0:
            # Delete all
            deleted = db.query(TranslationCache).delete()
            db.commit()
            print(f"Deleted {deleted} cached translations")
            print("Cache cleared successfully!")
        else:
            print("Cache is already empty")

    except Exception as e:
        print(f"Error clearing cache: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_cache()
