# Configuration Reference for OpsAI

This document describes all environment variables, toggles, and secrets used in the system. Update this file as new configuration options are added.

## Core Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for LLM operations.
- `GOOGLE_API_KEY`: Google API key (if used).
- `DATABASE_URL`: Database connection string (e.g., `sqlite:///opsai.db`).

## Integration Driver Toggles

- `OPSAI_DRIVER_COMMUNICATION_ENABLED`: Enable/disable Gmail driver (`true`/`false`).
- `OPSAI_DRIVER_GMAIL_USER`: Gmail username for email driver.
- `OPSAI_DRIVER_GMAIL_PASS`: Gmail app password for email driver.
- `OPSAI_DRIVER_TASK_CREATION_ENABLED`: Enable/disable Linear driver (`true`/`false`).
- `OPSAI_DRIVER_LINEAR_KEY`: Linear API key.
- `OPSAI_DRIVER_LINEAR_TEAM_ID`: Linear team ID.

## Demo & Fallback

- `OPSAI_ALLOW_MISSING_TO`: Allow fallback to demo email if recipient is missing (`true`/`false`).
- `OPSAI_DEMO_EMAIL`: Demo email address for fallback.

## Logging

- `OPSAI_LOG_LEVEL`: Log level (e.g., `INFO`, `DEBUG`).
- `OPSAI_LOG_FORMAT`: Log format (`json` or `text`).

## Other

- `OPSAI_SKIP_DRIVER_CHECKS`: Skip driver health checks on startup (`true`/`false`).

---

**Location:** `.env` file at project root. See `.env.example` for template.

**Security:** Never commit real secrets to version control. Use `.env.example` for safe sharing.
