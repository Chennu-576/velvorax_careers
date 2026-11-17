from typing import List, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or session has expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check header token first, then cookie token
    actual_token = token
    if not actual_token:
        actual_token = request.cookies.get("access_token")
        if actual_token and actual_token.startswith("Bearer "):
            actual_token = actual_token.replace("Bearer ", "")

    if not actual_token:
        raise credentials_exception

    payload = decode_token(actual_token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Please contact support."
        )

    return user

def require_roles(allowed_roles: List[str]):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # SUPER_ADMIN has access to everything
        if current_user.role == "SUPER_ADMIN":
            return current_user
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role in {allowed_roles}, your role is {current_user.role}."
            )
        return current_user
    return role_checker

require_admin = require_roles(["ADMIN", "SUPER_ADMIN"])
require_recruiter = require_roles(["RECRUITER", "ADMIN", "SUPER_ADMIN"])
require_candidate = require_roles(["CANDIDATE"])
