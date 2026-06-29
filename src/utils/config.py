# SPDX-License-Identifier: GPL-3.0-or-later
"""Application configuration management."""

from __future__ import annotations

import json
import os
import platform
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class AppConfig:
    """Central application configuration."""

    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = field(default_factory=lambda: Path("data"))
    model_dir: Path = field(default_factory=lambda: Path("models"))
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    database_url: str = "sqlite:///data/lecture_notes.db"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "phi3:mini"
    llama_cpp_model_path: Optional[str] = None
    llm_backend: str = "ollama"
    context_length: int = 4096
    temperature: float = 0.1
    tesseract_enabled: bool = False
    tesseract_path: str = ""
    tesseract_lang: str = "eng"
    tesseract_timeout: int = 60
    max_file_size_mb: int = 50
    supported_formats: list = field(default_factory=lambda: ["pdf", "docx", "txt"])
    cache_enabled: bool = True
    page_title: str = "Lecture Notes Organizer"
    config_filename: str = "app_config.json"

    def __post_init__(self) -> None:
        """Normalize path-based fields after initialization."""
        self.base_dir = Path(self.base_dir)
        self.data_dir = Path(self.data_dir)
        self.model_dir = Path(self.model_dir)
        self.log_dir = Path(self.log_dir)
        if not self.tesseract_path:
            self.tesseract_path = get_default_tesseract_path()

    @property
    def config_path(self) -> Path:
        """Return the persistent config file location."""
        return self.base_dir / self.data_dir / self.config_filename

    def to_dict(self) -> dict[str, Any]:
        """Serialize the configuration for persistence."""
        payload = asdict(self)
        payload["base_dir"] = str(self.base_dir)
        payload["data_dir"] = str(self.data_dir)
        payload["model_dir"] = str(self.model_dir)
        payload["log_dir"] = str(self.log_dir)
        return payload

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "AppConfig":
        """Build a config instance from a serialized dictionary."""
        normalized = dict(values)
        for key in ("base_dir", "data_dir", "model_dir", "log_dir"):
            if key in normalized and normalized[key]:
                normalized[key] = Path(normalized[key])
        return cls(**normalized)


def get_default_tesseract_path() -> str:
    """Return a sensible default Tesseract path for the current platform."""
    system = platform.system().lower()
    if system == "windows":
        return r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if system == "darwin":
        return "/opt/homebrew/bin/tesseract"
    return "/usr/bin/tesseract"


def _load_config_file(config_path: Path) -> dict[str, Any]:
    """Load persisted configuration data from disk."""
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(config: AppConfig) -> AppConfig:
    """Persist application configuration to disk."""
    config.data_dir.mkdir(parents=True, exist_ok=True)
    config.model_dir.mkdir(parents=True, exist_ok=True)
    config.log_dir.mkdir(parents=True, exist_ok=True)
    config.config_path.parent.mkdir(parents=True, exist_ok=True)
    config.config_path.write_text(
        json.dumps(config.to_dict(), indent=2),
        encoding="utf-8",
    )
    return config


def reset_config(base_dir: Optional[Path] = None) -> AppConfig:
    """Reset persisted configuration back to defaults."""
    config = AppConfig(base_dir=base_dir or AppConfig.base_dir)
    if config.config_path.exists():
        config.config_path.unlink()
    return config


def load_config(base_dir: Optional[Path] = None) -> AppConfig:
    """Load configuration from disk and environment with defaults."""
    cfg = AppConfig(base_dir=base_dir or AppConfig.base_dir)
    persisted_values = _load_config_file(cfg.config_path)
    if persisted_values:
        persisted_values.setdefault("base_dir", cfg.base_dir)
        cfg = AppConfig.from_dict(persisted_values)
    if os.getenv("OLLAMA_BASE_URL"):
        cfg.ollama_base_url = os.environ["OLLAMA_BASE_URL"]
    if os.getenv("OLLAMA_MODEL"):
        cfg.ollama_model = os.environ["OLLAMA_MODEL"]
    if os.getenv("LLM_BACKEND"):
        cfg.llm_backend = os.environ["LLM_BACKEND"]
    if os.getenv("TESSERACT_PATH"):
        cfg.tesseract_path = os.environ["TESSERACT_PATH"]
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    cfg.model_dir.mkdir(parents=True, exist_ok=True)
    cfg.log_dir.mkdir(parents=True, exist_ok=True)
    return cfg
