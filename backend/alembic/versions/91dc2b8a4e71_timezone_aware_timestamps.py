"""Make persisted timestamps timezone-aware.

Revision ID: 91dc2b8a4e71
Revises: 65cbf53cb47b
Create Date: 2026-11-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "91dc2b8a4e71"
down_revision: Union[str, Sequence[str], None] = "65cbf53cb47b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TIMESTAMP_COLUMNS = {
    "users": ("created_at", "updated_at"),
    "audit_logs": ("created_at",),
    "notifications": ("created_at",),
    "email_verification_tokens": ("expires_at", "created_at"),
    "password_reset_tokens": ("expires_at", "created_at"),
    "companies": ("created_at", "updated_at"),
    "recruiter_profiles": ("created_at", "updated_at"),
    "candidate_profiles": ("created_at", "updated_at"),
    "candidate_resumes": ("created_at", "updated_at"),
    "saved_jobs": ("created_at",),
    "job_categories": ("created_at", "updated_at"),
    "job_subcategories": ("created_at",),
    "jobs": ("application_deadline", "approved_at", "created_at", "updated_at"),
    "applications": ("applied_at", "updated_at"),
    "application_status_history": ("created_at",),
    "recruiter_notes": ("created_at",),
    "interviews": ("scheduled_time", "created_at", "updated_at"),
    "employer_hiring_requests": ("created_at", "updated_at"),
    "hiring_request_status_history": ("created_at",),
    "training_programs": ("created_at", "updated_at"),
    "training_enrollments": ("enrollment_date", "created_at", "updated_at"),
    "invoices": ("issued_at", "paid_at", "created_at", "updated_at"),
    "payments": ("created_at",),
    "cms_contents": ("updated_at",),
    "announcements": ("created_at",),
}


def _alter_timestamp_columns(*, timezone: bool) -> None:
    if op.get_bind().dialect.name != "postgresql":
        raise RuntimeError("The timestamp migration requires PostgreSQL.")

    for table_name, column_names in TIMESTAMP_COLUMNS.items():
        for column_name in column_names:
            target_type = sa.DateTime(timezone=timezone)
            op.alter_column(
                table_name,
                column_name,
                existing_type=sa.DateTime(timezone=not timezone),
                type_=target_type,
                postgresql_using=f'"{column_name}" AT TIME ZONE \'UTC\'',
            )


def upgrade() -> None:
    _alter_timestamp_columns(timezone=True)


def downgrade() -> None:
    _alter_timestamp_columns(timezone=False)
