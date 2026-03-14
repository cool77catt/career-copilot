# AGENTS.md

## Purpose
This repository builds a full-stack application that helps a user:
- Build/refine a job-seeking profile from PDFs and follow-up chat
- Get targeted job recommendations
- Generate tailored resume/cover letter/job-fit materials per selected job

## Source of Truth
- Product intent starts in `docs/prompt.md`.
- Global execution rules live in `docs/spec.md`.
- Global sequencing/governance lives in `docs/plan.md`.
- Feature-specific requirements live in `docs/features/<feature-name>/spec.md`.
- Feature-specific sequencing lives in `docs/features/<feature-name>/plan.md`.
- If conflicts exist while implementing a feature:
  `docs/features/<feature-name>/spec.md` > `docs/features/<feature-name>/plan.md` > `docs/spec.md` > `docs/plan.md` > `docs/prompt.md`.

## Tech Constraints
- Frontend: Next.js + TypeScript + pnpm
- Backend: FastAPI + Python + uv
- Database: Postgres
- Auth: JWT-based authentication
- Packaging/Runtime: Dockerized backend service(s), runnable on macOS/Linux
- Tests: pytest for backend APIs/services/db functions
- E2E: Cypress for frontend end-to-end tests

## Delivery Rules
- Build in small, reviewable increments tied to the active feature plan in `docs/features/<feature-name>/plan.md`.
- Favor readable, explicit code over clever abstractions.
- Keep architecture modular so job sourcing/providers can be extended later.
- Do not add extra infrastructure unless required by a plan item.

## Testing Rules
- Every backend feature should include focused tests for:
  - Core success paths
  - Key validation failures
  - Critical edge cases
- Frontend workflow regressions should include Cypress E2E coverage for key user-visible flows.
- Keep tests concise and high-signal.
- Avoid low-value snapshot-style overtesting.

## Data and Artifact Rules
- Persist user profile as a markdown flat file (`profile.md`) and store the file location in DB.
- For accepted jobs, maintain markdown artifacts per job:
  - `job-description.md` (or equivalent markdown record + source link)
  - `resume.md`
  - `cover-letter.md`
  - `job-fit.md`
- Artifact versions must be preserved (no destructive overwrite of prior versions).

## Product Workflow Guardrails
Implement workflow in this order unless instructed otherwise:
1. User profile ingestion and refinement
2. LinkedIn profile optimization guidance
3. Job search and recommendation presentation
4. Job selection state management (accept/reject/skip + reason)
5. Material generation and versioning for accepted jobs

## UX Guardrails (Current Scope)
- Early frontend phases can be UI skeleton first.
- Deliverable 2 explicitly bypasses login screen and auto-authenticates using configured seeded credentials.
- Preserve a clear path to re-enable full login flow later.

## Security and Secrets
- Never hardcode production secrets.
- Use environment variables for DB URL, JWT secret, and external provider credentials.
- Seed credentials in development only.

## Definition of Done (Per Task)
A task is done when:
- Code compiles/runs locally
- Relevant tests pass
- Docs are updated if behavior/contracts changed
- Changes align with acceptance criteria in the active feature plan (`docs/features/<feature-name>/plan.md`) and applicable global rules
