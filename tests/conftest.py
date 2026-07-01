"""Shared fixtures and configuration for all tests."""

from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.storage.models import init_db
from src.utils.config import AppConfig


class MockSessionState(dict):
    """Mock Streamlit session state as a dict-like object."""

    def __getattr__(self, key: str) -> Any:
        if key in self:
            return self[key]
        raise AttributeError(key)

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value


class MockStreamlitContext:
    """Simple context manager used for Streamlit layout primitives."""

    def __init__(self, label: str) -> None:
        self.label = label

    def __enter__(self) -> MockStreamlitContext:
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False

    def container(self, **_: Any) -> MockStreamlitContext:
        return MockStreamlitContext(f"{self.label}.container")


class MockProgressBar:
    """Track progress updates made by Streamlit progress bars."""

    def __init__(self) -> None:
        self.updates: list[tuple[Any, Any]] = []
        self.emptied = False

    def progress(self, value: Any, text: Any = None) -> None:
        self.updates.append((value, text))

    def empty(self) -> None:
        self.emptied = True


class MockPlaceholder(MockStreamlitContext):
    """Streamlit placeholder double with nested container support."""

    def __init__(self) -> None:
        super().__init__("placeholder")


class MockQueryParams(dict):
    """Query params double with a clear method."""

    def clear(self) -> None:
        super().clear()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test file operations."""
    tmp = Path(tempfile.mkdtemp(prefix="lecture_test_"))
    yield tmp
    shutil.rmtree(str(tmp))


@pytest.fixture
def temp_pdf_file(temp_dir: Path) -> Path:
    """Create a minimal valid PDF file for testing."""
    pdf_path = temp_dir / "test.pdf"
    # Minimal PDF content
    pdf_content = (
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td "
        b"(Test Lecture Content) Tj ET\nendstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n"
        b"0000000058 00000 n \n0000000115 00000 n \n0000000266 00000 n \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n367\n"
        b"%%EOF"
    )
    pdf_path.write_bytes(pdf_content)
    return pdf_path


@pytest.fixture
def temp_docx_file(temp_dir: Path) -> Path:
    """Create a minimal DOCX file (ZIP-based XML) for testing."""
    import zipfile

    docx_path = temp_dir / "test.docx"
    doc_content = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        "<w:p><w:r><w:t>Test Document Content</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>Second paragraph</w:t></w:r></w:p>"
        "</w:body></w:document>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.'
        'wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument'
        '/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        "</Relationships>"
    )

    with zipfile.ZipFile(str(docx_path), "w") as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", doc_content)
    return docx_path


@pytest.fixture
def temp_txt_file(temp_dir: Path) -> Path:
    """Create a simple text file."""
    txt_path = temp_dir / "test.txt"
    txt_path.write_text(
        "This is a test lecture about Python programming.", encoding="utf-8"
    )
    return txt_path


@pytest.fixture
def temp_image_file(temp_dir: Path) -> Path:
    """Create a minimal PNG file for OCR testing."""
    img_path = temp_dir / "test.png"
    # Minimal 1x1 pixel PNG
    img_content = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    img_path.write_bytes(img_content)
    return img_path


@pytest.fixture
def sample_text() -> str:
    """Return sample lecture text for AI testing."""
    return (
        "Machine Learning Fundamentals\n\n"
        "Machine learning is a subset of artificial intelligence that enables "
        "systems to learn and improve from experience. There are three main "
        "types: supervised learning, unsupervised learning, and reinforcement "
        "learning. Supervised learning uses labeled data to train models. "
        "Unsupervised learning finds patterns in unlabeled data. "
        "Reinforcement learning uses rewards and punishments.\n\n"
        "Key concepts include training data, features, labels, and models. "
        "The goal is to create accurate predictions on new, unseen data."
    )


@pytest.fixture
def mock_config() -> AppConfig:
    """Return a default AppConfig suitable for testing."""
    config = AppConfig()
    config.ollama_base_url = "http://localhost:11434"
    config.ollama_model = "phi3:mini"
    config.llm_backend = "ollama"
    config.temperature = 0.1
    config.context_length = 4096
    config.tesseract_enabled = True
    config.tesseract_path = "/usr/bin/tesseract"
    config.tesseract_lang = "eng"
    config.cache_enabled = True
    return config


@pytest.fixture
def mock_requests_get(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock requests.get for Ollama API tests."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"models": [{"name": "phi3:mini"}]}

    def mock_get(url: str, **kwargs: Any) -> MagicMock:
        return mock

    import src.utils.integrations

    monkeypatch.setattr(src.utils.integrations.requests, "get", mock_get)
    monkeypatch.setattr("src.ai.model_manager.requests.get", mock_get)
    return mock


@pytest.fixture
def mock_requests_post(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock requests.post for Ollama generate API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": json.dumps(
            {
                "title": "Test Lecture",
                "subject": "Computer Science",
                "topics": ["Machine Learning"],
                "keywords": ["ML", "AI"],
                "summary": "A test summary.",
                "important_points": ["Point 1"],
                "possible_exam_questions": [
                    "What is ML?",
                ],
                "flashcards": [
                    {"front": "What is ML?", "back": "Machine Learning"},
                ],
                "difficulty": "Beginner",
            }
        )
    }

    def mock_post(url: str, **kwargs: Any) -> MagicMock:
        return mock_response

    monkeypatch.setattr("src.ai.model_manager.requests.post", mock_post)
    return mock_response


@pytest.fixture
def mock_requests_post_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock requests.post returning error to trigger fallback."""

    def mock_post(url: str, **kwargs: Any) -> MagicMock:
        mock = MagicMock()
        mock.status_code = 503
        return mock

    monkeypatch.setattr("src.ai.model_manager.requests.post", mock_post)


