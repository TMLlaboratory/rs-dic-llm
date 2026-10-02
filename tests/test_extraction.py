"""Tests for the uniform first-line / first-sentence extraction (decision D009).

The inputs are real stored outputs (audit F3, F4; E2 workbook), shortened where long.
Run: PYTHONPATH=src python -m pytest tests/test_extraction.py
"""

import pytest

from rs_dic_llm.extraction import (
    content_tokens,
    cut_removes_content,
    extract_records,
    first_sentence,
)


@pytest.mark.parametrize(
    "stored, expected",
    [
        # a clean single sentence is returned unchanged
        ("A narrow break or split in something, often caused by pressure or impact.",
         "A narrow break or split in something, often caused by pressure or impact."),
        # list markers and markup are formatting, not content
        ("A. A <b>plank</b> is a piece of wood or other material that is used for a bed.",
         "A plank is a piece of wood or other material that is used for a bed."),
        ("1. Habit is a habit of doing something.", "Habit is a habit of doing something."),
        ("I. <strong>Bury</strong> is a verb that means to bury.", "Bury is a verb that means to bury."),
        ("*   **retarded**", "retarded"),
        ("<strong>Answer:</strong>", "Answer:"),
        # the old _first_sentence kept everything up to a later ".\n"; the first line is cut here
        ("Which of the following is a possible outcome of a Punnett square?\n\n"
         "A. 4 genotypes and 2 phenotypes\n\nB. 2 genotypes and 4 phenotypes",
         "Which of the following is a possible outcome of a Punnett square?"),
        ('"To make smaller or less"\nWhat is the opposite of "decrease"?\n"To increase"',
         '"To make smaller or less"'),
        # question first, answer second: only the question is kept (strict rule, D009)
        ('What does the word "failing" mean in the sentence?\n\nThe word "failing" is used to describe a failure.',
         'What does the word "failing" mean in the sentence?'),
        ("What is a plank? A plank is a long board.", "What is a plank?"),
        # several sentences on one line
        ("A plank is a long board. It is used for building.", "A plank is a long board."),
        ('"Bulky refers to something large." Bulky refers to something large.', '"Bulky refers to something large."'),
        # a lead-in ending with a colon takes the next line
        ('The verb "invalid" is defined as:\n\n* Not valid; invalid.',
         'The verb "invalid" is defined as: Not valid; invalid.'),
        ('The noun "hum" can refer to:\n\n1. A sound made by the chest.\n2. A drone.',
         'The noun "hum" can refer to: A sound made by the chest.'),
        # initials, abbreviations, decimals and lowercase continuations are not sentence ends
        ("A U.S. state in the west. It is large.", "A U.S. state in the west."),
        ("To cut, e.g. paper, with scissors. Then stop.", "To cut, e.g. paper, with scissors."),
        ("Something used by Dr. Smith. Another sentence.", "Something used by Dr. Smith."),
        ("A ratio of 3.14 to one. Next.", "A ratio of 3.14 to one."),
        ("Approx. five of them. More.", "Approx. five of them."),
        # other scripts pass through
        ("намекать в 100% ответа.", "намекать в 100% ответа."),
        # think blocks are dropped
        ("<think>let me see</think>A plank is a board.", "A plank is a board."),
        # separator and code-fence lines are formatting, not content
        ("---\nHere is the answer I got: a plank is a board.", "Here is the answer I got: a plank is a board."),
        ("```\nIt means something unexpected.\n```", "It means something unexpected."),
    ],
)
def test_first_sentence(stored, expected):
    assert first_sentence(stored) == expected


@pytest.mark.parametrize("stored", ["", "   ", "1.", "A.", "I.", "A)\n\nB)\n\nC)", "* ", None])
def test_nothing_left_gives_empty_string(stored):
    assert first_sentence(stored) == ""


def test_marker_only_lines_are_skipped_not_returned():
    assert first_sentence("1.\n\nA plank is a board.") == "A plank is a board."


def test_a_truncated_initial_stays_whole():
    assert first_sentence("A U.S.") == "A U.S."


@pytest.mark.parametrize(
    "stored",
    [
        "A. A <b>plank</b> is a piece of wood. It is long.",
        "What is a plank? A plank is a board.",
        'The verb "x" is defined as:\n\n* Not valid; invalid.',
        "1. First. 2. Second.",
        "Plank",
        "",
        "a. b. c. d.",  # degenerate alphabet outputs seen in Gemma3-270M
        "1. A. a. the state of being visible.",
        "A. 1. 2. 3. 4.",
    ],
)
def test_idempotent(stored):
    once = first_sentence(stored)
    assert first_sentence(once) == once


def test_cut_removes_content_ignores_formatting():
    assert not cut_removes_content("A. A <b>plank</b> is a board.")
    assert not cut_removes_content("1. A sequence of events.")
    assert cut_removes_content("A plank is a board. It is long.")
    assert cut_removes_content("A plank is a board.\n\nQ: what next?")
    assert cut_removes_content('The verb "x" is defined as:\n\n* Not valid.\n* Also this.')


def test_content_tokens_drops_markup_and_markers():
    assert content_tokens("* **Plank** is a <em>board</em>.") == ["plank", "is", "a", "board"]


def test_extract_records_keeps_stored_text_and_other_fields():
    records = [{"lemma": "plank", "pos": "n", "status": "ok", "definition": "1. A board.\n\nQ: next?"}]
    out = extract_records(records)
    assert out[0]["definition"] == "A board."
    assert out[0]["definition_stored"] == "1. A board.\n\nQ: next?"
    assert out[0]["status"] == "ok" and out[0]["lemma"] == "plank"
    assert records[0]["definition"] == "1. A board.\n\nQ: next?"  # input untouched
