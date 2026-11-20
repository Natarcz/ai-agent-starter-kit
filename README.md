# AI-Assisted Engineering Starter Kit

Переиспользуемый воркспейс с конфигурациями, правилами и инструментами для оркестрации ИИ-агентов (Claude Code / Cursor / Codex) в коммерческой разработке.

## Что включено в шаблон:

1. **Архитектурные гардрейлы (`CLAUDE.md`):** Проверяемые правила типизации, обработки ошибок, безопасности, мобильной специфики (main thread, батарея, offline-first) и контроля стоимости LLM-токенов. Плюс Project Map, команды проекта и Agent Workflow с Definition of Done.
2. **Мультиагентный пайплайн (`AGENTS.md`):** Правила координации субагентов: когда оркестрировать, роли (Planner → Implementer → QA/Security в две фазы), протокол параллелизации, самодостаточное делегирование, верификация результатов и эскалация.
3. **Команды, субагенты и скиллы (`.claude/`):** `/review-pr`, `/plan`, `/test-edge-cases` — slash-команды; `.claude/agents/` — файлы субагентов (planner / implementer / qa-security) для оркестрации; `.claude/skills/api-debug` — скилл отладки API через MCP; `.claude/settings.json` — deny-правила для protected paths.
4. **AI-ревью в CI (`.github/workflows/ai-review.yml` + `scripts/ai_review.py`):** Рабочий pipeline: скрипт читает `git diff`, применяет правила из `CLAUDE.md`/`AGENTS.md` через Anthropic API и постит структурированный отчёт `[CRITICAL]/[IMPROVEMENT]/[OK]` комментарием в PR. `[CRITICAL]` блокирует мерж (красный чек), usage токенов логируется.
5. **Кастомный MCP-сервер (`mcp_tools/api_health_mcp.py` + `.mcp.json`):** Инструмент на базе `FastMCP` с типизированным контрактом `ApiHealthReport`, SSRF-фильтром и bounded retry — агент сам проверяет статус, latency и заголовки API при отладке. `.mcp.json` подключает сервер к Claude Code одной командой `claude mcp list`.
6. **Cursor-правила (`.cursor/rules/*.mdc`):** Проектные правила для Cursor Agent в актуальном формате (`.cursorrules` deprecated): always-on гардрейлы + scoped-правила для `mcp_tools/`.
7. **Тесты и CI для самого шаблона (`tests/`, `.github/workflows/tests.yml`):** Unit-тесты на `ai_review.py` и SSRF-фильтр MCP; workflow прогоняет `pytest` на каждый PR — kit проверяет сам себя.

## Быстрый старт

Требуется **Python 3.11+** (`.python-version` подсказывает pyenv/uv).
`.venv` не версионируется — создание venv нужно один раз; если `.venv` уже
есть, пропустите первые две строки и просто поставьте зависимости.

```bash
# pip
python3.11 -m venv .venv && source .venv/bin/activate   # только если .venv нет
pip install -e ".[dev]"

# или uv (быстрее):
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -e ".[dev]"

api-health-mcp        # запуск MCP-сервера (entrypoint из pyproject.toml)
pytest tests/         # unit-тесты скриптов
```

Для LLM-вызовов скопируйте `.env.example` в `.env` и заполните `ANTHROPIC_API_KEY` (`.env` в `.gitignore`).

MCP-сервер уже зарегистрирован в `.mcp.json` и `.cursor/mcp.json` — Claude Code
и Cursor подхватят его автоматически, `claude mcp add` не нужен. Для запуска
без установки пакета: `python mcp_tools/api_health_mcp.py`.

Для CI-ревью добавьте секрет `ANTHROPIC_API_KEY` в Settings → Secrets репозитория (без него ревью gracefully пропускается). Модель ревьюера переопределяется переменной `REVIEW_MODEL` (дефолт — `claude-haiku-4-5`).

Скопируйте `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.cursor/` в корень целевого проекта и адаптируйте команды под его стек.
