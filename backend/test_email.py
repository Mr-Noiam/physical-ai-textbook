"""
Test Email Sending
Run this script to test if SMTP configuration is working.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.getenv("FROM_NAME", "Physical AI Textbook")

print("=" * 60)
print("SMTP Configuration Test")
print("=" * 60)
print(f"SMTP_HOST: {SMTP_HOST}")
print(f"SMTP_PORT: {SMTP_PORT}")
print(f"SMTP_USER: {SMTP_USER}")
print(f"SMTP_PASSWORD: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else '(NOT SET)'}")
print(f"FROM_EMAIL: {FROM_EMAIL}")
print(f"FROM_NAME: {FROM_NAME}")
print("=" * 60)

if not SMTP_USER or not SMTP_PASSWORD:
    print("\n❌ ERROR: SMTP credentials not configured!")
    print("\nPlease set these environment variables:")
    print("  SMTP_USER=your.email@gmail.com")
    print("  SMTP_PASSWORD=your_app_password")
    exit(1)

print(f"\n✅ Configuration looks good!")
print(f"\nTesting email to: {SMTP_USER}")

async def test_email():
    """Test sending an email."""
    try:
        from app.services.email import send_email

        test_email_address = SMTP_USER  # Send to yourself for testing

        print(f"\n📧 Sending test email to {test_email_address}...")

        success = await send_email(
            to_email=test_email_address,
            subject="Test Email - Physical AI Textbook",
            html_content="""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #0066cc;">🎉 Email Test Successful!</h2>
                <p>This is a test email from your Physical AI Textbook backend.</p>
                <p>If you're reading this, your SMTP configuration is working correctly!</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Sent from: {from_name}<br>
                    SMTP Server: {smtp_host}:{smtp_port}<br>
                    User: {smtp_user}
                </p>
            </body>
            </html>
            """.format(
                from_name=FROM_NAME,
                smtp_host=SMTP_HOST,
                smtp_port=SMTP_PORT,
                smtp_user=SMTP_USER
            ),
            text_content="Email Test Successful! Your SMTP configuration is working."
        )

        if success:
            print("\n✅ Email sent successfully!")
            print(f"   Check your inbox at: {test_email_address}")
        else:
            print("\n⚠️ Email sending returned False (SMTP not configured)")

    except Exception as e:
        print(f"\n❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    asyncio.run(test_email())
