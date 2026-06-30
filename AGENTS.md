# AGENTS.md — AI Agent Guidelines

## Purpose

This document provides guidance for AI coding agents working on the Lecture Notes Organizer project. It defines expectations, constraints, and communication protocols to ensure consistent and reliable contributions.

## Core Principles

1. **Offline-First** — All AI features must run 100% locally with CPU inference. No external API calls.
2. **CPU-First** — Optimize for CPU inference using quantized models (e.g., INT8, ONNX Runtime, llama.cpp). Avoid GPU-only dependencies.
3. **Hackathon-Grade** — Prefer pragmatic, working solutions over academic perfection. Time-to-value matters.
4. **Test Coverage** — Every AI module must have corresponding tests in `tests/test_ai/`.

## Technology Stack

- **Python** ≥ 3.11
- **spaCy** — NLP pipeline (fast, CPU-native)
- **sentence-transformers** — Embedding generation
- **scikit-learn** — Clustering & classification
- **FastAPI** — Local web API
- **SQLite** — On-device storage

## Code Standards

- Follow Ruff linting rules (`ruff check src/ tests/`)
- Format with Black (line-length=88)
- Sort imports with isort (profile=black)
- Type hints required for all function signatures
- Docstrings for all public modules and functions (NumPy-style)

## Safety & Security

- Never commit secrets, API keys, or tokens
- All dependencies must be pinned in `requirements.txt`
- Run `bandit -ll -q -r src/` before committing new code
- Run `detect-secrets scan` before final commit

## Communication

- When making changes, update `CHANGELOG.md` under the appropriate version header
- Always reference the relevant issue or spec when making changes
- Flag any security concerns immediately

---

*Last updated: 2026-06-30*