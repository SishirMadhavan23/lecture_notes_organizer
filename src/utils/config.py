# SPDX-License-Identifier: GPL-3.0-or-later
"""Application configuration management."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


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
    tesseract_lang: str = "eng"
    tesseract_timeout: int = 60
    max_file_size_mb: int = 50
    supported_formats: list = field(default_factory=lambda: ["pdf", "docx", "txt"])
    cache_enabled: bool = True
    page_title: str = "Lecture Notes Organizer"


def load_config() -> AppConfig:
    """Load configuration from environment with defaults."""
    cfg = AppConfig()
    if os.getenv("OLLAMA_BASE_URL"):
        cfg.ollama_base_url = os.environ["OLLAMA_BASE_URL"]
    if os.getenv("OLLAMA_MODEL"):
        cfg.ollama_model = os.environ["OLLAMA_MODEL"]
    if os.getenv("LLM_BACKEND"):
        cfg.llm_backend = os.environ["LLM_BACKEND"]
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    cfg.model_dir.mkdir(parents=True, exist_ok=True)
    cfg.log_dir.mkdir(parents=True, exist_ok=True)
    return cfg
