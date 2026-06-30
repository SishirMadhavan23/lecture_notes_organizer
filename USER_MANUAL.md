# User Manual

## Offline Web Application

The Offline AI Lecture Notes Organizer is a local Streamlit web application. It
uses the existing Python ingestion pipeline, local Tesseract OCR, local Ollama
inference, and SQLite storage. It does not use cloud inference APIs.

## Local Setup

Install the local prerequisites:

- Python 3.11+
- Ollama
- Tesseract OCR, optional but required for scanned PDFs
- LibreOffice, optional and only needed for legacy `.ppt` files

Create the environment and start the app:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
ollama pull phi3:mini
streamlit run src/app.py
```

Open the URL printed by Streamlit, usually `http://localhost:8501`.

## Offline Operation

Before disconnecting from the internet, install Python dependencies and pull the
Ollama model you plan to use. After that, the core workflow runs locally:

- Upload lecture files
- Extract text and OCR scanned documents
- Generate summaries, exam questions, and flashcards with Ollama
- Save notes to SQLite
- Search and review saved notes

## Ollama Configuration

Start Ollama locally and confirm the model is installed:

```bash
ollama list
ollama pull phi3:mini
```

In **Settings**, configure:

- Ollama Host: `http://localhost:11434`
- Model: `phi3:mini` or another locally installed Ollama model

## Tesseract Configuration

Install Tesseract and language data locally. In **Settings**, enable OCR and set
the Tesseract executable path. Common paths:

- Windows: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- macOS: `/opt/homebrew/bin/tesseract`
- Linux: `/usr/bin/tesseract`

## Supported Formats

- PDF
- DOCX
- TXT
- PPTX
- PPT with LibreOffice conversion available locally

## Troubleshooting

- Streamlit will not start: activate the virtual environment and reinstall
  `requirements.txt`.
- AI summaries are unavailable: start Ollama and confirm the configured model is
  installed with `ollama list`.
- OCR does not work: confirm Tesseract is installed and enabled in Settings.
- Upload fails: confirm the file format is supported and below the configured
  size limit.
- Search is empty: process at least one note and confirm the SQLite database path
  in Settings.
