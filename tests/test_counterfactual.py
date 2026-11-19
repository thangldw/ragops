import json
import sys
from pathlib import Path

import pytest

from ragops.cli import main
from ragops.counterfactual import (
    CommandAnswerer,
    _changed_number,
    _check_remove_support,
    _check_swap_number,
    _jaccard,
    _support_indexes,
    counterfactual_markdown,
    run_counterfactual,
)
from ragops.loader import ContractError
from ragops.models import EvalCase, RecordedResponse

DEMO = Path("examples/counterfactual_demo")


class Fake:
    """Answerer stand-in that records what it was asked."""

    def __init__(self, reply):
        self.reply, self.calls = reply, []

    def answer(self, case_id, question, evidence):
        self.calls.append((case_id, question, list(evidence)))
        return self.reply(case_id, question, evidence) if callable(self.reply) else self.reply


def _case(case_id="c", question="How many days?", evidence=("Refunds within 30 days.", "Free shipping.")):
    return EvalCase(case_id, question, tuple(evidence), ())


def _resp(case_id, answer):
    return RecordedResponse(case_id=case_id, answer=answer, citation_ids=(), latency_ms=0, cost_usd=0)


def test_changed_number_formats():
    assert _changed_number("30") == "223"
    assert _changed_number("3.5") == "37.5"
    assert _changed_number("1,000") == "7013"
    assert _changed_number("0.25") == "14.75"
    assert all(_changed_number(n) != n for n in ("0", "1", "13", "999"))


def test_support_selection():
    evidence = ("refunds are paid within thirty days", "free shipping on large orders", "refunds need receipts")
    assert _support_indexes(evidence, "refunds paid within thirty days") == [0]
    both = _support_indexes(("refunds paid", "refunds paid within", "free shipping"), "refunds paid within")
    assert both == [0, 1]
    assert _support_indexes(evidence, "") == []
    assert _support_indexes(evidence, "completely unrelated words here") == []
    assert _support_indexes((), "anything") == []
    # nothing reaches the overlap bar, so the single best passage is used
    weak = _support_indexes(("alpha one", "beta"), "alpha gamma delta epsilon zeta eta theta")
    assert weak == [0]


def test_jaccard():
    assert _jaccard("", "") == 1.0
    assert _jaccard("alpha beta", "alpha beta") == 1.0
    assert _jaccard("alpha beta", "gamma delta") == 0.0
    assert _jaccard("alpha beta gamma", "alpha beta delta") == pytest.approx(0.5)


def test_remove_support_sensitive_insensitive_and_skipped():
    case = _case()
    baseline = "Refunds within 30 days."
    ignoring = Fake(baseline)
    check = _check_remove_support(case, baseline, ignoring, 0.8)
    assert check.status == "insensitive" and "similarity 1.00" in check.detail
    assert ignoring.calls == [("c", "How many days?", ["Free shipping."])]  # the supporting passage was removed
    changed = _check_remove_support(case, baseline, Fake("I do not know."), 0.8)
    assert changed.status == "sensitive" and changed.new_answer == "I do not know."
    skipped = _check_remove_support(case, "qqq www", Fake("x"), 0.8)
    assert skipped.status == "skipped" and "no evidence passage" in skipped.detail


def test_remove_support_similarity_boundary_counts_as_unchanged():
    case = _case(evidence=("alpha beta gamma delta",))
    baseline = "alpha beta gamma delta"
    new = "alpha beta gamma epsilon"  # jaccard 3/5 = 0.6
    assert _check_remove_support(case, baseline, Fake(new), 0.6).status == "insensitive"
    assert _check_remove_support(case, baseline, Fake(new), 0.61).status == "sensitive"


def test_swap_number_detects_stuck_and_followed_numbers():
    case = _case(question="How long is the warranty?", evidence=("Warranty lasts 24 months from 2020 delivery.",))
    stuck = Fake("The warranty lasts 24 months.")
    check = _check_swap_number(case, "The warranty lasts 24 months.", stuck)
    assert check.status == "insensitive" and "still states 24" in check.detail and "181" in check.detail
    assert stuck.calls[0][2] == ["Warranty lasts 181 months from 2020 delivery."]
    followed = _check_swap_number(case, "The warranty lasts 24 months.", Fake("The warranty lasts 181 months."))
    assert followed.status == "sensitive"
    abstained = _check_swap_number(case, "The warranty lasts 24 months.", Fake("I do not know."))
    assert abstained.status == "sensitive"


def test_swap_number_skips_numbers_from_the_question_or_not_in_evidence():
    case = _case(question="What happened in 2020?", evidence=("In 2020 revenue grew.",))
    assert _check_swap_number(case, "In 2020 revenue grew.", Fake("x")).status == "skipped"
    case = _case(evidence=("No digits here.",))
    assert _check_swap_number(case, "It is 5.", Fake("x")).status == "skipped"
    assert _check_swap_number(case, "No numbers.", Fake("x")).status == "skipped"


