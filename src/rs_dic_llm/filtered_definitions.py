"""Apply the extraction rule and a non-definition filter to stored definition records (D009, D010, D023, D024).

`filter_records(records, variant, unit)` returns copies of the records that `graph_build.build_graph`
turns into a filtered graph:

  * the decision (keep or drop) is always made on the first sentence of the stored text, with the
    default filter (`rs_dic_llm.quality_filter`) or the strict one (`rs_dic_llm.quality_filter_strict`);
  * a kept record gets as definition the first sentence (`unit="first_sentence"`, the primary unit,
    D009) or the stored text unchanged (`unit="stored"`, the sensitivity row);
  * a dropped record gets an empty definition and keeps its lemma and status. With a fixed vocabulary
    (`fixed_vocabulary`, D010) its node stays in the graph and only the edges it would have added
    are missing.

Records whose status is not "ok" or "self_referential" are not looked at: the graph builder skips them.
"""

import collections

from . import quality_filter, quality_filter_strict
from .extraction import first_sentence

def _keep_all(text: str, word: str, *, drop_imperatives: bool = False) -> quality_filter.Decision:
    """The `extract` variant: cut to the first sentence (or keep the stored text) and drop nothing, so that
    the effect of the extraction rule can be told apart from the effect of the filter."""
    return quality_filter.KEEP


VARIANTS = {"default": quality_filter.classify, "strict": quality_filter_strict.classify, "extract": _keep_all}
UNITS = ("first_sentence", "stored")
VALID_STATUSES = {"ok", "self_referential"}


def fixed_vocabulary(word_list: list[dict]) -> set[str]:
    """The lemmas of the word list: the node set of every filtered graph (D010)."""
    return {entry["lemma"] for entry in word_list}


def filter_records(
    records: list[dict],
    variant: str = "default",
    unit: str = "first_sentence",
    drop_imperatives: bool = False,
) -> tuple[list[dict], dict]:
    """Return (records for build_graph, statistics of what was dropped)."""
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {sorted(VARIANTS)}, not {variant!r}")
    if unit not in UNITS:
        raise ValueError(f"unit must be one of {UNITS}, not {unit!r}")
    classify = VARIANTS[variant]
    out = []
    reasons: collections.Counter = collections.Counter()
    rules: collections.Counter = collections.Counter()
    n_valid = 0
    for record in records:
        new = dict(record)
        if record.get("status", "ok") in VALID_STATUSES:
            n_valid += 1
            stored = record.get("definition") or ""
            text = first_sentence(stored)
            decision = classify(text, record["word"], drop_imperatives=drop_imperatives)
            if decision.keep:
                new["definition"] = text if unit == "first_sentence" else stored
            else:
                new["definition"] = ""
                reasons[decision.reason] += 1
                rules[decision.rule] += 1
        out.append(new)
    dropped = sum(reasons.values())
    stats = {
        "n_records": len(records),
        "n_valid_status": n_valid,
        "n_dropped": dropped,
        "dropped_share": round(dropped / n_valid, 4) if n_valid else 0.0,
        "by_reason": dict(reasons),
        "by_rule": dict(rules),
    }
    return out, stats
