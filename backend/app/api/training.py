from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_candidate, require_admin
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.models.training import TrainingProgram, TrainingEnrollment
from app.schemas.training import (
    TrainingProgramCreate,
    TrainingProgramResponse,
    TrainingEnrollmentResponse
)

router = APIRouter(prefix="/training", tags=["Training & Career Development"])

@router.get("/programs", response_model=List[TrainingProgramResponse])
async def list_programs(
    is_published: bool = True,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = (
        select(TrainingProgram)
        .where(TrainingProgram.is_published == is_published)
        .order_by(desc(TrainingProgram.created_at))
    )
    programs = (await db.execute(stmt)).scalars().all()
    return [TrainingProgramResponse.model_validate(p) for p in programs]

@router.post("/programs/{program_id}/enroll", response_model=TrainingEnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_program(
    program_id: int,
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    prof_stmt = select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    cand_profile = (await db.execute(prof_stmt)).scalar_one_or_none()
    if not cand_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Candidate profile required.")

    prog_stmt = select(TrainingProgram).where(TrainingProgram.id == program_id)
    program = (await db.execute(prog_stmt)).scalar_one_or_none()
    if not program or not program.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training program not found.")

    # Check if already enrolled
    existing_stmt = select(TrainingEnrollment).where(
        TrainingEnrollment.program_id == program_id,
        TrainingEnrollment.candidate_id == cand_profile.id
    )
    existing = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are already enrolled in this program.")

    enrollment = TrainingEnrollment(
        program_id=program_id,
        candidate_id=cand_profile.id,
        status="ENROLLED",
        progress_percentage=0
    )
    db.add(enrollment)
    program.enrolled_count += 1
    await db.commit()
    await db.refresh(enrollment)

    # Reload with program
    stmt = select(TrainingEnrollment).where(TrainingEnrollment.id == enrollment.id).options(selectinload(TrainingEnrollment.program))
    loaded = (await db.execute(stmt)).scalar_one()
    return TrainingEnrollmentResponse.model_validate(loaded)

@router.get("/my-enrollments", response_model=List[TrainingEnrollmentResponse])
async def list_my_enrollments(
    current_user: User = Depends(require_candidate),
    db: AsyncSession = Depends(get_db)
) -> Any:
    prof_stmt = select(CandidateProfile.id).where(CandidateProfile.user_id == current_user.id)
    cand_id = (await db.execute(prof_stmt)).scalar_one_or_none()
    if not cand_id:
        return []

    stmt = (
        select(TrainingEnrollment)
        .where(TrainingEnrollment.candidate_id == cand_id)
        .options(selectinload(TrainingEnrollment.program))
        .order_by(desc(TrainingEnrollment.enrollment_date))
    )
    enrollments = (await db.execute(stmt)).scalars().all()
    return [TrainingEnrollmentResponse.model_validate(e) for e in enrollments]

@router.post("/programs", response_model=TrainingProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
    payload: TrainingProgramCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    import re
    slug = re.sub(r'[^a-z0-9\-]', '', payload.title.lower().replace(" ", "-"))
    prog = TrainingProgram(
        title=payload.title,
        slug=slug,
        description=payload.description,
        category=payload.category,
        skills_covered=payload.skills_covered,
        training_provider=payload.training_provider or "VELVORAX Academy",
        instructor=payload.instructor,
        start_date=payload.start_date,
        end_date=payload.end_date,
        duration=payload.duration,
        mode=payload.mode,
        eligibility=payload.eligibility,
        fees=payload.fees,
        currency=payload.currency,
        available_seats=payload.available_seats,
        is_published=True
    )
    db.add(prog)
    await db.commit()
    await db.refresh(prog)
    return TrainingProgramResponse.model_validate(prog)
