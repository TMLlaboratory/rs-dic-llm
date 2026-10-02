"""Validate the non-definition filter against the hand labels (decision D023).

Protocol (D023, item 3). The 100 labeled words are split at random, with a fixed seed, into 50
development and 50 test words; the split is by word, so a lemma listed twice (two parts of speech)
falls on one side, and it is the same in every model tab. Rules are written looking at development
words only. The test words are scored once, after the rules are frozen: `--test` refuses to run
twice (it writes outputs/14_test_scored.lock with a hash of the filter module) unless --force is
given, and `--all` (the final table over all 100 words) refuses to run before `--test`.

Two units are scored with the same filter decisions:
  first sentence (primary): text = rs_dic_llm.extraction.first_sentence(stored); labels from the
    first-sentence validation set (outputs/11_unit_a_validation_set.csv, script 11): the
    first-pass label where the rule does not cut, the second-pass label where it cuts a former
    `definition` or `unclear`, and an inferred non-definition (class unknown) for the other cut rows;
  stored text (sensitivity): same decisions, labels = the first-pass labels of the whole output.
A record is "positive" (should be dropped) when its label is anything but `definition`.

Usage:
    python research/audit_scripts/14_filter_validation.py --explore   # development words only
    python research/audit_scripts/14_filter_validation.py --dev       # score development words
    python research/audit_scripts/14_filter_validation.py --test      # score test words, once
    python research/audit_scripts/14_filter_validation.py --all       # final tables, all 100 words
"""
import argparse
import collections
import csv
import hashlib
import math
import random
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")
from rs_dic_llm.extraction import first_sentence  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"
WORKBOOK = ROOT / "data" / "exp2_labeling_workbook_labeled.xlsx"
UNIT_A = OUT / "11_unit_a_validation_set.csv"
SPLIT_SEED = "e2-filter-split-2026-10-01"
CLASS_OF_REASON = {"echo": "echo", "question": "question", "offtopic": "offtopic",
                   "fragment": "restatement", "refusal": "refusal"}


def norm(word):
    return str(word).strip().lower()


def load_rows():
    """All 2,300 labeled rows: both units' texts and labels."""
    unit_a = {}
    for r in csv.DictReader(open(UNIT_A, encoding="utf-8-sig")):
        unit_a[(r["tab"], int(r["row"]))] = r
    wb = openpyxl.load_workbook(WORKBOOK)
    rows = []
    for tab in [s for s in wb.sheetnames if s != "Read me"]:
        ws = wb[tab]
        for r in range(3, 103):
            stored = ws.cell(r, 2).value or ""
            a = unit_a[(tab, r)]
            label_a = a["unit_a_label"]
            rows.append(dict(
                tab=tab, row=r, word=ws.cell(r, 1).value, stored=stored,
                text_a=first_sentence(stored), note=ws.cell(r, 4).value or "",
                label_b=ws.cell(r, 3).value, label_a=label_a, source_a=a["source"],
                inferred=label_a.startswith("non-definition"),
            ))
    return rows


def split_words(rows):
    words = sorted({norm(r["word"]) for r in rows})
    shuffled = words[:]
    random.Random(SPLIT_SEED).shuffle(shuffled)
    half = len(words) // 2
    return set(shuffled[:half]), set(shuffled[half:])


def nondef(label):
    return label != "definition"


def kappa(tp, fp, fn, tn):
    n = tp + fp + fn + tn
    if n == 0:
        return float("nan")
    po = (tp + tn) / n
    pe = ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / (n * n)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def binary(rows, key):
    tp = sum(1 for r in rows if not r["keep"] and nondef(r[key]))
    fp = sum(1 for r in rows if not r["keep"] and not nondef(r[key]))
    fn = sum(1 for r in rows if r["keep"] and nondef(r[key]))
    tn = sum(1 for r in rows if r["keep"] and not nondef(r[key]))
    pct = lambda a, b: f"{100 * a / b:5.1f}%" if b else "   n/a"
    return dict(n=len(rows), tp=tp, fp=fp, fn=fn, tn=tn, precision=pct(tp, tp + fp), recall=pct(tp, tp + fn),
                false_drop=pct(fp, fp + tn), kappa=kappa(tp, fp, fn, tn))


