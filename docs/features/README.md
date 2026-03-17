# Feature Docs Guide

Use feature docs to keep implementation details scoped and maintainable.

## Required Structure
For each feature, create:
- `docs/features/<feature-name>/spec.md`
- `docs/features/<feature-name>/plan.md`

## What Goes Where
- Global `docs/spec.md`: shared technical/product rules across all features
- Global `docs/plan.md`: high-level project sequencing and governance
- Feature `spec.md`: behavior, contracts, APIs, data model specifics for one feature
- Feature `plan.md`: execution phases, tasks, and acceptance criteria for one feature

## Working Rule
When implementing a feature, rely primarily on that feature's docs.
Only update global docs when a cross-feature rule or project-level sequence changes.

## Current Features
- `user-profiles`
- `resume-builder`
