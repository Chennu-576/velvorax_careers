from pathlib import Path
from typing import List, Literal, Optional

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "VELVORAX Careers API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str
    # Security & Verification
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    SUPERADMIN_EMAIL: str = "admin@velvorax.tech"
    SUPERADMIN_PASSWORD: Optional[str] = None
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "https://velvorax-careers.vercel.app"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    # Email delivery
    EMAIL_PROVIDER: Literal["resend", "smtp"] = "resend"
    RESEND_API_KEY: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False
    EMAIL_FROM: str = Field(
        default="no-reply@velvorax.tech",
        validation_alias=AliasChoices("EMAIL_FROM", "SMTP_FROM_EMAIL"),
    )

    # Vercel Blob / Resume Storage
    BLOB_READ_WRITE_TOKEN: str = ""
    MAX_RESUME_SIZE_BYTES: int = 2 * 1024 * 1024  # 2 MB limit
    MAX_TOTAL_STORAGE_BYTES: int = 950 * 1024 * 1024  # 950 MB safety threshold

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "https://velvorax-careers.vercel.app",
    ]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()



# from typing import List, Optional

# from pydantic import field_validator
# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     PROJECT_NAME: str = "VELVORAX Careers API"
#     VERSION: str = "1.0.0"
#     API_V1_STR: str = "/api/v1"

#     # PostgreSQL is mandatory
#     DATABASE_URL: str

#     # Security
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

#     SUPERADMIN_EMAIL: Optional[str] = None
#     SUPERADMIN_PASSWORD: Optional[str] = None

#     # Storage
#     BLOB_READ_WRITE_TOKEN: str = ""
#     MAX_RESUME_SIZE_BYTES: int = 2 * 1024 * 1024
#     MAX_TOTAL_STORAGE_BYTES: int = 950 * 1024 * 1024

#     # CORS
#     CORS_ORIGINS: List[str] = [
#         "http://localhost:3000",
#         "http://127.0.0.1:3000",
#         "http://localhost:3001"
#     ]

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore"
#     )

#     @field_validator("DATABASE_URL")
#     @classmethod
#     def validate_database_url(cls, value: str) -> str:
#         if not value.startswith("postgresql+asyncpg://"):
#             raise ValueError(
#                 "Only PostgreSQL with asyncpg is supported."
#             )
#         return value


# settings = Settings()
