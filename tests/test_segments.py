from ctx_squeeze.segments import split_segments


def test_empty_text_has_no_segments():
    assert split_segments("") == []


def test_single_paragraph_is_one_segment():
    segments = split_segments("one line\nanother line")
    assert len(segments) == 1
    assert segments[0].text == "one line\nanother line"
    assert segments[0].start_line == 1
    assert segments[0].end_line == 2
    assert segments[0].is_code is False


def test_blank_line_splits_paragraphs():
    text = "para one line one\npara one line two\n\npara two\n"
    segments = split_segments(text)
    assert [s.text for s in segments] == [
        "para one line one\npara one line two",
        "para two",
    ]
    assert (segments[0].start_line, segments[0].end_line) == (1, 2)
    assert (segments[1].start_line, segments[1].end_line) == (4, 4)


def test_multiple_blank_lines_do_not_create_empty_segments():
    text = "a\n\n\n\nb\n"
    segments = split_segments(text)
    assert [s.text for s in segments] == ["a", "b"]


def test_fenced_code_block_is_one_segment_even_with_blank_lines():
    text = "before\n\n```python\ndef f():\n\n    pass\n```\n\nafter\n"
    segments = split_segments(text)
    assert [s.text for s in segments] == [
        "before",
        "```python\ndef f():\n\n    pass\n```",
        "after",
    ]
    assert [s.is_code for s in segments] == [False, True, False]
    assert (segments[1].start_line, segments[1].end_line) == (3, 7)


def test_tilde_fence_is_also_a_code_block():
    text = "~~~\ncode\n~~~"
    segments = split_segments(text)
    assert len(segments) == 1
    assert segments[0].is_code is True


def test_unclosed_fence_runs_to_end_of_text():
    text = "before\n\n```\ncode that never closes"
    segments = split_segments(text)
    assert segments[-1].is_code is True
    assert segments[-1].text == "```\ncode that never closes"
