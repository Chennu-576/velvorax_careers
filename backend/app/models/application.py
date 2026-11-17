from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("candidate_resumes.id", ondelete="SET NULL"), nullable=True)

    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status Lifecycle: APPLIED, UNDER_REVIEW, SHORTLISTED, INTERVIEW_SCHEDULED, INTERVIEW_COMPLETED, SELECTED, REJECTED, WITHDRAWN
    status: Mapped[str] = mapped_column(String(50), default="APPLIED", index=True)
    recruiter_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1 to 5 stars
    
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("CandidateProfile", back_populates="applications")
    resume = relationship("Resume")
    history = relationship("ApplicationStatusHistory", back_populates="application", cascade="all, delete-orphan")
    notes = relationship("RecruiterNote", back_populates="application", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")

class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    application = relationship("Application", back_populates="history")

class RecruiterNote(Base):
    __tablename__ = "recruiter_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    recruiter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    application = relationship("Application", back_populates="notes")

class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_by_recruiter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    interview_type: Mapped[str] = mapped_column(String(50), default="Video")  # Screening, Technical, HR, Managerial, In-Person
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    timezone_str: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata")
    meeting_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    location_details: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status: SCHEDULED, COMPLETED, CANCELLED, RESCHEDULED
    status: Mapped[str] = mapped_column(String(50), default="SCHEDULED", index=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    application = relationship("Application", back_populates="interviews")