def _suite(n=4):
    cases = tuple(_case(f"c{i}", evidence=(f"Refunds within {30 + i} days.", "Free shipping.")) for i in range(n))
    responses = {c.id: _resp(c.id, f"Refunds within {30 + i} days.") for i, c in enumerate(cases)}
    return cases, responses


def test_run_pass_block_and_inconclusive():
    cases, responses = _suite()
    ok = run_counterfactual("s", cases, responses, Fake("I do not know."), min_eligible=3)
    assert ok.decision == "PASS" and ok.failed_gates == ()
    assert [(s.perturbation, s.eligible, s.insensitive, s.skipped) for s in ok.summaries] == [
        ("remove_support", 4, 0, 0), ("swap_number", 4, 0, 0)]
    ignoring = Fake(lambda cid, q, ev: f"Refunds within {30 + int(cid[1:])} days.")
    bad = run_counterfactual("s", cases, responses, ignoring, min_eligible=3)
    assert bad.decision == "BLOCK" and bad.failed_gates == ("insensitive_rate:remove_support", "insensitive_rate:swap_number")
    few = run_counterfactual("s", cases, responses, Fake("I do not know."), min_eligible=5)
    assert few.decision == "INCONCLUSIVE" and few.failed_gates == ("too_few_cases:remove_support", "too_few_cases:swap_number")
    assert bad.to_dict()["decision"] == "BLOCK" and len(bad.checks) == 8


def test_rate_boundary_is_inclusive_and_block_beats_inconclusive():
    cases, responses = _suite(5)
    one_ignored = Fake(lambda cid, q, ev: f"Refunds within {30} days." if cid == "c0" else "I do not know.")
    exactly = run_counterfactual("s", cases, responses, one_ignored, perturbations=("remove_support",), max_insensitive_rate=0.2)
    assert exactly.summaries[0].insensitive_rate == 0.2 and exactly.decision == "PASS"
    tighter = run_counterfactual("s", cases, responses, one_ignored, perturbations=("remove_support",), max_insensitive_rate=0.19)
    assert tighter.decision == "BLOCK"
    allignore = Fake(lambda cid, q, ev: f"Refunds within {30 + int(cid[1:])} days.")
    cases2 = _suite(2)
    mixed = run_counterfactual("s", cases2[0], cases2[1], allignore, perturbations=("remove_support", "swap_number"), min_eligible=3)
    assert mixed.decision == "INCONCLUSIVE"
    big, resp = _suite(4)
    blocked = run_counterfactual("s", big, resp, allignore, perturbations=("remove_support",), min_eligible=4)
    assert blocked.decision == "BLOCK"


def test_limit_perturbation_selection_and_validation():
    cases, responses = _suite(5)
    fake = Fake("I do not know.")
    report = run_counterfactual("s", cases, responses, fake, perturbations=("swap_number",), limit=2, min_eligible=1)
    assert len(fake.calls) == 2 and len(report.checks) == 2 and [s.perturbation for s in report.summaries] == ["swap_number"]
    for kwargs, message in (
        ({"perturbations": ()}, "Perturbations"),
        ({"perturbations": ("nope",)}, "Perturbations"),
        ({"same_threshold": 2}, "same_threshold"),
        ({"max_insensitive_rate": -0.1}, "max_insensitive_rate"),
        ({"max_insensitive_rate": True}, "max_insensitive_rate"),
        ({"min_eligible": 0}, "min_eligible"),
        ({"limit": 0}, "limit"),
    ):
        with pytest.raises(ContractError, match=message):
            run_counterfactual("s", cases, responses, fake, **kwargs)
    with pytest.raises(ContractError, match="No recorded response for case 'c0'"):
        run_counterfactual("s", cases, {}, fake)


def _script(tmp_path, body):
    path = tmp_path / "app.py"
    path.write_text(body, encoding="utf-8")
    return CommandAnswerer((sys.executable, str(path)), timeout_seconds=20)


def test_command_answerer_protocol_and_errors(tmp_path):
    good = _script(tmp_path, "import json,sys\nr=json.load(sys.stdin)\nprint(json.dumps({'answer': r['case_id']+':'+str(len(r['evidence']))}))")
    assert good.answer("c1", "q", ["a", "b"]) == "c1:2"
    for body, message in (
        ("import sys; sys.exit(3)", "exited 3"),
        ("import sys; sys.stderr.write('boom'); sys.exit(1)", "boom"),
        ("print('not json')", "must print"),
        ("print('{}')", "must print"),
        ("print('[]')", "must print"),
        ("print('{\"answer\": 5}')", "must be text"),
        ("print('{\"answer\": \"' + 'x'*200000 + '\"}')", "too large"),
    ):
        with pytest.raises(ContractError, match=message):
            _script(tmp_path, body).answer("c", "q", [])
    with pytest.raises(ContractError, match="failed for c"):
        CommandAnswerer(("definitely-not-a-real-binary-xyz",)).answer("c", "q", [])
    with pytest.raises(ContractError, match="failed for c"):
        CommandAnswerer((sys.executable, "-c", "import time; time.sleep(5)"), timeout_seconds=0.2).answer("c", "q", [])
    for bad in ((), ("",)):
        with pytest.raises(ValueError):
            CommandAnswerer(bad)
    for timeout in (0, -1, float("nan")):
        with pytest.raises(ValueError):
            CommandAnswerer(("x",), timeout_seconds=timeout)


