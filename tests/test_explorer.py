import base64
import hashlib
import re
from pathlib import Path

from ragops.cli import main
from ragops.evaluators import unsupported_spans
from ragops.explorer import SCRIPT

DEMO = Path("examples/customer_support_demo")


def test_unsupported_spans_mark_only_words_missing_from_evidence() -> None:
    answer = "Refunds take 30 days via wire"
    spans = unsupported_spans(answer, ("Refunds take 5 days",))
    marked = [answer[a:b] for a, b in spans]
    assert "30" in marked and "wire" in marked and "Refunds" not in marked


def test_unsupported_spans_handle_cjk_and_empty() -> None:
    assert unsupported_spans("", ("x",)) == []
    assert unsupported_spans("返金は30日", ("返金は5日",)) != []


def test_explorer_report_is_self_contained_and_escapes_content(monkeypatch, tmp_path) -> None:
    output = tmp_path / "explorer.html"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops", "compare",
            "--scenario", str(DEMO / "scenario.json"),
            "--baseline", str(DEMO / "output/baseline.json"),
            "--candidate", str(DEMO / "output/candidate.json"),
            "--format", "explorer", "--output", str(output),
        ],
    )
    assert main() == 2
    page = output.read_text(encoding="utf-8")
    digest = base64.b64encode(hashlib.sha256(SCRIPT.encode()).digest()).decode()
    assert f"script-src 'sha256-{digest}'" in page
    assert "default-src 'none'" in page
    assert not re.search(r"(src|href)=[\"']https?://", page)
    assert page.count("<script") == 1 and "innerHTML" not in page
    assert 'id="f-category"' in page and "<mark>" in page
