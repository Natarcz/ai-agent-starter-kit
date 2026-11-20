import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_mcp_configs_define_same_servers():
    """.mcp.json (Claude Code) и .cursor/mcp.json (Cursor) должны
    регистрировать одинаковый набор MCP-серверов — иначе агент в одном
    из инструментов не увидит сервер."""
    claude = _load(".mcp.json")["mcpServers"]
    cursor = _load(".cursor/mcp.json")["mcpServers"]

    assert set(claude) == set(cursor), (
        f"Расхождение серверов: только в .mcp.json: {set(claude) - set(cursor)}, "
        f"только в .cursor/mcp.json: {set(cursor) - set(claude)}"
    )


def test_mcp_server_entries_have_command():
    for config_path in (".mcp.json", ".cursor/mcp.json"):
        servers = _load(config_path)["mcpServers"]
        for name, cfg in servers.items():
            assert "command" in cfg, f"{config_path}: сервер '{name}' без command"
