# Web Application Testing Report

Date: 2026-06-30

## Scope

This report covers the Streamlit web application only.

## Verified In This Environment

- Streamlit routing includes Upload, View Notes, Flashcards, Search, Settings,
  and System Status.
- AI generation code now uses local Ollama as the only model inference path.
- System Status reports the local web stack: Ollama, Tesseract, SQLite, and
  installed Python packages.
- Python syntax check passes:

```bash
python -m py_compile src\app.py src\ui\pages\flashcards.py src\ai\model_manager.py src\ui\pages\settings.py src\ui\pages\system_status.py
```

## Pending Manual Verification

These checks require the local runtime services and sample documents:

- Launch with `streamlit run src/app.py`
- Upload PDF, DOCX, TXT, and PPTX files through drag-and-drop
- Process a scanned PDF with Tesseract OCR enabled
- Generate AI summaries and exam questions with Ollama
- Review generated flashcards
- Confirm notes save to SQLite
- Confirm Search returns saved notes
- Disconnect the internet and repeat the core upload, AI, flashcard, search, and
  view-notes workflow using already installed dependencies and pulled models

## Offline Checklist

- Python dependencies installed locally
- Ollama installed and running locally
- Required Ollama model already pulled
- Tesseract installed locally for OCR demos
- No OpenAI, Anthropic, Gemini, Hugging Face Inference API, or cloud endpoint
  configured
