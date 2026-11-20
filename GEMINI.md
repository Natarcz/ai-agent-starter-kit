# Gemini Instructions

Read `CLAUDE.md` first — it is the single source of truth for engineering
rules, agent workflow and project conventions. `AGENTS.md` holds
multi-agent coordination rules.

Non-negotiables: strict typing at API boundaries, no empty exception
handlers, secrets via env only, edge-case tests with new logic, no changes
to `.github/workflows/` or deploy configs without an explicit request.
