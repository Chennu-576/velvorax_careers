from typing import Optional, List, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import get_current_user, require_candidate, require_recruiter
from app.models.user import User, Notification
from app.models.candidate import CandidateProfile, Resume
from app.models.company import Company, RecruiterProfile
from app.models.job import Job
from app.models.application import Application, ApplicationStatusHistory, RecruiterNote, Interview
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatusUpdate,
    ApplicationResponse,
    InterviewCreate,
    InterviewResponse,
    CandidateSummary
)
from app.schemas.job import JobResponse
from app.schemas.candidate import ResumeResponse

router = APIRouter(tags=["Applications & ATS"])

@router.get("/notifications")
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Notification).where(Notification.user_id == current_user.id).order_by(desc(Notification.created_at))
    notifications = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": item.id,
            "title": item.title,
            "message": item.message,
            "type": item.type,
            "is_read": item.is_read,
            "action_url": item.action_url,
            "created_at": item.created_at,
        }
        for item in notifications
    ]

@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    notification = (
        await db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    notification.is_read = True
    await db.commit()
    return {"message": "Notification marked as read."}

@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def submit_application(
    payload: ApplicationCreate,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # 1. Fetch Candidate Profile
    prof_stmt = select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    candidate_profile = (await db.execute(prof_stmt)).scalar_one_or_none()
    if not candidate_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate profile not found. Please complete profile first."
        )

    # 2. Check Job validity
    job_stmt = (
        select(Job)
        .where(Job.id == payload.job_id)
        .options(selectinload(Job.company))
    )
    job = (await db.execute(job_stmt)).scalar_one_or_none()
    if not job or job.status != "PUBLISHED":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job is either not published or does not exist."
        )

    # 3. Duplicate Application Prevention (Section 16 requirement)
    dup_stmt = select(Application).where(
        Application.job_id == payload.job_id,
        Application.candidate_id == candidate_profile.id
    )
    existing_app = (await db.execute(dup_stmt)).scalar_one_or_none()
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied for this job position."
        )

    # 4. Resolve Resume
    resume_id = payload.resume_id
    if resume_id:
        resume = (
            await db.execute(
                select(Resume).where(
                    Resume.id == resume_id,
                    Resume.candidate_id == candidate_profile.id,
                )
            )
        ).scalar_one_or_none()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only apply with a resume from your own profile.",
            )
    if not resume_id:
        def_res_stmt = select(Resume).where(
            Resume.candidate_id == candidate_profile.id,
            Resume.is_default == True
        )
        def_resume = (await db.execute(def_res_stmt)).scalar_one_or_none()
        if def_resume:
            resume_id = def_resume.id

    # 5. Save Application
    application = Application(
        job_id=payload.job_id,
        candidate_id=candidate_profile.id,
        resume_id=resume_id,
        cover_letter=payload.cover_letter,
        status="APPLIED"
    )
    db.add(application)
    await db.flush()

    # 6. Status History Record
    history = ApplicationStatusHistory(
        application_id=application.id,
        previous_status=None,
        new_status="APPLIED",
        changed_by_user_id=current_user.id,
        notes="Application submitted by candidate."
    )
    db.add(history)

    # 7. Increment job application count
    job.applications_count += 1

    # 8. Notifications
    cand_notif = Notification(
        user_id=current_user.id,
        title="Application Submitted",
        message=f"You successfully applied for '{job.title}' at {job.company.name}.",
        type="APPLICATION",
        action_url=f"/candidate/applications"
    )
    db.add(cand_notif)

    recruiter_stmt = select(RecruiterProfile).where(RecruiterProfile.company_id == job.company_id)
    recruiter_profiles = (await db.execute(recruiter_stmt)).scalars().all()
    for recruiter_profile in recruiter_profiles:
        db.add(Notification(
            user_id=recruiter_profile.user_id,
            title="New Job Application",
            message=f"{current_user.full_name} applied for '{job.title}'.",
            type="APPLICATION",
            action_url="/recruiter/dashboard"
        ))

    await db.commit()

    # Return full loaded application
    full_stmt = (
        select(Application)
        .where(Application.id == application.id)
        .options(
            selectinload(Application.job).selectinload(Job.company),
            selectinload(Application.job).selectinload(Job.category),
            selectinload(Application.job).selectinload(Job.skills),
            selectinload(Application.resume),
            selectinload(Application.history),
            selectinload(Application.interviews)
        )
    )
    full_app = (await db.execute(full_stmt)).scalar_one()
    return ApplicationResponse.model_validate(full_app)

