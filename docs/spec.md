# Job Finder LLM - Global Product and Engineering Specification

## 1. Purpose
Define project-wide product intent, engineering constraints, and governance.
Detailed feature behavior lives in `docs/features/<feature-name>/spec.md`.

## 2. Documentation Governance
- Product intent starts in `docs/prompt.md`.
- Global standards and rules live in `docs/spec.md`.
- Global sequencing lives in `docs/plan.md`.
- Feature-level requirements live in `docs/features/<feature-name>/spec.md`.
- Feature-level sequencing lives in `docs/features/<feature-name>/plan.md`.

## 3. Source-of-Truth Precedence
When working on a feature, resolve conflicts in this order:
1. `docs/features/<feature-name>/spec.md`
2. `docs/features/<feature-name>/plan.md`
3. `docs/spec.md`
4. `docs/plan.md`
5. `docs/prompt.md`

## 4. Product-Level Scope
### In Scope
- Build a full-stack application that helps users:
  - Build/refine profile context
  - Discover and evaluate job opportunities
  - Generate tailored, versioned job-application artifacts
- Use agent-assisted workflows where useful
- Keep artifact outputs traceable and revisioned

### Out of Scope (Global)
- Browser automation that auto-submits applications
- Enterprise multi-tenant controls in initial scope
- Hardcoded external provider assumptions that prevent extensibility

## 5. Global Technical Constraints
- Frontend: Next.js + TypeScript + pnpm
- Backend: FastAPI + Python + uv
- Database: Postgres
- Auth: JWT-based authentication
- Packaging/runtime: Dockerized backend services runnable on macOS/Linux
- Testing: pytest (backend) and Cypress (frontend E2E)

## 6. Global Architecture Rules
- Use modular layering in backend:
  - API routes
  - Services/domain logic
  - Persistence layer (`backend/app/db/*`)
  - Integrations (agents/providers/parsers)
- Keep DB-hit operations isolated to repository/data-access layer.
- Keep integrations behind clear interfaces to allow future provider changes.
- Prefer readable and explicit code over clever abstraction.

## 7. Data and Artifact Rules
- Markdown files are the source of truth for generated/intake artifacts where applicable.
- DB should store file locations and metadata, not large markdown bodies.
- Artifact history must be revisioned (no destructive overwrite of prior versions).
- Naming/path conventions can be feature-specific but must be deterministic and documented in each feature spec.

## 8. Agent and CLI Rules
- Each agent must be isolated in its own directory/file set under a clear namespace.
- Agent workflows must be runnable from API flows and from CLI.
- Use environment variables for API keys/secrets; never hardcode production credentials.

## 9. Quality and Testing Rules
- Every feature must include focused backend tests for:
  - Core success paths
  - Key validation failures
  - Critical edge cases
- Frontend user-visible workflows should include concise Cypress E2E coverage.
- Keep tests high-signal; avoid low-value snapshot-heavy testing.

## 10. Feature Registry
- User Profiles: `docs/features/user-profiles/spec.md`

New features should be added by creating:
- `docs/features/<feature-name>/spec.md`
- `docs/features/<feature-name>/plan.md`
And then adding the feature path to this registry.
