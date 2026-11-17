from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class TrainingProgramCreate(BaseModel):
    title: str
    description: str
    category: Optional[str] = "Artificial Intelligence"
    skills_covered: Optional[str] = None
    training_provider: Optional[str] = "VELVORAX Academy"
    instructor: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = "8 Weeks"
    mode: str = "Online"
    eligibility: Optional[str] = "Open to all candidates"
    fees: float = 0.0
    currency: str = "INR"
    available_seats: int = 50
    enrollment_deadline: Optional[str] = None

class TrainingProgramResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    category: Optional[str] = None
    skills_covered: Optional[str] = None
    training_provider: str
    instructor: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    mode: str
    eligibility: Optional[str] = None
    fees: float
    currency: str
    available_seats: int
    enrolled_count: int
    enrollment_deadline: Optional[str] = None
    status: str
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TrainingEnrollmentResponse(BaseModel):
    id: int
    program_id: int
    candidate_id: int
    enrollment_date: datetime
    status: str
    progress_percentage: int
    certificate_url: Optional[str] = None
    certificate_number: Optional[str] = None
    program: Optional[TrainingProgramResponse] = None

    class Config:
        from_attributes = True
