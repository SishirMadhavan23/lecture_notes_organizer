# Feature Specification: Multilingual Support

## Overview
Add complete multilingual support for English, Telugu, and Hindi languages throughout the Lecture Notes Organizer application. All user-facing strings must use a dictionary-based translation system with a `t()` helper function.

## Requirements
1. Create translations directory with en.json, te.json, hi.json
2. Create translation helper module with `t()` function
3. Add language selector in sidebar
4. Translate all UI elements: titles, buttons, labels, placeholders, warnings, errors, success messages, navigation, footers, help text, tooltips
5. Language preference persists via Streamlit session state
6. Support dot-notation for translation keys
7. Fall back to English if translation key not found in selected language
8. No hardcoded user-facing strings in UI components

## Acceptance Criteria
1. Language selector appears in sidebar
2. Switching language immediately updates all visible text
3. Language preference persists across page navigation
4. All pages show translated content: Upload, View Notes, Flashcards, Search, Settings, System Status
5. All components show translated content: sidebar, dashboard, note cards, page headers, footer
6. English, Telugu, and Hindi translations are complete
7. Missing translations gracefully fall back to English
8. AI response text is passed through translation pipeline
9. No hardcoded strings remain in UI components
10. Tests cover translation helper, language switching, and session persistence

## Implementation Plan
1. Create `src/utils/translations.py` with `t()`, `get_language()`, `set_language()`, `render_language_selector()`
2. Create `translations/en.json`, `translations/te.json`, `translations/hi.json` with complete translations
3. Update `src/ui/components/sidebar.py` to include language selector and use `t()` for all strings
4. Update all page files to use `t()` for user-facing strings
5. Update all component files to use `t()` for user-facing strings
6. Update `src/app.py` to initialize language state
7. Write tests in `tests/test_utils/` for translation functionality

## Testing Strategy
1. Unit tests for `t()` function with various key formats
2. Unit tests for language switching and persistence
3. Unit tests for fallback behavior when key is missing
4. Integration tests for UI rendering with different languages
5. Mock translation files for testing