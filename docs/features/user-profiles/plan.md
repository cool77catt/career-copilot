# Feature Plan - User Profiles

## Goal
Deliver a `Profiles` workspace with two core sections:
`User Information` (global intake/profile) and `Job-Specific Profiles` (targeted profile generation and refinement).

## Phase A - Profiles Navigation, Submenu, and Overview Shell
### Tasks
- Add `Profiles` item to the application navigation.
- Implement route-backed Profiles workspace:
  - `GET /profiles` for Profiles Overview
  - `GET /profiles/{profileId}` for each job-specific profile workspace
- Add dropdown submenu under `Profiles` containing:
  - `Overview`
  - One menu item per job-specific profile
- Render two top-level sections:
  - `User Information`
  - `Job-Specific Profiles`
- In `Job-Specific Profiles` Overview, render a profile table with list entries and explicit open actions.
- Ensure clicking either submenu items or table rows navigates to the same URL-backed profile routes.

### Acceptance Criteria
- User can navigate to `Profiles` from nav bar.
- `Profiles` navigation supports submenu expansion/collapse.
- `Overview` and profile entries are URL-backed and deep-linkable.
- Profiles Overview consistently renders both top-level sections.
- Profiles Overview table lists available job-specific profiles and supports click-through navigation to `/profiles/{profileId}`.

## Phase B - User Information Intake and Global Profile Generation
### Tasks
- On `/profiles` Overview, render sections in a vertical stack:
  - `User Information` first
  - `Job-Specific Profiles` second
- Implement global intake controls for LinkedIn, resume(s), and additional information.
- Include follow-up question answer inputs in `User Information`.
- Provide one `Update Profile` action that submits all user information inputs together.
- Persist intake markdown artifacts.
- Generate combined full global profile markdown and surface it to user.
- Ensure updates are revisioned.

### Acceptance Criteria
- Profiles Overview renders `User Information` above `Job-Specific Profiles` (not side-by-side).
- User can submit/update global profile inputs.
- User can edit LinkedIn/resume/additional information/follow-up answers and submit with a single update action.
- Full global profile markdown is generated and visible.
- Global profile markdown revisions are preserved.

## Phase C - Job-Specific Profiles List and Add Flow
### Tasks
- Implement job-specific profile list UI/state.
- Connect job-specific profile list to backend persistence so Profiles submenu and Overview table are sourced from API, not transient client state.
- Add `Add Profile` flow supporting:
  - Agent-generated suggestions from global profile
  - User-defined custom profile input
- Support accept/reject/finalize actions for suggested profiles.
- Persist profile list and statuses.

### Acceptance Criteria
- User can create profile targets from agent suggestions and manual input.
- User can accept/reject and finalize target profiles.
- Finalized list persists and is retrievable.

## Phase D - Legacy User Profile Removal
### Tasks
- Remove legacy `User Profile` navigation/tab surface.
- Remove duplicate profile-intake UI paths outside `Profiles > Overview`.
- Ensure profile editing is centralized in `Profiles > Overview` only.
- Update E2E assertions to reflect removal of legacy `User Profile` entry.

### Acceptance Criteria
- Sidebar/navigation no longer contains a legacy `User Profile` item.
- User Information intake is only accessible via `Profiles > Overview`.
- No duplicate or conflicting profile update surfaces remain in the UI.

## Phase E - Job-Specific Profile Detail Artifacts
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

## Phase F - Additional Context and Global Sync
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
  - Expand/collapse Profiles submenu
  - Navigate using `Overview` submenu and `/profiles/{profileId}` submenu entries
  - Navigate from Profiles Overview table row to the same profile route
  - Fill User Information and generate global profile
  - Add/accept/customize job-specific profiles
  - View generated assessment/resume/tailored profile
  - Add context and verify sync behavior

## Definition of Done
- All phase acceptance criteria are met
- Relevant backend and E2E tests pass
- Spec and plan docs reflect implemented behavior
