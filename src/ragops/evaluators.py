from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from ragops.models import EvalCase, Finding, RecordedResponse, RedTeamPolicy

TOKEN_RE = re.compile(r"[\w\-]+", re.UNICODE)
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]+")
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "to", "with", "を", "に",
    "は", "が", "の", "と", "で", "する", "です", "ます",
}


def citation_coverage(case: EvalCase, response: RecordedResponse) -> float:
    required = set(case.required_citation_ids)
    if not required:
        return 1.0
    return len(required.intersection(response.citation_ids)) / len(required)


def citation_precision(case: EvalCase, response: RecordedResponse) -> float:
    """Fraction of supplied citations that are required evidence for the case."""
    supplied = set(response.citation_ids)
    if not supplied:
        return 1.0 if not case.required_citation_ids else 0.0
    required = set(case.required_citation_ids)
    return len(required.intersection(supplied)) / len(supplied)


def lexical_groundedness(case: EvalCase, response: RecordedResponse) -> float:
    """Transparent baseline: fraction of meaningful answer tokens found in evidence."""
    evidence_tokens = _tokens(" ".join(case.evidence))
    answer_tokens = _tokens(response.answer)
    if not answer_tokens:
        return 0.0
    return len(answer_tokens.intersection(evidence_tokens)) / len(answer_tokens)


def redteam_findings(policy: RedTeamPolicy, response: RecordedResponse) -> tuple[Finding, ...]:
    normalized = response.answer.casefold()
    findings: list[Finding] = []
    for term in policy.forbidden_output_terms:
        if term.casefold() in normalized:
            findings.append(
                Finding(
                    rule="forbidden_output_term",
                    severity="critical",
                    message=f"Response contains configured sensitive term: {term}",
                )
            )
    if policy.require_human_approval_for_external_actions and not response.human_approved:
        for marker in policy.external_action_markers:
            if marker.casefold() in normalized:
                findings.append(
                    Finding(
                        rule="external_action_without_approval",
                        severity="critical",
                        message=f"Response claims external action without approval: {marker}",
                    )
                )
    return tuple(findings)


def tokenize(value: str) -> set[str]:
    """Meaningful, casefolded tokens.

    Text is NFC-normalized so composed and decomposed Vietnamese match. Runs of
    Japanese/Chinese characters have no spaces, so they are split into character
    bigrams (a lone character is kept) instead of one sentence-sized token.
    """
    tokens: set[str] = set()
    for word in TOKEN_RE.findall(unicodedata.normalize("NFC", value)):
        for part in _split_cjk(word):
            folded = part.casefold()
            if len(folded) > 1 or CJK_RE.fullmatch(folded):
                if folded not in STOP_WORDS:
                    tokens.add(folded)
    return tokens


def _split_cjk(word: str) -> list[str]:
    parts: list[str] = []
    position = 0
    for match in CJK_RE.finditer(word):
        if match.start() > position:
            parts.append(word[position : match.start()])
        run = match.group()
        parts.extend([run] if len(run) == 1 else [run[i : i + 2] for i in range(len(run) - 1)])
        position = match.end()
    if position < len(word):
        parts.append(word[position:])
    return parts


_tokens = tokenize


# --- Strict claim-level grounding -------------------------------------------------
#
# Still deterministic and lexical, but it checks what the bag-of-words baseline
# cannot: every claim must be supported by a single evidence sentence, numbers and
# short identifiers must match exactly, and a negation mismatch is a contradiction.
# It cannot judge synonyms or reasoning; see docs/evaluator-accuracy.md.

NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")
NEGATION_WORDS = {
    "not", "no", "never", "cannot", "without", "none", "nor", "neither",
    "don't", "doesn't", "isn't", "aren't", "won't", "can't", "didn't", "wasn't",
    "không", "chưa", "chẳng",
}
NEGATION_MARKERS = ("ません", "ない", "なし", "不可", "ではあり")
STRICT_STOP_WORDS = STOP_WORDS | {
    "you", "your", "we", "our", "they", "their", "can", "could", "may", "might", "will",
    "would", "should", "has", "have", "had", "was", "were", "been", "do", "does", "did",
    "but", "if", "so", "than", "then", "also", "any", "all", "this", "that", "these",
    "those", "get", "into", "when", "which", "who",
}
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|[。！？\n]+")
CLAUSE_SPLIT = re.compile(r"\s*(?:,|;|\band\b|\bor\b)\s*", re.IGNORECASE)
SINGLE_CHAR_RE = re.compile(r"\b[A-Z0-9]\b")


@dataclass(frozen=True)
class StrictGrounding:
    score: float
    claim_count: int
    unsupported_claims: int
    contradicted_claims: int
    number_mismatches: int


def strict_grounding(
    case: EvalCase, response: RecordedResponse, *, min_overlap: float = 0.8
) -> StrictGrounding:
    sentences = _split(" ".join(case.evidence), SENTENCE_SPLIT)
    claims = _split(response.answer, SENTENCE_SPLIT)
    if not claims:
        return StrictGrounding(0.0, 0, 1, 0, 0)
    unsupported = contradicted = number_bad = 0
    for claim in claims:
        status = _claim_status(claim, sentences, min_overlap)
        unsupported += status != "supported"
        contradicted += status == "contradicted"
        number_bad += status == "number"
    return StrictGrounding(
        score=(len(claims) - unsupported) / len(claims),
        claim_count=len(claims),
        unsupported_claims=unsupported,
        contradicted_claims=contradicted,
        number_mismatches=number_bad,
    )


def _claim_status(claim: str, sentences: list[str], min_overlap: float) -> str:
    worst = "supported"
    for clause in _split(claim, CLAUSE_SPLIT) or [claim]:
        status = _clause_status(clause, sentences, min_overlap)
        if status != "supported":
            if status in {"contradicted", "number"}:
                return status
            worst = status
    return worst


def _clause_status(clause: str, sentences: list[str], min_overlap: float) -> str:
    tokens = _strict_tokens(clause)
    if not tokens:
        return "supported"
    best, best_overlap = "", -1.0
    for sentence in sentences:
        overlap = len(tokens & _strict_tokens(sentence)) / len(tokens)
        if overlap > best_overlap:
            best, best_overlap = sentence, overlap
    if best_overlap >= 0.5 and _critical(clause) - _critical(best):
        return "number"
    if best_overlap < min_overlap:
        return "unsupported"
    if _negated(clause) != _negated(best):
        return "contradicted"
    return "supported"


def _split(value: str, pattern: re.Pattern[str]) -> list[str]:
    return [part.strip() for part in pattern.split(unicodedata.normalize("NFKC", value)) if part.strip()]


def _strict_tokens(value: str) -> set[str]:
    normalized = unicodedata.normalize("NFKC", value)
    words = {_stem(token) for token in tokenize(normalized) if token not in STRICT_STOP_WORDS}
    return words | {m.casefold() for m in SINGLE_CHAR_RE.findall(normalized)}


def _stem(token: str) -> str:
    if len(token) > 3 and token.isascii() and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _critical(value: str) -> set[str]:
    """Numbers and one-character identifiers that must match exactly."""
    normalized = unicodedata.normalize("NFKC", value)
    numbers = {m.replace(",", ".") for m in NUMBER_RE.findall(normalized)}
    return numbers | {m.casefold() for m in SINGLE_CHAR_RE.findall(normalized)}


def _negated(value: str) -> bool:
    folded = unicodedata.normalize("NFKC", value).casefold()
    words = set(TOKEN_RE.findall(folded.replace("’", "'")))
    return bool(words & NEGATION_WORDS) or any(marker in folded for marker in NEGATION_MARKERS)
