from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class EmployerHiringRequest(Base):
    __tablename__ = "employer_hiring_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    vacancies_count: Mapped[int] = mapped_column(Integer, default=1)
    required_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experience_range: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(50), default="Full-time")
    salary_range: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    job_description: Mapped[Text] = mapped_column(Text, nullable=False)
    expected_hiring_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    additional_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status: SUBMITTED, UNDER_REVIEW, MORE_INFO_REQUIRED, APPROVED, REJECTED, CONVERTED_TO_JOB, CLOSED
    status: Mapped[str] = mapped_column(String(50), default="SUBMITTED", index=True)
    converted_job_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    history = relationship("HiringRequestStatusHistory", back_populates="request", cascade="all, delete-orphan")

class HiringRequestStatusHistory(Base):
    __tablename__ = "hiring_request_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("employer_hiring_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    request = relationship("EmployerHiringRequest", back_populates="history")
