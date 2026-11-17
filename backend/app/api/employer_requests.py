from typing import Optional, List, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_admin
from app.models.user import User
from app.models.company import Company
from app.models.taxonomy import JobCategory
from app.models.job import Job
from app.models.employer_request import EmployerHiringRequest, HiringRequestStatusHistory
from app.schemas.employer_request import (
    EmployerRequestCreate,
    EmployerRequestStatusUpdate,
    EmployerRequestResponse
)

router = APIRouter(tags=["Employer Hiring Requests"])

@router.post("/employer-requests", response_model=EmployerRequestResponse, status_code=status.HTTP_201_CREATED)
async def submit_employer_request(
    payload: EmployerRequestCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    request = EmployerHiringRequest(
        company_name=payload.company_name,
        contact_person=payload.contact_person,
        contact_email=payload.contact_email,
        phone=payload.phone,
        job_title=payload.job_title,
        job_category=payload.job_category,
        vacancies_count=payload.vacancies_count,
        required_skills=payload.required_skills,
        experience_range=payload.experience_range,
        job_location=payload.job_location,
        employment_type=payload.employment_type,
        salary_range=payload.salary_range,
        job_description=payload.job_description,
        expected_hiring_date=payload.expected_hiring_date,
        additional_requirements=payload.additional_requirements,
        status="SUBMITTED"
    )
    db.add(request)
    await db.flush()

    history = HiringRequestStatusHistory(
        request_id=request.id,
        previous_status=None,
        new_status="SUBMITTED",
        notes="Employer hiring requirement submitted online."
    )
    db.add(history)
    await db.commit()
    await db.refresh(request)
    return EmployerRequestResponse.model_validate(request)

@router.get("/admin/employer-requests", response_model=List[EmployerRequestResponse])
async def list_employer_requests(
    status_filter: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    conditions = []
    if status_filter:
        conditions.append(EmployerHiringRequest.status == status_filter.upper())

    stmt = (
        select(EmployerHiringRequest)
        .where(and_(*conditions))
        .order_by(desc(EmployerHiringRequest.created_at))
    )
    requests = (await db.execute(stmt)).scalars().all()
    return [EmployerRequestResponse.model_validate(r) for r in requests]

@router.patch("/admin/employer-requests/{request_id}", response_model=EmployerRequestResponse)
async def update_employer_request_status(
    request_id: int,
    payload: EmployerRequestStatusUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(EmployerHiringRequest).where(EmployerHiringRequest.id == request_id)
    req = (await db.execute(stmt)).scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hiring request not found.")

    old_status = req.status
    new_status = payload.status.upper()
    req.status = new_status
    if payload.admin_notes:
        req.admin_notes = payload.admin_notes
    req.updated_at = datetime.now(timezone.utc)

    # Convert to job posting workflow (Section 13.3)
    if new_status == "CONVERTED_TO_JOB" and not req.converted_job_id:
        # Check or create Company
        comp_slug = req.company_name.lower().replace(" ", "-").replace(".", "")
        c_stmt = select(Company).where(Company.slug == comp_slug)
        company = (await db.execute(c_stmt)).scalar_one_or_none()
        if not company:
            company = Company(
                name=req.company_name,
                slug=comp_slug,
                country="India",
                city=req.job_location or "Hyderabad",
                is_verified=True
            )
            db.add(company)
            await db.flush()

        # Find or use default category
        cat_stmt = select(JobCategory.id).where(JobCategory.name.ilike(f"%{req.job_category or 'Software'}%"))
        cat_id = (await db.execute(cat_stmt)).scalar_one_or_none()
        if not cat_id:
            cat_id = 1

        import re
        slug_base = re.sub(r'[^a-z0-9\-]', '', req.job_title.lower().replace(" ", "-"))
        job_slug = f"{slug_base}-{int(datetime.now(timezone.utc).timestamp())}"

        new_job = Job(
            title=req.job_title,
            slug=job_slug,
            company_id=company.id,
            category_id=cat_id,
            job_type="IT",
            employment_type=req.employment_type or "Full-time",
            work_arrangement="Hybrid",
            experience_level="Mid-level",
            country="India",
            city=req.job_location or "Hyderabad",
            description=req.job_description,
            openings=req.vacancies_count,
            status="PUBLISHED"
        )
        db.add(new_job)
        await db.flush()
        req.converted_job_id = new_job.id

    history = HiringRequestStatusHistory(
        request_id=req.id,
        previous_status=old_status,
        new_status=new_status,
        changed_by_user_id=current_user.id,
        notes=payload.admin_notes or f"Status changed to {new_status}."
    )
    db.add(history)
    await db.commit()
    await db.refresh(req)
    return EmployerRequestResponse.model_validate(req)
