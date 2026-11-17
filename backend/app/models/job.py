from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, index=True, nullable=False)
    
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    subcategory_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("job_subcategories.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by_recruiter_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("recruiter_profiles.id", ondelete="SET NULL"), nullable=True)

    # Classifications
    job_type: Mapped[str] = mapped_column(String(20), default="IT", index=True)  # IT, NON_IT
    employment_type: Mapped[str] = mapped_column(String(50), default="Full-time", index=True)  # Full-time, Part-time, Contract, Internship, Apprenticeship, Freelance
    work_arrangement: Mapped[str] = mapped_column(String(50), default="Remote", index=True)  # On-site, Hybrid, Remote, Work from home
    experience_level: Mapped[str] = mapped_column(String(50), default="Mid-level", index=True)  # Fresher, Entry-level, Junior, Mid-level, Senior, Lead, Manager, Executive
    experience_min_years: Mapped[float] = mapped_column(Float, default=0.0)
    experience_max_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Compensation
    salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(10), default="INR")
    is_salary_negotiable: Mapped[bool] = mapped_column(Boolean, default=False)

    # Geographic Location
    country: Mapped[str] = mapped_column(String(100), default="India", index=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pin_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Remote Restrictions
    remote_eligibility: Mapped[Optional[str]] = mapped_column(String(100), default="Worldwide")
    visa_sponsorship: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Detailed Content
    description: Mapped[str] = mapped_column(Text, nullable=False)
    responsibilities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    qualifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    benefits: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    openings: Mapped[int] = mapped_column(Integer, default=1)
    application_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Lifecycle & Status: DRAFT, PENDING_APPROVAL, PUBLISHED, REJECTED, PAUSED, CLOSED, ARCHIVED
    status: Mapped[str] = mapped_column(String(50), default="PENDING_APPROVAL", index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by_admin_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    applications_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    company = relationship("Company", back_populates="jobs")
    category = relationship("JobCategory", back_populates="jobs")
    subcategory = relationship("JobSubcategory", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

class JobSkill(Base):
    __tablename__ = "job_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)

    job = relationship("Job", back_populates="skills")
