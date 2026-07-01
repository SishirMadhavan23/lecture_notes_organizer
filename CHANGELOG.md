# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-06-30

### Added
- Flashcards page generated from existing local note metadata
- Web documentation for local installation, offline runtime, Ollama, Tesseract, and troubleshooting
- Web testing report for the offline Streamlit workflow
- Comprehensive Streamlit UI test coverage for app routing, themed components, note cards, upload flows, settings interactions, search, system status, view notes, and flashcards

### Notes
- The project remains a Streamlit web application
- AI generation is configured for local Ollama only; no cloud inference APIs are used

## [0.2.0] - 2026-06-29

### Added
- Full PDF text extraction via PyMuPDF with page limit support
- Full DOCX text extraction via python-docx
- Full TXT file reading with encoding auto-detection
- Tesseract OCR support for scanned documents and images
- Text preprocessing: HTML stripping, unicode normalization, whitespace collapse
- Title extraction from content (markdown headings, first line) or filename
- Text chunking with sentence-aware boundaries for LLM processing
- Local LLM integration with Ollama
- Structured JSON generation matching required schema
- Graceful fallback generation when AI models are unavailable
- SQLite database with SQLAlchemy ORM
- FTS5 full-text search across all note fields
- CRUD operations: save, search, get all, get by ID, delete
- Database statistics and health monitoring
- Streamlit multi-page UI with full navigation
- Upload page with drag-and-drop, progress tracking, pipeline display
- View Notes page with expandable note cards and delete support
- Search page with FTS5-powered full-text search
- Settings page for LLM backend, model, OCR, and storage configuration
- System Status dashboard with model availability, package checks, DB stats
- Note card component with topics, keywords, exam questions display
- Graceful error handling for missing dependencies
- Caching configuration support

### Changed
- All stub modules replaced with full implementations
- Enhanced config system with session state persistence
- Improved error hierarchy for better diagnostic messages

## [0.1.0] - 2026-06-29

### Added
- Initial project structure with modular architecture
- Specification document (SPECIFICATION.md)
- README with project overview, setup instructions, and architecture
- CONTRIBUTING.md with contribution guidelines
- CODE_OF_CONDUCT.md with community standards
- SECURITY.md with security policy
- LICENSE (GNU GPL v3.0)
- pyproject.toml with project metadata and tool configuration
- requirements.txt with core dependencies
- .gitignore for Python projects
- .pre-commit-config.yaml with automated checks
- .gitlab-ci.yml with 10 CI pipeline stages
- Basic skeleton modules for all packages
- Work division plan for team roles
