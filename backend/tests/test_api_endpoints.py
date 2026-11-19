import io
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy import DateTime

from app.main import app
from app.core.config import settings
from app.core.database import async_session_maker, Base
from app.models.user import User
from app.models.company import Company, RecruiterProfile
from app.models.candidate import CandidateProfile, Resume
from app.services.email_service import EmailService

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_auth_registration_preflight_and_duplicate_email(async_client: AsyncClient):
    origin = settings.CORS_ORIGINS[0]
    preflight = await async_client.options(
        "/api/v1/auth/register/candidate",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert preflight.status_code == 200
    assert "POST" in preflight.headers["access-control-allow-methods"]

    email = f"duplicate.{uuid.uuid4().hex}@velvorax.tech"
    payload = {
        "full_name": "Duplicate Candidate",
        "email": email,
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "terms_accepted": True,
    }
    first = await async_client.post("/api/v1/auth/register/candidate", json=payload)
    duplicate = await async_client.post("/api/v1/auth/register/candidate", json=payload)

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Email already exists."

def test_all_persisted_datetime_columns_are_timezone_aware():
    datetime_columns = [
        column
        for table in Base.metadata.tables.values()
        for column in table.columns
        if isinstance(column.type, DateTime)
    ]
    assert datetime_columns
    assert all(column.type.timezone for column in datetime_columns)

@pytest.mark.asyncio
async def test_recruiter_must_have_verified_company_before_posting(
    async_client: AsyncClient, test_recruiter, test_admin
):
    async with async_session_maker() as db:
        company = await db.get(Company, test_recruiter["company_id"])
        profile = (
            await db.execute(
                select(RecruiterProfile).where(
                    RecruiterProfile.user_id == test_recruiter["user"].id
                )
            )
        ).scalar_one()
        company.is_verified = False
        profile.is_approved = False
        await db.commit()

    job_payload = {
        "title": f"Verified Employer Role {uuid.uuid4().hex[:6]}",
        "category_id": 1,
        "description": "A test role requiring manual employer verification.",
        "skills": ["Python"],
    }
    blocked = await async_client.post(
        "/api/v1/jobs", headers=test_recruiter["headers"], json=job_payload
    )
    assert blocked.status_code == 403

    verification = await async_client.patch(
        f"/api/v1/admin/companies/{test_recruiter['company_id']}/verify",
        params={
            "is_verified": "true",
            "is_hiring_partner": "true",
            "verification_notes": "Registration information manually reviewed.",
        },
        headers=test_admin["headers"],
    )
    assert verification.status_code == 200

    allowed = await async_client.post(
        "/api/v1/jobs", headers=test_recruiter["headers"], json=job_payload
    )
    assert allowed.status_code == 201

@pytest.mark.asyncio
async def test_candidate_cannot_apply_with_another_candidates_resume(
    async_client: AsyncClient, test_candidate, test_recruiter, test_admin
):
    job = await async_client.post(
        "/api/v1/jobs",
        headers=test_recruiter["headers"],
        json={
            "title": f"Resume Ownership Role {uuid.uuid4().hex[:6]}",
            "category_id": 1,
            "description": "A test role for resume ownership validation.",
            "skills": ["Python"],
        },
    )
    assert job.status_code == 201
    job_id = job.json()["id"]
    approved = await async_client.post(
        f"/api/v1/admin/jobs/{job_id}/approve", headers=test_admin["headers"]
    )
    assert approved.status_code == 200

    async with async_session_maker() as db:
        other_user = User(
            email=f"other.candidate.{uuid.uuid4().hex}@velvorax.tech",
            hashed_password="not-used",
            full_name="Other Candidate",
            role="CANDIDATE",
            is_active=True,
            is_verified=True,
        )
        db.add(other_user)
        await db.flush()
        other_profile = CandidateProfile(user_id=other_user.id)
        db.add(other_profile)
        await db.flush()
        other_resume = Resume(
            candidate_id=other_profile.id,
            original_filename="resume.pdf",
            blob_pathname=f"resumes/test/{uuid.uuid4().hex}.pdf",
            blob_url="/uploads/resume.pdf",
            file_size_bytes=100,
            mime_type="application/pdf",
        )
        db.add(other_resume)
        await db.commit()
        other_resume_id = other_resume.id

    response = await async_client.post(
        "/api/v1/applications",
        headers=test_candidate["headers"],
        json={"job_id": job_id, "resume_id": other_resume_id},
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_candidate_can_add_certification(async_client: AsyncClient, test_candidate):
    response = await async_client.post(
        "/api/v1/candidates/me/certifications",
        headers=test_candidate["headers"],
        json={
            "name": "Cloud Practitioner",
            "issuing_organization": "Example Certification Board",
            "credential_id": "CERT-123",
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Cloud Practitioner"

@pytest.mark.asyncio
async def test_role_mismatch_rejected(async_client: AsyncClient, test_candidate):
    """Critical Security Requirement: Role selector mismatch must be strictly rejected!"""
    response = await async_client.post("/api/v1/auth/login", json={
        "email": test_candidate["email"],
        "password": test_candidate["password"],
        "role": "Admin"
    })
    assert response.status_code == 403
    assert "Access forbidden" in response.json()["detail"]

@pytest.mark.asyncio
async def test_email_verification_flow(async_client: AsyncClient):
    """Test full email verification token generation, login restriction, and verification."""
    unique_email = f"verify.{uuid.uuid4().hex[:8]}@velvorax.tech"
    password = "SecurePassword123!"

    # 1. Register candidate with verification required
    reg_res = await async_client.post("/api/v1/auth/register/candidate", json={
        "full_name": "Unverified Candidate",
        "email": unique_email,
        "phone": "+91 9999900001",
        "password": password,
        "confirm_password": password,
        "country": "India",
        "state": "Telangana",
        "city": "Hyderabad"
    })
    assert reg_res.status_code == 201

    # 2. Get verification token from DB
    async with async_session_maker() as db:
        user = (await db.execute(select(User).where(User.email == unique_email))).scalar_one()
        # Ensure is_verified is False when AUTO_VERIFY is False
        user.is_verified = False
        await db.commit()
        # Generate token
        raw_token = await EmailService.create_verification_token(user.id, db)

    # 3. Attempt login while unverified -> must be rejected 403
    login_attempt = await async_client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": password,
        "role": "Candidate"
    })
    assert login_attempt.status_code == 403
    assert "verified" in login_attempt.json()["detail"].lower()

    # 4. Verify email with token
    verify_res = await async_client.post("/api/v1/auth/verify-email", json={
        "token": raw_token
    })
    assert verify_res.status_code == 200
    assert verify_res.json()["verified"] is True

    # 5. Token reuse prevention: Second attempt with same token must fail
    reuse_res = await async_client.post("/api/v1/auth/verify-email", json={
        "token": raw_token
    })
    assert reuse_res.status_code == 400

    # 6. Login now succeeds
    success_login = await async_client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": password,
        "role": "Candidate"
    })
    assert success_login.status_code == 200
    assert "access_token" in success_login.json()

