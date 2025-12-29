"""
Fix User table columns - add missing columns individually.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.neon import engine


def add_column_if_not_exists(conn, table, column, column_type):
    """Add a column if it doesn't exist."""
    result = conn.execute(text(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='{table}' AND column_name='{column}'
    """))

    if not result.fetchone():
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))
        print(f"  [OK] Added column '{column}' to '{table}' table")
    else:
        print(f"  [SKIP] Column '{column}' already exists in '{table}' table")


def run_fix():
    print("=" * 60)
    print("Fixing User Table Columns")
    print("=" * 60)

    try:
        with engine.connect() as conn:
            trans = conn.begin()

            try:
                print("\nAdding missing columns...")
                add_column_if_not_exists(conn, "users", "password_hash", "VARCHAR(255)")
                add_column_if_not_exists(conn, "users", "name", "VARCHAR(255)")
                add_column_if_not_exists(conn, "users", "email_verified", "TIMESTAMP WITH TIME ZONE")
                add_column_if_not_exists(conn, "users", "image", "VARCHAR(500)")

                trans.commit()
                print("\n" + "=" * 60)
                print("[SUCCESS] User table columns fixed!")
                print("=" * 60)

            except Exception as e:
                trans.rollback()
                print(f"\n[ERROR] Fix failed: {e}")
                raise

    except Exception as e:
        print(f"\n[ERROR] Database connection failed: {e}")
        raise


if __name__ == "__main__":
    run_fix()
