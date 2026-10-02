"""Uniform "first line, first sentence" extraction of a stored definition (decision D009).

The stored `definition` of many base-model records (and of E5 records) holds more than one
sentence: a question, a list, an essay prompt. `generation._first_sentence` cuts at the first
".\\n" even when an earlier newline exists, so those extras reached the graph (audit F3).
This module applies one rule to every model, after the fact, to the stored text:

  1. drop <think> blocks, HTML-like tags and markdown emphasis (`**bold**`);
  2. skip blank lines, lines that are only a list marker (`1.`, `A)`, `*`) and lines without a
     letter or digit (`---`, a code fence);
  3. take the first remaining line, without its list marker (`A.`, `1.`, `(b)`, `iv.`, `-`, `*`);
  4. cut that line at its first sentence end: `.`, `!` or `?` (plus closing quotes or
     brackets) followed by whitespace and then something that is not a lowercase letter, where
     the period does not belong to an initial (`U.S.`, `e.g.`) or an abbreviation (`Dr.`);
  5. if the result ends with a colon (a lead-in such as `The verb "x" is defined as:`), append
     the first sentence of the next non-empty line.

What the rule does not do: it never looks for the "best" sentence. A question followed by its
answer keeps only the question; a definition that comes second is lost. That is deliberate:
the primary analysis uses this strict unit and the stored text is reported as a sensitivity
row, and the second labeling pass validates the filter on this unit (research/DECISION_LOG.md
D009, research/E2_LABELING_INSTRUCTIONS.md section 8).

The function is pure and idempotent: first_sentence(first_sentence(x)) == first_sentence(x).
"""

import re

_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)
_TAG = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>")
_EMPHASIS = re.compile(r"\*{1,3}|_{2,3}")
_MARKER = re.compile(r"^(?:[-*•]\s+|\(?(?:[A-Za-z]|\d{1,3}|[ivxIVX]{2,4})[.)]\s+)")
_MARKER_ONLY = re.compile(r"^(?:[-*•]|\(?(?:[A-Za-z]|\d{1,3}|[ivxIVX]{2,4})[.)])$")
_TERMINATOR = re.compile(r"[.!?]+[\"'”’)\]]*(?=\s|$)")
_ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "prof", "st", "vs", "approx"}


def _clean_line(raw: str) -> str:
    """One line without markup, collapsed whitespace and a leading list marker; '' if nothing is left."""
    line = _TAG.sub(" ", raw)
    line = _EMPHASIS.sub("", line)
    line = re.sub(r"\s+", " ", line).strip()
    while True:  # "* 1. text" carries two markers; "a. b. c." carries three
        match = _MARKER.match(line)
        if not match:
            break
        line = line[match.end():].strip()
    # marker-only lines ("1.", "A)") and lines without a letter or digit ("---", "```") are formatting
    return "" if _MARKER_ONLY.match(line) or not re.search(r"\w", line) else line


def _is_initial_or_abbreviation(line: str, dot: int) -> bool:
    """True if the period at index `dot` ends an initial (U.S., e.g.) or an abbreviation (Dr.)."""
    if line[dot] != ".":
        return False
    word = re.search(r"([A-Za-z]+)$", line[:dot])
    if not word:
        return False
    if word.group(1).lower() in _ABBREVIATIONS:
        return True
    if len(word.group(1)) == 1:
        before = line[: dot - 1][-1:]
        return before == "" or before in " .(\"'"
    return False


def _cut_sentence(line: str) -> str:
    """The first sentence of a single cleaned line."""
    for match in _TERMINATOR.finditer(line):
        rest = line[match.end():].lstrip()
        if not rest:
            return line[: match.end()].strip()
        if rest[0].islower() or _is_initial_or_abbreviation(line, match.start()):
            continue
        return line[: match.end()].strip()
    return line.strip()


def _cleaned_lines(text: str) -> list[str]:
    text = _THINK.sub("", text or "")
    return [line for line in (_clean_line(raw) for raw in text.splitlines()) if line]


def first_sentence(text: str) -> str:
    """First line and first sentence of `text`, without markup or list marker ('' if none)."""
    lines = _cleaned_lines(text)
    if not lines:
        return ""
    sentence = _cut_sentence(lines[0])
    if sentence.endswith(":") and len(lines) > 1:
        sentence = f"{sentence} {_cut_sentence(lines[1])}".strip()
    return sentence


def content_tokens(text: str) -> list[str]:
    """Word tokens of `text` after removing markup and list markers, for comparing two versions."""
    return re.findall(r"\w+", " ".join(_cleaned_lines(text)).lower())


def cut_removes_content(stored: str) -> bool:
    """True if first_sentence drops words of `stored` (not merely markup or list markers)."""
    return content_tokens(first_sentence(stored)) != content_tokens(stored)


def extract_records(records: list[dict]) -> list[dict]:
    """Copies of `records` whose `definition` is first_sentence(definition); the stored text is
    kept under `definition_stored`. Status and every other field are left as they were."""
    out = []
    for record in records:
        copy = dict(record)
        copy["definition_stored"] = record.get("definition") or ""
        copy["definition"] = first_sentence(copy["definition_stored"])
        out.append(copy)
    return out
