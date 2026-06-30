# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for configuration module."""

import os
import tempfile
from pathlib import Path

from src.utils.config import AppConfig, load_config, reset_config, save_config


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
                load_config()
                assert Path("data").exists()
                assert Path("models").exists()
                assert Path("logs").exists()
            finally:
                os.chdir(original_cwd)

    def test_config_env_overrides(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom:11434")
        monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:1.5b")
        monkeypatch.setenv("LLM_BACKEND", "ignored")

        config = load_config()
        assert config.ollama_base_url == "http://custom:11434"
        assert config.ollama_model == "qwen2.5:1.5b"
        assert config.llm_backend == "ollama"

    def test_config_persists_to_disk(self):
        """Test that config is saved and loaded from the JSON config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            config = AppConfig(base_dir=base_dir)
            config.ollama_base_url = "http://localhost:22434"
            config.ollama_model = "phi3"
            config.tesseract_path = "/custom/tesseract"
            save_config(config)

            loaded = load_config(base_dir=base_dir)
            assert loaded.ollama_base_url == "http://localhost:22434"
            assert loaded.ollama_model == "phi3"
            assert loaded.tesseract_path == "/custom/tesseract"
            assert loaded.config_path.exists()

    def test_reset_config_removes_persisted_file(self):
        """Test that reset removes the stored configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            config = AppConfig(base_dir=base_dir)
            save_config(config)
            assert config.config_path.exists()

            reset = reset_config(base_dir=base_dir)
            assert not reset.config_path.exists()
