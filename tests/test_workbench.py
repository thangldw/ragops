from pathlib import Path


def test_workbench_exposes_evaluation_and_team_history() -> None:
    page = Path("apps/web/index.html").read_text(encoding="utf-8")

    assert 'id="scenario"' in page
    assert 'id="responses"' in page
    assert 'id="api-key" type="password"' in page
    assert "'x-api-key':apiKey.value" in page
    assert "localStorage" not in page
    assert 'id="runs"' in page
    assert "fetch('/v1/evaluate'" in page
    assert "fetch(`/v1/runs?limit=" in page
    assert "RAGOPS_STORE" in page
    assert "NOT EVALUATED" in page
    assert "metrics.innerHTML=''" in page
    assert "gates.innerHTML='<li>Not evaluated</li>'" in page
