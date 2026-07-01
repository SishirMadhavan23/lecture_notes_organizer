"""Tests for system integration helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

# Don't import the test functions directly to avoid pytest collection conflicts
from src.utils.integrations import (
    _parse_ollama_list_output,
    _run_command,
    detect_ollama_host,
    detect_tesseract_path,
    get_common_tesseract_paths,
    get_ollama_models,
    get_ollama_version,
)


class TestRunCommand:
    """Tests for _run_command function."""

    def test_successful_command(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test running a successful command."""
        import subprocess

        mock_result = MagicMock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""

        def mock_run(*args, **kwargs) -> MagicMock:
            return mock_result

        monkeypatch.setattr(subprocess, "run", mock_run)
        result = _run_command(["echo", "test"])
        assert result.returncode == 0


class TestGetCommonTesseractPaths:
    """Tests for get_common_tesseract_paths function."""

    def test_returns_list_of_paths(self) -> None:
        """Test returns a list of paths."""
        paths = get_common_tesseract_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0

    def test_no_duplicates(self) -> None:
        """Test no duplicate paths in the list."""
        paths = get_common_tesseract_paths()
        assert len(paths) == len(set(paths))


class TestDetectTesseractPath:
    """Tests for detect_tesseract_path function."""

    def test_returns_none_when_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns None when tesseract not found."""
        monkeypatch.setattr("src.utils.integrations.Path.exists", lambda self: False)
        result = detect_tesseract_path()
        assert result is None

    def test_returns_path_when_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns path when tesseract is found."""
        monkeypatch.setattr("src.utils.integrations.Path.exists", lambda self: True)
        result = detect_tesseract_path()
        assert result is not None


