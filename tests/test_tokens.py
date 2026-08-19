from ctx_squeeze.tokens import estimate_tokens, truncate_to_tokens


def test_empty_string_is_zero_tokens():
    assert estimate_tokens("") == 0


def test_whitespace_only_is_one_token():
    assert estimate_tokens("   ") == 1


def test_word_run_is_four_chars_per_token():
    assert estimate_tokens("wordword") == 2  # 8 letters / 4


def test_digit_run_is_three_chars_per_token():
    assert estimate_tokens("123456") == 2  # 6 digits / 3


def test_newline_is_half_a_token():
    assert estimate_tokens("\n\n\n\n") == 2  # 4 newlines * 0.5


def test_symbol_is_point_six_of_a_token():
    assert estimate_tokens("!!!") == 2  # 3 symbols * 0.6 = 1.8, rounds to 2


def test_cjk_is_one_token_per_character():
    assert estimate_tokens("你好世界") == 4


def test_spaces_between_words_are_not_counted():
    assert estimate_tokens("word word") == estimate_tokens("wordword")


def test_mixed_classes_sum_independently():
    # 8 letters -> 2.0, one newline -> 0.5, 6 digits -> 2.0 => 4.5, ties round to even
    assert estimate_tokens("wordword\n123456") == 4


def test_longer_text_estimates_more_tokens():
    short = "the quick brown fox"
    long_text = short * 10
    assert estimate_tokens(long_text) > estimate_tokens(short)


def test_truncate_respects_budget():
    text = "wordword " * 50
    budget = 20
    truncated = truncate_to_tokens(text, budget)
    assert estimate_tokens(truncated) <= budget


def test_truncate_returns_full_text_when_under_budget():
    text = "short text"
    assert truncate_to_tokens(text, 1000) == text


def test_truncate_zero_budget_is_empty():
    assert truncate_to_tokens("anything", 0) == ""


def test_truncate_negative_budget_is_empty():
    assert truncate_to_tokens("anything", -5) == ""


def test_truncate_is_a_prefix():
    text = "wordword " * 50
    truncated = truncate_to_tokens(text, 20)
    assert text.startswith(truncated)


def test_truncate_is_the_longest_fitting_prefix():
    # One more character than the truncation should blow the budget,
    # otherwise the binary search stopped early.
    text = "wordword " * 50
    budget = 20
    truncated = truncate_to_tokens(text, budget)
    assert len(truncated) == len(text) or estimate_tokens(text[: len(truncated) + 1]) > budget
