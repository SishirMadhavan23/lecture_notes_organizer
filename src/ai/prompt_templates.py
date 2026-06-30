# SPDX-License-Identifier: GPL-3.0-or-later
"""Prompt templates for LLM interactions."""

SYSTEM_PROMPT = (
    "You are a knowledgeable lecture note analyzer. Your task is to "
    "extract structured information from lecture notes and return it "
    "as valid JSON. Focus on accuracy and completeness."
)

USER_PROMPT_TEMPLATE = """Analyze the following lecture notes and return a JSON object with these fields:
- title: A concise title for this lecture
- subject: The academic subject area
- topics: Array of main topics covered (3-8 items)
- keywords: Array of important keywords (5-15 items)
- summary: A 3-5 sentence summary of the content
- important_points: Array of key takeaways (3-6 items)
- possible_exam_questions: Array of potential exam questions (2-5 items)
- flashcards: Array of 3-6 objects with "front" and "back" fields for offline study
- difficulty: One of "Beginner", "Intermediate", or "Advanced"
- created_at: Current date in ISO 8601 format

Return ONLY valid JSON without any additional text.

Lecture notes:
{text}
"""
