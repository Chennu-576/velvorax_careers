from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class TrainingProgram(Base):
    __tablename__ = "training_programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    skills_covered: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    training_provider: Mapped[str] = mapped_column(String(255), default="VELVORAX Academy")
    instructor: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    start_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "8 Weeks"
    mode: Mapped[str] = mapped_column(String(50), default="Online")  # Online, Offline, Hybrid
    eligibility: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    fees: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    available_seats: Mapped[int] = mapped_column(Integer, default=50)
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0)
    enrollment_deadline: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="UPCOMING")  # UPCOMING, ONGOING, COMPLETED, CANCELLED
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    enrollments = relationship("TrainingEnrollment", back_populates="program", cascade="all, delete-orphan")

class TrainingEnrollment(Base):
    __tablename__ = "training_enrollments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_programs.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    enrollment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String(50), default="ENROLLED")  # ENROLLED, IN_PROGRESS, COMPLETED, DROPPED
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    
    certificate_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    certificate_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    program = relationship("TrainingProgram", back_populates="enrollments")
    candidate = relationship("CandidateProfile")
