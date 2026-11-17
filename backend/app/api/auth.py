from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime, timezone
from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.permissions import get_current_user
from app.models.user import User, AuditLog
from app.models.candidate import CandidateProfile
from app.models.company import Company, RecruiterProfile
from app.services.email_service import EmailService
from app.schemas.auth import (
    LoginRequest,
    CandidateRegisterRequest,
    RecruiterRegisterRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

ROLE_MAPPINGS = {
    "Admin": ["ADMIN", "SUPER_ADMIN"],
    "Recruiter/HR": ["RECRUITER"],
    "Candidate": ["CANDIDATE"]
}

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    # 1. Fetch user by email
    stmt = select(User).where(User.email == payload.email.lower().strip())
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact system support."
        )

    if not user.is_verified and user.role not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address has not been verified. Please verify your email before logging in."
        )

    # 2. Critical Role Selector Validation: Reject Role Mismatch!
    selected_role_label = payload.role.strip()
    allowed_db_roles = ROLE_MAPPINGS.get(selected_role_label)
    if not allowed_db_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown login role selector '{selected_role_label}'. Must be Admin, Recruiter/HR, or Candidate."
        )

    if user.role not in allowed_db_roles:
        # Audit log the unauthorized role mismatch attempt
        audit = AuditLog(
            user_id=user.id,
            action="LOGIN_ROLE_MISMATCH_REJECTED",
            resource="AUTH",
            details=f"User with role '{user.role}' attempted to log in using '{selected_role_label}' portal selector.",
            ip_address=request.client.host if request.client else None
        )
        db.add(audit)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: You selected '{selected_role_label}', but your account is registered as a {user.role}. Please select the appropriate role."
        )

    # 3. Create Access Token
    access_token = create_access_token(
        subject=user.email,
        role=user.role,
        user_id=user.id
    )

    # 4. Set HttpOnly cookie for web security
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,  # Set to True in HTTPS production
        samesite="lax",
        max_age=86400
    )

    # 5. Record successful login audit
    audit = AuditLog(
        user_id=user.id,
        action="LOGIN_SUCCESS",
        resource="AUTH",
        details=f"Logged in via {selected_role_label} portal selector.",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user=UserResponse.model_validate(user)
    )

@router.post("/register/candidate", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_candidate(
    payload: CandidateRegisterRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match."
        )

    # Check duplicate email
    stmt = select(User).where(User.email == payload.email.lower().strip())
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists."
        )

    # Create candidate user
    is_auto_verified = settings.AUTO_VERIFY_NEW_USERS
    user = User(
        email=payload.email.lower().strip(),
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name.strip(),
        phone=payload.phone.strip() if payload.phone else None,
        role="CANDIDATE",
        is_active=True,
        is_verified=is_auto_verified
    )
    db.add(user)
    await db.flush()

    # Create Candidate Profile
    profile = CandidateProfile(
        user_id=user.id,
        country=payload.country,
        state=payload.state,
        city=payload.city
    )
    db.add(profile)

    # If verification required, dispatch token
    if not is_auto_verified:
        token = await EmailService.create_verification_token(user.id, db)
        await EmailService.send_verification_email(user.email, token, user.full_name)

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="REGISTER_CANDIDATE",
        resource="AUTH",
        details=f"Candidate registered successfully (verified={is_auto_verified}).",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(
        subject=user.email,
        role=user.role,
        user_id=user.id
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user=UserResponse.model_validate(user)
    )

@router.post("/register/recruiter", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_recruiter(
    payload: RecruiterRegisterRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match."
        )

    # Check duplicate email
    stmt = select(User).where(User.email == payload.work_email.lower().strip())
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this work email already exists."
        )

    # Check or create Company
    comp_slug = payload.company_name.lower().replace(" ", "-").replace(".", "")
    stmt_comp = select(Company).where(Company.slug == comp_slug)
    company = (await db.execute(stmt_comp)).scalar_one_or_none()
    if not company:
        company = Company(
            name=payload.company_name.strip(),
            slug=comp_slug,
            website=payload.company_website,
            headquarters=payload.company_location,
            country="India",
            city=payload.company_location,
            is_verified=False  # Recruiters / Companies require admin verification workflow
        )
        db.add(company)
        await db.flush()

    # Create recruiter user
    is_auto_verified = settings.AUTO_VERIFY_NEW_USERS
    user = User(
        email=payload.work_email.lower().strip(),
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name.strip(),
        phone=payload.phone.strip() if payload.phone else None,
        role="RECRUITER",
        is_active=True,
        is_verified=is_auto_verified
    )
    db.add(user)
    await db.flush()

    recruiter_profile = RecruiterProfile(
        user_id=user.id,
        company_id=company.id,
        designation=payload.designation,
        work_email=payload.work_email,
        phone=payload.phone,
        is_approved=True  # Enabled for immediate testing
    )
    db.add(recruiter_profile)

    if not is_auto_verified:
        token = await EmailService.create_verification_token(user.id, db)
        await EmailService.send_verification_email(user.email, token, user.full_name)

    audit = AuditLog(
        user_id=user.id,
        action="REGISTER_RECRUITER",
        resource="AUTH",
        details=f"Recruiter registered for company '{company.name}' (verified={is_auto_verified}).",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(
        subject=user.email,
        role=user.role,
        user_id=user.id
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    return UserResponse.model_validate(current_user)

@router.post("/logout")
async def logout(response: Response) -> Any:
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out."}

@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    user = await EmailService.verify_email_token(payload.token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token."
        )
    audit = AuditLog(
        user_id=user.id,
        action="EMAIL_VERIFIED",
        resource="AUTH",
        details="Email successfully verified via verification token.",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    await db.commit()
    return {"message": "Email address verified successfully. You may now log in.", "verified": True}

@router.post("/resend-verification")
async def resend_verification(
    payload: ResendVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(User).where(User.email == payload.email.lower().strip())
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        return {"message": "If an account exists with this email, a verification link has been sent."}
    if user.is_verified:
        return {"message": "Account is already verified. You can log in."}
    token = await EmailService.create_verification_token(user.id, db)
    await EmailService.send_verification_email(user.email, token, user.full_name)
    return {"message": "If an account exists with this email, a verification link has been sent."}

@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(User).where(User.email == payload.email.lower().strip())
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        return {"message": "If an account exists with this email, a password reset link has been sent."}
    token = await EmailService.create_password_reset_token(user.id, db)
    await EmailService.send_password_reset_email(user.email, token, user.full_name)
    return {"message": "If an account exists with this email, a password reset link has been sent."}

@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match."
        )
    user = await EmailService.verify_password_reset_token(payload.token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token."
        )
    user.hashed_password = get_password_hash(payload.new_password)
    user.updated_at = datetime.now(timezone.utc)
    audit = AuditLog(
        user_id=user.id,
        action="PASSWORD_RESET_COMPLETED",
        resource="AUTH",
        details="User password reset successfully using one-time token.",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    await db.commit()
    return {"message": "Password has been successfully reset. You may now log in with your new password."}
