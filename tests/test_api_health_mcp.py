import pytest

from mcp_tools.api_health_mcp import _is_blocked_host


@pytest.mark.parametrize("url", [
    "http://169.254.169.254/latest/meta-data",
    "http://127.0.0.1:8080/admin",
    "http://10.0.0.5/internal",
    "http://192.168.1.1/router",
    "http://[::1]/",
    "http://localhost/health",
    "http://service.local/api",
    "http://db.internal/query",
    "ftp://example.com/file",
    "file:///etc/passwd",
])
def test_blocked_urls(url):
    assert _is_blocked_host(url) is not None


@pytest.mark.parametrize("url", [
    "https://api.example.com/health",
    "https://8.8.8.8/dns",
    "http://93.184.216.34/",
])
def test_allowed_urls(url):
    assert _is_blocked_host(url) is None
