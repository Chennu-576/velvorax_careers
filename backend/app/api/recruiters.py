from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.permissions import require_recruiter
from app.models.user import User
from app.models.company import Company, RecruiterProfile
from app.models.job import Job
from app.models.application import Application, Interview
from app.schemas.job import JobResponse

router = APIRouter(prefix="/recruiters", tags=["Recruiter Portal"])

class RecruiterDashboardStats(BaseModel):
    total_jobs: int
    published_jobs: int
    draft_jobs: int
    pending_approval_jobs: int
    total_applicants: int
    shortlisted_candidates: int
    interviews_scheduled: int
    closed_positions: int

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    slug: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    headquarters: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    is_verified: bool
    is_hiring_partner: bool

    class Config:
        from_attributes = True

@router.get("/dashboard", response_model=RecruiterDashboardStats)
async def get_recruiter_dashboard(
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
) -> Any:
    rec_stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
    rec_profile = (await db.execute(rec_stmt)).scalar_one_or_none()

    company_id = rec_profile.company_id if rec_profile else None
    if not company_id:
        return RecruiterDashboardStats(
            total_jobs=0,
            published_jobs=0,
            draft_jobs=0,
            pending_approval_jobs=0,
            total_applicants=0,
            shortlisted_candidates=0,
            interviews_scheduled=0,
            closed_positions=0
        )

    # Database-driven queries
    total_jobs = (await db.execute(select(func.count(Job.id)).where(Job.company_id == company_id))).scalar_one()
    published_jobs = (await db.execute(select(func.count(Job.id)).where(Job.company_id == company_id, Job.status == "PUBLISHED"))).scalar_one()
    draft_jobs = (await db.execute(select(func.count(Job.id)).where(Job.company_id == company_id, Job.status == "DRAFT"))).scalar_one()
    pending_jobs = (await db.execute(select(func.count(Job.id)).where(Job.company_id == company_id, Job.status == "PENDING_APPROVAL"))).scalar_one()
    closed_jobs = (await db.execute(select(func.count(Job.id)).where(Job.company_id == company_id, Job.status == "CLOSED"))).scalar_one()

    # Total applicants for this company's jobs
    applicants_stmt = select(func.count(Application.id)).join(Job, Application.job_id == Job.id).where(Job.company_id == company_id)
    total_applicants = (await db.execute(applicants_stmt)).scalar_one()

    # Shortlisted applicants
    shortlisted_stmt = select(func.count(Application.id)).join(Job, Application.job_id == Job.id).where(Job.company_id == company_id, Application.status == "SHORTLISTED")
    shortlisted_candidates = (await db.execute(shortlisted_stmt)).scalar_one()

    # Interviews scheduled
    interview_stmt = select(func.count(Interview.id)).join(Application, Interview.application_id == Application.id).join(Job, Application.job_id == Job.id).where(Job.company_id == company_id, Interview.status == "SCHEDULED")
    interviews_scheduled = (await db.execute(interview_stmt)).scalar_one()

    return RecruiterDashboardStats(
        total_jobs=total_jobs,
        published_jobs=published_jobs,
        draft_jobs=draft_jobs,
        pending_approval_jobs=pending_jobs,
        total_applicants=total_applicants,
        shortlisted_candidates=shortlisted_candidates,
        interviews_scheduled=interviews_scheduled,
        closed_positions=closed_jobs
    )

@router.get("/company", response_model=Optional[CompanyResponse])
async def get_my_company(
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
) -> Any:
    rec_stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
    rec_profile = (await db.execute(rec_stmt)).scalar_one_or_none()
    if not rec_profile or not rec_profile.company_id:
        return None

    comp_stmt = select(Company).where(Company.id == rec_profile.company_id)
    comp = (await db.execute(comp_stmt)).scalar_one_or_none()
    if not comp:
        return None
    return CompanyResponse.model_validate(comp)

@router.put("/company", response_model=CompanyResponse)
async def update_my_company(
    payload: CompanyUpdate,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
) -> Any:
    rec_stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
    rec_profile = (await db.execute(rec_stmt)).scalar_one_or_none()
    if not rec_profile or not rec_profile.company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found for recruiter.")

    comp_stmt = select(Company).where(Company.id == rec_profile.company_id)
    comp = (await db.execute(comp_stmt)).scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(comp, field, val)

    await db.commit()
    await db.refresh(comp)
    return CompanyResponse.model_validate(comp)

@router.get("/jobs", response_model=List[JobResponse])
async def get_my_company_jobs(
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
) -> Any:
    rec_stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
    rec_profile = (await db.execute(rec_stmt)).scalar_one_or_none()
    if not rec_profile or not rec_profile.company_id:
        return []

    stmt = (
        select(Job)
        .where(Job.company_id == rec_profile.company_id)
        .options(
            selectinload(Job.company),
            selectinload(Job.category),
            selectinload(Job.skills)
        )
        .order_by(Job.created_at.desc())
    )
    jobs = (await db.execute(stmt)).scalars().all()
    return [JobResponse.model_validate(j) for j in jobs]