@router.get("/applications/my", response_model=List[ApplicationResponse])
async def get_my_applications(
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    prof_stmt = select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    candidate_profile = (await db.execute(prof_stmt)).scalar_one_or_none()
    if not candidate_profile:
        return []

    stmt = (
        select(Application)
        .where(Application.candidate_id == candidate_profile.id)
        .options(
            selectinload(Application.job).selectinload(Job.company),
            selectinload(Application.job).selectinload(Job.category),
            selectinload(Application.job).selectinload(Job.skills),
            selectinload(Application.resume),
            selectinload(Application.history),
            selectinload(Application.interviews)
        )
        .order_by(desc(Application.applied_at))
    )
    apps = (await db.execute(stmt)).scalars().all()
    return [ApplicationResponse.model_validate(a) for a in apps]

@router.get("/recruiter/applications", response_model=List[ApplicationResponse])
async def get_recruiter_applications(
    job_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None),
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
) -> Any:
    conditions = []

    if current_user.role == "RECRUITER":
        rec_stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
        rec_profile = (await db.execute(rec_stmt)).scalar_one_or_none()
        if not rec_profile or not rec_profile.company_id:
            return []
        # Enforce company scope
        conditions.append(Job.company_id == rec_profile.company_id)

    if job_id:
        conditions.append(Application.job_id == job_id)
    if status_filter:
        conditions.append(Application.status == status_filter.upper())

    stmt = (
        select(Application)
        .join(Application.job)
        .where(and_(*conditions))
        .options(
            selectinload(Application.job).selectinload(Job.company),
            selectinload(Application.job).selectinload(Job.category),
            selectinload(Application.job).selectinload(Job.skills),
            selectinload(Application.candidate).selectinload(CandidateProfile.user),
            selectinload(Application.resume),
            selectinload(Application.history),
            selectinload(Application.interviews)
        )
        .order_by(desc(Application.applied_at))
    )
    results = (await db.execute(stmt)).scalars().all()

    response_items = []
    for app in results:
        app_resp = ApplicationResponse.model_validate(app)
        if app.candidate and app.candidate.user:
            app_resp.candidate_summary = CandidateSummary(
                id=app.candidate.id,
                user_id=app.candidate.user_id,
                full_name=app.candidate.user.full_name,
                email=app.candidate.user.email,
                phone=app.candidate.user.phone,
                headline=app.candidate.headline,
                city=app.candidate.city,
                country=app.candidate.country
            )
        response_items.append(app_resp)

    return response_items

@router.patch("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = (
        select(Application)
        .where(Application.id == application_id)
        .options(
            selectinload(Application.job),
            selectinload(Application.candidate).selectinload(CandidateProfile.user)
        )
    )
    application = (await db.execute(stmt)).scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

    if current_user.role == "RECRUITER":
        rec_stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
        rec_profile = (await db.execute(rec_stmt)).scalar_one_or_none()
        if not rec_profile or not application.job or rec_profile.company_id != application.job.company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to modify this application.")

    old_status = application.status
    new_status = payload.status.upper()
    allowed_statuses = {
        "APPLIED", "UNDER_REVIEW", "SHORTLISTED", "INTERVIEW_SCHEDULED",
        "INTERVIEW_COMPLETED", "SELECTED", "REJECTED", "WITHDRAWN"
    }
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid application status.")
    application.status = new_status
    application.updated_at = datetime.now(timezone.utc)

    # History record
    history = ApplicationStatusHistory(
        application_id=application.id,
        previous_status=old_status,
        new_status=new_status,
        changed_by_user_id=current_user.id,
        notes=payload.notes
    )
    db.add(history)

    # Notify Candidate
    if application.candidate and application.candidate.user:
        notif = Notification(
            user_id=application.candidate.user.id,
            title="Application Status Updated",
            message=f"Your application status for '{application.job.title}' changed from {old_status} to {new_status}.",
            type="APPLICATION",
            action_url=f"/candidate/applications"
        )
        db.add(notif)

    await db.commit()
    return {"message": f"Application status updated to {new_status}."}

@router.post("/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    payload: InterviewCreate,
    current_user: User = Depends(require_recruiter),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = (
        select(Application)
        .where(Application.id == payload.application_id)
        .options(
            selectinload(Application.job),
            selectinload(Application.candidate).selectinload(CandidateProfile.user)
        )
    )
    application = (await db.execute(stmt)).scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

    if current_user.role == "RECRUITER":
        rec_stmt = select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
        rec_profile = (await db.execute(rec_stmt)).scalar_one_or_none()
        if not rec_profile or not application.job or rec_profile.company_id != application.job.company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to schedule this interview.")

    interview = Interview(
        application_id=payload.application_id,
        scheduled_by_recruiter_id=current_user.id,
        interview_type=payload.interview_type,
        scheduled_time=payload.scheduled_time,
        timezone_str=payload.timezone_str,
        meeting_link=payload.meeting_link,
        location_details=payload.location_details,
        status="SCHEDULED"
    )
    db.add(interview)

    # Update application status to INTERVIEW_SCHEDULED
    old_status = application.status
    application.status = "INTERVIEW_SCHEDULED"
    history = ApplicationStatusHistory(
        application_id=application.id,
        previous_status=old_status,
        new_status="INTERVIEW_SCHEDULED",
        changed_by_user_id=current_user.id,
        notes=f"Interview scheduled for {payload.scheduled_time} ({payload.interview_type})."
    )
    db.add(history)

    # Notify Candidate
    if application.candidate and application.candidate.user:
        notif = Notification(
            user_id=application.candidate.user.id,
            title="Interview Invitation",
            message=f"You have been invited for an interview ({payload.interview_type}) on {payload.scheduled_time} for '{application.job.title}'.",
            type="INTERVIEW",
            action_url=f"/candidate/interviews"
        )
        db.add(notif)

    await db.commit()
    await db.refresh(interview)
    return InterviewResponse.model_validate(interview)