class TestTesseractConnection:
    """Tests for test_tesseract_connection function (imported directly)."""

    def test_invalid_path(self) -> None:
        """Test returns error for invalid path."""
        from src.utils.integrations import test_tesseract_connection as ttc

        result = ttc("")
        assert result["ok"] is False
        assert "executable not found" in result["message"]

    def test_nonexistent_path(self) -> None:
        """Test returns error for nonexistent path."""
        from src.utils.integrations import test_tesseract_connection as ttc

        result = ttc("/nonexistent/tesseract.exe")
        assert result["ok"] is False

    def test_successful_connection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns success for valid tesseract."""
        import subprocess

        from src.utils.integrations import test_tesseract_connection as ttc

        mock_result = MagicMock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "tesseract v5.0\n"
        mock_result.stderr = ""

        def mock_run(*args, **kwargs) -> MagicMock:
            return mock_result

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.setattr("src.utils.integrations.Path.exists", lambda self: True)

        result = ttc("/usr/bin/tesseract")
        assert result["ok"] is True
        assert result["version"] == "tesseract v5.0"

    def test_failed_command(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns error when command fails."""
        import subprocess

        from src.utils.integrations import test_tesseract_connection as ttc

        mock_result = MagicMock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error"

        def mock_run(*args, **kwargs) -> MagicMock:
            return mock_result

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.setattr("src.utils.integrations.Path.exists", lambda self: True)

        result = ttc("/usr/bin/tesseract")
        assert result["ok"] is False

    def test_subprocess_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns error on subprocess exception."""
        import subprocess

        from src.utils.integrations import test_tesseract_connection as ttc

        def mock_run(*args, **kwargs) -> None:
            raise OSError("Command not found")

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.setattr("src.utils.integrations.Path.exists", lambda self: True)

        result = ttc("/usr/bin/tesseract")
        assert result["ok"] is False


class TestDetectOllamaHost:
    """Tests for detect_ollama_host function."""

    def test_ollama_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns host when Ollama is available."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        def mock_get(url: str, **kwargs) -> MagicMock:
            return mock_resp

        monkeypatch.setattr("src.utils.integrations.requests.get", mock_get)
        result = detect_ollama_host("http://localhost:11434")
        assert result == "http://localhost:11434"

    def test_ollama_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns None when Ollama is unavailable."""
        from requests import RequestException

        def mock_get(url: str, **kwargs) -> None:
            raise RequestException("Connection failed")

        monkeypatch.setattr("src.utils.integrations.requests.get", mock_get)
        result = detect_ollama_host("http://localhost:11434")
        assert result is None

    def test_non_200_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns None when response is not 200."""
        mock_resp = MagicMock()
        mock_resp.status_code = 503

        def mock_get(url: str, **kwargs) -> MagicMock:
            return mock_resp

        monkeypatch.setattr("src.utils.integrations.requests.get", mock_get)
        result = detect_ollama_host("http://localhost:11434")
        assert result is None


class TestParseOllamaListOutput:
    """Tests for _parse_ollama_list_output function."""

    def test_parses_model_names(self) -> None:
        """Test parses model names from output."""
        output = (
            "NAME\tID\tSIZE\tMODIFIED\n"
            "phi3:mini\tabc123\t2.3GB\t2 days ago\n"
            "llama3:latest\tdef456\t4.7GB\t1 week ago\n"
        )

        models = _parse_ollama_list_output(output)
        assert "phi3:mini" in models
        assert "llama3:latest" in models

    def test_skips_header(self) -> None:
        """Test skips header line."""
        output = "NAME\tID\nphi3:mini\tabc\n"
        models = _parse_ollama_list_output(output)
        assert "NAME" not in models

    def test_empty_output(self) -> None:
        """Test returns empty list for empty output."""
        assert _parse_ollama_list_output("") == []

    def test_handles_empty_lines(self) -> None:
        """Test handles empty lines gracefully."""
        output = "\n\nphi3:mini\tabc\n\n"
        models = _parse_ollama_list_output(output)
        assert "phi3:mini" in models


class TestGetOllamaModels:
    """Tests for get_ollama_models function."""

    def test_returns_from_cli(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns models from CLI output."""
        import subprocess

        mock_result = MagicMock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "phi3:mini\tabc\nllama3\tdef\n"

        def mock_run(*args, **kwargs) -> MagicMock:
            return mock_result

        monkeypatch.setattr(subprocess, "run", mock_run)
        models = get_ollama_models("http://localhost:11434")
        assert "phi3:mini" in models

    def test_fallback_to_api(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test falls back to API when CLI fails."""
        import subprocess

        def mock_run(*args, **kwargs) -> None:
            raise OSError("ollama not found")

        monkeypatch.setattr(subprocess, "run", mock_run)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "models": [{"name": "phi3:mini"}, {"name": "llama3"}]
        }

        def mock_get(url: str, **kwargs) -> MagicMock:
            return mock_resp

        monkeypatch.setattr("src.utils.integrations.requests.get", mock_get)
        models = get_ollama_models("http://localhost:11434")
        assert "phi3:mini" in models
        assert "llama3" in models

    def test_returns_empty_on_all_failures(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test returns empty list when all methods fail."""
        import subprocess

        def mock_run(*args, **kwargs) -> None:
            raise OSError("ollama not found")

        monkeypatch.setattr(subprocess, "run", mock_run)

        from requests import RequestException

        def mock_get(url: str, **kwargs) -> None:
            raise RequestException("API unavailable")

        monkeypatch.setattr("src.utils.integrations.requests.get", mock_get)
        models = get_ollama_models("http://localhost:11434")
        assert models == []


class TestGetOllamaVersion:
    """Tests for get_ollama_version function."""

    def test_returns_version(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns version string."""
        import subprocess

        mock_result = MagicMock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 0
        mock_result.stdout = "ollama version 0.1.32\n"
        mock_result.stderr = ""

        def mock_run(*args, **kwargs) -> MagicMock:
            return mock_result

        monkeypatch.setattr(subprocess, "run", mock_run)
        version = get_ollama_version()
        assert "0.1.32" in version

    def test_returns_empty_on_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns empty string on failure."""
        import subprocess

        def mock_run(*args, **kwargs) -> None:
            raise OSError("ollama not found")

        monkeypatch.setattr(subprocess, "run", mock_run)
        assert get_ollama_version() == ""

    def test_returns_empty_on_nonzero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns empty string on non-zero return code."""
        import subprocess

        mock_result = MagicMock(spec=subprocess.CompletedProcess)
        mock_result.returncode = 1

        def mock_run(*args, **kwargs) -> MagicMock:
            return mock_result

        monkeypatch.setattr(subprocess, "run", mock_run)
        assert get_ollama_version() == ""


class TestOllamaConnection:
    """Tests for test_ollama_connection function."""

    def test_successful_connection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns success when Ollama is available."""
        from src.utils.integrations import test_ollama_connection as toc

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "models": [{"name": "phi3:mini"}, {"name": "llama3"}]
        }

        def mock_get(url: str, **kwargs) -> MagicMock:
            return mock_resp

        monkeypatch.setattr("src.utils.integrations.requests.get", mock_get)
        result = toc("http://localhost:11434", "phi3:mini")
        assert result["ok"] is True
        assert "Connected" in result["message"]

    def test_connection_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns failure when connection fails."""
        from requests import RequestException

        from src.utils.integrations import test_ollama_connection as toc

        def mock_get(url: str, **kwargs) -> None:
            raise RequestException("Connection failed")

        monkeypatch.setattr("src.utils.integrations.requests.get", mock_get)
        result = toc("http://localhost:11434", "phi3:mini")
        assert result["ok"] is False

    def test_model_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test returns failure when model is not installed."""
        from src.utils.integrations import test_ollama_connection as toc

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"models": [{"name": "llama3"}]}

        def mock_get(url: str, **kwargs) -> MagicMock:
            return mock_resp

        monkeypatch.setattr("src.utils.integrations.requests.get", mock_get)
        result = toc("http://localhost:11434", "phi3:mini")
        assert result["ok"] is False
        assert "not installed" in result["message"]
