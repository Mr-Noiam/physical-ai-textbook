"""
Debug API endpoint to check SMTP configuration.
TEMPORARY - Remove in production!
"""
from fastapi import APIRouter
import os

router = APIRouter(prefix="/api/v1/debug", tags=["debug"])


@router.get("/smtp-config")
async def check_smtp_config():
    """
    Check if SMTP environment variables are configured.

    WARNING: This endpoint exposes configuration status.
    Remove this in production!
    """
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = os.getenv("SMTP_PORT", "")
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    from_email = os.getenv("FROM_EMAIL", "")
    from_name = os.getenv("FROM_NAME", "")

    return {
        "smtp_configured": bool(smtp_user and smtp_password),
        "smtp_host": smtp_host,
        "smtp_port": smtp_port,
        "smtp_user": smtp_user if smtp_user else "NOT SET",
        "smtp_password_set": bool(smtp_password),
        "smtp_password_length": len(smtp_password) if smtp_password else 0,
        "from_email": from_email if from_email else "NOT SET",
        "from_name": from_name if from_name else "NOT SET",
        "expected_password_length": 19,  # "kncs oigg dzpi bwlw" = 19 chars with spaces
        "note": "If smtp_password_length is 0, environment variables are not set in Railway"
    }
