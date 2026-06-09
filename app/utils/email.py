# Required .env variables:
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_USERNAME=your_username
# SMTP_PASSWORD=your_password
# EMAILS_FROM_EMAIL=noreply@cmo-ai.com

from __future__ import annotations

import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def _smtp_is_configured() -> bool:
    """Return True if SMTP settings appear configured."""
    return bool(settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD)


def _send_email_sync(to_email: str, subject: str, body: str) -> None:
    """Send an email synchronously via SMTP.

    This is executed in a worker thread by `send_email()` to keep the API async.
    """
    message = EmailMessage()
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as smtp:
        smtp.ehlo()
        if settings.SMTP_PORT in (587, 25):
            smtp.starttls()
            smtp.ehlo()
        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(message)


async def send_email(to_email: str, subject: str, body: str) -> None:
    """Send a plain-text email.

    If SMTP is not configured, the email is printed to console (dev-friendly)
    and a warning is logged.

    Raises:
        ValueError: if inputs are empty/invalid.
        RuntimeError: if SMTP is configured but the send fails.
    """
    to_email = (to_email or "").strip()
    subject = (subject or "").strip()
    body = body or ""

    if not to_email or "@" not in to_email:
        raise ValueError("to_email must be a valid email address")
    if not subject:
        raise ValueError("subject must not be empty")
    if not body.strip():
        raise ValueError("body must not be empty")
    if not settings.EMAILS_FROM_EMAIL or "@" not in settings.EMAILS_FROM_EMAIL:
        raise ValueError("EMAILS_FROM_EMAIL must be configured with a valid email address")

    if not _smtp_is_configured():
        logger.warning(
            "SMTP not configured; printing email to console instead. "
            "Set SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD to enable real sending."
        )
        print("\n--- EMAIL (SMTP not configured) ---")
        print(f"From: {settings.EMAILS_FROM_EMAIL}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}\n")
        print(body)
        print("--- END EMAIL ---\n")
        return

    try:
        await asyncio.to_thread(_send_email_sync, to_email, subject, body)
    except Exception as e:
        raise RuntimeError(f"Failed to send email via SMTP: {e}") from e


async def send_password_reset_email(to_email: str, reset_token: str) -> None:
    """Send a password reset email containing the reset link."""
    reset_token = (reset_token or "").strip()
    if not reset_token:
        raise ValueError("reset_token must not be empty")

    subject = "CMO.AI — Reset Your Password"
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
    body = (
        "Hi,\n\n"
        "We received a request to reset your CMO.AI password.\n\n"
        f"Reset your password using this link:\n{reset_link}\n\n"
        "If you didn't request this, you can safely ignore this email.\n\n"
        "— CMO.AI"
    )
    await send_email(to_email, subject, body)


async def send_welcome_email(to_email: str, name: str) -> None:
    """Send a welcome email to a newly registered user."""
    name = (name or "").strip()
    if not name:
        raise ValueError("name must not be empty")

    subject = f"Welcome to CMO.AI, {name}!"
    body = (
        f"Hi {name},\n\n"
        "Welcome to CMO.AI — we're excited to have you.\n\n"
        "To get started, create your first brand and we’ll help generate strategies, content, and campaigns.\n\n"
        "— CMO.AI"
    )
    await send_email(to_email, subject, body)

