# Project Constitution

## Core Principles

1. **Offline-First**: All processing must work without internet connectivity.
2. **Privacy by Design**: No data leaves the user's machine.
3. **CPU-First**: Optimize for CPU-only environments; GPU is optional.
4. **Accessibility**: Support multiple languages (English, Telugu, Hindi).
5. **Open Source**: AGPL-3.0 licensed with full source transparency.

## Development Standards

1. All code must be typed with Python type hints.
2. All user-facing strings must use the `t()` translation helper.
3. All files must include SPDX license headers.
4. Tests must accompany all new features.
5. Conventional commits are required for all changes.

## Quality Gates

1. Zero lint errors (Ruff, Flake8, Pylint).
2. Zero type errors (mypy strict mode).
3. 80%+ test coverage.
4. All CI pipeline stages must pass.
5. No hardcoded secrets or credentials.