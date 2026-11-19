import unicodedata

from ragops.evaluators import tokenize


def test_english_tokens_drop_stop_words_and_single_letters() -> None:
    assert tokenize("The refund is a policy") == {"refund", "policy"}


def test_japanese_runs_become_bigrams_not_one_sentence_token() -> None:
    tokens = tokenize("返金は購入後30日以内")
    assert {"返金", "購入", "入後", "30", "日以", "以内"} <= tokens
    assert "返金は購入後30日以内" not in tokens


def test_japanese_paraphrase_shares_tokens() -> None:
    assert tokenize("返金ポリシー") & tokenize("返金の手順")


def test_vietnamese_composed_and_decomposed_forms_match() -> None:
    composed = unicodedata.normalize("NFC", "hoàn tiền")
    decomposed = unicodedata.normalize("NFD", "hoàn tiền")
    assert tokenize(composed) == tokenize(decomposed) == {"hoàn", "tiền"}


def test_lone_cjk_character_is_kept() -> None:
    assert "猫" in tokenize("猫 cat")
