from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, field_validator

class JobSkillSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_name: str
    is_required: bool = True

class CompanySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    is_verified: bool
    is_hiring_partner: bool

class JobCategorySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    category_type: str
    icon: Optional[str] = None

class JobCreate(BaseModel):
    title: str
    category_id: int
    subcategory_id: Optional[int] = None
    company_id: Optional[int] = None
    job_type: str = "IT"
    employment_type: str = "Full-time"
    work_arrangement: str = "Remote"
    experience_level: str = "Mid-level"
    experience_min_years: float = 0.0
    experience_max_years: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "INR"
    is_salary_negotiable: bool = False
    country: str = "India"
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    pin_code: Optional[str] = None
    remote_eligibility: Optional[str] = "Worldwide"
    visa_sponsorship: bool = False
    description: str
    responsibilities: Optional[str] = None
    qualifications: Optional[str] = None
    benefits: Optional[str] = None
    openings: int = 1
    application_deadline: Optional[datetime] = None
    skills: List[str] = []

    @field_validator("application_deadline")
    @classmethod
    def deadline_is_utc(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is not None:
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("Application deadline must include a timezone.")
            return value.astimezone(timezone.utc)
        return value

class JobUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    job_type: Optional[str] = None
    employment_type: Optional[str] = None
    work_arrangement: Optional[str] = None
    experience_level: Optional[str] = None
    experience_min_years: Optional[float] = None
    experience_max_years: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    is_salary_negotiable: Optional[bool] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    pin_code: Optional[str] = None
    remote_eligibility: Optional[str] = None
    visa_sponsorship: Optional[bool] = None
    description: Optional[str] = None
    responsibilities: Optional[str] = None
    qualifications: Optional[str] = None
    benefits: Optional[str] = None
    openings: Optional[int] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    application_deadline: Optional[datetime] = None
    skills: Optional[List[str]] = None

    @field_validator("application_deadline")
    @classmethod
    def deadline_is_utc(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is not None:
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("Application deadline must include a timezone.")
            return value.astimezone(timezone.utc)
        return value

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    company_id: int
    category_id: int
    subcategory_id: Optional[int] = None
    job_type: str
    employment_type: str
    work_arrangement: str
    experience_level: str
    experience_min_years: float
    experience_max_years: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str
    is_salary_negotiable: bool
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    pin_code: Optional[str] = None
    remote_eligibility: Optional[str] = None
    visa_sponsorship: bool
    description: str
    responsibilities: Optional[str] = None
    qualifications: Optional[str] = None
    benefits: Optional[str] = None
    openings: int
    application_deadline: Optional[datetime] = None
    status: str
    is_featured: bool
    rejection_reason: Optional[str] = None
    approved_by_admin_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    views_count: int
    applications_count: int
    created_at: datetime
    updated_at: datetime
    
    company: Optional[CompanySummary] = None
    category: Optional[JobCategorySummary] = None
    skills: List[JobSkillSchema] = []

class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
