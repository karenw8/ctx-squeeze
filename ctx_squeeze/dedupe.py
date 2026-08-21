"""Near-duplicate detection via word shingling and Jaccard similarity.

Agent transcripts repeat themselves almost verbatim (the same file read
twice, the same traceback after each retry) but rarely byte-for-byte, so an
exact-match filter misses most of it. Comparing sets of overlapping word
n-grams catches those near-misses without needing to align the text.
"""


def shingles(text, size=5):
    """Return the set of `size`-word shingles in `text`.

    A shingle is a tuple of `size` consecutive words. Text with fewer than
    `size` words becomes a single shingle covering all of it, so short
    segments still compare meaningfully instead of producing an empty set.
    """
    words = text.split()
    if not words:
        return frozenset()
    if len(words) <= size:
        return frozenset([tuple(words)])
    return frozenset(tuple(words[i : i + size]) for i in range(len(words) - size + 1))


def jaccard(a, b):
    """Return the Jaccard similarity of two shingle sets, in [0, 1].

    Two empty sets are treated as identical (similarity 1.0) rather than
    undefined, since that's the shingle set of two blank segments.
    """
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def dedupe_segments(segments, threshold=0.8, shingle_size=5):
    """Drop segments that are near-duplicates of an earlier kept segment.

    Keeps the first occurrence of each near-duplicate group and drops later
    ones whose shingle-set Jaccard similarity to a kept segment meets
    `threshold`. Returns `(kept_segments, dropped_count)`.
    """
    kept = []
    kept_shingles = []
    dropped = 0
    for segment in segments:
        current = shingles(segment.text, shingle_size)
        if any(jaccard(current, other) >= threshold for other in kept_shingles):
            dropped += 1
            continue
        kept.append(segment)
        kept_shingles.append(current)
    return kept, dropped
