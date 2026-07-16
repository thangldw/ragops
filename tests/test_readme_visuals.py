from pathlib import Path
from xml.etree import ElementTree


README_VISUALS = (
    "docs/demo/ragops-demo.gif",
    "docs/demo/infographics/release-gate-flow.svg",
    "docs/demo/infographics/evidence-stack.svg",
)


def test_readme_visual_assets_exist_and_are_referenced() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for asset in README_VISUALS:
        path = Path(asset)
        assert path.is_file()
        assert path.stat().st_size > 0
        assert asset in readme

    pr_comment = Path("docs/demo/ragops-pr-comment.png")
    assert pr_comment.is_file()
    assert pr_comment.stat().st_size > 0
    assert str(pr_comment) in readme


def test_readme_infographics_are_well_formed_accessible_svg() -> None:
    namespace = {"svg": "http://www.w3.org/2000/svg"}

    for asset in README_VISUALS[1:]:
        root = ElementTree.parse(asset).getroot()
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        assert root.attrib["role"] == "img"
        assert root.find("svg:title", namespace) is not None
        assert root.find("svg:desc", namespace) is not None


def test_readme_infographics_use_local_system_fonts() -> None:
    for asset in README_VISUALS[1:]:
        svg = Path(asset).read_text(encoding="utf-8").lower()
        assert "system-ui" in svg
        assert "inter" not in svg
        assert "fonts.googleapis" not in svg


def test_readme_architecture_is_a_board_style_mermaid_release_flow() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert 'subgraph CORE["LOCAL OPEN-SOURCE CORE"]' in readme
    assert 'GATE{"Release gate"}' in readme
    assert 'PASS["PASS<br/>continue"]' in readme
    assert 'BLOCK["BLOCK<br/>fix and re-run"]' in readme
    assert "classDef source fill:#bfe8ff" in readme
    assert "classDef core fill:#ffdc7c" in readme
    assert "classDef report fill:#d8ceff" in readme
    assert "classDef pass fill:#aee8c9" in readme
    assert "classDef block fill:#ffc0dd" in readme
    assert '"edgeLabelBackground":"#fffef9"' in readme
    assert '"fontFamily":"system-ui' in readme
    assert "RAG / agent application\n        │ portable traces" not in readme
