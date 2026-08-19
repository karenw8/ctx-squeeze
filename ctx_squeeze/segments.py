"""Paragraph and code-block segmentation.

Downstream stages (dedupe, scoring, extraction) all operate on segments
rather than raw text, so this is the one place that decides where the cut
points are.
"""

import re
from dataclasses import dataclass

_FENCE_RE = re.compile(r"^(```|~~~)")


@dataclass(frozen=True)
class Segment:
    text: str
    start_line: int  # 1-indexed, inclusive
    end_line: int  # 1-indexed, inclusive
    is_code: bool


def split_segments(text):
    """Split `text` into paragraphs, keeping fenced code blocks intact.

    Paragraphs are runs of non-blank lines separated by one or more blank
    lines. A fenced code block (``` or ~~~) is always its own segment,
    blank lines inside it included, so a truncation pass never has to
    reason about slicing into the middle of one.
    """
    lines = text.split("\n")
    segments = []
    buf = []
    buf_start = 1
    buf_is_code = False
    in_fence = False
    line_no = 0

    def flush(end_line):
        if buf:
            segments.append(
                Segment(
                    text="\n".join(buf),
                    start_line=buf_start,
                    end_line=end_line,
                    is_code=buf_is_code,
                )
            )

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()

        if in_fence:
            buf.append(line)
            if _FENCE_RE.match(stripped):
                in_fence = False
                flush(line_no)
                buf = []
                buf_is_code = False
            continue

        if _FENCE_RE.match(stripped):
            flush(line_no - 1)
            buf = [line]
            buf_start = line_no
            buf_is_code = True
            in_fence = True
            continue

        if stripped == "":
            flush(line_no - 1)
            buf = []
            buf_is_code = False
            continue

        if not buf:
            buf_start = line_no
        buf.append(line)

    flush(line_no)
    return segments
