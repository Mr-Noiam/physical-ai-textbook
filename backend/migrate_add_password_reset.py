"""
Quick migration script to add password reset columns
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("NEON_DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env file")
    exit(1)

# Replace postgresql:// with postgresql+psycopg:// for psycopg3
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

print(f"Connecting to database...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Add the missing columns
        print("Adding reset_token and reset_token_expires columns...")
        conn.execute(text("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255),
            ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP
        """))
        conn.commit()

        print("[SUCCESS] Migration successful!")

        # Verify
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name IN ('reset_token', 'reset_token_expires')
        """))

        print("\nVerified columns:")
        for row in result:
            print(f"  - {row[0]}: {row[1]}")

except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

print("\n[SUCCESS] Database migration complete! You can now run the server.")
