# import os
# from contextlib import asynccontextmanager
# from fastapi import FastAPI, Request, status
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles

# from app.core.config import settings
# from app.core.database import engine, Base
# from app.api import (
#     auth,
#     jobs,
#     categories,
#     locations,
#     applications,
#     candidates,
#     recruiters,
#     employer_requests,
#     training,
#     finance,
#     admin,
#     cms
# )
# # Import models to ensure they register on metadata
# import app.models

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Initialize tables on startup
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     # Cleanup
#     await engine.dispose()

# app = FastAPI(
#     title=settings.PROJECT_NAME,
#     version=settings.VERSION,
#     openapi_url=f"{settings.API_V1_STR}/openapi.json",
#     docs_url=f"{settings.API_V1_STR}/docs",
#     redoc_url=f"{settings.API_V1_STR}/redoc",
#     lifespan=lifespan
# )

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Private Uploads Directory (Accessible only via authenticated /candidates/resumes/{id}/download endpoint)
# upload_dir = os.path.join(os.getcwd(), "uploads")
# os.makedirs(upload_dir, exist_ok=True)

# # Mount Routers under API_V1_STR
# app.include_router(auth.router, prefix=settings.API_V1_STR)
# app.include_router(jobs.router, prefix=settings.API_V1_STR)
# app.include_router(categories.router, prefix=settings.API_V1_STR)
# app.include_router(locations.router, prefix=settings.API_V1_STR)
# app.include_router(applications.router, prefix=settings.API_V1_STR)
# app.include_router(candidates.router, prefix=settings.API_V1_STR)
# app.include_router(recruiters.router, prefix=settings.API_V1_STR)
# app.include_router(employer_requests.router, prefix=settings.API_V1_STR)
# app.include_router(training.router, prefix=settings.API_V1_STR)
# app.include_router(finance.router, prefix=settings.API_V1_STR)
# app.include_router(admin.router, prefix=settings.API_V1_STR)
# app.include_router(cms.router, prefix=settings.API_V1_STR)

# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "service": "VELVORAX Careers API",
#         "version": settings.VERSION
#     }

# @app.get("/")
# async def root():
#     return {
#         "message": "Welcome to VELVORAX Careers API Ecosystem",
#         "docs": f"{settings.API_V1_STR}/docs"
#     }




import os
from contextlib import asynccontextmanager

from sqlalchemy import text
from fastapi.responses import JSONResponse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine

from app.api import (
    auth,
    jobs,
    categories,
    locations,
    applications,
    candidates,
    recruiters,
    employer_requests,
    training,
    finance,
    admin,
    cms,
)

# Import all models to ensure model registration.
import app.models


# --------------------------------------------------
# Application Lifespan
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Production application lifecycle.

    Database schema creation and updates are handled
    separately through Alembic migrations.

    No create_all() here because multiple Gunicorn
    workers can execute startup simultaneously.
    """

    print("VELVORAX Careers API starting...")

    yield

    # Dispose database connections during shutdown.
    await engine.dispose()

    print("VELVORAX Careers API shutting down...")


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="VELVORAX Careers API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Upload Directory
# --------------------------------------------------

upload_dir = os.path.join(os.getcwd(), "uploads")

os.makedirs(upload_dir, exist_ok=True)


# --------------------------------------------------
# API Routers
# --------------------------------------------------

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(locations.router, prefix=settings.API_V1_STR)
app.include_router(applications.router, prefix=settings.API_V1_STR)
app.include_router(candidates.router, prefix=settings.API_V1_STR)
app.include_router(recruiters.router, prefix=settings.API_V1_STR)
app.include_router(employer_requests.router, prefix=settings.API_V1_STR)
app.include_router(training.router, prefix=settings.API_V1_STR)
app.include_router(finance.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(cms.router, prefix=settings.API_V1_STR)


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Welcome to VELVORAX Careers API Ecosystem",
        "docs": f"{settings.API_V1_STR}/docs",
    }


# --------------------------------------------------
# HEAD Endpoint (Render Health Check)
# --------------------------------------------------

@app.head("/")
async def root_head():
    return {}


# --------------------------------------------------
# Health Check Endpoint
# --------------------------------------------------

@app.get("/health")
@app.head("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "VELVORAX Careers API",
        "version": settings.VERSION,
    }

# --------------------------------------------------
# Database Connectivity Check
# --------------------------------------------------

@app.get("/health/database")
async def database_health_check():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            result.scalar_one()

        return {
            "status": "success",
            "database": "connected",
            "message": "PostgreSQL connection is working"
        }

    except Exception:
        import logging

        logging.exception("Database connectivity check failed")

        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "database": "disconnected",
                "message": "Database connection failed"
            }
        )