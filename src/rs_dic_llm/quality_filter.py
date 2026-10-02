"""Non-definition filter (decision D023): is a model output a definition of its word?

`classify(text, word)` looks at one extracted unit of text (normally the first sentence, see
`rs_dic_llm.extraction.first_sentence`) and returns a `Decision`: keep it, or drop it with a reason
(`fragment`, `question`, `echo`, `refusal`, `offtopic`) and the name of the rule that fired. Rules
are explicit and tried in the order below; the default is to keep, so a record is dropped only
when a rule fires. Dropped means (D010) that the node stays in the graph and the edges the record
would have contributed are not added.

Rules, in order (the reason code in brackets):
  1. blank text, or text without a single latin letter                    [fragment]
  2. nothing but the headword and grammar words ("Plank", "Yes.", "Clip (verb)",
     '"slick" is a verb.', "Performer is a noun.")                        [fragment]
  3. a question: ends with "?" or starts with a wh-word and an auxiliary
     ("What does ...", "Which of the following ...", "How many ...")      [question]
  4. first person ("I can't find ...", "I think it is ...")               [refusal or offtopic]
  5. echoed or task language: a span of the prompt, "Define the noun ...", "in one short sentence",
     "Write a sentence ...", "The definition should ...", an instruction verb with a task word
     ("Use only one sentence.")                                           [echo]
  6. off-topic text: exam markers ("the following", answer options), "is used in the sentence",
     "is not a word", "For example, ...", "This is ...", "If you ..."     [offtopic]
  7. a lead-in that never arrives (ends with ":"), or a sentence that stops before it says
     anything (no final punctuation and a last word such as "means", or an article before the
     final period, with fewer than three content words before the cut: "The word "all" is defined
     as" goes, "A bank that is not able to meet its debts is called a" stays)   [fragment]

What it deliberately does not do, because the hand-labeled development words and a read-through of
unlabeled records showed that each would drop real definitions:
  - no length cut (valid definitions such as "To make smaller." have three words or fewer);
  - no rule on the subject of a sentence ("The sun is a star." is off topic, but "A courageous
    person is willing to face danger." defines "brave" and "The tool is used to ..." defines
    "brush"); off-topic declaratives are therefore partly missed;
  - no rule on imperative verbs such as "Give" or "Provide" at the start ("Give a measured amount of
    something." defines "dose"); and none on the headword appearing in its own definition;
  - no use of part of speech or of an external dictionary.
Bare imperatives built on the headword ("Bury something in the ground.") cannot be told from short
definitions without part of speech, so rule 8, `drop_imperatives=True`, is a sensitivity option that
is off by default (D023 item 4).

The rules were written looking at the development words of the hand-labeled sample only, and at
records of other words that have no label (to look for rules that drop real definitions); they were
scored once on the test words (research/audit_scripts/14_filter_validation.py).
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    keep: bool
    reason: str  # "definition" when kept; otherwise fragment, question, echo, refusal or offtopic
    rule: str  # the rule that fired; "default" when kept


KEEP = Decision(True, "definition", "default")

_QUOTES = "\"'“”‘’`"
_TOKEN = re.compile(r"[a-z]+(?:'[a-z]+)*")
# grammar words that, with the headword, make a statement about the word and not a definition
_GRAMMAR = {
    "a", "an", "the", "is", "are", "word", "term", "noun", "verb", "adjective", "adverb", "phrase", "and", "or",
    "for", "means", "refers", "to", "called", "named",
}
# a last word that cannot end a sentence that has said something; an article or conjunction cannot
# stand directly before the final period either ("is called the .")
# (not is / are: "How far apart two things are" is a complete definition)
_TRUNCATION_WORDS = {"means", "the", "a", "an", "which", "whose", "and", "or", "because", "as", "who"}
_ARTICLE_OR_CONJUNCTION = {"a", "an", "the", "and", "or", "but", "because", "which", "whose"}
# words that mark an instruction about the output; "word", "words", "example", "answer" are not here because
# valid verb definitions use them ("Use lips to say words.", "Explain the meaning of a word.")
_TASK_WORDS = {
    "sentence", "sentences", "definition", "definitions", "markdown", "format", "concise", "grammatically",
    "tense", "jargon", "brief", "explanation", "response",
}
_STOP3 = {"the", "a", "an", "in", "of", "is", "to", "and", "or", "do", "not", "does", "be", "by", "as"}

# the prompts the models saw (generation._PROMPT_TEMPLATE and the E3 few-shot header); the slots for
# the part of speech and the headword are not part of any span
_PROMPT_SEGMENTS = (
    "define the noun", "define the verb", "define the adjective", "define the word",
    "in one short sentence use only common english words do not use the word itself in the definition",
    "below are example word definitions each definition is one sentence uses only simple english words "
    "and does not repeat the word being defined",
    "q define the noun", "q define the verb", "q define the adjective",
)

# a question without its question mark (cut off): only forms that ask about words or give a quiz item;
# "How much light is present in a place." and "What will happen after today." are definitions
_WH_START = re.compile(
    r"^\W*(?:what\s+(?:does|do|is|are|was|were)\s+(?:the\s+)?(?:word|term|noun|verb|adjective|phrase|meaning|"
    r"definition|difference|correct|best|main|name|purpose)\b|which of the following\b|"
    r"how\s+(?:do|does|did|can|could|would|should)\s+(?:you|i|we|one)\b|what do you\b)", re.I)
_AUX_QUESTION = re.compile(r"^\W*(?:is|are|do|does|did|can|could|would|should|will|was|were|has|have)\b", re.I)
_FIRST_PERSON = re.compile(r"^\W*(?:i|i'm|i've|i'll|i'd|im)\b|^\W*(?:let me|let's|sorry|unfortunately|as an ai)\b", re.I)
_REFUSAL = re.compile(
    r"\b(?:can't|cannot|can not|unable|not sure|don't know|do not know|sorry|trying to|no way to)\b", re.I)
# "Make sure something is true." and "Answer: Accountable, reliable." are definitions, so neither is a start here
_ECHO_START = re.compile(
    r"^\W*(?:(?:also|then|and|now),?\s+)?(?:define (?:the|a|an|this|that)\b|"
    r"write (?:a|an|one|the) (?:short |long |complete |single )?(?:sentence|definition|paragraph|essay|story|poem)\b|"
    r"use the word\b|in (?:one|a|1) (?:short |long )?sentence\b|"
    r"make it\b|do not\b|don't\b|put the answer\b|"
    r"the definition (?:should|must|needs|has|is)\b)", re.I)
# task rules about the output ("The sentence must be in the form of a question.") anywhere in the text
_TASK_RULE = re.compile(
    r"\b(?:the|your) (?:definition|sentence|answer|response|output) (?:should|must|needs to|has to|will|can|may)\b", re.I)
# only the prompt's own wording; "A group of words functioning together in a sentence." defines "phrase"
_ECHO_ANYWHERE = re.compile(
    r"\bin one (?:short |long )?sentence\b|\bone short sentence\b|\bcommon english words?\b|\bthe word itself\b", re.I)
_ECHO_FRAGMENT = re.compile(r"^\W*\S+\s+in a sentence\W*$", re.I)  # "Decrease in a sentence." (from "Use X in a sentence")
_INSTRUCTION_START = re.compile(
    r"^\W*(?:also,?\s+)?(?:use|avoid|keep|make sure|do not|don't|remember|note|ensure|include|add|mention|"
    r"explain|describe|state|list|try|be)\b", re.I)
# "the following" and "true or false" alone are not enough ("Prior to the following." defines "foregoing",
# "Question if something is true or false." defines "doubt")
_EXAM = re.compile(
    r"\bthe following (?:sentence|word|question|passage|text|statement|paragraph|options?)\b|"
    r"\bin (?:this|the) passage\b|\bparagraph \d|\bmultiple choice\b|\b[a-d][.)] \S.{2,50}?\b[b-e][.)] \S", re.I)
_META_USAGE = re.compile(
    r"\bis used in (?:a|an|the|this|that) (?:sentence|definition)\b|\bis not a (?:common )?(?:english )?word\b|"
    r"^\W*(?:for example\b|this is\b|if you\b)", re.I)
_IMPERATIVE_FOLLOWER = {
    "a", "an", "the", "this", "that", "some", "something", "someone", "somebody", "one", "to", "in", "on", "at",
    "for", "with", "between", "from", "by", "of", "up", "down", "out", "off", "into", "over", "under", "people",
    "things", "your", "my", "our", "their", "his", "her", "its", "it", "them", "him", "us", "me", "any", "all",
    "each", "every", "other", "very", "too", "not",
}


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower().replace("’", "'").replace("‘", "'"))


_SUFFIXES = ("ingly", "edly", "ing", "ed", "es", "s", "er", "est", "ly")


def _stems(token: str) -> set[str]:
    """Candidate stems: the token, the token without one inflectional suffix, each also without a final e
    and with a doubled final consonant undoubled (yelling -> yell, yel)."""
    token = token.removesuffix("'s")
    out = {token}
    for suffix in _SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 2:
            out.add(token[: -len(suffix)])
    for stem in list(out):
        if len(stem) > 2 and stem.endswith("e"):
            out.add(stem[:-1])
        if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            out.add(stem[:-1])
    return out


def _same_word(token: str, headword: str) -> bool:
    """Token is the headword or an inflected form of it (yell / yelling, draped / draping, bias / biased,
    sue / sued); evening is not eve, sunlight is not sun, mountain is not mount."""
    return token == headword or bool(_stems(token) & _stems(headword))


def _mostly_non_latin(text: str) -> bool:
    """At least a third of the letters are outside the Latin alphabets (Chinese, Cyrillic, Arabic ...)."""
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and sum(ord(c) > 0x024F for c in letters) / len(letters) >= 1 / 3


def _headword_only(tokens: list[str], head: list[str]) -> bool:
    """True if every token is the headword (or a close form) or a grammar word."""
    if not tokens:
        return False
    rest = [t for t in tokens if t not in _GRAMMAR and not any(_same_word(t, h) for h in head)]
    return not rest


def _prompt_spans() -> set[tuple[str, ...]]:
    spans = set()
    for segment in _PROMPT_SEGMENTS:
        words = segment.split()
        for i in range(len(words) - 2):
            gram = tuple(words[i:i + 3])
            if sum(w in _STOP3 for w in gram) < 2:
                spans.add(gram)
    return spans


_SPANS = _prompt_spans()


def _shares_prompt_span(tokens: list[str]) -> bool:
    return any(tuple(tokens[i:i + 3]) in _SPANS for i in range(len(tokens) - 2))


def _trim(text: str) -> str:
    return text.rstrip(" \t" + _QUOTES + ")]")


def _lead_in(text: str) -> bool:
    """A lead-in whose content never arrives: the text ends with a colon."""
    return _trim(text).endswith(":")


def _truncated(text: str) -> bool:
    """A sentence that stops before it says anything: no final punctuation and a last word such as
    "means", or an article or conjunction directly before the final period ("is called the .")."""
    if re.search(r"[.!?][" + _QUOTES + r")\]]+\s*$", text):  # the period is inside a quotation: 'meaning "the."'
        return False
    stripped = _trim(text)
    if not stripped:
        return False
    body = stripped.rstrip(".!? \t")
    words = body.split()
    if not words:
        return False
    chunk = words[-1].strip(_QUOTES + ",;()").lower().replace("’", "'")
    if not re.fullmatch(r"[a-z]+(?:'[a-z]+)*", chunk):  # ends in a digit or a symbol ("2²"): not cut off
        return False
    return chunk in (_ARTICLE_OR_CONJUNCTION if stripped[-1] in ".!?" else _TRUNCATION_WORDS)


_FUNCTION_STOP = _GRAMMAR | {
    "that", "who", "which", "whose", "whom", "be", "been", "being", "was", "were", "has", "have", "had", "not", "of",
    "in", "on", "at", "by", "from", "as", "it", "its", "this", "these", "those", "defined", "mean", "used", "describe",
    "describes", "one", "any", "can", "will", "would", "could", "someone", "something", "but", "if", "so", "than", "then",
    "with", "when", "where",
}


def _content_words(tokens: list[str], head: list[str]) -> int:
    """Words that say something: not grammar or function words and not the headword."""
    return sum(1 for t in tokens if t not in _FUNCTION_STOP and not any(_same_word(t, h) for h in head))


def _starts_with_imperative(tokens: list[str], head: list[str]) -> bool:
    return len(tokens) >= 2 and any(_same_word(tokens[0], h) for h in head) and tokens[1] in _IMPERATIVE_FOLLOWER


def classify(text: str, word: str, *, drop_imperatives: bool = False) -> Decision:
    """Keep or drop one extracted text for its headword. See the module docstring for the rules."""
    stripped = (text or "").strip()
    if not stripped:
        return Decision(False, "fragment", "blank")
    head = _tokens(str(word))
    tokens = _tokens(stripped)
    if _mostly_non_latin(stripped):  # a definition in Chinese or another script: no English words, no edges
        return Decision(False, "fragment", "non_latin_text")
    if not tokens:
        return Decision(False, "fragment", "no_text")
    # a text that starts with the headword is an attempt at its definition ("Define means ...",
    # "Write something down."), so the rules that look at the first words of the text do not apply
    starts_with_headword = any(_same_word(tokens[0], h) for h in head)

    if _headword_only(tokens, head) and not re.search(r"\d", stripped):  # a number is content
        return Decision(False, "fragment", "headword_only")
    if _trim(stripped).endswith("?") or (_WH_START.match(stripped) and not starts_with_headword):
        return Decision(False, "question", "question")
    if _AUX_QUESTION.match(stripped) and "?" in stripped:
        return Decision(False, "question", "question")
    if _FIRST_PERSON.match(stripped):
        refusal = bool(_REFUSAL.search(stripped))
        return Decision(False, "refusal" if refusal else "offtopic", "first_person")
    if _ECHO_START.match(stripped) and not starts_with_headword:
        return Decision(False, "echo", "task_start")
    if _ECHO_ANYWHERE.search(stripped) or _ECHO_FRAGMENT.match(stripped):
        return Decision(False, "echo", "task_phrase")
    if _shares_prompt_span(tokens):
        return Decision(False, "echo", "prompt_span")
    if _TASK_RULE.search(stripped):
        return Decision(False, "echo", "task_rule")
    if (_INSTRUCTION_START.match(stripped) and not starts_with_headword
            and any(t.removesuffix("'s") in _TASK_WORDS for t in tokens[1:])):
        return Decision(False, "echo", "instruction")
    if _EXAM.search(stripped):
        return Decision(False, "offtopic", "exam_marker")
    if _META_USAGE.search(stripped):
        return Decision(False, "offtopic", "meta_usage")
    if _lead_in(stripped):
        return Decision(False, "fragment", "lead_in")
    if _truncated(stripped) and _content_words(tokens, head) < 3:  # "A bank that ... is called a" has content
        return Decision(False, "fragment", "truncated")
    if drop_imperatives and _starts_with_imperative(tokens, head):
        return Decision(False, "offtopic", "imperative")
    return KEEP
