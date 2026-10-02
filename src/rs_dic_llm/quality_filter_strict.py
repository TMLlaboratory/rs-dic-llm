"""A more aggressive non-definition filter (decision D024): the default rules plus the rules D023 dropped.

`classify(text, word)` first applies the default filter of `rs_dic_llm.quality_filter` (frozen, D023,
hash in research/audit_scripts/outputs/14_test_scored.lock) and, when that keeps the text, a few more
rules. The extra rules are the ones D023 removed or narrowed because they dropped valid definitions
when they were read through on records without labels. Here they are put back on purpose: the strict
filter catches more junk and drops more real definitions, and the pair (default, strict) brackets what
the junk that the default filter leaves does to R. It is applied to every model alike and is reported
beside the default filter, never instead of it.

Extra rules (the reason code in brackets):
  S1. a sentence with its own subject: "the/a/an/this/that ... <one or two words> is/was/are/were" where
      the subject is not the headword ("The sun is a star.", but also "A courageous person is willing to
      face danger." defines "brave")                                           [offtopic]
  S2. a wh-word and an auxiliary at the start ("What will happen after today.", "How much light ...";
      the first is a definition of "future")                                   [question]
  S3. "Please", "Provide", "Give a", "Make sure" or "Answer:" at the start (all of which begin valid
      verb definitions: "Make sure something is true.")                        [echo]
  S4. "in a/the/this/that sentence" anywhere ("A group of words functioning together in a sentence."
      defines "phrase")                                                        [echo]
  S5. "the following" or "true or false" anywhere ("Prior to the following." defines "foregoing")
                                                                               [offtopic]
  S6. a sentence that stops at "is", "are", "was", "were" or "that" with no final punctuation, or any
      unfinished sentence whatever its content ("How far apart two things are")  [fragment]

Rules about the start of the text do not apply when the text begins with the headword.
"""

import re

from .quality_filter import Decision, _tokens, _same_word, _trim, _truncated, classify as classify_default

_SUBJECT = re.compile(
    r"^\W*(?:the|a|an|my|our|his|her|their|this|that|these|those)\s+(?P<subject>[a-z][a-z' -]{0,40}?)\s+"
    r"(?:is|was|are|were)\b", re.I)
_RELATIVE = {"who", "whom", "whose", "that", "which", "where", "when", "whereby"}
_ANSWER_LIKE = {"answer", "solution", "definition", "meaning", "explanation", "example", "result"}
_WH_BROAD = re.compile(
    r"^\W*(?:(?:what|which|who|whom|whose|when|where|why|how)\s+(?:is|are|was|were|do|does|did|can|could|would|"
    r"should|will|has|have|had|many|much|word|kind|type)\b|what's\b|whats\b)", re.I)
_ECHO_START_OLD = re.compile(r"^\W*(?:please\b|provide\b|give (?:a|an|the|me)\b|make sure\b|answer:)", re.I)
_IN_SENTENCE = re.compile(r"\bin (?:a|an|one|the|this|that|the following) (?:short |long )?sentences?\b", re.I)
_EXAM_BARE = re.compile(r"\bthe following\b|\btrue or false\b", re.I)
_UNFINISHED_END = {"is", "are", "was", "were", "that"}


def _own_subject(text: str, head: list[str]) -> bool:
    match = _SUBJECT.match(text)
    if not match:
        return False
    subject = _tokens(match.group("subject"))
    if not subject or len(subject) > 2 or subject[-1] in _ANSWER_LIKE or any(t in _RELATIVE for t in subject):
        return False
    return not any(_same_word(t, h) for t in subject for h in head)


def classify(text: str, word: str, *, drop_imperatives: bool = False) -> Decision:
    """The default decision; when it keeps the text, the extra rules of this module."""
    decision = classify_default(text, word, drop_imperatives=drop_imperatives)
    if not decision.keep:
        return decision
    stripped = (text or "").strip()
    head = _tokens(str(word))
    tokens = _tokens(stripped)
    starts_with_headword = bool(tokens) and any(_same_word(tokens[0], h) for h in head)

    if _own_subject(stripped, head):
        return Decision(False, "offtopic", "strict_own_subject")
    if not starts_with_headword and _WH_BROAD.match(stripped):
        return Decision(False, "question", "strict_wh_start")
    if not starts_with_headword and _ECHO_START_OLD.match(stripped):
        return Decision(False, "echo", "strict_task_start")
    if _IN_SENTENCE.search(stripped):
        return Decision(False, "echo", "strict_in_sentence")
    if _EXAM_BARE.search(stripped):
        return Decision(False, "offtopic", "strict_exam_marker")
    if _truncated(stripped):
        return Decision(False, "fragment", "strict_truncated")
    trimmed = _trim(stripped)
    if trimmed and trimmed[-1] not in ".!?" and _tokens(trimmed) and _tokens(trimmed)[-1] in _UNFINISHED_END:
        return Decision(False, "fragment", "strict_unfinished")
    return decision
