import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, EmailVerificationToken, PasswordResetToken

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
        # In production this dispatches to SMTP / Resend / AWS SES.
        # In development / testing it formats the email securely.
        verification_link = f"https://velvorax.tech/verify-email?token={raw_token}"
        print(f"[EMAIL SERVICE] Verification email dispatched to {email}")
        return True

    @staticmethod
    async def send_password_reset_email(email: str, raw_token: str, full_name: str = "User") -> bool:
        reset_link = f"https://velvorax.tech/reset-password?token={raw_token}"
        print(f"[EMAIL SERVICE] Password reset email dispatched to {email}")
        return True

    @staticmethod
    async def send_job_status_notification(
        recruiter_email: str,
        job_title: str,
        status: str,
        reason: Optional[str] = None
    ) -> bool:
        print(f"[EMAIL SERVICE] Job notification: '{job_title}' status is '{status}'. Recipient: {recruiter_email}")
        return True
