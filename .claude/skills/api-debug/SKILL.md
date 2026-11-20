---
name: api-debug
description: Debug client-server integration issues — verifies API availability, latency and response shape using the api-health MCP tool before touching client code.
---

# API Debug

Когда клиентская часть «не работает» с бэкендом — сначала проверь API, а не код клиента.

## Порядок

1. **Health-check эндпоинта** — вызови MCP-инструмент `inspect_api_endpoint`
   с URL и методом. Проверь `ok`, `status_code`, `latency_ms`, `content_type`.
2. **Если `ok: false`** — проблема на бэкенде/сети, не в клиенте. Зафиксируй
   `error` и эскалируй.
3. **Если 5xx/таймаут** — инструмент уже ретраил; проверь `body_preview`
   на детали ошибки.
4. **Только потом** смотри клиентский код: соответствие контракта
   (поля, типы), обработку ошибок, main-thread вызовы.

## Правила

- Не модифицируй клиентский код, пока health-check не подтвердил,
  что API отвечает корректно.
- `body_preview` обрезан до 500 символов — для полного ответа используй
  прямой запрос, а не MCP-инструмент.
