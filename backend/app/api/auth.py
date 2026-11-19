from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.permissions import get_current_user
from app.models.user import User, AuditLog, EmailVerificationToken
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
    ResetPasswordRequest,
    RegistrationResponse
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

    if not user.is_verified:
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
        secure=settings.COOKIE_SECURE or settings.ENVIRONMENT.lower() == "production",
        samesite="none" if settings.ENVIRONMENT.lower() == "production" else settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
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

@router.post("/register/candidate", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_candidate(
    payload: CandidateRegisterRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    if not payload.terms_accepted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Terms and privacy acceptance is required.")
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
            detail="Email already exists."
        )

    # Create candidate user
    user = User(
        email=payload.email.lower().strip(),
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name.strip(),
        phone=payload.phone.strip() if payload.phone else None,
        role="CANDIDATE",
        is_active=True,
        is_verified=False
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

    token = await EmailService.create_verification_token(user.id, db, commit=False)

    audit = AuditLog(
        user_id=user.id,
        action="REGISTER_CANDIDATE",
        resource="AUTH",
        details="Candidate registered; email verification is required.",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    verification_email_sent = await EmailService.send_verification_email(
        user.email, token, user.full_name
    )
    await db.refresh(user)

    return RegistrationResponse(
        message=(
            "Registration successful. Please verify your email before logging in."
            if verification_email_sent
            else "Registration successful, but the verification email could not be sent. Use resend verification."
        ),
        email=user.email,
        is_verified=user.is_verified,
        verification_required=True,
        verification_email_sent=verification_email_sent
    )

@router.post("/register/recruiter", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_recruiter(
    payload: RecruiterRegisterRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    if not payload.terms_accepted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Terms and privacy acceptance is required.")
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
            detail="Email already exists."
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
            gstin=payload.company_gstin.strip().upper() if payload.company_gstin else None,
            cin=payload.company_cin.strip().upper() if payload.company_cin else None,
            headquarters=payload.company_location,
            country="India",
            city=payload.company_location,
            is_verified=False  # Recruiters / Companies require admin verification workflow
        )
        db.add(company)
        await db.flush()

    # Create recruiter user
    user = User(
        email=payload.work_email.lower().strip(),
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name.strip(),
        phone=payload.phone.strip() if payload.phone else None,
        role="RECRUITER",
        is_active=True,
        is_verified=False
    )
    db.add(user)
    await db.flush()

    recruiter_profile = RecruiterProfile(
        user_id=user.id,
        company_id=company.id,
        designation=payload.designation,
        work_email=payload.work_email,
        phone=payload.phone,
        is_approved=False
    )
    db.add(recruiter_profile)

    token = await EmailService.create_verification_token(user.id, db, commit=False)

    audit = AuditLog(
        user_id=user.id,
        action="REGISTER_RECRUITER",
        resource="AUTH",
        details=f"Recruiter registered for company '{company.name}'; email verification is required.",
        ip_address=request.client.host if request.client else None
    )
    db.add(audit)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account or company with these details already exists.",
        )

    verification_email_sent = await EmailService.send_verification_email(
        user.email, token, user.full_name
    )
    await db.refresh(user)

    return RegistrationResponse(
        message=(
            "Registration successful. Please verify your email before logging in."
            if verification_email_sent
            else "Registration successful, but the verification email could not be sent. Use resend verification."
        ),
        email=user.email,
        is_verified=user.is_verified,
        verification_required=True,
        verification_email_sent=verification_email_sent
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> Any:
    return UserResponse.model_validate(current_user)

@router.post("/logout")
async def logout(response: Response) -> Any:
    response.delete_cookie(
        key="access_token",
        secure=settings.COOKIE_SECURE or settings.ENVIRONMENT.lower() == "production",
        samesite="none" if settings.ENVIRONMENT.lower() == "production" else settings.COOKIE_SAMESITE,
    )
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
    now = datetime.now(timezone.utc)
    ip_address = request.client.host if request.client else None
    if ip_address:
        recent_requests = await db.scalar(
            select(func.count(AuditLog.id)).where(
                AuditLog.action == "RESEND_VERIFICATION_REQUEST",
                AuditLog.ip_address == ip_address,
                AuditLog.created_at >= now - timedelta(minutes=1),
            )
        )
        if recent_requests and recent_requests >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many verification requests. Please try again in a minute.",
                headers={"Retry-After": "60"},
            )

    stmt = (
        select(User)
        .where(User.email == payload.email.lower().strip())
        .with_for_update()
    )
    user = (await db.execute(stmt)).scalar_one_or_none()
    raw_token = None
    if user and not user.is_verified and user.is_active:
        recent_user_tokens = await db.scalar(
            select(func.count(EmailVerificationToken.id)).where(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.created_at >= now - timedelta(hours=1),
            )
        )
        if not recent_user_tokens or recent_user_tokens < 5:
            raw_token = await EmailService.create_verification_token(
                user.id, db, commit=False
            )

    db.add(
        AuditLog(
            user_id=user.id if user else None,
            action="RESEND_VERIFICATION_REQUEST",
            resource="AUTH",
            details="Verification email request received.",
            ip_address=ip_address,
        )
    )
    await db.commit()
    verification_email_sent = False
    if user and raw_token:
        verification_email_sent = await EmailService.send_verification_email(
            user.email, raw_token, user.full_name
        )
    return {
        "message": "If an unverified account exists, we will send a verification link when possible.",
        "verification_email_sent": verification_email_sent,
    }

@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(User).where(User.email == payload.email.lower().strip())
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        return {"message": "If an account exists, we received the password reset request."}
    token = await EmailService.create_password_reset_token(user.id, db, commit=False)
    await db.commit()
    await EmailService.send_password_reset_email(user.email, token, user.full_name)
    return {"message": "If an account exists, we received the password reset request."}

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
