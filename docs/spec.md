# Job Finder LLM - Product and Technical Specification

## 1. Objective
Build a web full-stack application that automates job discovery and application prep by:
- Creating a richer user profile from uploaded documents and chat-based follow-up
- Recommending new jobs aligned to user preferences
- Generating tailored application materials (resume, cover letter, job-fit rationale)

## 2. Scope (Initial)
### In Scope
- Single-user initial implementation with seeded dev user
- PDF ingestion for LinkedIn profile PDF and resume PDF
- Interactive profile refinement via chat/follow-up questions
- LinkedIn optimization recommendations
- Job search against LinkedIn and Indeed (initial providers)
- Job recommendation list of 3 new jobs per search action
- Job decision states: accepted, rejected (with reason), skipped
- Material generation for accepted jobs with version history

### Out of Scope (For Now)
- Browser automation that auto-submits job applications
- Multi-tenant enterprise features
- Advanced role-based access controls
- Non-LinkedIn/Indeed provider breadth beyond simple extensibility stubs

## 3. Users and Primary Journey
### User
A job seeker who wants to quickly find relevant opportunities and generate tailored application materials.

### Primary Journey
1. User profile is created/refined from PDFs and chat
2. User sets/updates job preferences
3. User gets LinkedIn profile optimization tips
4. User triggers job search and receives 3 new jobs
5. User accepts/rejects/skips jobs and may revise later
6. Accepted jobs generate versioned resume/cover letter/job-fit docs

## 4. Functional Requirements

## 4.1 User Profile Stage
- Provide four clearly labeled input sections:
  - LinkedIn profile input (PDF)
  - Resume input (PDF)
  - Follow-up questions with answer inputs
  - Additional information (free-form text)
- User edits all sections and applies changes with a single action (`Update Profile`)
- System extracts profile signals from LinkedIn/resume uploads
- System generates and refreshes follow-up questions to fill missing context
- System stores follow-up answers and additional information
- Persist profile as markdown flat file (`profile.md`)
- Persist each profile section as its own markdown file:
  - `linkedin-profile.md`
  - `resume.md`
  - `follow-up-answers.md`
  - `additional-information.md`
- Store only profile/section markdown file paths in DB (markdown files are source of truth)
- Profile viewer must support two tabs:
  - Raw markdown view
  - Rendered markdown view

## 4.2 LinkedIn Profile Optimizer Stage
- Provide guidance for profile improvements tailored to target roles/preferences
- Guidance should include actionable edits (headline, summary/about, experience bullets, skills)

## 4.3 Job Search Stage
- User triggers search from UI
- System returns exactly 3 new job recommendations per run
- "New" means at least one differs from already seen jobs by JD content or company or title
- Search focuses on LinkedIn and Indeed for initial phase
- Store recommendation record and source metadata

## 4.4 Job Selection Stage
- Show each job with:
  - Job description summary/snippet
  - Link to source posting
  - Why the job fits the user
- User actions per job:
  - Accept
  - Reject (with optional/required reason, configurable)
  - Skip
- User can revisit historical jobs and update statuses

## 4.5 Material Generation Stage
- On acceptance, generate:
  - `resume.md`
  - `cover-letter.md`
  - `job-fit.md`
- Track job description and source link in markdown
- Support regeneration to produce new versions
- Preserve prior versions and enable viewing history

## 5. Non-Functional Requirements
- Fast local startup for frontend/backend/db
- Backend containerized and runnable on macOS/Linux
- API responses should be deterministic where feasible for testability
- Structured logs for backend services
- Basic input validation and safe error handling
- Frontend E2E coverage using Cypress for critical workflow skeleton behavior

## 6. Technical Architecture
### Frontend
- Next.js app (TypeScript, pnpm)
- Initial deliverable UI skeleton for workflow stages
- Temporary auth bypass: app boots and auto-calls backend login with seeded credentials

### Backend
- FastAPI service (Python, uv)
- Layering target:
  - API routers
  - Domain/services
  - Persistence layer
  - Integrations (LLM, job providers, document parsing)
- All DB-hit operations must be isolated in the database layer (`backend/app/db/*`).

### Database
- Postgres for users, job records, statuses, artifact metadata, and version metadata
- Profile/artifact markdown content stored in files; DB stores locations and metadata

### Auth
- JWT-based auth end-to-end
- Development seed user:
  - Name: Chris Carl
  - Email: chris77carl@gmail.com
  - Password: default

## 7. Initial Data Model (Conceptual)
- User
  - id, name, email, password_hash, created_at, updated_at
- UserProfile
  - id, user_id, profile_markdown_path, linkedin_markdown_path, resume_markdown_path, follow_up_markdown_path, additional_info_markdown_path, updated_at
- JobPreference
  - id, user_id, preferences_json, updated_at
- JobRecommendation
  - id, user_id, source, source_job_id, title, company, location, url, jd_markdown_path, fit_summary, first_seen_at
- JobDecision
  - id, recommendation_id, status (accepted/rejected/skipped), reason, updated_at
- GeneratedArtifact
  - id, recommendation_id, artifact_type (resume/cover-letter/job-fit), version, markdown_path, created_at

## 8. API Surface (Initial)
- `POST /auth/login` -> returns JWT
- `GET /me` -> current user
- `POST /profile/update` -> single update action for LinkedIn PDF, resume PDF, follow-up answers, and additional information
- `GET /profile` -> returns profile metadata/content reference
- `POST /linkedin/optimize` -> returns tailored LinkedIn recommendations
- `POST /jobs/search` -> fetch/store/return 3 new recommendations
- `GET /jobs` -> list jobs with current statuses
- `PATCH /jobs/{id}/decision` -> accept/reject/skip + reason
- `POST /jobs/{id}/generate-materials` -> generate versioned docs
- `GET /jobs/{id}/artifacts` -> list versions and artifact metadata

## 9. Testing Strategy
- Use `pytest` for backend tests
- Use Cypress for frontend E2E tests
- Prioritize tests for:
  - Auth and token validation
  - Core profile ingestion/refinement behavior
  - Job dedup/newness logic
  - Decision state transitions
  - Artifact version incrementing rules
- Include at least one E2E test that validates:
  - App boot and stage visibility
  - Auto-login request behavior from frontend to backend auth endpoint
- Keep tests concise and value-focused

## 10. Open Decisions
- Which PDF extraction library/toolchain to use
- Exact heuristic for job "newness" vs semantic near-duplicate
- Rejection reason required vs optional
- Storage location conventions for markdown artifacts
- LLM provider abstraction boundary and prompt versioning strategy
