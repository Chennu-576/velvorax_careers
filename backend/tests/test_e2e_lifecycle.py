import os
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.job import Job

@pytest.mark.asyncio
async def test_full_lifecycle_e2e(async_client: AsyncClient, test_candidate, test_recruiter, test_admin):
    """
    End-to-End Recruitment Lifecycle:
    1. Recruiter creates vacancy -> Status PENDING_APPROVAL
    2. Admin approves vacancy -> Status PUBLISHED
    3. Candidate applies for published vacancy -> Application submitted
    4. Candidate views application history
    5. Recruiter reviews application & updates status to SHORTLISTED
    6. Recruiter schedules interview
    7. Admin verifies platform metrics reflect live data
    """
    # 1. Recruiter creates vacancy
    job_res = await async_client.post("/api/v1/jobs", headers=test_recruiter["headers"], json={
        "title": f"Full-Stack Specialist {uuid.uuid4().hex[:4]}",
        "category_id": 1,
        "job_type": "IT",
        "employment_type": "Full-time",
        "work_arrangement": "Remote",
        "experience_level": "Senior",
        "experience_min_years": 4.0,
        "salary_min": 1800000,
        "salary_max": 2600000,
        "description": "Develop modern Next.js and FastAPI enterprise applications.",
        "skills": ["Next.js", "FastAPI", "PostgreSQL"]
    })
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]
    assert job_res.json()["status"] == "PENDING_APPROVAL"

    # 2. Admin approves vacancy
    approve_res = await async_client.post(
        f"/api/v1/admin/jobs/{job_id}/approve",
        headers=test_admin["headers"]
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "PUBLISHED"

    # 3. Candidate applies for the published job
    apply_res = await async_client.post("/api/v1/applications", headers=test_candidate["headers"], json={
        "job_id": job_id,
        "cover_letter": "I have 5+ years building full-stack applications with FastAPI and Next.js."
    })
    assert apply_res.status_code in [201, 409]
    app_id = apply_res.json()["id"]

    # 4. Candidate checks my applications
    my_apps = await async_client.get("/api/v1/applications/my", headers=test_candidate["headers"])
    assert my_apps.status_code == 200
    app_list = my_apps.json()
    assert any(a["id"] == app_id for a in app_list)

    # 5. Recruiter reviews application & updates status to SHORTLISTED
    review_res = await async_client.patch(
        f"/api/v1/applications/{app_id}/status",
        headers=test_recruiter["headers"],
        json={"status": "SHORTLISTED", "notes": "Strong background in Next.js and FastAPI."}
    )
    assert review_res.status_code == 200

    # 6. Recruiter schedules interview
    interview_res = await async_client.post(
        "/api/v1/interviews",
        headers=test_recruiter["headers"],
        json={
            "application_id": app_id,
            "interview_type": "Technical Round",
            "scheduled_time": "2026-11-25T14:00:00Z",
            "timezone_str": "Asia/Kolkata",
            "meeting_link": "https://meet.google.com/velvorax-tech-interview"
        }
    )
    assert interview_res.status_code == 201
    assert interview_res.json()["status"] == "SCHEDULED"

    # 7. Admin dashboard stats verification
    stats_res = await async_client.get("/api/v1/admin/dashboard/stats", headers=test_admin["headers"])
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_applications"] > 0
    assert stats["total_interviews"] > 0
