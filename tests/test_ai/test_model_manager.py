"""Tests for AI model manager."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from src.ai.model_manager import (
    _generate_fallback,
    _normalize_flashcards,
    _normalize_question_text,
    _pack_study_items,
    _parse_json_response,
    _query_ollama,
    generate_structured_notes,
    is_llama_cpp_available,
    is_ollama_available,
)
from src.utils.exceptions import AIError, ModelNotFoundError


class TestOllamaAvailability:
    """Tests for is_ollama_available function."""

    def test_ollama_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns True when Ollama responds with 200."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        def mock_get(url: str, **kwargs) -> MagicMock:
            return mock_resp

        monkeypatch.setattr("src.ai.model_manager.requests.get", mock_get)
        assert is_ollama_available("http://localhost:11434") is True

    def test_ollama_unavailable_connection_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test returns False on connection error."""
        from requests import ConnectionError

        def mock_get(url: str, **kwargs) -> None:
            raise ConnectionError("Connection failed")

        monkeypatch.setattr("src.ai.model_manager.requests.get", mock_get)
        assert is_ollama_available("http://localhost:11434") is False

    def test_ollama_unavailable_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns False on timeout."""
        from requests import Timeout

        def mock_get(url: str, **kwargs) -> None:
            raise Timeout("Request timed out")

        monkeypatch.setattr("src.ai.model_manager.requests.get", mock_get)
        assert is_ollama_available("http://localhost:11434") is False

    def test_ollama_non_200(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns False when status is not 200."""
        mock_resp = MagicMock()
        mock_resp.status_code = 503

        def mock_get(url: str, **kwargs) -> MagicMock:
            return mock_resp

        monkeypatch.setattr("src.ai.model_manager.requests.get", mock_get)
        assert is_ollama_available("http://localhost:11434") is False


class TestLlamaCppAvailable:
    """Tests for is_llama_cpp_available function."""

    def test_no_path(self) -> None:
        """Test returns False when no path given."""
        assert is_llama_cpp_available() is False
        assert is_llama_cpp_available("") is False

    def test_file_exists(self, tmp_path) -> None:
        """Test returns True when file exists."""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("dummy")
        assert is_llama_cpp_available(str(model_file)) is True

    def test_file_not_found(self, tmp_path) -> None:
        """Test returns False when file does not exist."""
        assert is_llama_cpp_available(str(tmp_path / "nonexistent.gguf")) is False


class TestNormalizeQuestionText:
    """Tests for _normalize_question_text function."""

    def test_dict_with_text(self) -> None:
        """Test extracts text key from dict."""
        result = _normalize_question_text({"text": "What is ML?"})
        assert result == "What is ML?"

    def test_dict_with_question(self) -> None:
        """Test extracts question key from dict."""
        result = _normalize_question_text({"question": "Define AI"})
        assert result == "Define AI"

    def test_dict_with_empty_keys(self) -> None:
        """Test returns empty string when both keys missing."""
        result = _normalize_question_text({"other": "value"})
        assert result == ""

    def test_string_input(self) -> None:
        """Test returns string as-is stripped."""
        result = _normalize_question_text("  What is ML?  ")
        assert result == "What is ML?"

    def test_empty_string(self) -> None:
        """Test returns empty string for empty input."""
        result = _normalize_question_text("")
        assert result == ""


class TestNormalizeFlashcards:
    """Tests for _normalize_flashcards function."""

    def test_non_list_input(self) -> None:
        """Test returns empty list for non-list input."""
        assert _normalize_flashcards("not a list") == []
        assert _normalize_flashcards(None) == []
        assert _normalize_flashcards({}) == []

    def test_empty_list(self) -> None:
        """Test returns empty list for empty input."""
        assert _normalize_flashcards([]) == []

    def test_valid_flashcards(self) -> None:
        """Test normalizes valid flashcard objects."""
        items = [
            {"front": "Q1", "back": "A1"},
            {"question": "Q2", "answer": "A2"},
            {"prompt": "Q3", "response": "A3"},
        ]
        result = _normalize_flashcards(items)
        assert len(result) == 3
        assert result[0]["front"] == "Q1"
        assert result[0]["back"] == "A1"
        assert result[1]["front"] == "Q2"
        assert result[1]["back"] == "A2"
        assert result[2]["front"] == "Q3"
        assert result[2]["back"] == "A3"

    def test_skips_non_dict_items(self) -> None:
        """Test skips non-dict items in the list."""
        items = [
            {"front": "Q1", "back": "A1"},
            "not a dict",
            42,
            None,
        ]
        result = _normalize_flashcards(items)
        assert len(result) == 1
        assert result[0]["front"] == "Q1"


