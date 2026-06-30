# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for prompt templates."""

from src.ai.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class TestPromptTemplates:
    """Test prompt template structure."""

    def test_system_prompt_exists(self):
        """Test that system prompt is defined."""
        assert SYSTEM_PROMPT is not None
        assert len(SYSTEM_PROMPT) > 50
        assert "lecture note analyzer" in SYSTEM_PROMPT.lower()

    def test_user_prompt_contains_required_fields(self):
        """Test that user prompt template includes all required fields."""
        fields = [
            "title",
            "subject",
            "topics",
            "keywords",
            "summary",
            "important_points",
            "possible_exam_questions",
            "difficulty",
            "created_at",
        ]
        for field in fields:
            assert field in USER_PROMPT_TEMPLATE, f"Missing field: {field}"

    def test_user_prompt_has_text_placeholder(self):
        """Test that user prompt has {text} placeholder."""
        assert "{text}" in USER_PROMPT_TEMPLATE

    def test_user_prompt_formatting(self):
        """Test that user prompt formats correctly."""
        test_text = "This is a test lecture."
        formatted = USER_PROMPT_TEMPLATE.format(text=test_text)
        assert test_text in formatted
        assert "{text}" not in formatted
