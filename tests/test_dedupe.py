from ctx_squeeze.dedupe import dedupe_segments, jaccard, shingles
from ctx_squeeze.segments import Segment


def _segment(text):
    return Segment(text=text, start_line=1, end_line=1, is_code=False)


def test_empty_text_has_no_shingles():
    assert shingles("") == frozenset()


def test_short_text_is_a_single_shingle():
    assert shingles("a b c", size=5) == frozenset([("a", "b", "c")])


def test_long_text_has_overlapping_shingles():
    result = shingles("a b c d e f", size=5)
    assert result == frozenset(
        [
            ("a", "b", "c", "d", "e"),
            ("b", "c", "d", "e", "f"),
        ]
    )


def test_jaccard_of_identical_sets_is_one():
    s = shingles("the quick brown fox jumps")
    assert jaccard(s, s) == 1.0


def test_jaccard_of_disjoint_sets_is_zero():
    a = shingles("completely different words entirely here")
    b = shingles("nothing overlaps at all today")
    assert jaccard(a, b) == 0.0


def test_jaccard_of_two_empty_sets_is_one():
    assert jaccard(frozenset(), frozenset()) == 1.0


def test_jaccard_partial_overlap():
    a = shingles("one two three four five", size=3)
    b = shingles("one two three four six", size=3)
    # shared: (one,two,three), (two,three,four); union has 4 total
    assert jaccard(a, b) == 2 / 4


def test_dedupe_keeps_all_when_no_duplicates():
    segments = [_segment("first paragraph text"), _segment("second unrelated content")]
    kept, dropped = dedupe_segments(segments)
    assert kept == segments
    assert dropped == 0


def test_dedupe_drops_near_identical_segment():
    original = _segment("the build failed after the runner image was bumped today")
    near_duplicate = _segment("the build failed after the runner image was bumped again")
    segments = [original, near_duplicate]
    kept, dropped = dedupe_segments(segments, threshold=0.7)
    assert kept == [original]
    assert dropped == 1


def test_dedupe_respects_threshold():
    original = _segment("the build failed after the runner image was bumped today")
    near_duplicate = _segment("the build failed after the runner image was bumped again")
    segments = [original, near_duplicate]
    kept, dropped = dedupe_segments(segments, threshold=0.99)
    assert kept == segments
    assert dropped == 0


def test_dedupe_keeps_first_occurrence():
    a = _segment("repeated line of text right here")
    b = _segment("repeated line of text right here")
    c = _segment("something else entirely different")
    kept, dropped = dedupe_segments([a, b, c])
    assert kept == [a, c]
    assert dropped == 1
