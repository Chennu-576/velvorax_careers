import os
import secrets
import hashlib
import smtplib
import logging
import asyncio
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, EmailVerificationToken, PasswordResetToken
from app.core.config import settings

class EmailService:
    @staticmethod
    def generate_token() -> Tuple[str, str]:
        """
        Generates a secure 32-byte hex token and returns (raw_token, sha256_hash).
        The raw_token is sent to the user; the sha256_hash is stored in the database.
        """
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        return raw_token, token_hash

    @staticmethod
    async def create_verification_token(user_id: int, db: AsyncSession, hours_valid: int = 24) -> str:
        raw_token, token_hash = EmailService.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=hours_valid)

        token_record = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_used=False
        )
        db.add(token_record)
        await db.commit()
        return raw_token

    @staticmethod
    async def verify_email_token(raw_token: str, db: AsyncSession) -> Optional[User]:
        token_hash = hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()
        stmt = (
            select(EmailVerificationToken)
            .where(
                EmailVerificationToken.token_hash == token_hash,
                EmailVerificationToken.is_used == False
            )
        )
        result = await db.execute(stmt)
        token_record = result.scalar_one_or_none()

        if not token_record:
            return None

        # Check expiration
        now = datetime.now(timezone.utc)
        token_expiry = token_record.expires_at
        if token_expiry.tzinfo is None:
            token_expiry = token_expiry.replace(tzinfo=timezone.utc)

        if token_expiry < now:
            return None

        # Mark token as used
        token_record.is_used = True

        # Fetch and verify user
        user = (await db.execute(select(User).where(User.id == token_record.user_id))).scalar_one_or_none()
        if user:
            user.is_verified = True
            await db.commit()
            return user

        await db.commit()
        return None

    @staticmethod
    async def create_password_reset_token(user_id: int, db: AsyncSession, hours_valid: int = 2) -> str:
        raw_token, token_hash = EmailService.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=hours_valid)

        token_record = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_used=False
        )
        db.add(token_record)
        await db.commit()
        return raw_token

    @staticmethod
    async def verify_password_reset_token(raw_token: str, db: AsyncSession) -> Optional[User]:
        token_hash = hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()
        stmt = (
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.is_used == False
            )
        )
        result = await db.execute(stmt)
        token_record = result.scalar_one_or_none()

        if not token_record:
            return None

        # Check expiration
        now = datetime.now(timezone.utc)
        token_expiry = token_record.expires_at
        if token_expiry.tzinfo is None:
            token_expiry = token_expiry.replace(tzinfo=timezone.utc)

        if token_expiry < now:
            return None

        # Mark token as used
        token_record.is_used = True
        user = (await db.execute(select(User).where(User.id == token_record.user_id))).scalar_one_or_none()
        await db.commit()
        return user

    @staticmethod
    async def send_verification_email(email: str, raw_token: str, full_name: str = "User") -> bool:
        verification_link = f"{settings.FRONTEND_URL.rstrip('/')}/verify-email?token={raw_token}"
        subject = "Verify your VELVORAX Careers email"
        body = (
            f"Hello {full_name},\n\n"
            "Please verify your VELVORAX Careers account by opening this link:\n"
            f"{verification_link}\n\n"
            "This link expires in 24 hours.\n"
        )
        return await EmailService._send_smtp(email, subject, body)

    @staticmethod
    async def send_password_reset_email(email: str, raw_token: str, full_name: str = "User") -> bool:
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={raw_token}"
        subject = "Reset your VELVORAX Careers password"
        body = (
            f"Hello {full_name},\n\n"
            "Use this link to reset your password:\n"
            f"{reset_link}\n\n"
            "This link expires in 2 hours.\n"
        )
        return await EmailService._send_smtp(email, subject, body)

    @staticmethod
    async def send_job_status_notification(
        recruiter_email: str,
        job_title: str,
        status: str,
        reason: Optional[str] = None
    ) -> bool:
        subject = f"VELVORAX job status update: {job_title}"
        body = f"Your job '{job_title}' has status '{status}'."
        if reason:
            body += f"\n\nReason: {reason}"
        return await EmailService._send_smtp(recruiter_email, subject, body)

    @staticmethod
    async def _send_smtp(to_email: str, subject: str, body: str) -> bool:
        if not settings.SMTP_HOST:
            logging.warning("SMTP_HOST is not configured; email was not sent to %s", to_email)
            return False

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message.set_content(body)

        def dispatch() -> None:
            if settings.SMTP_USE_SSL:
                server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
            else:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)

            with server:
                if settings.SMTP_USE_TLS and not settings.SMTP_USE_SSL:
                    server.starttls()
                if settings.SMTP_USERNAME:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)

        try:
            await asyncio.to_thread(dispatch)
            return True
        except Exception:
            logging.exception("SMTP delivery failed for %s", to_email)
            return False
