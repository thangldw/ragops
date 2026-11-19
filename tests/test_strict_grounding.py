from ragops.evaluators import strict_grounding
from ragops.models import EvalCase, RecordedResponse


def test_number_words_match_digits_and_wrong_ones_do_not() -> None:
    case = EvalCase("c", "", ("The warranty lasts 9 months.",), ())
    ok = strict_grounding(case, RecordedResponse("c", "The warranty lasts nine months.", (), 0, 0))
    bad = strict_grounding(case, RecordedResponse("c", "The warranty lasts twelve months.", (), 0, 0))
    assert ok.score == 1.0 and bad.score == 0.0 and bad.number_mismatches == 1


def test_reversed_two_word_name_is_a_contradiction() -> None:
    case = EvalCase("c", "", ("The song was performed by Garth Brooks in 1990.",), ())
    same = strict_grounding(case, RecordedResponse("c", "The song was performed by Garth Brooks.", (), 0, 0))
    swapped = strict_grounding(case, RecordedResponse("c", "The song was performed by Brooks Garth.", (), 0, 0))
    assert same.score == 1.0 and swapped.contradicted_claims == 1
