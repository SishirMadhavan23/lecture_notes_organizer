# Offline AI Lecture Notes Organizer

> CPU-First Hackathon — Convert unstructured lecture notes into structured study material, completely offline.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Overview

The **Offline AI Lecture Notes Organizer** is a Streamlit-based desktop application that transforms unstructured lecture notes (PDF, DOCX, TXT, PPTX, PPT, and optionally scanned PDFs/images) into rich, structured study material. It runs **entirely on CPU** with **no cloud dependencies**, using local Small Language Models (SLMs) to extract topics, keywords, summaries, exam questions, and more.

Priorities:
- Privacy — All processing happens on your machine
- Offline capability — No internet required after initial setup
- CPU efficiency — Optimized for laptops and low-resource environments
- Graceful degradation — Works even when optional components are unavailable

## Problem Statement

Students and professionals accumulate vast collections of lecture notes. Manually organizing these into searchable, structured study material is time-consuming. Existing solutions require cloud AI services, compromising privacy and requiring internet connectivity.

**Our solution**: A fully offline, CPU-only desktop application that automatically extracts, cleans, and enriches lecture notes using local AI models, storing everything in a local SQLite database for fast search and retrieval.

## Features

- Multi-format Ingestion: PDF, DOCX, TXT, PPTX, and PPT with auto-detection
- Scanned Document OCR: Tesseract OCR (optional, graceful fallback)
- Text Normalization: Automated cleaning and structure detection
- Local AI: Phi-3 Mini / Qwen2.5 via Ollama on CPU
- Structured Output: Topics, keywords, summaries, exam questions, difficulty
- Flashcards: Offline review cards generated from saved exam questions and key points
- Local Storage: SQLite — no cloud
- Full-text Search: Across titles, topics, keywords, and content
- System Dashboard: Real-time status of models, storage, system health
- Fully Offline: Zero internet after setup
- Graceful Failure: Missing dependencies handled cleanly

## AI Workflow

Input Documents -> Text Extraction (PyMuPDF/python-docx/python-pptx/Tesseract) -> Text Cleaning -> Local LLM -> JSON -> SQLite -> Search

## Tech Stack

Language: Python 3.11+ | UI: Streamlit | PDF: PyMuPDF | DOCX: python-docx | PPTX: python-pptx | OCR: pytesseract | LLM: Ollama | DB: SQLite+SQLAlchemy | Search: FTS5 | Tools: Ruff/Black/isort/mypy/Bandit/pytest

---

## Installation

### Prerequisites
- Python 3.11+
- Tesseract OCR (optional, for scanned documents)
- Ollama (recommended, for AI features)
- LibreOffice (optional, only for legacy `.ppt` conversion)

### Setup

```bash
git clone https://code.swecha.org/SishirMadhavan23/lecture-notes-organizer.git
cd lecture-notes-organizer
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
ollama pull phi3:mini    # Optional
streamlit run src/app.py
```

## Upload Support

- Native support: `PDF`, `DOCX`, `TXT`, and `PPTX`
- Legacy `PPT` support: requires LibreOffice so the app can convert `.ppt` to `.pptx` locally before extraction
- PowerPoint extraction preserves slide order, titles, bullets, tables, and speaker notes when available

## Offline Web Setup

The application runs as a local Streamlit web app:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
ollama pull phi3:mini
streamlit run src/app.py
```

After the first setup and model download, the app can run without internet
access. Keep Ollama running locally and open the Streamlit URL printed in the
terminal, usually `http://localhost:8501`.

### Ollama Configuration

Set the model in **Settings** or through environment variables before launch:

```bash
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=phi3:mini
```

Pull models while online, then run offline:

```bash
ollama pull phi3:mini
ollama list
```

The app uses local Ollama inference only. It does not call OpenAI, Anthropic,
Gemini, Hugging Face Inference API, or any other cloud inference service.

### Tesseract Configuration

Install Tesseract and language data locally. In **Settings**, enable OCR and set:

```text
Tesseract path: path to the local tesseract executable
Language: eng
```

OCR is used for scanned PDFs when normal PDF text extraction returns too little
text.

### Troubleshooting

- Streamlit does not launch: confirm the virtual environment is active and
  dependencies are installed.
- AI summary is missing: confirm Ollama is running and the configured model is
  already pulled.
- OCR does not run: confirm Tesseract and language data are installed locally.
- Upload fails: confirm the file is `PDF`, `DOCX`, `TXT`, or `PPTX`.
- Search returns no results: upload and process at least one document, then check
  the SQLite database path in **Settings**.

## Testing

```bash
pytest
pytest --cov=src --cov-report=html
```

Web verification checklist:

- `streamlit run src/app.py` launches successfully
- Drag-and-drop uploads PDF, DOCX, TXT, and PPTX
- OCR works for scanned documents when Tesseract is installed
- AI summary, exam questions, and flashcards are generated by local Ollama
- Notes save to SQLite and Search returns saved content
- The workflow continues after disconnecting from the internet

## License

GNU General Public License v3.0 — see LICENSE.

## Contributing

See CONTRIBUTING.md.

## Security

See SECURITY.md.

---

<p align="center">Built for the CPU-First Hackathon</p>
