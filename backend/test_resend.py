"""
Test Resend email configuration and send a test email.

This script helps diagnose Resend API issues.
"""
import asyncio
import os
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
FROM_NAME = os.getenv("FROM_NAME", "Physical AI Textbook")


async def test_resend_api():
    """Test Resend API configuration."""

    print("=" * 60)
    print("RESEND API CONFIGURATION TEST")
    print("=" * 60)

    # Check API key
    if not RESEND_API_KEY:
        print("[ERROR] RESEND_API_KEY not found in .env file")
        return False

    print(f"[OK] RESEND_API_KEY found: {RESEND_API_KEY[:10]}...")
    print(f"FROM_EMAIL: {FROM_EMAIL}")
    print(f"FROM_NAME: {FROM_NAME}")
    print()

    # Check if FROM_EMAIL is using Gmail (not allowed by Resend)
    if "@gmail.com" in FROM_EMAIL or "@yahoo.com" in FROM_EMAIL or "@hotmail.com" in FROM_EMAIL:
        print("[WARNING] You're using a free email provider (Gmail/Yahoo/Hotmail)")
        print("   Resend requires you to use a verified domain.")
        print()
        print("   Options:")
        print("   1. Use the default: onboarding@resend.dev (for testing only)")
        print("   2. Verify your own domain in Resend dashboard")
        print()

        # Ask if they want to use default
        use_default = input("   Use onboarding@resend.dev for testing? (y/n): ").lower().strip()
        if use_default == 'y':
            test_from = "onboarding@resend.dev"
        else:
            print("   Please verify your domain in Resend: https://resend.com/domains")
            return False
    else:
        test_from = FROM_EMAIL

    # Get test recipient email
    print()
    test_to = input("Enter your email address to receive test email: ").strip()

    if not test_to:
        print("[ERROR] No email address provided")
        return False

    print()
    print(f"Sending test email to {test_to}...")
    print()

    # Send test email
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": f"{FROM_NAME} <{test_from}>",
                    "to": [test_to],
                    "subject": "Test Email - Resend Configuration",
                    "html": """
                    <h1>Resend is Working!</h1>
                    <p>This is a test email from your Physical AI Textbook backend.</p>
                    <p>If you received this, your Resend integration is configured correctly.</p>
                    """,
                    "text": "Resend is Working! This is a test email from your Physical AI Textbook backend.",
                },
                timeout=10.0,
            )

            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            print()

            if response.status_code == 200:
                result = response.json()
                print("[SUCCESS] Email sent successfully!")
                print(f"   Email ID: {result.get('id', 'N/A')}")
                print()
                print("   Check your inbox (and spam folder) for the test email.")
                return True
            else:
                error_data = response.json()
                print("[FAILED] Failed to send email")
                print()
                print("   Error Details:")
                print(f"   Status Code: {response.status_code}")
                print(f"   Error: {error_data}")
                print()

                # Provide helpful error messages
                if response.status_code == 401:
                    print("   [Solution] Invalid API key. Check your RESEND_API_KEY in .env")
                elif response.status_code == 422:
                    print("   [Solution] Invalid email address or unverified domain.")
                    print("      - Verify your domain in Resend dashboard")
                    print("      - Or use onboarding@resend.dev for testing")
                elif response.status_code == 429:
                    print("   [Solution] Rate limit exceeded. Wait a few minutes.")

                return False

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return False


if __name__ == "__main__":
    print()
    asyncio.run(test_resend_api())
    print()
