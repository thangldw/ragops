from pathlib import Path


def test_workbench_exposes_evaluation_and_team_history() -> None:
    page = Path("apps/web/index.html").read_text(encoding="utf-8")

    assert 'id="scenario"' in page
    assert 'id="responses"' in page
    assert 'id="runs"' in page
    assert "fetch('/v1/evaluate'" in page
    assert "fetch(`/v1/runs?limit=" in page
    assert "RAGOPS_STORE" in page
