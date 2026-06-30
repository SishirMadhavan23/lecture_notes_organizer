# Lecture Notes Organizer — Spec-Driven Development Constitution

## Purpose

This constitution establishes Spec-Driven Development (SDD) as the standard methodology for building features in the Lecture Notes Organizer project. Every new feature must start with a specification before any implementation begins.

## Core Rules

### Rule 1: Spec First, Code Later
No feature shall be implemented without an approved specification in `specs/`.

### Rule 2: One Spec Per Feature
Each feature gets its own `.spec.md` file under `specs/`.

### Rule 3: Review Before Implementation
All specs must be peer-reviewed before implementation starts.

## Spec Template

Every spec file must include:

1. **Title** — Feature name
2. **Status** — [Draft | Proposed | Approved | Implemented | Deprecated]
3. **Objective** — What problem this feature solves
4. **Requirements** — Bullet list of functional requirements
5. **AI Constraints** — CPU-first, offline, quantized models only
6. **Acceptance Criteria** — How to verify completion
7. **Dependencies** — Internal/external dependencies

## Enforcement

- CI pipeline will check that `specs/` exists and contains at least one spec
- PRs with new features must reference their spec
- Violations require remediation before merge

---

*Constitution adopted: 2026-06-30*