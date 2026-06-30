# Contributing to Lecture Notes Organizer

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes using conventional commits
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Merge Request

## Development Setup

See README.md for basic setup instructions.

## Code Standards

- Python 3.11+
- Type hints for all function signatures
- Docstrings for all public functions (Google style)
- Line length: 88 characters
- Follow PEP 8 conventions

## Testing

- All new features must include tests
- Run `pytest` before submitting
- Maintain minimum 80% code coverage
- For web UI changes, launch `streamlit run src/app.py` and verify upload,
  OCR, AI summaries, flashcards, SQLite persistence, search, and offline
  operation.

## Commit Guidelines

Use conventional commits:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- test: Adding tests
- refactor: Code refactoring
- chore: Maintenance tasks

## Code Review

All submissions require review. Maintainers will review within 48 hours.