def decide(rows, variant="default", **kw):
    if variant == "strict":
        from rs_dic_llm import quality_filter_strict as module
    else:
        from rs_dic_llm import quality_filter as module
    for r in rows:
        d = module.classify(r["text_a"], r["word"], **kw)
        r["keep"], r["reason"], r["rule"] = d.keep, d.reason, d.rule


def module_path(variant):
    return ROOT / "src" / "rs_dic_llm" / ("quality_filter_strict.py" if variant == "strict" else "quality_filter.py")


def lock_path(variant):
    return OUT / ("14_test_scored_strict.lock" if variant == "strict" else "14_test_scored.lock")


def report(rows, title):
    print(f"\n{'=' * 100}\n{title}: {len(rows)} rows, {len({norm(r['word']) for r in rows})} words\n{'=' * 100}")
    for unit, key, sub in (("FIRST SENTENCE (primary)", "label_a", rows), ("STORED TEXT (sensitivity)", "label_b", rows)):
        b = binary(sub, key)
        print(f"\n{unit}: dropped {b['tp'] + b['fp']} of {b['n']}; true non-definitions {b['tp'] + b['fn']}")
        print(f"   precision of a drop {b['precision']}   recall of non-definitions {b['recall']}   definitions wrongly dropped "
              f"{b['false_drop']} ({b['fp']} of {b['fp'] + b['tn']})   kappa vs labels {b['kappa']:.2f}")
        for grp, test in (("base models", lambda t: t.endswith("-pt")), ("instruct models", lambda t: not t.endswith("-pt"))):
            g = binary([r for r in sub if test(r["tab"])], key)
            print(f"   {grp:16} n={g['n']:4}  non-def {g['tp'] + g['fn']:4}  dropped {g['tp'] + g['fp']:4}  precision {g['precision']}  "
                  f"recall {g['recall']}  false drops {g['fp']:3}  kappa {g['kappa']:.2f}")
    print("\nPER CLASS, first sentence (rows whose class was labeled; `inferred` rows are only in the binary tables)")
    labeled = [r for r in rows if not r["inferred"]]
    print(f"   {'label':12}{'n':>5}{'dropped':>9}{'recall':>9}   dropped with the matching reason")
    for label in ("definition", "echo", "question", "offtopic", "restatement", "refusal", "unclear"):
        sub = [r for r in labeled if r["label_a"] == label]
        if not sub:
            continue
        dropped = [r for r in sub if not r["keep"]]
        match = [r for r in dropped if CLASS_OF_REASON.get(r["reason"]) == label]
        tag = "(= false drops)" if label == "definition" else f"{len(match)} of {len(dropped)}" if dropped else ""
        print(f"   {label:12}{len(sub):>5}{len(dropped):>9}{(100 * len(dropped) / len(sub)):>8.1f}%   {tag}")
    print("\nPER REASON CODE, first sentence (precision: share of drops with this code that are truly non-definitions)")
    print(f"   {'reason':10}{'drops':>7}{'non-def':>9}{'of the class':>14}   rules that fired")
    for reason in ("fragment", "question", "echo", "refusal", "offtopic"):
        d = [r for r in rows if not r["keep"] and r["reason"] == reason]
        if not d:
            continue
        nd = sum(1 for r in d if nondef(r["label_a"]))
        same = sum(1 for r in d if r["label_a"] == CLASS_OF_REASON[reason])
        rules = collections.Counter(r["rule"] for r in d).most_common(6)
        print(f"   {reason:10}{len(d):>7}{nd:>9}{same:>14}   {rules}")
    print("\nPER MODEL, first sentence: n / non-definitions / dropped / correct drops / false drops / missed")
    for tab in dict.fromkeys(r["tab"] for r in rows):
        b = binary([r for r in rows if r["tab"] == tab], "label_a")
        print(f"   {tab:24}{b['n']:4}{b['tp'] + b['fn']:5}{b['tp'] + b['fp']:5}{b['tp']:5}{b['fp']:5}{b['fn']:5}   "
              f"precision {b['precision']}  recall {b['recall']}")


