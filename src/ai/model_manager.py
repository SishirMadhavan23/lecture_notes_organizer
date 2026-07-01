# SPDX-License-Identifier: GPL-3.0-or-later
"""Local LLM model management through Ollama."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

import requests

from src.ai.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.utils.config import load_config
from src.utils.exceptions import AIError, ModelNotFoundError

logger = logging.getLogger(__name__)


def is_ollama_available(base_url: str | None = None) -> bool:
    """Check if Ollama service is running."""
    resolved_base_url = base_url or load_config().ollama_base_url
    try:
        resp = requests.get(f"{resolved_base_url}/api/tags", timeout=3)
        return bool(resp.status_code == 200)
    except (requests.ConnectionError, requests.Timeout):
        return False


def is_llama_cpp_available(model_path: str | None = None) -> bool:
    """Check if llama.cpp model file exists."""
    if not model_path:
        return False
    import os

    return os.path.isfile(model_path)


def _normalize_question_text(item: Any) -> str:
    """Return a plain-text question from varied model output formats."""
    if isinstance(item, dict):
        return str(item.get("text") or item.get("question") or "").strip()
    return str(item).strip()


def _normalize_flashcards(items: Any) -> list[dict[str, str]]:
    """Normalize model flashcards into a stable storage format."""
    normalized: list[dict[str, str]] = []
    if not isinstance(items, list):
        return normalized

    for item in items:
        if not isinstance(item, dict):
            continue
        front = str(
            item.get("front") or item.get("question") or item.get("prompt") or ""
        ).strip()
        back = str(
            item.get("back") or item.get("answer") or item.get("response") or ""
        ).strip()
        if front or back:
            normalized.append(
                {
                    "type": "flashcard",
                    "front": front,
                    "back": back,
                }
            )
    return normalized


def _pack_study_items(result: dict[str, Any]) -> dict[str, Any]:
    """Persist questions and flashcards in the existing storage field."""
    questions = []
    for item in result.get("possible_exam_questions", []):
        text = _normalize_question_text(item)
        if text:
            questions.append({"type": "question", "text": text})

    flashcards = _normalize_flashcards(result.get("flashcards", []))
    result["possible_exam_questions"] = questions + flashcards
    result["flashcards"] = flashcards
    return result


def generate_structured_notes(
    text: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate structured notes from text using local LLM.

    Tries local Ollama first, then uses deterministic offline fallback output.

    Args:
        text: Cleaned lecture text
        config: Model configuration overrides

    Returns:
        Dict matching output schema
    """
    saved_config = load_config()
    cfg = {
        "llm_backend": saved_config.llm_backend,
        "ollama_base_url": saved_config.ollama_base_url,
        "ollama_model": saved_config.ollama_model,
        "temperature": saved_config.temperature,
        "context_length": saved_config.context_length,
        **(config or {}),
    }
    if is_ollama_available(cfg.get("ollama_base_url", "http://localhost:11434")):
        try:
            return _query_ollama(text, cfg)
        except Exception as exc:
            logger.warning(f"Ollama failed: {exc}")

    return _generate_fallback(text, cfg)


def _query_ollama(text: str, config: dict[str, Any]) -> dict[str, Any]:
    """Query Ollama API for structured note generation."""
    base_url = config.get("ollama_base_url", "http://localhost:11434")
    model = config.get("ollama_model", "phi3:mini")
    prompt = USER_PROMPT_TEMPLATE.format(text=text[:3000])
    payload = {
        "model": model,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": config.get("temperature", 0.1),
            "num_ctx": config.get("context_length", 4096),
        },
    }
    timeout = config.get("timeout", 120)

    resp = requests.post(
        f"{base_url}/api/generate",
        json=payload,
        timeout=timeout,
    )
    if resp.status_code == 404:
        raise ModelNotFoundError(f"Model '{model}' not found. Run: ollama pull {model}")
    if resp.status_code != 200:
        raise AIError(f"Ollama error: {resp.status_code}")
    return _parse_json_response(resp.json().get("response", ""), text)


def _parse_json_response(response_text: str, original_text: str) -> dict[str, Any]:
    """Parse JSON from LLM response with fallback."""
    import re

    json_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        response_text,
        re.DOTALL,
    )

    if not json_match:
        json_match = re.search(
            r"\{[^{}]*\"title\"[^{}]*\}",
            response_text,
            re.DOTALL,
        )

    if json_match:
        try:
            result = json.loads(json_match.group(1))
            result["created_at"] = datetime.now(UTC).isoformat()
            return _pack_study_items(result)
        except (json.JSONDecodeError, KeyError):
            pass

    return _generate_fallback(original_text, {})


def _generate_fallback(text: str, config: dict[str, Any]) -> dict[str, Any]:
    """Generate structured data fallback when AI is unavailable."""
    from src.preprocessing.text_cleaner import extract_title

    logger.info("Using fallback generation (no AI model available)")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    words = text.split()
    word_count = len(words)
    avg_word_len = sum(len(w) for w in words) / max(word_count, 1)

    if avg_word_len < 5 and word_count < 500:
        difficulty = "Beginner"
    elif avg_word_len < 7 or word_count < 2000:
        difficulty = "Intermediate"
    else:
        difficulty = "Advanced"

    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "from",
    }
    words_lower = [
        w.lower().strip(".,;:!?()[]{}'\"") for w in words if w.isalpha() and len(w) > 3
    ]
    freq: dict[str, int] = {}
    for w in words_lower:
        if w not in stop_words:
            freq[w] = freq.get(w, 0) + 1
    sorted_w = sorted(freq.items(), key=lambda x: -x[1])
    keywords = [w for w, _ in sorted_w[:15]]
    important_points = [
        lines[i] for i in range(min(5, len(lines))) if len(lines[i]) > 20
    ]
    exam_questions = [
        {"type": "question", "text": f"What is the significance of: {point[:80]}?"}
        for point in important_points[:3]
    ]
    flashcards = []
    for index, point in enumerate(important_points[:4], start=1):
        topic_hint = (
            keywords[index - 1] if index - 1 < len(keywords) else "this lecture"
        )
        flashcards.append(
            {
                "type": "flashcard",
                "front": f"What should you remember about {topic_hint}?",
                "back": point,
            }
        )

    return {
        "title": extract_title(text),
        "subject": "General",
        "topics": ["Lecture Content"],
        "keywords": keywords,
        "summary": text[:500].strip() + ("..." if len(text) > 500 else ""),
        "important_points": important_points,
        "possible_exam_questions": exam_questions + flashcards,
        "flashcards": flashcards,
        "difficulty": difficulty,
        "created_at": datetime.now(UTC).isoformat(),
    }
