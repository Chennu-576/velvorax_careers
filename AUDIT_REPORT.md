# VELVORAX Careers Authentication Audit

Audit date: 2026-11-19

## Findings and changes

- Candidate and recruiter registration now always create unverified accounts, persist
  their profiles and SHA-256 verification-token hashes, and commit before attempting
  email delivery. A failed delivery is returned accurately; neither account is
  automatically verified.
- Verification tokens are one-time and time-limited. Resending invalidates earlier
  unused tokens, persists the replacement before delivery, and is rate-limited by
  source IP and account. Verification and password-reset token consumption is committed
  with the corresponding account update.
- Password reset uses the same persisted, hashed, expiring-token flow. Unknown
  accounts receive a non-enumerating response that does not claim delivery.
- Admin provisioning remains a trusted CLI-only flow. Bootstrap now validates the
  email and administrator name; login and API access require active, verified users.
- Company verification no longer changes recruiter approval. An explicit admin
  recruiter-approval endpoint and dashboard controls require the recruiter to be
  active and email-verified and the company to be verified. General admin user-status
  updates cannot bypass email verification.
- JWT authorization checks the current database user, token subject and role, active
  status, and verification state. Recruiter job and applicant-management operations
  require both recruiter approval and company verification.
- Email delivery supports Resend over HTTPS and explicit SMTP compatibility. Delivery
  results are logged without recipient addresses, credentials, or raw tokens; provider
  response details are not returned to users. Job approval/rejection notifications
  are dispatched after the status transaction commits.
- The unified login keeps the three role choices, validates role-specific redirects,
  and sends credentials with the cross-origin session cookie. Registration reports
  delivery failure, a dedicated forgot-password page is available, and logout clears
  both the browser state and API cookie.

## Email connectivity

The reported `OSError: [Errno 101] Network is unreachable` occurs at network
connectivity, before SMTP TLS negotiation. Changing SMTP TLS/SSL flags cannot fix an
unreachable outbound SMTP route. The configured Resend HTTPS API avoids SMTP egress
requirements, but it still requires a valid Render API key and a verified sender
domain. No real inbox delivery or production verification was performed in this
workspace.

## Database and migrations

- Existing SQLAlchemy user, profile, verification-token, and reset-token tables
  already support the audited flows; no schema change was needed.
- The local PostgreSQL database reports Alembic revision `a6fb1d9e3c42` as current
  head. No production migration was run.
- Application startup remains migration-oriented; it does not call
  `Base.metadata.create_all()`.

## Validation

- Focused PostgreSQL authentication/approval tests: 15 passed. Covered candidate and
  recruiter registration/verification/login, admin bootstrap/login/access, approval
  separation, token reuse/expiry, inactive and unverified login, role mismatch,
  password reset, logout, and simulated email success/failure.
- Full backend suite: 22 passed, 3 failed due missing local taxonomy/geography seed
  records and a resume-storage `502`; those failures are outside authentication.
- Frontend production build and backend Python compilation passed.
- Alembic reports `a6fb1d9e3c42` as current head. Render `/health` and the Vercel site
  returned HTTP 200.

## Deployment status

The public Render health endpoint and Vercel site responded successfully during this
audit. Commit `df97461` was pushed to `main`, but the repository has no GitHub Actions
workflows, and the newly added API/frontend routes still returned 404 after the push.
Render/Vercel environment settings were not inspectable or changed from this
workspace, and no deployment controls are available here. Production delivery remains
dependent on configuring `EMAIL_PROVIDER`, `RESEND_API_KEY`, `EMAIL_FROM`,
`FRONTEND_URL`, and `CORS_ORIGINS` in Render and `NEXT_PUBLIC_API_URL` /
`NEXT_PUBLIC_APP_URL` in Vercel, then deploying both services.