def test_markdown_report():
    cases, responses = _suite(4)
    bad = run_counterfactual("s", cases, responses, Fake(lambda cid, q, ev: f"Refunds within {30 + int(cid[1:])} days."))
    text = counterfactual_markdown(bad)
    assert text.startswith("## RAGOps counterfactual-evidence test: BLOCK\n")
    assert "| `remove_support` | 4 | 4 | 100% | 0 |" in text
    assert "- `c0` (remove_support): answer barely changed" in text and "leads, not verdicts" in text
    ok = counterfactual_markdown(run_counterfactual("s", cases, responses, Fake("I do not know.")))
    assert "Cases whose answer ignored" not in ok
    many_cases, many_resp = _suite(15)
    many = counterfactual_markdown(run_counterfactual("s", many_cases, many_resp, Fake(lambda cid, q, ev: f"Refunds within {30 + int(cid[1:])} days.")))
    assert "- … and 10 more" in many
    weird = (_case("a|b`c", evidence=("Refunds within 30 days.",)),)
    text = counterfactual_markdown(run_counterfactual("s", weird, {"a|b`c": _resp("a|b`c", "Refunds within 30 days.")},
                                                     Fake("Refunds within 30 days."), min_eligible=1))
    assert "`a\\|b\\`c`" in text


def _cli(monkeypatch, capsys, app, *extra):
    argv = ["ragops", "counterfactual", "--scenario", str(DEMO / "scenario.json"),
            "--responses", str(DEMO / "responses.json"),
            "--answer-command", f"{sys.executable} {DEMO / app}", *extra]
    monkeypatch.setattr("sys.argv", argv)
    code = main()
    return code, capsys.readouterr().out


def test_demo_faithful_system_passes_and_memorizing_system_is_blocked(monkeypatch, capsys):
    code, out = _cli(monkeypatch, capsys, "faithful_app.py")
    assert code == 0 and "counterfactual-evidence test: PASS" in out
    code, out = _cli(monkeypatch, capsys, "memorizing_app.py")
    assert code == 2 and "BLOCK" in out and "still states 30" in out
    code, out = _cli(monkeypatch, capsys, "memorizing_app.py", "--min-eligible", "99")
    assert code == 3 and "INCONCLUSIVE" in out


def test_cli_json_output_options_and_errors(monkeypatch, capsys, tmp_path):
    dest = tmp_path / "nested" / "cf.json"
    code, _ = _cli(monkeypatch, capsys, "memorizing_app.py", "--format", "json", "--output", str(dest),
                   "--perturbation", "swap_number", "--limit", "3", "--min-eligible", "1")
    data = json.loads(dest.read_text())
    assert code == 2 and [s["perturbation"] for s in data["summaries"]] == ["swap_number"] and len(data["checks"]) == 3
    with pytest.raises(SystemExit, match="counterfactual error"):
        _cli(monkeypatch, capsys, "memorizing_app.py", "--perturbation", "bogus")


def test_defaults_and_inclusive_argument_bounds():
    cases, responses = _suite(3)
    fake = Fake("I do not know.")
    default = run_counterfactual("s", cases, responses, fake)
    assert default.min_eligible == 3 and default.max_insensitive_rate == 0.2 and default.same_threshold == 0.8
    assert default.decision == "PASS"  # exactly 3 eligible cases is enough
    for kwargs in ({"same_threshold": 0}, {"same_threshold": 1}, {"max_insensitive_rate": 0}, {"max_insensitive_rate": 1}):
        run_counterfactual("s", cases, responses, fake, **kwargs)


def test_all_skipped_perturbation_has_zero_rate_and_is_inconclusive():
    cases = (_case("n", evidence=("No digits at all.",)),)
    report = run_counterfactual("s", cases, {"n": _resp("n", "No digits at all.")}, Fake("x"), perturbations=("swap_number",), min_eligible=1)
    assert report.summaries[0].insensitive_rate == 0.0 and report.summaries[0].skipped == 1
    assert report.decision == "INCONCLUSIVE"


def test_checks_keep_the_new_answer_and_exact_details():
    case = _case(question="How long?", evidence=("Warranty lasts 24 months.",))
    ok = _check_swap_number(case, "It lasts 24 months.", Fake("It lasts 181 months."))
    assert ok.new_answer == "It lasts 181 months." and ok.detail == "the old number is gone from the answer"
    stuck = _check_swap_number(case, "It lasts 24 months.", Fake("It lasts 24 months."))
    assert stuck.new_answer == "It lasts 24 months."
    ignored = _check_remove_support(_case(), "Refunds within 30 days.", Fake("Refunds within 30 days."), 0.8)
    assert ignored.new_answer == "Refunds within 30 days." and ignored.perturbation == "remove_support"
