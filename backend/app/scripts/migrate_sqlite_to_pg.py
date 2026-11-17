import os
import sys
import argparse
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import Base
import app.models  # Load all models

# Dependency order for tables
TABLE_CLASSES = [
    # Auth & Users
    app.models.user.User,
    # Locations
    app.models.location.Country,
    app.models.location.StateProvince,
    app.models.location.District,
    app.models.location.MandalTehsil,
    app.models.location.CityTown,
    app.models.location.PostalCode,
    # Taxonomy
    app.models.taxonomy.JobCategory,
    app.models.taxonomy.JobSubcategory,
    # Companies & Recruiters
    app.models.company.Company,
    app.models.company.RecruiterProfile,
    # Candidates
    app.models.candidate.CandidateProfile,
    app.models.candidate.Skill,
    app.models.candidate.CandidateSkill,
    app.models.candidate.CandidateEducation,
    app.models.candidate.CandidateExperience,
    app.models.candidate.CandidateCertification,
    app.models.candidate.Resume,
    app.models.candidate.SavedJob,
    # Jobs
    app.models.job.Job,
    app.models.job.JobSkill,
    # Applications & Interviews
    app.models.application.Application,
    app.models.application.Interview,
    # Employer Requests
    app.models.employer_request.EmployerHiringRequest,
    # Training
    app.models.training.TrainingProgram,
    app.models.training.TrainingEnrollment,
    # Finance
    app.models.finance.Invoice,
    app.models.finance.InvoiceItem,
    app.models.finance.Payment,
    # CMS & Settings
    app.models.cms.CMSContent,
    app.models.cms.PlatformSetting,
    # Logs, Tokens & Notifications
    app.models.user.AuditLog,
    app.models.user.Notification,
    app.models.user.EmailVerificationToken,
    app.models.user.PasswordResetToken
]

async def migrate_data(source_url: str, target_url: str):
    print("=" * 70)
    print("VELVORAX CAREERS - SQLite to PostgreSQL Data Migration Utility")
    print("=" * 70)
    print(f"Source SQLite DB: {source_url}")
    # Redact credentials if present in target URL
    safe_target = target_url.split("@")[-1] if "@" in target_url else target_url
    print(f"Target DB: {safe_target}")

    source_engine = create_async_engine(source_url, echo=False)
    target_engine = create_async_engine(target_url, echo=False)

    source_session = async_sessionmaker(source_engine, class_=AsyncSession, expire_on_commit=False)
    target_session = async_sessionmaker(target_engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables in target database
    print("\n[1/3] Ensuring target database tables are provisioned...")
    async with target_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[SUCCESS] Target tables ready.")

    print("\n[2/3] Porting tables in topological order...")
    total_records = 0

    async with source_session() as s_db, target_session() as t_db:
        for model in TABLE_CLASSES:
            table_name = model.__tablename__
            try:
                # Fetch records from source
                stmt = select(model)
                res = await s_db.execute(stmt)
                records = res.scalars().all()

                if not records:
                    continue

                count = len(records)
                print(f"  -> Migrating {count:4d} rows for '{table_name}'...")

                for record in records:
                    # Create clean detached instance
                    record_dict = {
                        c.name: getattr(record, c.name)
                        for c in model.__table__.columns
                    }
                    new_instance = model(**record_dict)
                    await t_db.merge(new_instance)

                await t_db.commit()
                total_records += count

                # If target is PostgreSQL, advance primary key sequence
                if "postgresql" in target_url:
                    try:
                        seq_sql = text(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(MAX(id), 1)) FROM {table_name};")
                        await t_db.execute(seq_sql)
                        await t_db.commit()
                    except Exception:
                        pass

            except Exception as e:
                print(f"  [WARN] Issue during migration of '{table_name}': {str(e)}")
                await t_db.rollback()

    print(f"\n[3/3] Migration Complete! Total rows ported: {total_records}")
    print("=" * 70)

    await source_engine.dispose()
    await target_engine.dispose()

def main():
    parser = argparse.ArgumentParser(description="Migrate VELVORAX SQLite Database to PostgreSQL")
    parser.add_argument("--source-url", default="sqlite+aiosqlite:///./velvorax_careers.db", help="Source SQLite DB URL")
    parser.add_argument("--target-url", default=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./velvorax_careers_migrated.db"), help="Target PostgreSQL DB URL")

    args = parser.parse_args()
    asyncio.run(migrate_data(args.source_url, args.target_url))

if __name__ == "__main__":
    main()
