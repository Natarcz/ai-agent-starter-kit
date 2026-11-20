import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.ai_review import collect_rules, has_critical, truncate_diff


def test_truncate_diff_under_limit():
    diff = "a" * 100
    assert truncate_diff(diff, 200) == diff


def test_truncate_diff_over_limit():
    diff = "a" * 300
    out = truncate_diff(diff, 100)
    assert out.startswith("a" * 100)
    assert "обрезан" in out


def test_has_critical_finding_line():
    report = "## AI Review\n- [CRITICAL] app.py:10 — утечка токена"
    assert has_critical(report)


def test_has_critical_ignores_inline_mention():
    report = "## AI Review\n- [OK] маркер [CRITICAL] в коде обработан корректно"
    assert not has_critical(report)


def test_has_critical_ignores_prose():
    assert not has_critical("## AI Review\nНет существенных замечаний.")


def test_collect_rules_respects_cap():
    rules = collect_rules(max_chars=200)
    assert len(rules) < 200 + 200  # заголовки файлов добавляют overhead
    assert "обрезан" in rules or len(rules) <= 400


def test_collect_rules_includes_project_rules():
    rules = collect_rules()
    assert "CLAUDE.md" in rules
    assert "Engineering Rules" in rules
