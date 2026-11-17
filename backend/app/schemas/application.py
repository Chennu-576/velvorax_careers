from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.job import JobResponse
from app.schemas.candidate import ResumeResponse

class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    cover_letter: Optional[str] = None

class ApplicationStatusUpdate(BaseModel):
    status: str  # APPLIED, UNDER_REVIEW, SHORTLISTED, INTERVIEW_SCHEDULED, INTERVIEW_COMPLETED, SELECTED, REJECTED, WITHDRAWN
    notes: Optional[str] = None

class InterviewCreate(BaseModel):
    application_id: int
    interview_type: str = "Video"
    scheduled_time: datetime
    timezone_str: str = "Asia/Kolkata"
    meeting_link: Optional[str] = None
    location_details: Optional[str] = None

class InterviewResponse(BaseModel):
    id: int
    application_id: int
    scheduled_by_recruiter_id: int
    interview_type: str
    scheduled_time: datetime
    timezone_str: str
    meeting_link: Optional[str] = None
    location_details: Optional[str] = None
    status: str
    feedback: Optional[str] = None
    rating: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ApplicationHistoryResponse(BaseModel):
    id: int
    previous_status: Optional[str] = None
    new_status: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CandidateSummary(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    headline: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    resume_id: Optional[int] = None
    cover_letter: Optional[str] = None
    status: str
    recruiter_rating: Optional[int] = None
    applied_at: datetime
    updated_at: datetime
    
    job: Optional[JobResponse] = None
    resume: Optional[ResumeResponse] = None
    candidate_summary: Optional[CandidateSummary] = None
    history: List[ApplicationHistoryResponse] = []
    interviews: List[InterviewResponse] = []

    class Config:
        from_attributes = True
