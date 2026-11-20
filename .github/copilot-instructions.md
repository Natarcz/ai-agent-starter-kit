# Copilot Instructions

This repository uses `CLAUDE.md` as the single source of truth for engineering
rules, agent workflow and project conventions. Read it first — it applies to
every change regardless of the agent tool.

Multi-agent coordination rules live in `AGENTS.md`.

Key non-negotiables (full list in CLAUDE.md):

- Strict typing: pydantic models / TypedDict at API boundaries. No `Any`, no untyped `dict`.
- No empty `except`/`catch`; network calls need timeout + retry with backoff.
- Secrets only via env vars — never hardcode or log them.
- New business logic ships with edge-case unit tests in the same change.
- Do not modify `.github/workflows/` or deploy configs without an explicit request.
