import os
import sys
import uuid
import pytest
import pytest_asyncio

# Ensure backend directory is in python search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.core.database import async_session_maker, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.company import Company, RecruiterProfile
from app.models.candidate import CandidateProfile
from app.models.job import Job

# Test Credentials (configured for automated test runs)
TEST_PASSWORD = os.getenv("TEST_USER_PASSWORD", "TestAuth@Sec2026!")

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """Ensure database schema is ready for tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def test_admin(async_client):
    email = f"test.admin.{uuid.uuid4().hex[:6]}@velvorax.tech"
    async with async_session_maker() as db:
        user = User(
            email=email,
            hashed_password=get_password_hash(TEST_PASSWORD),
            full_name="Test SuperAdmin",
            role="SUPER_ADMIN",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Login and obtain token
    res = await async_client.post("/api/v1/auth/login", json={
        "email": email,
        "password": TEST_PASSWORD,
        "role": "Admin"
    })
    token = res.json()["access_token"]
    return {"user": user, "token": token, "email": email, "password": TEST_PASSWORD, "headers": {"Authorization": f"Bearer {token}"}}

@pytest_asyncio.fixture
async def test_recruiter(async_client):
    email = f"test.recruiter.{uuid.uuid4().hex[:6]}@velvorax.tech"
    async with async_session_maker() as db:
        comp = Company(
            name=f"Partner Corp {uuid.uuid4().hex[:4]}",
            slug=f"partner-corp-{uuid.uuid4().hex[:4]}",
            country="India",
            city="Hyderabad",
            is_verified=True,
            is_hiring_partner=True
        )
        db.add(comp)
        await db.flush()

        user = User(
            email=email,
            hashed_password=get_password_hash(TEST_PASSWORD),
            full_name="Test Recruiter",
            role="RECRUITER",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        await db.flush()

        rec = RecruiterProfile(
            user_id=user.id,
            company_id=comp.id,
            designation="Talent Acquisition Lead",
            is_approved=True
        )
        db.add(rec)
        await db.commit()
        await db.refresh(user)

    res = await async_client.post("/api/v1/auth/login", json={
        "email": email,
        "password": TEST_PASSWORD,
        "role": "Recruiter/HR"
    })
    token = res.json()["access_token"]
    return {"user": user, "token": token, "email": email, "password": TEST_PASSWORD, "company_id": comp.id, "headers": {"Authorization": f"Bearer {token}"}}

@pytest_asyncio.fixture
async def test_candidate(async_client):
    email = f"test.cand.{uuid.uuid4().hex[:6]}@velvorax.tech"
    async with async_session_maker() as db:
        user = User(
            email=email,
            hashed_password=get_password_hash(TEST_PASSWORD),
            full_name="Test Candidate",
            role="CANDIDATE",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        await db.flush()

        profile = CandidateProfile(
            user_id=user.id,
            country="India",
            state="Telangana",
            city="Hyderabad"
        )
        db.add(profile)
        await db.commit()
        await db.refresh(user)

    res = await async_client.post("/api/v1/auth/login", json={
        "email": email,
        "password": TEST_PASSWORD,
        "role": "Candidate"
    })
    token = res.json()["access_token"]
    return {"user": user, "token": token, "email": email, "password": TEST_PASSWORD, "profile_id": profile.id, "headers": {"Authorization": f"Bearer {token}"}}
