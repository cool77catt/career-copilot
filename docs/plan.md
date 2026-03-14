# Job Finder LLM - Global Implementation Plan

## Goal
Provide project-level sequencing, governance, and cross-feature milestones.
Detailed implementation plans live in `docs/features/<feature-name>/plan.md`.

## Documentation Model
- Global product/engineering rules: `docs/spec.md`
- Global sequencing and delivery governance: `docs/plan.md`
- Feature-specific behavior/contracts: `docs/features/<feature-name>/spec.md`
- Feature-specific execution tasks/acceptance: `docs/features/<feature-name>/plan.md`

## Active Feature Plans
- User Profiles: `docs/features/user-profiles/plan.md`

## Execution Workflow
1. Select one active feature to implement.
2. Use that feature's `spec.md` as behavior source of truth.
3. Use that feature's `plan.md` for task order and acceptance criteria.
4. Keep global docs focused on shared standards and cross-feature milestones.
5. Update both global and feature docs when scope boundaries change.

## Global Phases

## Phase 0 - Documentation Governance
### Tasks
- Maintain global and feature doc structure
- Ensure every active feature has both `spec.md` and `plan.md`
- Keep conflict-resolution rules explicit

### Acceptance Criteria
- Documentation structure is consistent and discoverable
- Feature-level implementation can proceed without editing global docs for routine details

## Phase 1 - Platform Foundation
### Tasks
- Maintain baseline runtime/tooling for frontend, backend, DB, auth, and test harnesses
- Keep local/dev scripts and environment templates current
- Preserve ability to run backend/frontend/tests on macOS/Linux

### Acceptance Criteria
- Clean setup path is documented and reproducible
- Core platform tests and smoke checks remain stable

## Phase 2 - Feature Delivery Loop (Repeat Per Feature)
### Tasks
- Implement one feature at a time using `docs/features/<feature-name>/*`
- Keep feature changes modular and reviewable
- Verify feature tests and regression coverage before moving to next feature

### Acceptance Criteria
- Active feature meets its own acceptance criteria
- Docs for that feature reflect actual behavior
- No regressions in previously completed core flows

## Phase 3 - Cross-Feature Integration
### Tasks
- Connect feature outputs/inputs across stages
- Validate end-to-end user journey across completed features
- Resolve data model and API contract overlaps between features

### Acceptance Criteria
- Multi-stage workflow works coherently end-to-end
- Integration contracts are documented and tested

## Phase 4 - Hardening and Release Readiness
### Tasks
- Expand reliability/performance/error-path coverage
- Tighten observability and operational runbooks
- Finalize known limitations and release documentation

### Acceptance Criteria
- High-confidence test suite for core journeys
- Stable runbook and clear operational guidance
- Known risks and constraints are documented

## Global Definition of Done
A task is done when:
- Implementation matches the active feature spec
- Feature acceptance criteria are met
- Relevant tests pass
- Documentation is updated at the correct level (feature and/or global)
