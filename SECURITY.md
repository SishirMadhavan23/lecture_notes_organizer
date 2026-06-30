# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.3.x   | :white_check_mark: |

## Reporting a Vulnerability

This is an offline desktop application with no network connectivity.
However, if you discover a security vulnerability, please report it by
opening an issue in the GitLab repository.

Do NOT disclose security vulnerabilities publicly until they have been
addressed by the maintainers.

## Security Considerations

- The application makes no external network calls
- User documents are processed only in memory
- SQLite database is stored locally with no network exposure
- AI models run locally via Ollama
- No user data is ever transmitted