import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_marketplace_lists_the_plugin_that_lives_in_this_repository():
    marketplace = _json(".claude-plugin/marketplace.json")
    manifest = _json("plugins/ragops/.claude-plugin/plugin.json")
    entries = marketplace["plugins"]
    assert [entry["name"] for entry in entries] == [manifest["name"]] == ["ragops"]
    assert entries[0]["source"] == "./plugins/ragops" and marketplace["name"] == "ragops"
    assert entries[0]["license"] == manifest["license"] == "Apache-2.0"
    assert "version" not in entries[0]  # the version lives only in plugin.json, so bumps cannot drift


def test_plugin_version_matches_the_package():
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    assert _json("plugins/ragops/.claude-plugin/plugin.json")["version"] == version


def test_claude_plugin_folder_holds_only_directory_safe_files():
    allowed = {".md", ".json", ".png"}
    files = [p for p in (ROOT / "plugins/ragops").rglob("*") if p.is_file()]
    assert files
    for path in files:
        assert path.suffix in allowed or path.name == "LICENSE", path
        assert not path.read_bytes().startswith(b"#!"), path
    shipped = sorted(path.parent.name for path in (ROOT / "plugins/ragops/skills").glob("*/SKILL.md"))
    assert shipped == ["evaluate-ai-release"]
    maintainer = sorted(path.parent.name for path in (ROOT / ".claude/skills").glob("*/SKILL.md"))
    assert maintainer == ["ragops-feature", "ragops-presentation", "ragops-release"]


def test_skill_documents_every_new_command_and_its_guardrails():
    skill = (ROOT / "plugins/ragops/skills/evaluate-ai-release/SKILL.md").read_text(encoding="utf-8")
    commands = (ROOT / "plugins/ragops/skills/evaluate-ai-release/references/commands.md").read_text(encoding="utf-8")
    for command in ("policy-suggest", "mine", "counterfactual", "stability", "triage", "calibrate"):
        assert f"`{command}`" in skill or f"`{command} " in skill
        assert command in commands
    assert "INCONCLUSIVE" in skill and "answer-command" in skill and "Only the toy demo has been measured" in skill
    assert skill.startswith("---\nname: evaluate-ai-release\n")


def test_readme_has_the_marketplace_install_line():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "/plugin marketplace add thangldw/ragops" in readme
    assert "/plugin install ragops --marketplace thangldw/ragops" in readme
