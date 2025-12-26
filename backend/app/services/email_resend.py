"""
Email Service using Resend API (Railway-compatible)

Resend is a modern email API that works on Railway (SMTP ports are blocked).
Free tier: 3,000 emails/month, 100 emails/day

Sign up: https://resend.com/
"""

import os
import httpx
from typing import Optional


# Resend API configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")  # Use your verified domain
FROM_NAME = os.getenv("FROM_NAME", "Physical AI Textbook")


async def send_email_resend(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send email using Resend API (works on Railway).

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML version of email body
        text_content: Plain text version (optional)

    Returns:
        True if email sent successfully, False otherwise
    """
    if not RESEND_API_KEY:
        print("WARNING: RESEND_API_KEY not configured. Email not sent.")
        print(f"Would have sent email to {to_email}: {subject}")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": f"{FROM_NAME} <{FROM_EMAIL}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content,
                    "text": text_content or html_content,
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                print(f"[SUCCESS] Email sent successfully to {to_email} via Resend")
                return True
            else:
                error_data = response.json()
                print(f"[ERROR] Resend API error: {error_data}")
                return False

    except Exception as e:
        print(f"[ERROR] Failed to send email via Resend: {e}")
        return False


async def send_password_reset_email_resend(
    to_email: str,
    reset_token: str,
    frontend_url: str = "https://mr-noiam.github.io/physical-ai-textbook"
) -> bool:
    """
    Send password reset email using Resend API.

    Args:
        to_email: User's email address
        reset_token: Password reset token
        frontend_url: Base URL of the frontend app

    Returns:
        True if email sent successfully
    """
    reset_url = f"{frontend_url}/reset-password?token={reset_token}&email={to_email}"

    subject = "Reset Your Password - Physical AI Textbook"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .button {{ display: inline-block; background-color: #0066cc; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
            .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Physical AI Textbook</h1>
            </div>
            <div class="content">
                <h2>Password Reset Request</h2>
                <p>Hello,</p>
                <p>We received a request to reset the password for your account.</p>

                <p>Click the button below to reset your password:</p>

                <a href="{reset_url}" class="button">Reset Password</a>

                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #f0f0f0; padding: 10px; border-radius: 3px;">{reset_url}</p>

                <div class="warning">
                    <strong>⚠️ Security Notice:</strong>
                    <ul>
                        <li>This link will expire in 1 hour</li>
                        <li>If you didn't request this reset, please ignore this email</li>
                        <li>Never share this link with anyone</li>
                    </ul>
                </div>

                <div class="footer">
                    <p>This is an automated email from Physical AI & Humanoid Robotics Textbook.</p>
                    <p>If you have any questions, please visit our <a href="{frontend_url}">website</a>.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Physical AI Textbook - Password Reset

    Hello,

    We received a request to reset the password for your account.

    Click this link to reset your password:
    {reset_url}

    Security Notice:
    - This link will expire in 1 hour
    - If you didn't request this reset, please ignore this email
    - Never share this link with anyone

    This is an automated email from Physical AI & Humanoid Robotics Textbook.
    """

    return await send_email_resend(to_email, subject, html_content, text_content)