class TestPackStudyItems:
    """Tests for _pack_study_items function."""

    def test_packs_questions_and_flashcards(self) -> None:
        """Test packs questions and flashcards into result."""
        result = {
            "possible_exam_questions": [
                {"text": "Q1"},
                {"text": "Q2"},
            ],
            "flashcards": [
                {"front": "F1", "back": "A1"},
            ],
        }
        packed = _pack_study_items(result)
        assert len(packed["possible_exam_questions"]) == 3
        assert packed["possible_exam_questions"][0]["type"] == "question"
        assert packed["possible_exam_questions"][2]["type"] == "flashcard"
        assert len(packed["flashcards"]) == 1


class TestQueryOllama:
    """Tests for _query_ollama function."""

    def test_successful_query(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test successful Ollama API query."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Use JSON wrapped in markdown code block (matches first regex)
        mock_response.json.return_value = {
            "response": (
                '```json\n{"title": "Test Lecture", "subject": "CS", '
                '"topics": ["AI"], "keywords": ["ML"], '
                '"summary": "Summary.", "important_points": ["Point"], '
                '"possible_exam_questions": ["Q1"], '
                '"flashcards": [{"front": "Q", "back": "A"}], '
                '"difficulty": "Beginner"}\n```'
            )
        }

        def mock_post(url: str, **kwargs) -> MagicMock:
            return mock_response

        monkeypatch.setattr("src.ai.model_manager.requests.post", mock_post)
        config = {
            "ollama_base_url": "http://localhost:11434",
            "ollama_model": "phi3:mini",
            "temperature": 0.1,
            "context_length": 4096,
            "timeout": 30,
        }
        result = _query_ollama("Test lecture text.", config)
        assert result["title"] == "Test Lecture"
        assert result["difficulty"] == "Beginner"
        assert "created_at" in result
        assert len(result["flashcards"]) > 0

    def test_model_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test raises ModelNotFoundError on 404."""
        mock_resp = MagicMock()
        mock_resp.status_code = 404

        def mock_post(url: str, **kwargs) -> MagicMock:
            return mock_resp

        monkeypatch.setattr("src.ai.model_manager.requests.post", mock_post)
        config = {
            "ollama_base_url": "http://localhost:11434",
            "ollama_model": "phi3:mini",
        }
        with pytest.raises(ModelNotFoundError):
            _query_ollama("test", config)

    def test_ai_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test raises AIError on non-200 response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500

        def mock_post(url: str, **kwargs) -> MagicMock:
            return mock_resp

        monkeypatch.setattr("src.ai.model_manager.requests.post", mock_post)
        config = {
            "ollama_base_url": "http://localhost:11434",
            "ollama_model": "phi3:mini",
        }
        with pytest.raises(AIError):
            _query_ollama("test", config)

    def test_default_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test uses default values when config keys are missing."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "response": '```json\n{"title": "Test", "subject": "CS"}\n```'
        }

        def mock_post(url: str, **kwargs) -> MagicMock:
            assert kwargs.get("json", {}).get("model") == "phi3:mini"
            return mock_resp

        monkeypatch.setattr("src.ai.model_manager.requests.post", mock_post)
        result = _query_ollama("test", {})
        assert result is not None
        assert result["title"] == "Test"


class TestParseJsonResponse:
    """Tests for _parse_json_response function."""

    def test_parse_valid_json_in_code_block(self) -> None:
        """Test parses JSON from markdown code block."""
        response = '```json\n{"title": "Test", "subject": "CS"}\n```'
        result = _parse_json_response(response, "original")
        assert result["title"] == "Test"
        assert result["subject"] == "CS"

    def test_parse_valid_json_without_code_block(self) -> None:
        """Test parses JSON without markdown block (via fallback regex)."""
        response = '{"title": "Test", "subject": "CS"}'
        result = _parse_json_response(response, "original")
        assert result["title"] == "Test"
        assert result["subject"] == "CS"

    def test_fallback_on_invalid_json(self, sample_text: str) -> None:
        """Test falls back to _generate_fallback on invalid JSON."""
        result = _parse_json_response("Not JSON at all", sample_text)
        assert result["title"] is not None
        assert result["difficulty"] is not None

    def test_fallback_on_empty_response(self, sample_text: str) -> None:
        """Test falls back on empty response."""
        result = _parse_json_response("", sample_text)
        assert result["title"] is not None

    def test_parse_valid_json_in_code_block_without_lang(self) -> None:
        """Test parses JSON from markdown code block without language specifier."""
        response = '```\n{"title": "Test", "subject": "CS"}\n```'
        result = _parse_json_response(response, "original")
        assert result["title"] == "Test"
        assert result["subject"] == "CS"


class TestGenerateFallback:
    """Tests for _generate_fallback function."""

    def test_beginner_level(self) -> None:
        """Test beginner difficulty for short simple text."""
        text = "This is a test lecture with basic content."
        result = _generate_fallback(text, {})
        assert result["difficulty"] == "Beginner"
        assert result["title"] is not None
        assert result["subject"] == "General"
        assert len(result["keywords"]) > 0

    def test_intermediate_level(self) -> None:
        """Test intermediate difficulty assignment."""
        text = " ".join(["word" for _ in range(100)])
        result = _generate_fallback(text, {})
        assert result["difficulty"] == "Beginner"

    def test_advanced_level(self) -> None:
        """Test advanced difficulty for long complex text."""
        words = [
            "algorithm",
            "optimization",
            "implementation",
            "parameterization",
            "dimensionality",
            "regularization",
        ]
        text = " ".join(words * 400)
        result = _generate_fallback(text, {})
        assert result["difficulty"] == "Advanced"

    def test_exam_questions_generation(self) -> None:
        """Test exam questions are generated from important points."""
        lines = [
            "This is an important line about machine learning that is long enough.",
            "Another important line about deep learning and neural networks.",
            "Yet another key insight about reinforcement learning algorithms.",
        ]
        text = "\n".join(lines)
        result = _generate_fallback(text, {})
        assert len(result["possible_exam_questions"]) >= 3

    def test_flashcards_generation(self) -> None:
        """Test flashcards are generated."""
        lines = []
        for i in range(10):
            lines.append(
                f"This is an important long line number {i} "
                "about machine learning and AI concepts."
            )
        text = "\n".join(lines)
        result = _generate_fallback(text, {})
        assert len(result["flashcards"]) > 0

    def test_summary_truncation(self) -> None:
        """Test summary truncation for long text."""
        text = "A " * 1000
        result = _generate_fallback(text, {})
        assert result["summary"].endswith("...")
        assert len(result["summary"]) <= 503

    def test_empty_text(self) -> None:
        """Test handles empty text gracefully."""
        result = _generate_fallback("", {})
        assert result["title"] is not None
        assert result["difficulty"] is not None

    def test_keywords_frequency_ranking(self) -> None:
        """Test keywords are ranked by frequency."""
        text = " ".join(
            ["machine"] * 50 + ["learning"] * 40 + ["algorithm"] * 30 + ["data"] * 20
        )
        result = _generate_fallback(text, {})
        assert "machine" in result["keywords"]
        assert len(result["keywords"]) <= 15


class TestGenerateStructuredNotes:
    """Tests for generate_structured_notes function."""

    def test_uses_ollama_when_available(
        self, sample_text: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test uses Ollama when available."""
        ollama_response = json.dumps(
            {
                "title": "Ollama Lecture",
                "subject": "CS",
                "topics": ["AI"],
                "keywords": ["ML"],
                "summary": "Summary.",
                "important_points": ["Point"],
                "possible_exam_questions": ["Q1"],
                "flashcards": [
                    {"front": "Q", "back": "A"},
                ],
                "difficulty": "Intermediate",
            }
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": f"```json\n{ollama_response}\n```"}

        def mock_post(url: str, **kwargs) -> MagicMock:
            return mock_resp

        def mock_get(url: str, **kwargs) -> MagicMock:
            resp = MagicMock()
            resp.status_code = 200
            return resp

        monkeypatch.setattr("src.ai.model_manager.requests.post", mock_post)
        monkeypatch.setattr("src.ai.model_manager.requests.get", mock_get)

        result = generate_structured_notes(sample_text)
        assert result["title"] == "Ollama Lecture"

    def test_fallback_when_ollama_unavailable(
        self, sample_text: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test falls back when Ollama is unavailable."""

        def mock_get(url: str, **kwargs) -> None:
            from requests import ConnectionError

            raise ConnectionError()

        monkeypatch.setattr("src.ai.model_manager.requests.get", mock_get)

        result = generate_structured_notes(sample_text)
        assert result["subject"] == "General"
        assert result["difficulty"] is not None

    def test_fallback_on_ollama_exception(
        self, sample_text: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test falls back when Ollama raises exception."""

        def mock_get(url: str, **kwargs) -> MagicMock:
            resp = MagicMock()
            resp.status_code = 200
            return resp

        def mock_post(url: str, **kwargs) -> None:
            raise Exception("Ollama error")

        monkeypatch.setattr("src.ai.model_manager.requests.post", mock_post)
        monkeypatch.setattr("src.ai.model_manager.requests.get", mock_get)

        result = generate_structured_notes(sample_text)
        assert result["subject"] == "General"

    def test_fallback_with_ollama_unavailable_check(
        self, sample_text: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test falls back when is_ollama_available returns False."""

        def mock_get(url: str, **kwargs) -> MagicMock:
            resp = MagicMock()
            resp.status_code = 503
            return resp

        monkeypatch.setattr("src.ai.model_manager.requests.get", mock_get)

        result = generate_structured_notes(sample_text)
        assert result["subject"] == "General"
        assert result["difficulty"] is not None
