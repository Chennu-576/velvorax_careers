from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class ResumeResponse(BaseModel):
    id: int
    candidate_id: int
    original_filename: str
    blob_pathname: str
    blob_url: Optional[str] = None
    file_size_bytes: int
    mime_type: str
    is_default: bool
    is_scanned_safe: bool
    created_at: datetime

    class Config:
        from_attributes = True

class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class EducationResponse(EducationBase):
    id: int
    candidate_id: int

    class Config:
        from_attributes = True

class ExperienceBase(BaseModel):
    company: str
    job_title: str
    employment_type: Optional[str] = "Full-time"
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceResponse(ExperienceBase):
    id: int
    candidate_id: int

    class Config:
        from_attributes = True

class SkillItem(BaseModel):
    skill_name: str
    proficiency: Optional[str] = "Intermediate"
    years_of_experience: Optional[float] = 1.0

class SkillResponse(SkillItem):
    id: int

    class Config:
        from_attributes = True

class CertificationBase(BaseModel):
    name: str
    issuing_organization: str
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None

class CertificationCreate(CertificationBase):
    pass

class CertificationResponse(CertificationBase):
    id: int

    class Config:
        from_attributes = True

class CandidateProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    pin_code: Optional[str] = None
    preferred_location: Optional[str] = None
    preferred_job_type: Optional[str] = None
    expected_salary: Optional[float] = None
    salary_currency: Optional[str] = "INR"
    experience_years: Optional[float] = None
    notice_period_days: Optional[int] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class CandidateProfileResponse(BaseModel):
    id: int
    user_id: int
    headline: Optional[str] = None
    summary: Optional[str] = None
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    pin_code: Optional[str] = None
    preferred_location: Optional[str] = None
    preferred_job_type: Optional[str] = None
    expected_salary: Optional[float] = None
    salary_currency: str = "INR"
    experience_years: Optional[float] = 0.0
    notice_period_days: Optional[int] = 30
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    
    educations: List[EducationResponse] = []
    experiences: List[ExperienceResponse] = []
    skills: List[SkillResponse] = []
    certifications: List[CertificationResponse] = []
    resumes: List[ResumeResponse] = []

    class Config:
        from_attributes = True
