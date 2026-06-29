# SPDX-License-Identifier: GPL-3.0-or-later
"""Text cleaning and normalization utilities."""

import re
from pathlib import Path
from typing import List, Optional


def clean_text(
    text: str,
    remove_html: bool = True,
    normalize_unicode: bool = True,
    collapse_whitespace: bool = True,
) -> str:
    """Clean and normalize extracted text."""
    if not text:
        return ""
    result = text
    if remove_html:
        result = re.sub(r"<[^>]+>", " ", result)
    if normalize_unicode:
        try:
            import unidecode
            result = unidecode.unidecode(result)
        except ImportError:
            pass
    if collapse_whitespace:
        result = re.sub(r"\r\n", "\n", result)
        result = re.sub(r"\r", "\n", result)
        result = re.sub(r"\n{3,}", "\n\n", result)
        result = re.sub(r" {2,}", " ", result)
        result = re.sub(r"\t", " ", result)
    return result.strip()


def extract_title(text: str, filename: Optional[str] = None) -> str:
    """Extract title from text or filename."""
    if not text:
        return _title_from_filename(filename) if filename else "Untitled"
    heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if heading:
        return heading.group(1).strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines and len(lines[0]) < 200:
        return lines[0]
    if filename:
        return _title_from_filename(filename)
    return "Untitled"


def _title_from_filename(filename: str) -> str:
    name = Path(filename).stem
    name = re.sub(r"[_-]", " ", name)
    return name.strip().title()


def split_into_chunks(
    text: str, max_chars: int = 2000, overlap: int = 100
) -> List[str]:
    """Split text into overlapping chunks for LLM processing."""
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + max_chars, text_len)
        if end < text_len:
            search_start = max(end - 200, start)
            sentence_end = max(
                text.rfind(". ", search_start, end),
                text.rfind("?\n", search_start, end),
                text.rfind("!\n", search_start, end),
                text.rfind("\n\n", search_start, end),
            )
            if sentence_end > search_start:
                end = sentence_end + 1
        chunks.append(text[start:end].strip())
        start = end - overlap if end < text_len else text_len
    return chunks
