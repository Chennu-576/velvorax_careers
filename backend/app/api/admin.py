from typing import Optional, List, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.permissions import require_admin
from app.models.user import User, AuditLog
from app.models.candidate import CandidateProfile
from app.models.company import Company, RecruiterProfile
from app.models.job import Job
from app.models.application import Application, Interview
from app.models.employer_request import EmployerHiringRequest
from app.models.training import TrainingEnrollment
from app.models.finance import Invoice
from app.models.cms import CMSContent, PlatformSetting
from app.schemas.auth import UserResponse
from app.schemas.job import JobResponse
from app.schemas.cms import CMSContentResponse, CMSContentUpdate

router = APIRouter(prefix="/admin", tags=["Admin Portal"])

class AdminDashboardStats(BaseModel):
    total_users: int
    total_candidates: int
    total_recruiters: int
    total_companies: int
    total_jobs: int
    published_jobs: int
    pending_jobs: int
    total_applications: int
    total_interviews: int
    employer_requests: int
    training_enrollments: int
    total_invoiced_amount: float

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CompanyAdminView(BaseModel):
    id: int
    name: str
    slug: str
    website: Optional[str] = None
    gstin: Optional[str] = None
    cin: Optional[str] = None
    registration_number: Optional[str] = None
    verification_notes: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    is_verified: bool
    is_hiring_partner: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/dashboard/stats", response_model=AdminDashboardStats)
async def get_admin_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # 100% Real Database Queries - Zero Fakes or Placeholders!
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_candidates = (await db.execute(select(func.count(User.id)).where(User.role == "CANDIDATE"))).scalar_one()
    total_recruiters = (await db.execute(select(func.count(User.id)).where(User.role == "RECRUITER"))).scalar_one()
    total_companies = (await db.execute(select(func.count(Company.id)))).scalar_one()
    total_jobs = (await db.execute(select(func.count(Job.id)))).scalar_one()
    published_jobs = (await db.execute(select(func.count(Job.id)).where(Job.status == "PUBLISHED"))).scalar_one()
    pending_jobs = (await db.execute(select(func.count(Job.id)).where(Job.status == "PENDING_APPROVAL"))).scalar_one()
    total_applications = (await db.execute(select(func.count(Application.id)))).scalar_one()
    total_interviews = (await db.execute(select(func.count(Interview.id)))).scalar_one()
    employer_requests = (await db.execute(select(func.count(EmployerHiringRequest.id)))).scalar_one()
    training_enrollments = (await db.execute(select(func.count(TrainingEnrollment.id)))).scalar_one()
    total_invoiced = (await db.execute(select(func.coalesce(func.sum(Invoice.total_amount), 0.0)))).scalar_one()

    return AdminDashboardStats(
        total_users=total_users,
        total_candidates=total_candidates,
        total_recruiters=total_recruiters,
        total_companies=total_companies,
        total_jobs=total_jobs,
        published_jobs=published_jobs,
        pending_jobs=pending_jobs,
        total_applications=total_applications,
        total_interviews=total_interviews,
        employer_requests=employer_requests,
        training_enrollments=training_enrollments,
        total_invoiced_amount=total_invoiced
    )

# Users
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    conditions = []
    if role:
        conditions.append(User.role == role.upper())
    stmt = select(User).where(and_(*conditions)).order_by(desc(User.created_at))
    users = (await db.execute(stmt)).scalars().all()
    return [UserResponse.model_validate(u) for u in users]

