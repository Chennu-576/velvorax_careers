from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

class EmployerRequestCreate(BaseModel):
    company_name: str
    contact_person: str
    contact_email: EmailStr
    phone: Optional[str] = None
    job_title: str
    job_category: Optional[str] = "Software Development"
    vacancies_count: int = 1
    required_skills: Optional[str] = None
    experience_range: Optional[str] = "3-5 years"
    job_location: Optional[str] = "Hyderabad, India"
    employment_type: Optional[str] = "Full-time"
    salary_range: Optional[str] = "15-25 LPA"
    job_description: str
    expected_hiring_date: Optional[str] = None
    additional_requirements: Optional[str] = None

class EmployerRequestStatusUpdate(BaseModel):
    status: str  # SUBMITTED, UNDER_REVIEW, MORE_INFO_REQUIRED, APPROVED, REJECTED, CONVERTED_TO_JOB, CLOSED
    admin_notes: Optional[str] = None

class EmployerRequestResponse(BaseModel):
    id: int
    company_name: str
    contact_person: str
    contact_email: str
    phone: Optional[str] = None
    job_title: str
    job_category: Optional[str] = None
    vacancies_count: int
    required_skills: Optional[str] = None
    experience_range: Optional[str] = None
    job_location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[str] = None
    job_description: str
    expected_hiring_date: Optional[str] = None
    additional_requirements: Optional[str] = None
    status: str
    converted_job_id: Optional[int] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
