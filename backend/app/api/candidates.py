import os
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_candidate, get_current_user
from app.models.user import User
from app.models.candidate import (
    CandidateProfile,
    Resume,
    CandidateEducation,
    CandidateExperience,
    CandidateSkill,
    CandidateCertification,
    SavedJob
)
from app.models.job import Job
from app.models.application import Application
from app.schemas.candidate import (
    CandidateProfileResponse,
    CandidateProfileUpdate,
    EducationCreate,
    EducationResponse,
    ExperienceCreate,
    ExperienceResponse,
    SkillItem,
    SkillResponse,
    CertificationCreate,
    CertificationResponse,
    ResumeResponse
)
from app.schemas.job import JobResponse
from app.services.storage_service import StorageService

router = APIRouter(prefix="/candidates", tags=["Candidate Portal"])

@router.get("/me", response_model=CandidateProfileResponse)
async def get_my_profile(
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = (
        select(CandidateProfile)
        .where(CandidateProfile.user_id == current_user.id)
        .options(
            selectinload(CandidateProfile.educations),
            selectinload(CandidateProfile.experiences),
            selectinload(CandidateProfile.skills),
            selectinload(CandidateProfile.certifications),
            selectinload(CandidateProfile.resumes)
        )
    )
    profile = (await db.execute(stmt)).scalar_one_or_none()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return CandidateProfileResponse.model_validate(profile)

@router.put("/me", response_model=CandidateProfileResponse)
async def update_my_profile(
    payload: CandidateProfileUpdate,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = (
        select(CandidateProfile)
        .where(CandidateProfile.user_id == current_user.id)
        .options(
            selectinload(CandidateProfile.educations),
            selectinload(CandidateProfile.experiences),
            selectinload(CandidateProfile.skills),
            selectinload(CandidateProfile.certifications),
            selectinload(CandidateProfile.resumes)
        )
    )
    profile = (await db.execute(stmt)).scalar_one_or_none()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    update_data = payload.model_dump(exclude_unset=True)
    for field in ("full_name", "phone"):
        val = update_data.pop(field, None)
        if val is not None:
            setattr(current_user, field, val)

    for field, val in update_data.items():
        setattr(profile, field, val)

    await db.commit()
    await db.refresh(profile)
    return CandidateProfileResponse.model_validate(profile)

async def _get_or_create_profile(current_user: User, db: AsyncSession) -> CandidateProfile:
    profile = (
        await db.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
        )
    ).scalar_one_or_none()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()
    return profile

@router.post("/me/education", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def add_education(
    payload: EducationCreate,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create_profile(current_user, db)
    item = CandidateEducation(candidate_id=profile.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return EducationResponse.model_validate(item)

@router.post("/me/experience", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def add_experience(
    payload: ExperienceCreate,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create_profile(current_user, db)
    item = CandidateExperience(candidate_id=profile.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ExperienceResponse.model_validate(item)

@router.post("/me/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def add_skill(
    payload: SkillItem,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create_profile(current_user, db)
    item = CandidateSkill(candidate_id=profile.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return SkillResponse.model_validate(item)

@router.post(
    "/me/certifications",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_certification(
    payload: CertificationCreate,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_or_create_profile(current_user, db)
    item = CandidateCertification(candidate_id=profile.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return CertificationResponse.model_validate(item)

# Resumes Management
@router.post("/me/resumes", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    profile = (await db.execute(stmt)).scalar_one_or_none()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        await db.flush()

    resume = await StorageService.upload_resume(
        file=file,
        candidate_id=profile.id,
        db=db
    )
    return ResumeResponse.model_validate(resume)

@router.get("/me/resumes", response_model=List[ResumeResponse])
async def list_my_resumes(
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(CandidateProfile.id).where(CandidateProfile.user_id == current_user.id)
    cand_id = (await db.execute(stmt)).scalar_one_or_none()
    if not cand_id:
        return []

    res_stmt = select(Resume).where(Resume.candidate_id == cand_id).order_by(Resume.created_at.desc())
    resumes = (await db.execute(res_stmt)).scalars().all()
    return [ResumeResponse.model_validate(r) for r in resumes]

@router.delete("/me/resumes/{resume_id}")
async def delete_my_resume(
    resume_id: int,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(CandidateProfile.id).where(CandidateProfile.user_id == current_user.id)
    cand_id = (await db.execute(stmt)).scalar_one_or_none()
    if not cand_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")

    await StorageService.delete_resume(resume_id=resume_id, candidate_id=cand_id, db=db)
    return {"message": "Resume successfully deleted."}

@router.get("/resumes/{resume_id}/download")
async def download_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    resume = (await db.execute(select(Resume).where(Resume.id == resume_id))).scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    # Authorization check: Candidate owner, Recruiter, or Admin
    if current_user.role == "CANDIDATE":
        cand_stmt = select(CandidateProfile.id).where(CandidateProfile.user_id == current_user.id)
        cand_id = (await db.execute(cand_stmt)).scalar_one_or_none()
        if not cand_id or resume.candidate_id != cand_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this resume.")
    elif current_user.role not in ["ADMIN", "SUPER_ADMIN", "RECRUITER"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this resume.")
    elif current_user.role == "RECRUITER":
        from app.models.company import RecruiterProfile
        rec_profile = (
            await db.execute(
                select(RecruiterProfile).where(RecruiterProfile.user_id == current_user.id)
            )
        ).scalar_one_or_none()
        if not rec_profile:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Recruiter profile not found.")
        authorized = (
            await db.execute(
                select(Application.id)
                .join(Job, Application.job_id == Job.id)
                .where(
                    Application.candidate_id == resume.candidate_id,
                    Job.company_id == rec_profile.company_id,
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if not authorized:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this resume.")

    # If Vercel blob URL
    if resume.blob_url and resume.blob_url.startswith("http"):
        return RedirectResponse(url=resume.blob_url)

    # Local secure storage file
    local_path = os.path.join(os.getcwd(), resume.blob_url.lstrip("/"))
    if not os.path.exists(local_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found on disk.")

    return FileResponse(
        path=local_path,
        media_type=resume.mime_type or "application/pdf",
        filename=resume.original_filename
    )

# Saved Jobs
@router.post("/me/saved-jobs/{job_id}")
async def save_job(
    job_id: int,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(CandidateProfile.id).where(CandidateProfile.user_id == current_user.id)
    cand_id = (await db.execute(stmt)).scalar_one_or_none()
    if not cand_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile required.")

    # Check already saved
    dup_stmt = select(SavedJob).where(SavedJob.candidate_id == cand_id, SavedJob.job_id == job_id)
    if (await db.execute(dup_stmt)).scalar_one_or_none():
        return {"message": "Job already saved."}

    saved = SavedJob(candidate_id=cand_id, job_id=job_id)
    db.add(saved)
    await db.commit()
    return {"message": "Job successfully saved."}

@router.delete("/me/saved-jobs/{job_id}")
async def remove_saved_job(
    job_id: int,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(CandidateProfile.id).where(CandidateProfile.user_id == current_user.id)
    cand_id = (await db.execute(stmt)).scalar_one_or_none()
    if not cand_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile required.")

    dup_stmt = select(SavedJob).where(SavedJob.candidate_id == cand_id, SavedJob.job_id == job_id)
    existing = (await db.execute(dup_stmt)).scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.commit()
    return {"message": "Job removed from saved list."}

@router.get("/me/saved-jobs", response_model=List[JobResponse])
async def list_saved_jobs(
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(CandidateProfile.id).where(CandidateProfile.user_id == current_user.id)
    cand_id = (await db.execute(stmt)).scalar_one_or_none()
    if not cand_id:
        return []

    stmt_jobs = (
        select(Job)
        .join(SavedJob, SavedJob.job_id == Job.id)
        .where(SavedJob.candidate_id == cand_id)
        .options(
            selectinload(Job.company),
            selectinload(Job.category),
            selectinload(Job.skills)
        )
    )
    jobs = (await db.execute(stmt_jobs)).scalars().all()
    return [JobResponse.model_validate(j) for j in jobs]
