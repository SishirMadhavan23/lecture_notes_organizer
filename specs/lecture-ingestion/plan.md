# Lecture Ingestion Pipeline — Implementation Plan

**Status:** Draft
**Author:** AI Agent
**Date:** 2026-06-30
**Spec Reference:** `specs/lecture-ingestion/spec.md`

## Implementation Steps

1. [ ] Extend the ingestion modules for PDF, DOCX, and TXT handling
2. [ ] Add validation and metadata persistence for uploaded files
3. [ ] Add tests for successful and invalid ingestion flows

## Files to Modify
- `src/ingestion/pdf_extractor.py` — Improve PDF text extraction and OCR fallback
- `src/ingestion/docx_extractor.py` — Ensure robust DOCX parsing
- `src/storage/database.py` — Persist ingestion metadata and status
- `tests/test_ingestion/` — Add regression tests

## Test Plan
- Unit tests for extraction helpers
- Integration tests for file validation and status tracking
- Coverage target: ≥ 80%

## Risks & Mitigations
- OCR dependencies may be missing → Document installation and provide graceful fallback
- Large files may slow processing → Enforce size limits and async handling

## Review Checklist
- [ ] Code follows project standards (Ruff, Black, isort)
- [ ] Type hints present
- [ ] Tests pass with coverage ≥ 80%
- [ ] Bandit security scan passes
- [ ] No secrets committed
