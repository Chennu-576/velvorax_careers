import os
import sys
import argparse
import getpass
import asyncio
import re
from datetime import datetime, timezone
from sqlalchemy import select

# Add parent directory to sys.path to allow running standalone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.models.user import User, AuditLog

def validate_password_strength(password: str) -> bool:
    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[^A-Za-z0-9]', password):
        return False
    return True

async def bootstrap_superadmin(email: str, password: str, full_name: str, phone: str = None):
    if not email or "@" not in email:
        print("[ERROR] A valid email address is required.")
        sys.exit(1)

    if not validate_password_strength(password):
        print("[ERROR] Password does not meet security requirements:")
        print("  - At least 8 characters long")
        print("  - At least one uppercase letter (A-Z)")
        print("  - At least one lowercase letter (a-z)")
        print("  - At least one numerical digit (0-9)")
        print("  - At least one special symbol (!@#$%^&*...)")
        sys.exit(1)

    async with async_session_maker() as session:
        stmt = select(User).where(User.email == email.lower().strip())
        existing = (await session.execute(stmt)).scalar_one_or_none()

        hashed_pwd = get_password_hash(password)

        if existing:
            print(f"[INFO] User with email '{email}' already exists. Updating credentials and elevating role...")
            existing.hashed_password = hashed_pwd
            existing.role = "SUPER_ADMIN"
            existing.full_name = full_name or existing.full_name
            if phone:
                existing.phone = phone
            existing.is_active = True
            existing.is_verified = True
            existing.updated_at = datetime.now(timezone.utc)

            audit = AuditLog(
                user_id=existing.id,
                action="SUPERADMIN_UPDATE",
                resource="USERS",
                details=f"Super Admin account updated via secure CLI bootstrap utility."
            )
            session.add(audit)
            await session.commit()
            print(f"[SUCCESS] Super Admin account for '{email}' has been successfully updated.")
            return

        # Create new Super Admin
        super_admin = User(
            email=email.lower().strip(),
            hashed_password=hashed_pwd,
            full_name=full_name,
            phone=phone,
            role="SUPER_ADMIN",
            is_active=True,
            is_verified=True
        )
        session.add(super_admin)
        await session.flush()

        audit = AuditLog(
            user_id=super_admin.id,
            action="SUPERADMIN_BOOTSTRAP",
            resource="USERS",
            details=f"Super Admin account provisioned via secure CLI bootstrap utility."
        )
        session.add(audit)
        await session.commit()
        print(f"[SUCCESS] Super Admin account for '{email}' successfully created and audit logged.")

def main():
    parser = argparse.ArgumentParser(description="VELVORAX CAREERS - Secure Super Admin Bootstrapper")
    parser.add_argument("--email", help="Super Admin Email address")
    parser.add_argument("--name", help="Super Admin Full Name")
    parser.add_argument("--phone", help="Super Admin Phone Number")

    args = parser.parse_args()

    email = args.email or os.getenv("SUPERADMIN_EMAIL")
    password = os.getenv("SUPERADMIN_PASSWORD")
    name = args.name or os.getenv("SUPERADMIN_NAME", "Velvorax Super Administrator")
    phone = args.phone or os.getenv("SUPERADMIN_PHONE", "+91 9985201116")

    if not email:
        email = input("Enter Super Admin Email: ").strip()

    if not password:
        password = getpass.getpass("Enter Super Admin Password: ")
        confirm_password = getpass.getpass("Confirm Super Admin Password: ")
        if password != confirm_password:
            print("[ERROR] Passwords do not match.")
            sys.exit(1)

    asyncio.run(bootstrap_superadmin(email, password, name, phone))

if __name__ == "__main__":
    main()
