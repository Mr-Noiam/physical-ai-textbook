"""
Database migration to add Better Auth tables and fields.

This migration adds:
1. password_hash, name, email_verified, image fields to users table
2. sessions table for Better Auth session management
3. accounts table for OAuth providers
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.neon import engine
from app.db.models import Base, User, Session, Account


def run_migration():
    """Run the migration to add auth tables and fields."""
    print("=" * 60)
    print("Running Auth Migration")
    print("=" * 60)

    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()

            try:
                # 1. Add new columns to users table
                print("\n1. Adding new columns to users table...")

                # Check if columns exist before adding
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='users' AND column_name='password_hash'
                """))

                if not result.fetchone():
                    conn.execute(text("""
                        ALTER TABLE users
                        ADD COLUMN password_hash VARCHAR(255),
                        ADD COLUMN name VARCHAR(255),
                        ADD COLUMN email_verified TIMESTAMP WITH TIME ZONE,
                        ADD COLUMN image VARCHAR(500)
                    """))
                    print("   [OK] Added password_hash, name, email_verified, image columns")
                else:
                    print("   [INFO] Columns already exist, skipping")

                # 2. Create sessions table
                print("\n2. Creating sessions table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id VARCHAR(255) PRIMARY KEY,
                        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        token VARCHAR(500) NOT NULL UNIQUE,
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        ip_address VARCHAR(45),
                        user_agent VARCHAR(500),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE
                    )
                """))
                print("   [OK] Created sessions table")

                # Create index on token for fast lookups
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token)
                """))
                print("   [OK] Created index on sessions.token")

                # 3. Create accounts table
                print("\n3. Creating accounts table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        account_id VARCHAR(255) NOT NULL,
                        provider_id VARCHAR(255) NOT NULL,
                        access_token TEXT,
                        refresh_token TEXT,
                        id_token TEXT,
                        expires_at TIMESTAMP WITH TIME ZONE,
                        scope VARCHAR(500),
                        password VARCHAR(255),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE
                    )
                """))
                print("   [OK] Created accounts table")

                # Create index for faster lookups
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id)
                """))
                print("   [OK] Created index on accounts.user_id")

                # Commit transaction
                trans.commit()

                print("\n" + "=" * 60)
                print("[SUCCESS] Migration completed successfully!")
                print("=" * 60)

            except Exception as e:
                trans.rollback()
                print(f"\n[ERROR] Migration failed: {e}")
                raise

    except Exception as e:
        print(f"\n[ERROR] Database connection failed: {e}")
        raise


if __name__ == "__main__":
    run_migration()
