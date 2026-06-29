# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for configuration module."""

import os
import tempfile
from pathlib import Path

from src.utils.config import AppConfig, load_config


class TestAppConfig:
    """Test AppConfig dataclass and load_config function."""

    def test_default_config_has_expected_values(self):
        """Test that default config has all required fields."""
        config = AppConfig()
        assert config.llm_backend == "ollama"
        assert config.ollama_model == "phi3:mini"
        assert config.temperature == 0.1
        assert config.context_length == 4096
        assert config.tesseract_enabled is False
        assert config.max_file_size_mb == 50
        assert "pdf" in config.supported_formats
        assert "docx" in config.supported_formats
        assert "txt" in config.supported_formats

    def test_config_creates_directories(self):
        """Test that load_config creates necessary directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                config = load_config()
                assert Path("data").exists()
                assert Path("models").exists()
                assert Path("logs").exists()
            finally:
                os.chdir(original_cwd)

    def test_config_env_overrides(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom:11434")
        monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:1.5b")
        monkeypatch.setenv("LLM_BACKEND", "llama.cpp")

        config = load_config()
        assert config.ollama_base_url == "http://custom:11434"
        assert config.ollama_model == "qwen2.5:1.5b"
        assert config.llm_backend == "llama.cpp"
