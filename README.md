# Lecture Notes Organizer

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linter-ruff-red)](https://github.com/astral-sh/ruff)

An offline-first Streamlit application for students and researchers to import, process, and organize lecture notes using local AI (Ollama) and OCR (Tesseract). Emphasizes privacy, CPU-first computation, and zero cloud dependencies.

## Features

- 📚 **Multi-format Import**: PDF, DOCX, TXT, PPTX, PPT
- 🔍 **OCR Support**: Tesseract integration for scanned documents and images
- 🤖 **Local AI Processing**: Ollama-based LLM for structured note generation
- 💬 **Multilingual UI**: English, Telugu (తెలుగు), and Hindi (हिन्दी)
- 🗂️ **Full-text Search**: FTS5-powered search across all notes
- 📇 **Flashcard Generation**: Auto-generated study cards from notes
- 🔒 **Privacy-First**: 100% offline, no data leaves your machine
- 🎨 **Dark Academic Theme**: Clean, focused reading experience
- 💾 **SQLite Storage**: Lightweight, portable database

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) (for AI features)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (optional, for OCR)

### Installation

```bash
# Clone the repository
git clone https://code.swecha.org/SishirMadhavan23/lecture-notes-organizer.git
cd lecture-notes-organizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the application
streamlit run src/app.py
```

### Pull an AI Model

```bash
ollama pull phi3:mini
```

## Usage

1. **Upload**: Drag and drop lecture notes (PDF, DOCX, TXT, PPTX)
2. **Process**: Automatic OCR (if enabled) → text cleaning → AI structuring
3. **Review**: Browse organized notes with summaries, topics, and key points
4. **Study**: Generate flashcards and exam questions from your notes
5. **Search**: Full-text search across your entire note collection

## Screenshots

*Screenshots coming soon.*

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

## Multilingual Support

The application supports three languages:
- **English** (default)
- **Telugu** (తెలుగు)
- **Hindi** (हिन्दी)

Switch languages via the dropdown in the sidebar. The preference persists throughout your session.

### Adding a New Language

1. Create a new translation file `translations/{lang_code}.json`
2. Add the language to the `LANGUAGES` dict in `src/utils/translations.py`
3. All UI elements automatically adapt

## Roadmap

- [x] Multi-format document import
- [x] Local AI processing with Ollama
- [x] OCR integration for scanned documents
- [x] Full-text search with FTS5
- [x] Flashcard generation
- [x] Multilingual UI (EN/TE/HI)
- [ ] Batch document processing
- [ ] Export to PDF/Anki
- [ ] Mobile-responsive UI
- [ ] Cloud sync (optional)

## Development

### Setup for Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest --cov=src/ --cov-report=term

# Type checking
mypy src/

# Linting
ruff check src/ tests/
black --check src/ tests/
isort --check-only src/ tests/
```

### Test Suite

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=src/ --cov-report=term --cov-report=html

# Run specific test file
pytest tests/test_utils/test_translations.py -v
```

### CI/CD Pipeline

The project uses GitLab CI with the following stages:
1. **Format**: ruff format, black, isort
2. **Lint**: ruff check, flake8, pylint
3. **Type Check**: mypy (strict mode)
4. **Test**: pytest
5. **Coverage**: Minimum 80% coverage
6. **Security**: bandit, pip-audit, semgrep
7. **Build**: Docker image

## Docker

```bash
# Build the image
docker build -t lecture-notes-organizer .

# Run the container
docker run -p 8501:8501 lecture-notes-organizer
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Branching Strategy

- `main` — Production-ready
- `develop` — Integration branch
- `feat/*` — Feature branches
- `fix/*` — Bug fixes

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Testing
- `chore:` Maintenance

## Acknowledgements

- [Streamlit](https://streamlit.io/) - Web framework
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- All contributors and users of this project

## License

This project is licensed under the **GNU Affero General Public License v3.0** - see [LICENSE](LICENSE) for details.

## Repository Health

[![Pipeline status](https://code.swecha.org/SishirMadhavan23/lecture-notes-organizer/badges/main/pipeline.svg)](https://code.swecha.org/SishirMadhavan23/lecture-notes-organizer/-/pipelines)
[![Coverage](https://code.swecha.org/SishirMadhavan23/lecture-notes-organizer/badges/main/coverage.svg)](https://code.swecha.org/SishirMadhavan23/lecture-notes-organizer/-/pipelines)

### Quality Tools

- **Formatting**: Black, Ruff, isort
- **Linting**: Ruff, Flake8, Pylint
- **Type Hints**: mypy (strict mode)
- **Security**: Bandit, pip-audit, Semgrep
- **Dead Code**: Vulture
- **Modernization**: Pyupgrade
- **Pre-commit**: Pre-commit hooks for all tools