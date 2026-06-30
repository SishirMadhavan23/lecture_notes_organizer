# AI Assistant Guide — Lecture Notes Organizer

## Project Overview

Lecture Notes Organizer is an offline-first Streamlit application designed for students and researchers to import, process, and organize lecture notes using local AI (Ollama) and OCR (Tesseract). It emphasizes privacy, CPU-first computation, and zero cloud dependencies.

**Stack:** Python 3.11+ | Streamlit | SQLAlchemy/SQLite | Ollama | Tesseract  
**License:** AGPL-3.0  
**Repository:** https://code.swecha.org/SishirMadhavan23/lecture-notes-organizer

## Architecture

```
src/
├── app.py                  # Streamlit entry point
├── ai/
│   ├── model_manager.py    # LLM query logic + fallback
│   └── prompt_templates.py # System/user prompt definitions
├── ingestion/
│   ├── pdf_extractor.py    # PyMuPDF-based PDF extraction
│   ├── docx_extractor.py
│   ├── pptx_extractor.py
│   ├── txt_extractor.py
│   └── ocr_processor.py    # Tesseract OCR integration
├── preprocessing/
│   └── text_cleaner.py     # Text normalization + cleaning
├── storage/
│   ├── database.py         # SQLAlchemy operations
│   ├── models.py           # ORM model definitions
│   └── _db.py              # Internal DB helpers
├── ui/
│   ├── theme.py            # Dark academic theme
│   ├── components/
│   │   ├── sidebar.py      # Navigation + language selector
│   │   ├── dashboard.py    # Stats, status cards, stepper, footer
│   │   ├── note_card.py    # Expandable note display
│   │   └── page_header.py  # Consistent page headers
│   └── pages/
│       ├── upload.py       # File upload + processing pipeline
│       ├── view_notes.py   # Browse archived notes
│       ├── flashcards.py   # Study card review
│       ├── search.py       # FTS5 full-text search
│       ├── settings.py     # Configuration management
│       └── system_status.py # Health dashboard
└── utils/
    ├── config.py           # AppConfig dataclass
    ├── translations.py     # Multilingual support (EN/TE/HI)
    ├── exceptions.py       # Custom exceptions
    ├── integrations.py     # External service detection
    └── validators.py       # File validation utilities
```

## Coding Standards

- **Language:** Python 3.11+ with `from __future__ import annotations`
- **Style:** PEP 8 with Black formatting (line-length=88)
- **Imports:** isort with black profile
- **Types:** Strict mypy mode with explicit annotations
- **Linting:** Ruff, Flake8, Pylint
- **Security:** Bandit, pip-audit, Semgrep
- **Docstrings:** Google/NumPy style for public functions
- **License header:** All files must start with `# SPDX-License-Identifier: AGPL-3.0-only`

## AI Assistant Guidelines

1. **Always check for existing patterns** before implementing new features.
2. **Use the `t()` translation helper** for all user-facing strings.
3. **Keep UI components modular** — pages import from `components/`, not vice versa.
4. **Never hardcode secrets** — use `.env` files and `python-dotenv`.
5. **Maintain backward compatibility** with existing database schemas.
6. **Write tests** in the `tests/` directory mirroring `src/` structure.
7. **Follow conventional commits** for all changes: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.

## Repository Structure

```
.specify/           # Spec-driven development artifacts
.specify/constitution.md
.specify/templates/
specs/              # Feature specifications
├── 2024-08-multilingual-support.md
├── ...
tests/
├── test_ai/
├── test_ingestion/
├── test_preprocessing/
├── test_storage/
├── test_utils/
translations/
├── en.json
├── te.json
└── hi.json
```

## Testing Workflow

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/ --cov-report=term --cov-report=html

# Type checking
mypy src/

# Linting
ruff check src/ tests/
black --check src/ tests/
isort --check-only src/ tests/

# Security
bandit -r src/
pip-audit
```

## Branching Strategy

- `main` — Production-ready, protected branch
- `develop` — Integration branch for features
- `feat/<name>` — Feature branches off `develop`
- `fix/<name>` — Bug fix branches
- `docs/<name>` — Documentation updates

## Contribution Workflow

1. Create a feature branch from `develop`
2. Implement changes following coding standards
3. Write/update tests
4. Run full test suite
5. Create merge request to `develop`
6. Code review by maintainer
7. Squash-merge to `develop`
8. Release branches from `develop` to `main`