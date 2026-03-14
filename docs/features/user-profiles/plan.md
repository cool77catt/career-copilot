# Feature Plan - User Profiles

## Goal
Deliver a `Profiles` workspace with two core sections:
`User Information` (global intake/profile) and `Job-Specific Profiles` (targeted profile generation and refinement).

## Phase A - Profiles Navigation and Page Shell
### Tasks
- Add `Profiles` item to the application navigation.
- Implement Profiles page route/view.
- Render two top-level sections:
  - `User Information`
  - `Job-Specific Profiles`

### Acceptance Criteria
- User can navigate to `Profiles` from nav bar.
- Profiles page consistently renders both top-level sections.

## Phase B - User Information Intake and Global Profile Generation
### Tasks
- Implement global intake controls for LinkedIn, resume(s), and additional information.
- Persist intake markdown artifacts.
- Generate combined full global profile markdown and surface it to user.
- Ensure updates are revisioned.

### Acceptance Criteria
- User can submit/update global profile inputs.
- Full global profile markdown is generated and visible.
- Global profile markdown revisions are preserved.

## Phase C - Job-Specific Profiles List and Add Flow
### Tasks
- Implement job-specific profile list UI/state.
- Add `Add Profile` flow supporting:
  - Agent-generated suggestions from global profile
  - User-defined custom profile input
- Support accept/reject/finalize actions for suggested profiles.
- Persist profile list and statuses.

### Acceptance Criteria
- User can create profile targets from agent suggestions and manual input.
- User can accept/reject and finalize target profiles.
- Finalized list persists and is retrievable.

## Phase D - Job-Specific Profile Detail Artifacts
### Tasks
- Implement per-profile detail workspace.
- Generate and display, per selected profile:
  - Overall fit assessment
  - Tailored resume
  - Tailored profile
- Persist each artifact as markdown with revisions.

### Acceptance Criteria
- Each selected profile displays all three generated artifact types.
- Artifacts are stored as markdown and revisioned.

## Phase E - Additional Context and Global Sync
### Tasks
- Add profile-specific context input for each selected job profile.
- On context update:
  - Update/regenerate selected profile artifacts as needed
  - Update global profile markdown context
- Ensure synchronization does not overwrite previous revisions.

### Acceptance Criteria
- User can add additional context to a job-specific profile.
- Changes propagate to both profile-specific outputs and global profile markdown.
- Revision history remains intact for all modified artifacts.

## Testing Plan
- Backend pytest coverage for:
  - Profile navigation/state endpoints
  - Global intake and markdown generation
  - Job profile creation/decisioning
  - Per-profile artifact generation contracts
  - Context sync to global profile
  - Revisioning behavior across artifact types
- Cypress E2E coverage for:
  - Navigate to Profiles page
  - Fill User Information and generate global profile
  - Add/accept/customize job-specific profiles
  - View generated assessment/resume/tailored profile
  - Add context and verify sync behavior

## Definition of Done
- All phase acceptance criteria are met
- Relevant backend and E2E tests pass
- Spec and plan docs reflect implemented behavior
