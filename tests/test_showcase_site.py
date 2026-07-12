from html.parser import HTMLParser
from pathlib import Path


class _ShowcaseParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.has_viewport = False
        self.has_main = False
        self.has_h1 = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.add(values["id"])
        if tag == "a" and "href" in values:
            self.links.append(values["href"])
        if tag == "meta" and values.get("name") == "viewport":
            self.has_viewport = True
        self.has_main |= tag == "main"
        self.has_h1 |= tag == "h1"


def test_showcase_has_accessible_structure_and_valid_local_links() -> None:
    root = Path("site")
    parser = _ShowcaseParser()
    parser.feed((root / "index.html").read_text(encoding="utf-8"))

    assert parser.has_viewport and parser.has_main and parser.has_h1
    assert {"main", "top", "problem", "system", "evidence", "decision"} <= parser.ids
    for link in parser.links:
        if link.startswith("#"):
            assert link[1:] in parser.ids
    assert (root / "styles.css").is_file()


def test_showcase_metrics_match_recorded_experiment() -> None:
    page = Path("site/index.html").read_text(encoding="utf-8")
    report = Path(
        "examples/japanese_troubleshooting_agent/results/comparison.md"
    ).read_text(encoding="utf-8")

    assert "−25.00%" in page
    assert "−21.88%" in page
    assert "| citation_coverage | 1 | 0.75 | -0.25 |" in report
    assert "| lexical_groundedness | 1 | 0.7812 | -0.2188 |" in report