@pytest.mark.asyncio
async def test_password_reset_flow(async_client: AsyncClient, test_candidate):
    """Test requesting password reset and resetting password via one-time token."""
    # 1. Request password reset
    forgot_res = await async_client.post("/api/v1/auth/forgot-password", json={
        "email": test_candidate["email"]
    })
    assert forgot_res.status_code == 200

    # 2. Fetch reset token from DB
    async with async_session_maker() as db:
        raw_token = await EmailService.create_password_reset_token(test_candidate["user"].id, db)

    # 3. Reset password
    new_pwd = "NewSecuredPassword2026!"
    reset_res = await async_client.post("/api/v1/auth/reset-password", json={
        "token": raw_token,
        "new_password": new_pwd,
        "confirm_password": new_pwd
    })
    assert reset_res.status_code == 200

    # 4. Login with old password fails
    old_login = await async_client.post("/api/v1/auth/login", json={
        "email": test_candidate["email"],
        "password": test_candidate["password"],
        "role": "Candidate"
    })
    assert old_login.status_code == 401

    # 5. Login with new password succeeds
    new_login = await async_client.post("/api/v1/auth/login", json={
        "email": test_candidate["email"],
        "password": new_pwd,
        "role": "Candidate"
    })
    assert new_login.status_code == 200

