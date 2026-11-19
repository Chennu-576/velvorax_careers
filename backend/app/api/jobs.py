import math
from typing import Optional, List, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import get_current_user, require_recruiter
from app.models.user import User
from app.models.company import Company, RecruiterProfile
from app.models.taxonomy import JobCategory, JobSubcategory
from app.models.job import Job, JobSkill
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("", response_model=JobListResponse)
async def list_jobs(
    q: Optional[str] = Query(None, description="Search keyword across title, description, skills"),
    job_type: Optional[str] = Query(None, description="IT or NON_IT"),
    category_id: Optional[int] = Query(None),
    category_slug: Optional[str] = Query(None),
    subcategory_id: Optional[int] = Query(None),
    subcategory_slug: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    work_arrangement: Optional[str] = Query(None),
    salary_min: Optional[float] = Query(None),
    salary_max: Optional[float] = Query(None),
    is_featured: Optional[bool] = Query(None),
    sort_by: str = Query("latest", description="latest, oldest, salary_asc, salary_desc, popular"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Base query for published jobs
    conditions = [Job.status == "PUBLISHED"]

    if job_type:
        conditions.append(Job.job_type == job_type.upper())

    if category_id:
        conditions.append(Job.category_id == category_id)
    elif category_slug:
        cat_stmt = select(JobCategory.id).where(JobCategory.slug == category_slug)
        cat_id = (await db.execute(cat_stmt)).scalar_one_or_none()
        if cat_id:
            conditions.append(Job.category_id == cat_id)

    if subcategory_id:
        conditions.append(Job.subcategory_id == subcategory_id)
    elif subcategory_slug:
        subcat_stmt = select(JobSubcategory.id).where(JobSubcategory.slug == subcategory_slug)
        subcat_id = (await db.execute(subcat_stmt)).scalar_one_or_none()
        if subcat_id:
            conditions.append(Job.subcategory_id == subcat_id)

    if country:
        conditions.append(Job.country.ilike(f"%{country}%"))
    if state:
        conditions.append(Job.state.ilike(f"%{state}%"))
    if city:
        conditions.append(Job.city.ilike(f"%{city}%"))

    if employment_type:
        conditions.append(Job.employment_type == employment_type)
    if experience_level:
        conditions.append(Job.experience_level == experience_level)
    if work_arrangement:
        conditions.append(Job.work_arrangement == work_arrangement)

    if salary_min is not None:
        conditions.append(or_(Job.salary_min >= salary_min, Job.salary_max >= salary_min))
    if salary_max is not None:
        conditions.append(Job.salary_min <= salary_max)

    if is_featured is not None:
        conditions.append(Job.is_featured == is_featured)

    if q:
        search_filter = or_(
            Job.title.ilike(f"%{q}%"),
            Job.description.ilike(f"%{q}%"),
            Job.city.ilike(f"%{q}%"),
            Job.country.ilike(f"%{q}%")
        )
        conditions.append(search_filter)

    # Count total
    count_query = select(func.count(Job.id)).where(and_(*conditions))
    total_count = (await db.execute(count_query)).scalar_one()

    # Base select query with relations
    stmt = (
        select(Job)
        .where(and_(*conditions))
        .options(
            selectinload(Job.company),
            selectinload(Job.category),
            selectinload(Job.skills)
        )
    )

    # Sorting
    if sort_by == "latest":
        stmt = stmt.order_by(desc(Job.created_at))
    elif sort_by == "oldest":
        stmt = stmt.order_by(asc(Job.created_at))
    elif sort_by == "salary_desc":
        stmt = stmt.order_by(desc(Job.salary_max))
    elif sort_by == "salary_asc":
        stmt = stmt.order_by(asc(Job.salary_min))
    elif sort_by == "popular":
        stmt = stmt.order_by(desc(Job.views_count), desc(Job.applications_count))
    else:
        stmt = stmt.order_by(desc(Job.created_at))

    # Pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    result = await db.execute(stmt)
    jobs = result.scalars().all()

    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

    return JobListResponse(
        items=[JobResponse.model_validate(job) for job in jobs],
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{identifier}", response_model=JobResponse)
async def get_job_by_slug_or_id(
    identifier: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Support lookup by integer ID or unique slug
    if identifier.isdigit():
        condition = Job.id == int(identifier)
    else:
        condition = Job.slug == identifier

    stmt = (
        select(Job)
        .where(condition, Job.status == "PUBLISHED")
        .options(
            selectinload(Job.company),
            selectinload(Job.category),
            selectinload(Job.skills)
        )
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found for '{identifier}'."
        )

    # Increment view count
    job.views_count += 1
    await db.commit()
    await db.refresh(job)

    return JobResponse.model_validate(job)

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
) -> Any:
    company_id = payload.company_id
    recruiter_profile_id = None

    if current_user.role == "RECRUITER":
        rec_stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
        rec_profile = (await db.execute(rec_stmt)).scalar_one_or_none()
        if not rec_profile or not rec_profile.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recruiter profile has no linked company. Please complete company setup first."
            )
        company_id = rec_profile.company_id
        recruiter_profile_id = rec_profile.id

    if not company_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company ID is required.")

    # Generate unique slug
    base_slug = payload.title.lower().replace(" ", "-").replace("/", "-").replace("&", "and")
    import re
    base_slug = re.sub(r'[^a-z0-9\-]', '', base_slug)
    slug = f"{base_slug}-{int(datetime.now(timezone.utc).timestamp())}"

    job = Job(
        title=payload.title,
        slug=slug,
        company_id=company_id,
        category_id=payload.category_id,
        subcategory_id=payload.subcategory_id,
        created_by_recruiter_id=recruiter_profile_id,
        job_type=payload.job_type,
        employment_type=payload.employment_type,
        work_arrangement=payload.work_arrangement,
        experience_level=payload.experience_level,
        experience_min_years=payload.experience_min_years,
        experience_max_years=payload.experience_max_years,
        salary_min=payload.salary_min,
        salary_max=payload.salary_max,
        salary_currency=payload.salary_currency,
        is_salary_negotiable=payload.is_salary_negotiable,
        country=payload.country,
        state=payload.state,
        city=payload.city,
        address=payload.address,
        pin_code=payload.pin_code,
        remote_eligibility=payload.remote_eligibility,
        visa_sponsorship=payload.visa_sponsorship,
        description=payload.description,
        responsibilities=payload.responsibilities,
        qualifications=payload.qualifications,
        benefits=payload.benefits,
        openings=payload.openings,
        application_deadline=payload.application_deadline,
        status="PUBLISHED" if current_user.role in ["ADMIN", "SUPER_ADMIN"] else "PENDING_APPROVAL"
    )
    db.add(job)
    await db.flush()

    # Add required skills
    for s in payload.skills:
        skill_entry = JobSkill(job_id=job.id, skill_name=s.strip(), is_required=True)
        db.add(skill_entry)

    await db.commit()
    
    # Reload with relationships
    stmt = (
        select(Job)
        .where(Job.id == job.id)
        .options(
            selectinload(Job.company),
            selectinload(Job.category),
            selectinload(Job.skills)
        )
    )
    job_full = (await db.execute(stmt)).scalar_one()
    return JobResponse.model_validate(job_full)

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    payload: JobUpdate,
    current_user: User = Depends(require_recruiter),
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

    if current_user.role == "RECRUITER":
        rec_stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
        rec_profile = (await db.execute(rec_stmt)).scalar_one_or_none()
        if not rec_profile or rec_profile.company_id != job.company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to modify this job.")

    # Apply updates
    update_data = payload.model_dump(exclude_unset=True)
    skills = update_data.pop("skills", None)
    for field, val in update_data.items():
        if field == "status" and current_user.role == "RECRUITER":
            if val.upper() in ["PUBLISHED", "APPROVED"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Recruiters cannot publish vacancies directly. Vacancies must be submitted for Admin approval."
                )
        setattr(job, field, val)

    if skills is not None:
        for skill in list(job.skills):
            await db.delete(skill)
        await db.flush()
        for skill_name in skills:
            if skill_name.strip():
                db.add(JobSkill(job_id=job.id, skill_name=skill_name.strip(), is_required=True))

    # Recruiter lifecycle state machine: If rejected job is edited by recruiter, reset to PENDING_APPROVAL
    if current_user.role == "RECRUITER" and job.status == "REJECTED":
        job.status = "PENDING_APPROVAL"
        job.rejection_reason = None

    job.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(job)
    return JobResponse.model_validate(job)

@router.patch("/{job_id}/status")
async def update_job_status(
    job_id: int,
    status_val: str = Query(..., description="DRAFT, PENDING_APPROVAL, PUBLISHED, REJECTED, PAUSED, CLOSED, ARCHIVED"),
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Job).where(Job.id == job_id)
    job = (await db.execute(stmt)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    if current_user.role == "RECRUITER":
        rec_stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
        rec_profile = (await db.execute(rec_stmt)).scalar_one_or_none()
        if not rec_profile or rec_profile.company_id != job.company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to modify this job.")

        target_status = status_val.upper()
        if target_status in ["PUBLISHED", "APPROVED"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Recruiters cannot publish vacancies directly. Vacancies must be submitted for Admin approval."
            )
        if target_status not in ["DRAFT", "PENDING_APPROVAL", "PAUSED", "CLOSED", "ARCHIVED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid target status '{target_status}' for recruiter."
            )
        if target_status == "PENDING_APPROVAL":
            job.rejection_reason = None
        job.status = target_status
    else:
        # Admin / Super Admin
        job.status = status_val.upper()
        if job.status == "PUBLISHED":
            job.approved_by_admin_id = current_user.id
            job.approved_at = datetime.now(timezone.utc)
            job.rejection_reason = None

    job.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": f"Job status updated to {job.status}."}

