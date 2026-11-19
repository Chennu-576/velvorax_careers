# VELVORAX Careers Audit Report

Audit date: 2026-11-19

## Implementation Status

- Candidate and recruiter registration no longer issue or store access tokens before verification.
- Candidate and recruiter registration now redirect to login with a verification-required notice.
- A real verification page and password-reset page were added.
- SMTP delivery was implemented with environment-configured host, port, TLS/SSL, credentials,
  sender, and frontend verification/reset links.
- Production cookies support Secure/SameSite configuration; logout also clears configured cookie attributes.
- Public job detail lookup is restricted to `PUBLISHED` jobs.
- Recruiter application status updates and interview scheduling now verify company ownership.
- Recruiter resume access is restricted to candidates who applied to jobs in the recruiter company.
- Recruiter job updates now synchronize submitted job skills.
- New application notifications are created for both candidates and recruiters.
- Notification list/read endpoints were added.
- Candidate profile updates support full name and phone as well as profile fields.
- Candidate education, experience, and skill creation endpoints were added.
- Frontend production build passes.

## Executive Summary

The project has a substantial Next.js/FastAPI/PostgreSQL implementation. Public job discovery,
candidate/recruiter/admin dashboards, moderation, applications, resumes, interviews, and
database models exist. The main remaining risks are authentication session issuance during
unverified registration, mock email dispatch, cross-company recruiter authorization gaps,
unpublished-job visibility, and missing frontend verification handling.

## Frontend

- Pages inspected: public jobs, categories, IT/non-IT/global jobs, job details, login,
  registration, candidate dashboard, recruiter dashboard, admin dashboard, and CMS-backed about page.
- API integration: most dashboard and public listing calls match existing FastAPI routes.
- Findings:
  - Registration immediately stores a token and redirects to a dashboard, even when email
    verification is required.
  - No frontend verification page exists.
  - The login and role-selector contracts match the backend role enforcement.
  - Candidate and recruiter dashboards consume real API data for core metrics and records.
  - Several expanded profile and notification features are not represented in complete UI flows.
  - Frontend build is currently successful.

## Backend

- Routers inspected: auth, jobs, categories, locations, applications, candidates,
  recruiters, employer requests, training, finance, admin, and CMS.
- Working areas: JWT login, role mismatch rejection, candidate/recruiter profile creation,
  PostgreSQL-backed listings, duplicate application prevention, job moderation, status history,
  and real resume file validation/storage.
- Findings:
  - Registration returns access tokens for unverified users and sets authentication cookies.
  - Verification and password-reset emails are currently print-only mock implementations.
  - Recruiter application status and interview endpoints need stronger company ownership checks.
  - Resume download authorization allows all recruiters instead of recruiters with a legitimate
    application for the candidate.
  - Public job lookup may expose unpublished jobs.
  - The test suite requires the local PostgreSQL test configuration or an equivalent async
    database environment.

## Database

- SQLAlchemy 2.x models cover users, profiles, companies, jobs, categories, applications,
  resumes, interviews, verification/reset tokens, notifications, audit logs, and finance.
- Core foreign keys, unique constraints, cascades, and indexes are present.
- Alembic migration exists for the baseline schema.
- No destructive migration or production database operation is included in this audit.

## Deployment and Environment

- Frontend API configuration is environment-driven in `frontend/lib/api.ts`.
- CORS is currently explicit for localhost and Vercel.
- Backend database initialization is migration-oriented and does not call `create_all()` at startup.
- SMTP credentials and delivery behavior need an explicit backend configuration.
- Existing `.env` files are not committed as implementation changes.