@pytest.mark.asyncio
async def test_recruiter_vacancy_moderation_lifecycle(async_client: AsyncClient, test_recruiter, test_admin):
    """
    Recruiter Vacancy Lifecycle Enforcement:
    1. Recruiter creates job -> Must enter PENDING_APPROVAL.
    2. Recruiter attempting to publish directly -> Must return 403 Forbidden.
    3. Admin rejects job with mandatory reason -> Status REJECTED.
    4. Recruiter edits rejected job -> Resets to PENDING_APPROVAL, clears rejection reason.
    5. Admin approves job -> Status PUBLISHED, approved_by_admin_id set.
    """
    # 1. Recruiter creates job
    job_payload = {
        "title": f"Test Automation Architect {uuid.uuid4().hex[:4]}",
        "category_id": 1,
        "job_type": "IT",
        "employment_type": "Full-time",
        "work_arrangement": "Remote",
        "experience_level": "Senior",
        "experience_min_years": 5.0,
        "salary_min": 2000000,
        "salary_max": 3000000,
        "description": "Lead testing automation using Playwright, pytest, and Next.js.",
        "skills": ["Python", "FastAPI", "Playwright"]
    }
    create_res = await async_client.post("/api/v1/jobs", headers=test_recruiter["headers"], json=job_payload)
    assert create_res.status_code == 201
    job_data = create_res.json()
    job_id = job_data["id"]
    assert job_data["status"] == "PENDING_APPROVAL"

    # 2. Recruiter attempts to set status to PUBLISHED directly
    unauth_publish = await async_client.patch(
        f"/api/v1/jobs/{job_id}/status?status_val=PUBLISHED",
        headers=test_recruiter["headers"]
    )
    assert unauth_publish.status_code == 403
    assert "cannot publish vacancies directly" in unauth_publish.json()["detail"]

    # 3. Admin rejects job with mandatory reason
    reject_res = await async_client.post(
        f"/api/v1/admin/jobs/{job_id}/reject",
        headers=test_admin["headers"],
        json={"reason": "Please provide clearer minimum requirements in description."}
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "REJECTED"

    # 4. Recruiter updates the rejected job -> Transitions back to PENDING_APPROVAL
    edit_res = await async_client.put(
        f"/api/v1/jobs/{job_id}",
        headers=test_recruiter["headers"],
        json={"description": "Updated detailed requirements: 5+ years building Playwright CI/CD suites."}
    )
    assert edit_res.status_code == 200
    assert edit_res.json()["status"] == "PENDING_APPROVAL"
    assert edit_res.json()["rejection_reason"] is None

    # 5. Admin approves job
    approve_res = await async_client.post(
        f"/api/v1/admin/jobs/{job_id}/approve",
        headers=test_admin["headers"]
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "PUBLISHED"

    # 6. Verify public /jobs API returns the published job
    public_res = await async_client.get(f"/api/v1/jobs/{job_data['slug']}")
    assert public_res.status_code == 200
    assert public_res.json()["status"] == "PUBLISHED"

@pytest.mark.asyncio
async def test_taxonomy_categories_coverage(async_client: AsyncClient):
    """Verify presence of 25 IT and 30 Non-IT categories."""
    it_res = await async_client.get("/api/v1/categories?category_type=IT")
    assert it_res.status_code == 200
    it_cats = it_res.json()
    assert len(it_cats) >= 25

    non_it_res = await async_client.get("/api/v1/categories?category_type=NON_IT")
    assert non_it_res.status_code == 200
    non_it_cats = non_it_res.json()
    assert len(non_it_cats) >= 30

@pytest.mark.asyncio
async def test_geographic_hierarchy_coverage(async_client: AsyncClient):
    """Verify full hierarchy: Country -> State -> District -> Mandal -> City -> PostalCode (PIN 500049 Miyapur)."""
    # 1. Countries
    countries_res = await async_client.get("/api/v1/locations/countries")
    assert countries_res.status_code == 200
    country_names = [c["name"] for c in countries_res.json()]
    assert "India" in country_names
    assert "United States" in country_names

    # 2. States in India
    states_res = await async_client.get("/api/v1/locations/states?country=India")
    assert states_res.status_code == 200
    state_names = [s["name"] for s in states_res.json()]
    assert "Telangana" in state_names

    # 3. Districts in Telangana
    districts_res = await async_client.get("/api/v1/locations/districts?state=Telangana")
    assert districts_res.status_code == 200
    district_names = [d["name"] for d in districts_res.json()]
    assert "Medchal-Malkajgiri" in district_names

    # 4. Search Postal Code 500049
    pin_res = await async_client.get("/api/v1/locations/postal-codes?q=500049")
    assert pin_res.status_code == 200
    pins = pin_res.json()
    assert len(pins) > 0
    assert pins[0]["pin_code"] == "500049"
    assert "Miyapur" in pins[0]["locality_name"]

@pytest.mark.asyncio
async def test_resume_upload_and_security(async_client: AsyncClient, test_candidate, test_admin):
    """Verify resume upload, magic byte validation, and authenticated download security."""
    # 1. Valid PDF file upload
    fake_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R >>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000117 00000 n\ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n168\n%%EOF"
    upload_res = await async_client.post(
        "/api/v1/candidates/me/resumes",
        headers=test_candidate["headers"],
        files={"file": ("resume.pdf", io.BytesIO(fake_pdf_content), "application/pdf")}
    )
    assert upload_res.status_code == 201
    resume_data = upload_res.json()
    resume_id = resume_data["id"]

    # 2. Candidate downloads own resume -> 200 OK
    download_owner = await async_client.get(
        f"/api/v1/candidates/resumes/{resume_id}/download",
        headers=test_candidate["headers"]
    )
    assert download_owner.status_code in [200, 307]

    # 3. Unauthenticated download attempt -> 401 Unauthorized
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as fresh_unauth_client:
        unauth_download = await fresh_unauth_client.get(f"/api/v1/candidates/resumes/{resume_id}/download")
        assert unauth_download.status_code == 401

    # 4. Admin downloads resume -> 200 OK
    admin_download = await async_client.get(
        f"/api/v1/candidates/resumes/{resume_id}/download",
        headers=test_admin["headers"]
    )
    assert admin_download.status_code in [200, 307]

@pytest.mark.asyncio
async def test_admin_dashboard_stats(async_client: AsyncClient, test_admin):
    """Verify admin dashboard statistics reflect real database metrics."""
    stats_res = await async_client.get("/api/v1/admin/dashboard/stats", headers=test_admin["headers"])
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_users"] > 0
    assert stats["total_jobs"] > 0
