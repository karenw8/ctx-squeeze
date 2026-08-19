"""Character-class token estimator.

BPE tokenizers tend to break at the same boundaries as character classes
(letters, digits, whitespace, symbols), so counting runs of each class with
a per-class weight gets within about 10% of a real tokenizer on English
prose without shipping a vocabulary file.
"""

# Weights are chars-per-token for the divided classes, tokens-per-char for
# the multiplied ones. Tuned against BPE output on prose; see README.
WORD_CHARS_PER_TOKEN = 4.0
DIGIT_CHARS_PER_TOKEN = 3.0
NEWLINE_TOKENS_PER_CHAR = 0.5
SYMBOL_TOKENS_PER_CHAR = 0.6
CJK_TOKENS_PER_CHAR = 1.0

# CJK scripts tokenize roughly one token per character in most BPE
# vocabularies, unlike space-delimited scripts, so they get their own class
# rather than being lumped in with "word".
_CJK_RANGES = (
    (0x4E00, 0x9FFF),  # CJK unified ideographs
    (0x3040, 0x309F),  # hiragana
    (0x30A0, 0x30FF),  # katakana
    (0xAC00, 0xD7A3),  # hangul syllables
)


def _is_cjk(ch):
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _CJK_RANGES)


def _char_class(ch):
    if ch == "\n":
        return "newline"
    if ch.isspace():
        return "space"
    if ch.isdigit():
        return "digit"
    if _is_cjk(ch):
        return "cjk"
    if ch.isalpha():
        return "word"
    return "symbol"


def estimate_tokens(text):
    """Estimate the token count of `text` without a tokenizer.

    Not exact: treat it as a planning figure, not a billing figure. See
    the README for the accuracy tradeoff.
    """
    if not text:
        return 0

    total = 0.0
    run_class = None
    run_len = 0

    def flush():
        nonlocal total
        if run_class == "word":
            total += run_len / WORD_CHARS_PER_TOKEN
        elif run_class == "digit":
            total += run_len / DIGIT_CHARS_PER_TOKEN
        elif run_class == "cjk":
            total += run_len * CJK_TOKENS_PER_CHAR
        elif run_class == "newline":
            total += run_len * NEWLINE_TOKENS_PER_CHAR
        elif run_class == "symbol":
            total += run_len * SYMBOL_TOKENS_PER_CHAR
        # "space" runs contribute nothing: they're boundaries, not tokens.

    for ch in text:
        cls = _char_class(ch)
        if cls == run_class:
            run_len += 1
        else:
            flush()
            run_class, run_len = cls, 1
    flush()

    # Non-empty input is at least one token, even if it's all whitespace.
    return max(1, round(total))


def truncate_to_tokens(text, budget):
    """Return the longest prefix of `text` that fits within `budget` tokens.

    Binary searches on character offset rather than walking the estimator
    forward one character at a time, since `estimate_tokens` is cheap but
    not free and documents can be long.
    """
    if budget <= 0:
        return ""
    if estimate_tokens(text) <= budget:
        return text

    lo, hi = 0, len(text)
    # Invariant: text[:lo] fits, text[:hi] does not.
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if estimate_tokens(text[:mid]) <= budget:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo]
