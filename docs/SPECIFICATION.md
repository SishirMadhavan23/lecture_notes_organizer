# Specification - Offline AI Lecture Notes Organizer

## 1. Functional Requirements

### FR1: Document Ingestion
- FR1.1: Accept PDF, extract text via PyMuPDF
- FR1.2: Accept DOCX, extract text via python-docx
- FR1.3: Accept TXT, read raw text
- FR1.4: Support scanned PDFs via Tesseract OCR (optional)
- FR1.5: Auto-detect file type from extension
- FR1.6: Graceful error on corrupt files

### FR2: Text Processing
- FR2.1: Remove extra whitespace, normalize line endings
- FR2.2: Strip HTML tags
- FR2.3: Normalize Unicode via unidecode
- FR2.4: Extract title from filename or first heading

### FR3: AI Processing
- FR3.1: Connect to local Ollama (Phi-3 Mini / Qwen2.5)
- FR3.2: Fall back to llama.cpp
- FR3.3: Generate structured JSON matching schema
- FR3.4: Handle model unavailability gracefully
- FR3.5: Cancellable long-running inference

### FR4: Storage
- FR4.1: Store all data in SQLite
- FR4.2: SQLAlchemy ORM
- FR4.3: FTS5 full-text search
- FR4.4: Export notes to JSON

### FR5: User Interface
- FR5.1: Streamlit multi-page app
- FR5.2: Upload page with drag-and-drop
- FR5.3: View organized notes with details
- FR5.4: Search with keyword/topic/title filters
- FR5.5: Settings for model/OCR config
- FR5.6: System status dashboard

### FR6: Offline Operation
- FR6.1: No external API calls
- FR6.2: Offline-installable dependencies
- FR6.3: Graceful degradation when features unavailable

## 2. Non-Functional Requirements

- NFR1: PDF extraction < 5s per 100 pages
- NFR2: Search results < 1s
- NFR3: Clear error messages for all failures
- NFR4: No data loss on unexpected shutdown
- NFR5: No network calls from application code
- NFR6: Type hints throughout
- NFR7: Unit tests for all modules

## 3. System Architecture

Streamlit UI -> Orchestrator -> Ingestion -> Preprocessing -> AI Engine -> SQLite

## 4. AI Pipeline

System Prompt -> User Prompt (lecture text) -> LLM -> JSON Response -> Parse

## 5. Output Schema

{
  "title": "",
  "subject": "",
  "topics": [],
  "keywords": [],
  "summary": "",
  "important_points": [],
  "possible_exam_questions": [],
  "difficulty": "",
  "created_at": ""
}

## 6. Database Schema

Table: documents (id, filename, file_type, file_size, raw_text, cleaned_text, created_at, processed_at, status, error_message)
Table: note_metadata (id, document_id FK, title, subject, topics JSON, keywords JSON, summary, important_points JSON, possible_exam_questions JSON, difficulty)
Table: fts_notes (FTS5 virtual: title, subject, topics, keywords, content)

## 7. Risks

- AI quality varies by model
- Large PDFs may cause memory pressure
- CPU inference 30-120s per document
- GGUF models are 2-8GB

## 8. Mitigations

- Graceful degradation
- Cancellable operations
- Progress indicators
- Clear system requirements documentation
