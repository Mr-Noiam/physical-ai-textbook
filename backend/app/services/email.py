"""
Email Service Module

Handles sending emails for password reset and other notifications.
Uses aiosmtplib for async email sending via Gmail SMTP.
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os


# Email configuration from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")  # Your Gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # App-specific password
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.getenv("FROM_NAME", "Physical AI Textbook")


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML version of email body
        text_content: Plain text version (optional, falls back to stripping HTML)

    Returns:
        True if email sent successfully, False otherwise

    Raises:
        Exception: If email sending fails
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print("WARNING: SMTP credentials not configured. Email not sent.")
        print(f"Would have sent email to {to_email}: {subject}")
        return False

    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject

        # Add plain text version
        if text_content:
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)

        # Add HTML version
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Send email
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
        )

        print(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        raise


async def send_password_reset_email(
    to_email: str,
    reset_token: str,
    frontend_url: str = "https://mr-noiam.github.io/physical-ai-textbook"
) -> bool:
    """
    Send password reset email with reset link.

    Args:
        to_email: User's email address
        reset_token: Password reset token
        frontend_url: Base URL of the frontend app

    Returns:
        True if email sent successfully, False otherwise
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
                <p>We received a request to reset the password for your account associated with this email address.</p>

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

    return await send_email(to_email, subject, html_content, text_content)


async def send_welcome_email(to_email: str, frontend_url: str = "https://mr-noiam.github.io/physical-ai-textbook") -> bool:
    """
    Send welcome email to new users.

    Args:
        to_email: User's email address
        frontend_url: Base URL of the frontend app

    Returns:
        True if email sent successfully, False otherwise
    """
    subject = "Welcome to Physical AI & Humanoid Robotics Textbook! 🤖"

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
            .feature {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #0066cc; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Welcome to Physical AI!</h1>
            </div>
            <div class="content">
                <h2>Your Learning Journey Starts Here</h2>
                <p>Thank you for joining Physical AI & Humanoid Robotics Textbook!</p>

                <p>You now have access to:</p>

                <div class="feature">
                    <strong>📚 13 Weeks of Content</strong><br>
                    Comprehensive coverage of ROS 2, Gazebo, Unity, NVIDIA Isaac, and Vision-Language-Action models
                </div>

                <div class="feature">
                    <strong>🤖 AI-Powered Chatbot</strong><br>
                    Ask questions about any topic and get instant, contextual answers with source references
                </div>

                <div class="feature">
                    <strong>👤 Personalized Learning</strong><br>
                    Set your experience level to get explanations tailored to your background
                </div>

                <a href="{frontend_url}/profile" class="button">Set Up Your Profile</a>

                <p>Ready to start learning? Visit the textbook and explore the first module!</p>

                <a href="{frontend_url}/docs/module-1-ros2/week1-intro" class="button">Start Learning</a>

                <p>Happy learning! 🚀</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Welcome to Physical AI & Humanoid Robotics Textbook!

    Thank you for joining! You now have access to:

    - 13 weeks of comprehensive robotics content
    - AI-powered chatbot for instant help
    - Personalized learning based on your experience level

    Set up your profile: {frontend_url}/profile
    Start learning: {frontend_url}/docs/module-1-ros2/week1-intro

    Happy learning!
    """

    return await send_email(to_email, subject, html_content, text_content)
