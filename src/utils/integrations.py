"""System integration helpers for Tesseract OCR and Ollama."""

from __future__ import annotations

import logging
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

import requests

from src.utils.config import get_default_tesseract_path

logger = logging.getLogger(__name__)


def _run_command(
    command: list[str], timeout: int = 5
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command and capture its output."""
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def get_common_tesseract_paths() -> list[str]:
    """Return common Tesseract installation paths for the current platform."""
    system = platform.system().lower()
    defaults = [get_default_tesseract_path()]
    if system == "windows":
        defaults.extend(
            [
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Tesseract-OCR\tesseract.exe",
            ]
        )
    elif system == "darwin":
        defaults.extend(
            [
                "/usr/local/bin/tesseract",
                "/opt/local/bin/tesseract",
            ]
        )
    else:
        defaults.extend(
            [
                "/usr/local/bin/tesseract",
                "/snap/bin/tesseract",
            ]
        )
    which_path = shutil.which("tesseract")
    if which_path:
        defaults.insert(0, which_path)

    unique_paths: list[str] = []
    seen = set()
    for item in defaults:
        if item and item not in seen:
            unique_paths.append(item)
            seen.add(item)
    return unique_paths


def detect_tesseract_path() -> str | None:
    """Detect an installed Tesseract executable."""
    for candidate in get_common_tesseract_paths():
        candidate_path = Path(candidate)
        if candidate_path.exists():
            return str(candidate_path)
    return None


def test_tesseract_connection(executable_path: str) -> dict[str, Any]:
    """Validate a Tesseract executable and return version information."""
    candidate = Path(executable_path.strip()) if executable_path.strip() else None
    if candidate is None or not candidate.exists():
        return {
            "ok": False,
            "message": "Invalid Tesseract installation: executable not found.",
            "version": "",
        }

    try:
        result = _run_command([str(candidate), "--version"])
    except (OSError, subprocess.SubprocessError) as exc:
        logger.warning("Tesseract version check failed: %s", exc)
        return {
            "ok": False,
            "message": "Invalid Tesseract installation.",
            "version": "",
        }

    if result.returncode != 0:
        return {
            "ok": False,
            "message": "Invalid Tesseract installation.",
            "version": "",
        }

    version = result.stdout.splitlines()[0].strip() if result.stdout else "Unknown"
    return {
        "ok": True,
        "message": "Connected",
        "version": version,
    }


def detect_ollama_host(host: str = "http://localhost:11434") -> str | None:
    """Detect whether an Ollama server is available at the supplied host."""
    try:
        response = requests.get(f"{host.rstrip('/')}/api/tags", timeout=3)
        if response.status_code == 200:
            return host.rstrip("/")
    except requests.RequestException:
        return None
    return None


def _parse_ollama_list_output(output: str) -> list[str]:
    """Parse model names from `ollama list` output."""
    models: list[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("name"):
            continue
        parts = stripped.split()
        if parts:
            models.append(parts[0])
    return models


def get_ollama_models(host: str) -> list[str]:
    """Return installed Ollama models using CLI when possible, then API fallback."""
    models: list[str] = []
    try:
        result = _run_command(["ollama", "list"])
        if result.returncode == 0:
            models = _parse_ollama_list_output(result.stdout)
    except (OSError, subprocess.SubprocessError) as exc:
        logger.info("Unable to run `ollama list`: %s", exc)

    if models:
        return models

    try:
        response = requests.get(f"{host.rstrip('/')}/api/tags", timeout=5)
        response.raise_for_status()
        payload = response.json()
        return [
            model.get("name", "")
            for model in payload.get("models", [])
            if model.get("name")
        ]
    except requests.RequestException as exc:
        logger.info("Unable to fetch Ollama models from API: %s", exc)
        return []


def get_ollama_version() -> str:
    """Return the local Ollama CLI version when available."""
    try:
        result = _run_command(["ollama", "--version"])
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return (result.stdout or result.stderr).strip()


def test_ollama_connection(host: str, selected_model: str) -> dict[str, Any]:
    """Validate Ollama server availability and model presence."""
    normalized_host = host.rstrip("/")
    try:
        response = requests.get(f"{normalized_host}/api/tags", timeout=5)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        logger.warning("Ollama connection test failed: %s", exc)
        return {
            "ok": False,
            "message": "Unable to connect to Ollama.",
            "version": get_ollama_version(),
            "models": [],
        }

    models = [
        model.get("name", "")
        for model in payload.get("models", [])
        if model.get("name")
    ]
    if selected_model and selected_model not in models:
        return {
            "ok": False,
            "message": "Selected model is not installed in Ollama.",
            "version": get_ollama_version(),
            "models": models,
        }

    return {
        "ok": True,
        "message": "Ollama Connected",
        "version": get_ollama_version(),
        "models": models,
    }
