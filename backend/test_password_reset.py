"""
Quick test for password reset email with your verified domain.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the email function
from app.services.email_resend import send_password_reset_email_resend


async def test_password_reset(test_email: str):
    """Test sending a password reset email."""

    print("=" * 60)
    print("PASSWORD RESET EMAIL TEST")
    print("=" * 60)
    print()
    print(f"FROM_EMAIL: {os.getenv('FROM_EMAIL')}")
    print(f"RESEND_API_KEY: {os.getenv('RESEND_API_KEY', '')[:10]}...")
    print(f"TO_EMAIL: {test_email}")
    print()

    print(f"Sending password reset email to {test_email}...")
    print()

    # Send test reset email
    result = await send_password_reset_email_resend(
        to_email=test_email,
        reset_token="test_token_12345_this_is_just_a_test",
        frontend_url="https://mr-noiam.github.io/physical-ai-textbook"
    )

    print()
    if result:
        print("[SUCCESS] Email sent successfully!")
        print(f"Check {test_email} inbox (and spam folder)")
        print()
        print("The email will contain a reset link (token is just for testing)")
    else:
        print("[FAILED] Email failed to send")
        print("Check the error messages above for details")

    print()
    return result


if __name__ == "__main__":
    # Get email from command line or use default
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = "ghulam.mustafa.muhammed@gmail.com"  # Default to your email

    result = asyncio.run(test_password_reset(email))
    sys.exit(0 if result else 1)
