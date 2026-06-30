# Lecture Ingestion Pipeline — Specification

**Status:** Draft
**Author:** AI Agent
**Date:** 2026-06-30

## Objective
Provide a robust ingestion pipeline that accepts PDF, DOCX, and audio lecture files, extracts text content, and prepares it for AI-powered categorization and summarization.

## Requirements
- [ ] Accept PDF uploads and extract text via OCR or native PDF parsing
- [ ] Accept DOCX uploads and extract text via python-docx
- [ ] Store extracted text with metadata (filename, upload date, file type)
- [ ] Validate file size (< 50MB) and format before processing
- [ ] Provide job status tracking for long-running ingestion tasks

## AI Constraints
- CPU-first inference only
- Offline-capable (no external API calls)
- spaCy NLP pipeline for preprocessing

## Acceptance Criteria
1. Successfully ingest a 10-page PDF and extract text with >90% accuracy
2. Successfully ingest a .docx file and extract all text content
3. Reject files >50MB with a clear error message
4. Return meaningful errors for corrupted or invalid files

## Dependencies
- Internal: `src/ingestion/`
- External: pytesseract, python-docx, pypdf2, spaCy

## Implementation Notes
- Use background task processing for long-running ingestion
- Store raw text in SQLite with indexing
- Run OCR only when native text extraction fails
