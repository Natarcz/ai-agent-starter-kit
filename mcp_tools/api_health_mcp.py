from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from urllib.parse import urlparse
import asyncio
import ipaddress
import time

import httpx

mcp = FastMCP("ApiContractInspector")

MAX_ATTEMPTS = 2
RETRYABLE_STATUS = {408, 429, 500, 502, 503}
ALLOWED_METHODS = {"GET", "HEAD", "OPTIONS"}
MAX_BODY_BYTES = 64 * 1024  # читаем с лимитом — не грузим многомегабайтные ответы в память
BODY_PREVIEW_CHARS = 500


class ApiHealthReport(BaseModel):
    """Typed contract for API health checks — agents get a stable schema, not a raw dict."""

    ok: bool
    status_code: int | None = None
    latency_ms: float | None = None
    content_type: str = "unknown"
    body_preview: str | None = None
    error: str | None = None


def _is_blocked_host(url: str) -> str | None:
    """SSRF-фильтр: блокируем не-http(s) схемы, IP-литералы из private/loopback
    диапазонов и локальные имена. DNS-имена не резолвим (rebinding остаётся
    за рамками — для health-check-инструмента это приемлемый компромисс)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return f"scheme '{parsed.scheme}' not allowed"

    host = parsed.hostname or ""
    if not host:
        return "empty host"

    # IP-литерал — проверяем напрямую через ipaddress.
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved \
                or ip.is_multicast or ip.is_unspecified:
            return f"private/reserved IP {host} blocked"
        return None
    except ValueError:
        pass  # не IP — идём проверять имя

    lowered = host.lower().rstrip(".")
    if lowered == "localhost" or lowered.endswith((".localhost", ".local", ".internal", ".lan")):
        return f"local hostname '{host}' blocked"
    return None


@mcp.tool()
async def inspect_api_endpoint(url: str, method: str = "GET") -> ApiHealthReport:
    """
    Проверяет доступность, задержку ответа (latency) и заголовки API-эндпоинта.
    Используется агентом при интеграции клиентской части с бэкендом.
    Разрешены только GET/HEAD/OPTIONS и публичные http/https хосты.
    """
    method = method.upper()
    if method not in ALLOWED_METHODS:
        return ApiHealthReport(ok=False, error=f"method '{method}' not allowed")

    blocked = _is_blocked_host(url)
    if blocked:
        return ApiHealthReport(ok=False, error=blocked)

    last_error: str | None = None
    # follow_redirects=False: иначе публичный URL может 302-редиректить на
    # приватный адрес в обход _is_blocked_host. 3xx вернётся как обычный ответ.
    async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
        for attempt in range(MAX_ATTEMPTS):
            try:
                started = time.perf_counter()
                async with client.stream(method, url) as response:
                    # Читаем тело с лимитом: большие ответы не попадают в память целиком.
                    body_buf = bytearray()
                    async for chunk in response.aiter_bytes(8192):
                        body_buf += chunk
                        if len(body_buf) >= MAX_BODY_BYTES:
                            break
                    latency_ms = round((time.perf_counter() - started) * 1000, 2)

                    if response.status_code in RETRYABLE_STATUS \
                            and attempt < MAX_ATTEMPTS - 1:
                        await asyncio.sleep(0.3 * (2 ** attempt))
                        continue

                    body = bytes(body_buf[:MAX_BODY_BYTES])
                    preview = body.decode("utf-8", errors="replace")[:BODY_PREVIEW_CHARS] \
                        if body else None
                    return ApiHealthReport(
                        ok=response.is_success,
                        status_code=response.status_code,
                        latency_ms=latency_ms,
                        content_type=response.headers.get("content-type", "unknown"),
                        body_preview=preview,
                    )
            except httpx.HTTPError as e:
                last_error = f"{type(e).__name__}: {e}"
                if attempt < MAX_ATTEMPTS - 1:
                    await asyncio.sleep(0.3 * (2 ** attempt))
    return ApiHealthReport(ok=False, error=last_error)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