def show_errors(rows, limit=70):
    fd = [r for r in rows if not r["keep"] and not nondef(r["label_a"])]
    ms = [r for r in rows if r["keep"] and nondef(r["label_a"])]
    print(f"\nFALSE DROPS (first sentence; dropped, labeled definition): {len(fd)}")
    for r in fd[:limit]:
        print(f"   [{r['tab']:14} {str(r['word'])[:12]:12}] {r['reason']}/{r['rule']}: {r['text_a'][:110]!r}")
    print(f"\nMISSED (first sentence; kept, labeled non-definition): {len(ms)}")
    for r in ms[:limit]:
        print(f"   [{r['tab']:14} {str(r['word'])[:12]:12}] {r['label_a'][:12]:12} {r['note'][:18]:18} {r['text_a'][:105]!r}")


def explore(rows):
    print(f"DEVELOPMENT WORDS ONLY: {len(rows)} rows")
    print("\nNON-DEFINITIONS on the first-sentence unit, by label (tab / word / note / text)")
    for label in ("echo", "question", "offtopic", "restatement", "refusal", "unclear", "non-definition (class not re-labeled)"):
        sub = [r for r in rows if r["label_a"] == label]
        print(f"\n--- {label}: {len(sub)}")
        for r in sub:
            print(f"   [{r['tab']:14} {str(r['word'])[:11]:11}] {r['note'][:16]:16} {r['text_a'][:112]!r}")


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    for m in ("explore", "dev", "test", "all"):
        mode.add_argument(f"--{m}", action="store_true")
    parser.add_argument("--force", action="store_true", help="score the test words again (invalidates the held-out test)")
    parser.add_argument("--errors", action="store_true", help="list false drops and misses")
    parser.add_argument("--drop-imperatives", action="store_true")
    parser.add_argument("--variant", choices=("default", "strict"), default="default",
                        help="strict = the more aggressive bracket of D024 (its own once-only test lock)")
    args = parser.parse_args()

    rows = load_rows()
    dev_words, test_words = split_words(rows)
    dev = [r for r in rows if norm(r["word"]) in dev_words]
    test = [r for r in rows if norm(r["word"]) in test_words]
    print(f"variant {args.variant}; split (seed {SPLIT_SEED!r}): {len(dev_words)} development words = {len(dev)} rows, "
          f"{len(test_words)} test words = {len(test)} rows")
    kw = dict(drop_imperatives=args.drop_imperatives)
    module, lock = module_path(args.variant), lock_path(args.variant)

    if args.explore:
        explore(dev)
    elif args.dev:
        decide(dev, args.variant, **kw)
        report(dev, f"DEVELOPMENT WORDS ({args.variant})")
        if args.errors:
            show_errors(dev)
    elif args.test:
        digest = hashlib.sha256(module.read_bytes()).hexdigest()
        if lock.exists() and not args.force:
            sys.exit(f"the test words were already scored ({lock.name}: {lock.read_text().strip()}); "
                     "scoring them again after changing the rules would make them a second development set")
        lock.write_text(f"{module.name} sha256 {digest}\n")
        decide(test, args.variant, **kw)
        report(test, f"TEST WORDS ({args.variant}; scored once)")
        if args.errors:
            show_errors(test)
    else:
        if not lock.exists():
            sys.exit("score the test words first (--test)")
        decide(rows, args.variant, **kw)
        report(rows, f"ALL 100 WORDS ({args.variant}; development words informed the rules)")
        if args.errors:
            show_errors(rows)
        print("\nfilter module hash at the test run:", lock.read_text().strip())
        print("filter module hash now           :", hashlib.sha256(module.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
