from pathlib import Path


def test_readme_is_trilingual_and_uses_board_style_mermaid() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for language in ("English", "Tiếng Việt", "日本語"):
        assert language in readme
    assert "```mermaid" in readme
    for color in ("#FFF4A3", "#D9EAFD", "#E9DDF7", "#DDF5E3", "#FFE1E6"):
        assert color in readme
