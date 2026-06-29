# Running Quality Checks Locally

This document explains how to run all code quality checks locally before submitting changes.

## Prerequisites

```bash
cd d:\lecture_notes_organizer\lecture-notes-organizer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Quick Start — Run All Checks

```bash
# Run all checks in sequence
ruff check src/ tests/
black --check --line-length=88 src/ tests/
isort --check-only --profile=black --line-length=88 src/ tests/
mypy --strict --ignore-missing-imports src/
pytest --cov=src/ --cov-report=term --cov-report=html tests/
bandit -ll -q -r src/
vulture src/ --min-confidence 80
```

## Individual Check Commands

### 1. Ruff (Linter)
```bash
ruff check src/ tests/
# Auto-fix:
ruff check --fix src/ tests/
# Format:
ruff format src/ tests/
```

### 2. Black (Code Formatter)
```bash
blacks --check --line-length=88 src/ tests/
# Auto-format:
black --line-length=88 src/ tests/
```

### 3. isort (Import Sorting)
```bash
isort --check-only --profile=black --line-length=88 src/ tests/
# Auto-fix:
isort --profile=black --line-length=88 src/ tests/
```

### 4. mypy (Type Checking)
```bash
mypy --strict --ignore-missing-imports src/
```

### 5. pytest (Unit Tests)
```bash
# All tests
pytest

# With coverage
pytest --cov=src/ --cov-report=term --cov-report=html tests/

# Specific test file
pytest tests/test_preprocessing/test_text_cleaner.py -v

# Specific test class
pytest tests/test_utils/test_validators.py::TestValidators -v
```

### 6. Bandit (Security Scan)
```bash
bandit -ll -q -r src/
```

### 7. Vulture (Dead Code Detection)
```bash
vulture src/ --min-confidence 80
```

### 8. Detect Secrets
```bash
detect-secrets scan --baseline .secrets.baseline
# Update baseline:
detect-secrets scan > .secrets.baseline
```

## Pre-commit Hooks

Install pre-commit hooks to run checks automatically:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Run all hooks once
```

The pre-commit config runs: trailing-whitespace, end-of-file-fixer,
check-yaml, check-json, ruff, black, isort, mypy, bandit, vulture,
detect-secrets.

## CI Pipeline (GitLab)

The `.gitlab-ci.yml` file defines the same checks in a CI pipeline with 8 stages:
1. `ruff` — Python linter (fail on error)
2. `black` — Code formatter check (fail on error)
3. `isort` — Import sorting check (fail on error)
4. `mypy` — Type checker (allow failure)
5. `pytest` — Unit tests with coverage (fail on error)
6. `bandit` — Security scanner (allow failure)
7. `vulture` — Dead code detector (allow failure)
8. `detect-secrets` — Secret scanner (allow failure)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ruff: command not found` | `pip install ruff` |
| `black: command not found` | `pip install black` |
| `isort: command not found` | `pip install isort` |
| `mypy: command not found` | `pip install mypy` |
| `bandit: command not found` | `pip install bandit` |
| `vulture: command not found` | `pip install vulture` |
| `detect-secrets: command not found` | `pip install detect-secrets` |
| Tests fail with ModuleNotFoundError | Ensure venv is activated and `pip install -r requirements.txt` is run |