@router.patch("/users/{user_id}/status")
async def toggle_user_status(
    user_id: int,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if is_active is not None:
        user.is_active = is_active
    if is_verified is not None:
        user.is_verified = is_verified

    audit = AuditLog(
        user_id=current_user.id,
        action="UPDATE_USER_STATUS",
        resource="USERS",
        details=f"Admin updated User ID {user_id}: active={user.is_active}, verified={user.is_verified}"
    )
    db.add(audit)
    await db.commit()
    return {"message": "User status updated successfully."}

# Companies
@router.get("/companies", response_model=List[CompanyAdminView])
async def list_companies(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Company).order_by(desc(Company.created_at))
    comps = (await db.execute(stmt)).scalars().all()
    return [CompanyAdminView.model_validate(c) for c in comps]

@router.patch("/companies/{company_id}/verify")
async def verify_company(
    company_id: int,
    is_verified: bool = Query(...),
    is_hiring_partner: Optional[bool] = Query(None),
    verification_notes: Optional[str] = Query(None, max_length=2000),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    comp = (await db.execute(select(Company).where(Company.id == company_id))).scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    comp.is_verified = is_verified
    comp.verification_notes = verification_notes.strip() if verification_notes else None
    comp.verified_at = datetime.now(timezone.utc) if is_verified else None
    comp.verified_by_user_id = current_user.id if is_verified else None
    if is_hiring_partner is not None:
        comp.is_hiring_partner = is_hiring_partner
    recruiter_profiles = (
        await db.execute(
            select(RecruiterProfile).where(RecruiterProfile.company_id == company_id)
        )
    ).scalars()
    for profile in recruiter_profiles:
        profile.is_approved = is_verified

    audit = AuditLog(
        user_id=current_user.id,
        action="VERIFY_COMPANY",
        resource="COMPANIES",
        details=f"Admin updated Company '{comp.name}': verified={comp.is_verified}, partner={comp.is_hiring_partner}"
    )
    db.add(audit)
    await db.commit()
    return {"message": f"Company '{comp.name}' verification status updated."}

class JobRejectRequest(BaseModel):
    reason: str

# Job Moderation
@router.get("/jobs/pending", response_model=List[JobResponse])
async def list_pending_jobs(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = (
        select(Job)
        .where(Job.status == "PENDING_APPROVAL")
        .options(
            selectinload(Job.company),
            selectinload(Job.category),
            selectinload(Job.skills)
        )
        .order_by(desc(Job.created_at))
    )
    jobs = (await db.execute(stmt)).scalars().all()
    return [JobResponse.model_validate(j) for j in jobs]

@router.post("/jobs/{job_id}/approve")
async def approve_job(
    job_id: int,
    is_featured: Optional[bool] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = (
        select(Job)
        .where(Job.id == job_id)
        .options(
            selectinload(Job.company),
            selectinload(Job.category),
            selectinload(Job.skills)
        )
    )
    job = (await db.execute(stmt)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    if not job.company or not job.company.is_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Verify the employer company before approving its jobs."
        )

    job.status = "PUBLISHED"
    job.rejection_reason = None
    job.approved_by_admin_id = current_user.id
    job.approved_at = datetime.now(timezone.utc)
    if is_featured is not None:
        job.is_featured = is_featured

    audit = AuditLog(
        user_id=current_user.id,
        action="APPROVE_JOB",
        resource="JOBS",
        details=f"Admin {current_user.email} approved job '{job.title}' (ID {job.id}) to PUBLISHED status."
    )
    db.add(audit)
    await db.commit()
    await db.refresh(job)
    return {"message": f"Job '{job.title}' has been successfully approved and published.", "status": "PUBLISHED"}

@router.post("/jobs/{job_id}/reject")
async def reject_job(
    job_id: int,
    payload: JobRejectRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if not payload.reason or len(payload.reason.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A clear and specific rejection reason is mandatory when rejecting a vacancy."
        )

    stmt = (
        select(Job)
        .where(Job.id == job_id)
        .options(
            selectinload(Job.company),
            selectinload(Job.category),
            selectinload(Job.skills)
        )
    )
    job = (await db.execute(stmt)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    job.status = "REJECTED"
    job.rejection_reason = payload.reason.strip()
    job.approved_by_admin_id = None
    job.approved_at = None

    audit = AuditLog(
        user_id=current_user.id,
        action="REJECT_JOB",
        resource="JOBS",
        details=f"Admin {current_user.email} rejected job '{job.title}' (ID {job.id}). Reason: {job.rejection_reason}"
    )
    db.add(audit)
    await db.commit()
    await db.refresh(job)
    return {"message": f"Job '{job.title}' was rejected.", "status": "REJECTED", "rejection_reason": job.rejection_reason}

@router.patch("/jobs/{job_id}/moderate")
async def moderate_job(
    job_id: int,
    status_val: str = Query(..., description="PUBLISHED, REJECTED, PAUSED, CLOSED"),
    is_featured: Optional[bool] = Query(None),
    rejection_reason: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    job = (await db.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    new_status = status_val.upper()
    if new_status == "REJECTED" and not rejection_reason:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rejection_reason is mandatory when rejecting.")

    job.status = new_status
    if new_status == "PUBLISHED":
        job.approved_by_admin_id = current_user.id
        job.approved_at = datetime.now(timezone.utc)
        job.rejection_reason = None
    elif new_status == "REJECTED":
        job.rejection_reason = rejection_reason

    if is_featured is not None:
        job.is_featured = is_featured

    audit = AuditLog(
        user_id=current_user.id,
        action="MODERATE_JOB",
        resource="JOBS",
        details=f"Admin moderated Job ID {job.id}: status={job.status}, featured={job.is_featured}"
    )
    db.add(audit)
    await db.commit()
    return {"message": f"Job moderation updated to {job.status}."}

# Audit Logs
@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
    logs = (await db.execute(stmt)).scalars().all()
    return [AuditLogResponse.model_validate(l) for l in logs]
