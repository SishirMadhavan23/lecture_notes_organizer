# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for text cleaning and normalization."""

from src.preprocessing.text_cleaner import clean_text, extract_title, split_into_chunks


class TestCleanText:
    """Test text cleaning functions."""

    def test_clean_text_removes_html(self):
        """Test that HTML tags are stripped."""
        text = "<h1>Title</h1><p>Paragraph with <b>bold</b> text.</p>"
        result = clean_text(text, remove_html=True, normalize_unicode=False)
        assert "<h1>" not in result
        assert "<p>" not in result
        assert "Title" in result
        assert "Paragraph" in result

    def test_clean_text_collapses_whitespace(self):
        """Test that extra whitespace is collapsed."""
        text = "Word1    Word2\n\n\n\nWord3"
        result = clean_text(text, remove_html=False, normalize_unicode=False)
        assert "    " not in result
        assert "\n\n\n" not in result

    def test_clean_text_handles_empty(self):
        """Test that empty text returns empty string."""
        assert clean_text("") == ""
        assert clean_text(None) == ""

    def test_clean_text_preserves_content(self):
        """Test that meaningful content is preserved."""
        text = "  Hello, this is a test.  "
        result = clean_text(text, remove_html=False, normalize_unicode=False)
        assert "Hello, this is a test." in result

    def test_extract_title_from_heading(self):
        """Test title extraction from markdown heading."""
        text = "# Introduction to Machine Learning\n\nContent here."
        title = extract_title(text)
        assert title == "Introduction to Machine Learning"

    def test_extract_title_from_first_line(self):
        """Test title extraction from first line."""
        text = "My Lecture Notes\n\nSome content."
        title = extract_title(text)
        assert title == "My Lecture Notes"

    def test_extract_title_from_filename(self):
        """Test title extraction from filename when text has no title."""
        # First line is very long (>200 chars) so title falls back to filename
        text = (
            "This is a very long first line that exceeds two hundred "
            "characters by a significant margin to force the title "
            "extraction function to skip it and fall back to the "
            "filename-based title extraction mechanism instead of using "
            "this as the title " * 2
        )
        title = extract_title(text, filename="deep_learning_basics.pdf")
        assert "Deep Learning Basics" in title

    def test_extract_title_fallback(self):
        """Test that untitled documents get a fallback title."""
        title = extract_title("", filename=None)
        assert title == "Untitled"

    def test_split_into_chunks_small_text(self):
        """Test that small text is not split."""
        text = "Short text."
        chunks = split_into_chunks(text, max_chars=1000)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_split_into_chunks_large_text(self):
        """Test that large text is split into multiple chunks."""
        text = "Word " * 500
        chunks = split_into_chunks(text, max_chars=200)
        assert len(chunks) > 1

    def test_split_into_chunks_empty(self):
        """Test that empty text returns empty list."""
        assert not split_into_chunks("")
        assert not split_into_chunks(None)
