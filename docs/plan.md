# Job Finder LLM - Implementation Plan

## Goal
Deliver the system iteratively, starting with foundational documents and infrastructure, then implementing workflow stages in user-value order.

## Phase 0 - Documentation Baseline (Deliverable 1)
### Tasks
- Create `AGENTS.md`
- Create `docs/spec.md`
- Create `docs/plan.md`

### Acceptance Criteria
- All three files exist and align with `docs/prompt.md`
- Scope, architecture, and workflow order are explicit
- Deliverable 2 has a clear handoff path

## Phase 1 - Project Infrastructure (Deliverable 2)
### Backend Foundation
- Scaffold FastAPI project using `uv`
- Add JWT auth endpoints/services
- Add Postgres integration + migrations
- Seed initial development user:
  - Chris Carl (`chris77carl@gmail.com` / `default`)

### Frontend Foundation
- Scaffold Next.js TypeScript app using `pnpm`
- Build UI skeleton for all workflow stages (no deep business logic yet)
- Bypass login UI and auto-authenticate at startup against backend

### Ops and Runtime
- Dockerize backend
- Add scripts to run services on macOS/Linux
- Establish environment variable templates

### Testing and Docs
- Add initial pytest suite for auth + basic health/core paths
- Add Cypress E2E test for frontend skeleton and auto-login flow
- Update `README.md` with architecture, setup, and run steps

### Acceptance Criteria
- Frontend and backend run locally
- Backend auth with JWT works
- Seed user exists and can authenticate
- UI skeleton renders workflow screens
- Cypress E2E passes for frontend skeleton and login bootstrap path
- Dockerized backend starts successfully
- README instructions are sufficient for a clean setup

## Phase 2 - User Profile Workflow
### Tasks
- Implement PDF ingestion endpoint and parsing pipeline
- Implement profile refinement via follow-up Q&A/chat input
- Persist `profile.md` and DB path linkage
- Build profile UI interactions for upload + chat refinement

### Acceptance Criteria
- User can upload PDFs and get an initial profile
- User can add information and trigger profile refinement
- Latest profile markdown is saved and referenceable
- Core tests validate ingestion/refinement and storage wiring

## Phase 3 - LinkedIn Optimizer
### Tasks
- Add backend service for tailored LinkedIn recommendations
- Add frontend section to display and refresh recommendations

### Acceptance Criteria
- Recommendations reflect user profile/preferences
- Output is structured/actionable (headline/about/experience/skills)
- Tests cover request validation and service response contracts

## Phase 4 - Job Search and Recommendation
### Tasks
- Implement provider interfaces for LinkedIn/Indeed connectors
- Add job search endpoint returning 3 new jobs
- Implement persistence and dedup/newness logic
- Build UI for trigger + recommendation cards

### Acceptance Criteria
- Each search returns 3 recommendations not previously shown
- Recommendations include JD/link/fit rationale
- Tests cover dedup/newness and result-shaping logic

## Phase 5 - Job Decisioning and History
### Tasks
- Add accept/reject/skip status update endpoints
- Store optional rejection reason and decision history metadata
- Build UI for status changes and historical browsing/editing

### Acceptance Criteria
- User can set/update decisions on jobs
- Historical jobs are queryable and editable
- Tests cover status transition behavior

## Phase 6 - Material Generation and Versioning
### Tasks
- Implement generation pipeline for resume/cover-letter/job-fit markdown
- Store artifact files and version metadata
- Add regeneration flow that creates next versions
- Build UI for viewing/regenerating historical versions

### Acceptance Criteria
- Accepted jobs produce all required artifacts
- Regeneration increments version and keeps old versions intact
- Tests cover versioning and artifact record integrity

## Phase 7 - Hardening and QA
### Tasks
- Expand tests for critical paths and failure handling
- Improve logging/observability and error messages
- Performance checks for common workflows

### Acceptance Criteria
- Stable local runbook
- High-confidence tests for core journeys
- Clear known limitations documented

## Execution Notes
- Build vertical slices where possible, but preserve the phase ordering.
- Keep provider integrations behind interfaces so additional job sources can be added later.
- Do not block early phases on perfect LLM prompt quality; use prompt versioning and iterate.
