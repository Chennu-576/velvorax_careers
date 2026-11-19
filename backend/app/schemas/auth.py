from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


def validate_bcrypt_password_length(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password must be no more than 72 UTF-8 bytes.")
    return password

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = Field(..., description="Role selected on frontend: Admin, Recruiter/HR, or Candidate")

class CandidateRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=8)
    confirm_password: str
    country: Optional[str] = "India"
    state: Optional[str] = "Telangana"
    city: Optional[str] = "Hyderabad"
    terms_accepted: bool = True

    @field_validator("password", "confirm_password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        return validate_bcrypt_password_length(value)

class RecruiterRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    work_email: EmailStr
    phone: Optional[str] = None
    company_name: str = Field(..., min_length=2, max_length=150)
    company_website: Optional[str] = None
    company_gstin: Optional[str] = Field(None, max_length=15)
    company_cin: Optional[str] = Field(None, max_length=21)
    company_location: Optional[str] = "Hyderabad, India"
    designation: Optional[str] = "Talent Acquisition Specialist"
    password: str = Field(..., min_length=8)
    confirm_password: str
    terms_accepted: bool = True

    @field_validator("password", "confirm_password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        return validate_bcrypt_password_length(value)

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user: UserResponse

class RegistrationResponse(BaseModel):
    message: str
    email: str
    is_verified: bool
    verification_required: bool
    verification_email_sent: bool = False

class VerifyEmailRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("new_password", "confirm_password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        return validate_bcrypt_password_length(value)
