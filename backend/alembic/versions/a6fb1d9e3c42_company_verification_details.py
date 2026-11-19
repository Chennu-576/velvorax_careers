"""Store company registration details and manual verification review.

Revision ID: a6fb1d9e3c42
Revises: 91dc2b8a4e71
Create Date: 2026-11-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a6fb1d9e3c42"
down_revision: Union[str, Sequence[str], None] = "91dc2b8a4e71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("gstin", sa.String(length=15), nullable=True))
    op.add_column("companies", sa.Column("cin", sa.String(length=21), nullable=True))
    op.add_column(
        "companies", sa.Column("registration_number", sa.String(length=100), nullable=True)
    )
    op.add_column("companies", sa.Column("verification_notes", sa.Text(), nullable=True))
    op.add_column(
        "companies", sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "companies",
        sa.Column("verified_by_user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_companies_verified_by_user_id_users",
        "companies",
        "users",
        ["verified_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_companies_verified_by_user_id_users", "companies", type_="foreignkey"
    )
    op.drop_column("companies", "verified_by_user_id")
    op.drop_column("companies", "verified_at")
    op.drop_column("companies", "verification_notes")
    op.drop_column("companies", "registration_number")
    op.drop_column("companies", "cin")
    op.drop_column("companies", "gstin")