@pytest.fixture
def in_memory_db() -> Generator[Any, None, None]:
    """Create an in-memory SQLite database for testing."""
    engine = init_db("sqlite:///:memory:")
    yield engine


@pytest.fixture
def mock_streamlit_session_state(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Mock Streamlit session state."""
    import streamlit as st

    state: dict[str, Any] = {
        "current_page": "Upload",
        "config": {
            "llm_backend": "ollama",
            "ollama_base_url": "http://localhost:11434",
            "ollama_model": "phi3:mini",
            "temperature": 0.1,
            "context_length": 4096,
            "tesseract_enabled": False,
            "tesseract_path": "",
            "tesseract_lang": "eng",
            "database_url": "sqlite:///data/lecture_notes.db",
            "cache_enabled": True,
        },
        "language": "en",
    }

    mock_state = MockSessionState(state)

    # Patch session_state
    monkeypatch.setattr(st, "session_state", mock_state)
    # Patch query_params
    monkeypatch.setattr(st, "query_params", MockQueryParams())

    return mock_state


@pytest.fixture
def mock_streamlit(monkeypatch: pytest.MonkeyPatch) -> Generator[MagicMock, None, None]:
    """Mock all common Streamlit UI functions."""
    import streamlit as st

    mock = MagicMock()
    mock.session_state = MockSessionState()
    mock.query_params = MockQueryParams()
    mock.secrets = {}
    mock.selectbox.return_value = "en"
    mock.select_slider.return_value = 0.1
    mock.number_input.return_value = 4096
    mock.text_input.return_value = ""
    mock.text_area.return_value = ""
    mock.checkbox.return_value = False
    mock.toggle.return_value = False
    mock.radio.return_value = "Upload"
    mock.file_uploader.return_value = None
    mock.button.return_value = False
    mock.slider.return_value = 0.1
    mock.columns.side_effect = lambda spec: [
        MockStreamlitContext(f"column_{index}")
        for index in range(spec if isinstance(spec, int) else len(spec))
    ]
    mock.tabs.side_effect = lambda labels: [
        MockStreamlitContext(f"tab_{index}") for index, _ in enumerate(labels)
    ]
    mock.expander.side_effect = lambda label, expanded=False: MockStreamlitContext(
        f"expander:{label}:{expanded}"
    )
    mock.container.side_effect = lambda **kwargs: MockStreamlitContext(
        f"container:{kwargs}"
    )
    mock.rerun = MagicMock()
    mock.markdown = MagicMock()
    mock.title = MagicMock()
    mock.header = MagicMock()
    mock.subheader = MagicMock()
    mock.caption = MagicMock()
    mock.write = MagicMock()
    mock.text = MagicMock()
    mock.json = MagicMock()
    mock.dataframe = MagicMock()
    mock.metric = MagicMock()
    mock.divider = MagicMock()
    mock.stop = MagicMock()
    mock.sidebar = MagicMock()
    mock.sidebar.__enter__.return_value = mock.sidebar
    mock.sidebar.__exit__.return_value = False
    mock.sidebar.container.side_effect = lambda **kwargs: MockStreamlitContext(
        f"sidebar.container:{kwargs}"
    )
    mock.sidebar.selectbox.return_value = "en"
    mock.sidebar.button.return_value = False
    mock.sidebar.markdown = MagicMock()
    mock.sidebar.title = MagicMock()
    mock.error = MagicMock()
    mock.success = MagicMock()
    mock.info = MagicMock()
    mock.warning = MagicMock()
    mock.spinner.side_effect = lambda text="": MockStreamlitContext(f"spinner:{text}")
    mock.progress.side_effect = lambda *args, **kwargs: MockProgressBar()
    mock.empty.side_effect = MockPlaceholder

    # Patch st.* functions
    monkeypatch.setattr(st, "set_page_config", mock.set_page_config)
    monkeypatch.setattr(st, "sidebar", mock.sidebar)
    monkeypatch.setattr(st, "selectbox", mock.selectbox)
    monkeypatch.setattr(st, "select_slider", mock.select_slider)
    monkeypatch.setattr(st, "number_input", mock.number_input)
    monkeypatch.setattr(st, "text_input", mock.text_input)
    monkeypatch.setattr(st, "text_area", mock.text_area)
    monkeypatch.setattr(st, "checkbox", mock.checkbox)
    monkeypatch.setattr(st, "toggle", mock.toggle)
    monkeypatch.setattr(st, "radio", mock.radio)
    monkeypatch.setattr(st, "file_uploader", mock.file_uploader)
    monkeypatch.setattr(st, "button", mock.button)
    monkeypatch.setattr(st, "slider", mock.slider)
    monkeypatch.setattr(st, "columns", mock.columns)
    monkeypatch.setattr(st, "tabs", mock.tabs)
    monkeypatch.setattr(st, "expander", mock.expander)
    monkeypatch.setattr(st, "container", mock.container)
    monkeypatch.setattr(st, "error", mock.error)
    monkeypatch.setattr(st, "success", mock.success)
    monkeypatch.setattr(st, "info", mock.info)
    monkeypatch.setattr(st, "warning", mock.warning)
    monkeypatch.setattr(st, "spinner", mock.spinner)
    monkeypatch.setattr(st, "progress", mock.progress)
    monkeypatch.setattr(st, "empty", mock.empty)
    monkeypatch.setattr(st, "rerun", mock.rerun)
    monkeypatch.setattr(st, "markdown", mock.markdown)
    monkeypatch.setattr(st, "title", mock.title)
    monkeypatch.setattr(st, "header", mock.header)
    monkeypatch.setattr(st, "subheader", mock.subheader)
    monkeypatch.setattr(st, "caption", mock.caption)
    monkeypatch.setattr(st, "write", mock.write)
    monkeypatch.setattr(st, "text", mock.text)
    monkeypatch.setattr(st, "json", mock.json)
    monkeypatch.setattr(st, "dataframe", mock.dataframe)
    monkeypatch.setattr(st, "metric", mock.metric)
    monkeypatch.setattr(st, "divider", mock.divider)
    monkeypatch.setattr(st, "stop", mock.stop)
    monkeypatch.setattr(st, "session_state", mock.session_state)
    monkeypatch.setattr(st, "query_params", mock.query_params)
    monkeypatch.setattr(
        st,
        "cache_data",
        lambda func=None, **kwargs: func if func is not None else (lambda inner: inner),
    )
    monkeypatch.setattr(
        st,
        "cache_resource",
        lambda func=None, **kwargs: func if func is not None else (lambda inner: inner),
    )

    return mock


@pytest.fixture
def mock_uploaded_file() -> Any:
    """Return a simple uploaded-file test double."""

    class UploadedFile:
        """Minimal Streamlit UploadedFile-compatible object."""

        def __init__(
            self, name: str = "notes.pdf", content: bytes = b"test content"
        ) -> None:
            self.name = name
            self._content = content
            self.size = len(content)

        def getvalue(self) -> bytes:
            return self._content

    return UploadedFile
