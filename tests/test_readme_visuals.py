from pathlib import Path
from xml.etree import ElementTree


README_VISUALS = (
    "docs/demo/infographics/release-gate-flow.svg",
    "docs/demo/infographics/evidence-stack.svg",
    "docs/demo/screenshots/ragops-adoption-hero.png",
    "docs/demo/screenshots/ragops-adoption-mobile.png",
    "docs/demo/screenshots/ragops-release-screen.jpg",
    "docs/demo/screenshots/ragops-limitations-screen.jpg",
)


def test_readme_visual_assets_exist_and_are_referenced() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for asset in README_VISUALS:
        path = Path(asset)
        assert path.is_file()
        assert path.stat().st_size > 0
        assert asset in readme


def test_readme_infographics_are_well_formed_accessible_svg() -> None:
    namespace = {"svg": "http://www.w3.org/2000/svg"}

    for asset in README_VISUALS[:2]:
        root = ElementTree.parse(asset).getroot()
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        assert root.attrib["role"] == "img"
        assert root.find("svg:title", namespace) is not None
        assert root.find("svg:desc", namespace) is not None


def test_readme_architecture_is_a_detailed_mermaid_release_flow() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert 'subgraph SOURCE["1 · SYSTEM UNDER TEST"]' in readme
    assert 'subgraph CORE["2 · RAGOPS LOCAL EVALUATION CORE"]' in readme
    assert 'subgraph DECIDE["3 · REGRESSION DECISION"]' in readme
    assert 'GATE{"Release gate"}' in readme
    assert 'PASS["PASS<br/>safe to continue"]' in readme
    assert 'BLOCK["BLOCK<br/>fix and re-run"]' in readme
    assert "classDef source fill:#10233f" in readme
    assert "RAG / agent application\n        │ portable traces" not in readme
