"""D029 (c): do the zero-shot, few-shot and instruct definitions of the same entries use the same defining words?

Gemma3 1B, 4B, 12B, 27B; default filter, first sentence, fixed 2,750-lemma vocabulary. An entry is one of the 3,000 rows of
the word list; S(s) is the set of entries whose zero-shot record survives the filter (D029). The defining words of an
entry are the in-vocabulary lemmas that `normalize` finds in its first sentence, the headword's lemma excluded.

  1. (c1) Jaccard index of the defining-word sets of the same entry in two conditions, on the entries kept in all three
     conditions (E(s)): zero-shot / instruct, few-shot / instruct, zero-shot / few-shot.
  2. (c2) Descriptors per condition on E(s), no reading.
  3. (c3) Recovery of the instruct dictionary's mutual pairs at equal coverage: T(s) = mutual pairs of the instruct graph whose
     two words both have a surviving zero-shot entry; share of T(s) that are mutual pairs in the zero-shot graph and in the
     few-shot graph limited to S(s) (the fsS graph of D029 (b)); Clopper-Pearson intervals, exact McNemar test.
  4. The readings fixed in D029, applied mechanically.
  5. Added after sections 1-4 had been read, and not part of D029: how many different pairs the pooled pair-instances of
     section 3 are (pairs recur across sizes), and the McNemar test with each different pair counted once.

Needs results_2026-10-02_Local/d029_survivor_restriction/ (restriction_sets.json and graphs/d029__fsS_*.json), which the
D029 run writes before it starts the null model. Output is recorded in outputs/28_defining_words.txt.
"""
import collections
import json
import os
import statistics
import sys
from pathlib import Path

from scipy.stats import beta, binomtest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(ROOT)

from experiments import d029_survivor_restriction as d  # noqa: E402
from rs_dic_llm.filtered_definitions import VALID_STATUSES, fixed_vocabulary  # noqa: E402
from rs_dic_llm.normalize import normalize  # noqa: E402
from rs_dic_llm.sampling import load_word_list  # noqa: E402

RES = ROOT / "results_2026-10-01_Local"
D029 = ROOT / "results_2026-10-02_Local" / "d029_survivor_restriction"
FRAME = {"define", "mean", "refer", "describe", "phrase", "use"}  # D025: the six frame words that are nodes
COND = {"zs": "zero-shot", "fs": "few-shot", "it": "instruct"}
SIZES = d.SIZES

vocab = fixed_vocabulary(load_word_list(d.e1.WORD_LIST))
sets = json.loads((D029 / "restriction_sets.json").read_text(encoding="utf-8"))


def kept(record):
    return record.get("status", "ok") in VALID_STATUSES and bool(record["definition"])


def mutual_pairs(path):
    g = json.loads(Path(path).read_text(encoding="utf-8"))
    edges = {tuple(e) for e in g["edges"]}
    return {tuple(sorted((u, v))) for (u, v) in edges if (v, u) in edges and u != v}


def jaccard(a, b):
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def overlap(a, b):
    return len(a & b) / min(len(a), len(b))


def cp(x, n, level=0.95):
    a = (1 - level) / 2
    return (beta.ppf(a, x, n - x + 1) if x > 0 else 0.0), (beta.ppf(1 - a, x + 1, n - x) if x < n else 1.0)


# ---------------------------------------------------------------------------------------------------------------------
# data
DATA = {}
for s in SIZES:
    raw = d.load_conditions(s)
    filt, _ = d.filtered_conditions(raw)
    S = d.survivors(filt["zs"])
    assert d.set_hash(S) == sets[s]["survivors_sha256"], f"{s}: survivors differ from the D029 run"
    E = [i for i in S if kept(filt["fs"][i]) and kept(filt["it"][i])]
    words = {c: {i: set(normalize(filt[c][i]["definition"], vocab)) - {filt[c][i]["lemma"]} for i in E} for c in COND}
    DATA[s] = {"S": S, "E": E, "words": words, "lemma": {i: filt["zs"][i]["lemma"] for i in range(d.N_ENTRIES)}}

print("1. (c1) DEFINING-WORD SETS OF THE SAME ENTRY IN TWO CONDITIONS: Jaccard index (E = entries kept in all three conditions)")
print(f"   {'size':>4} {'|S|':>6} {'|E|':>6}   {'pair':<22}{'mean J':>8}{'median J':>10}{'both empty':>12}")
C1 = {}
for s in SIZES:
    w = DATA[s]["words"]
    for a, b in (("zs", "it"), ("fs", "it"), ("zs", "fs")):
        js = [jaccard(w[a][i], w[b][i]) for i in DATA[s]["E"]]
        empty = sum(1 for i in DATA[s]["E"] if not (w[a][i] | w[b][i]))
        C1[(s, a, b)] = statistics.mean(js)
        print(f"   {s:>4} {len(DATA[s]['S']):>6} {len(DATA[s]['E']):>6}   {COND[a] + ' / ' + COND[b]:<22}{statistics.mean(js):8.3f}{statistics.median(js):10.3f}{empty:12d}")

print("\n2. (c2) DESCRIPTORS OF THE DEFINING WORDS PER CONDITION (on E, no reading)")
print(f"   {'size':>4} {'condition':<10}{'words/record':>13}{'median':>8}{'no word':>9}{'distinct':>10}{'top-5 share':>13}{'frame word':>12}")
for s in SIZES:
    for c in COND:
        sets_c = [DATA[s]["words"][c][i] for i in DATA[s]["E"]]
        n_words = [len(x) for x in sets_c]
        count = collections.Counter(w for x in sets_c for w in x)
        total = sum(count.values())
        top5 = sum(v for _, v in count.most_common(5)) / total
        frame = sum(1 for x in sets_c if x & FRAME) / len(sets_c)
        print(f"   {s:>4} {COND[c]:<10}{statistics.mean(n_words):13.2f}{statistics.median(n_words):8.0f}{sum(1 for n in n_words if n == 0) / len(n_words):9.3f}"
              f"{len(count):10d}{top5:13.3f}{frame:12.3f}")
print("   (words/record = defining words per kept record; no word = share of records with none; top-5 share = share of all defining-word"
      " occurrences carried by the five most used words;\n    frame word = share of records containing one of define, mean, refer, describe, phrase, use)")
print("\n   Overlap coefficient |A and B| / min(|A|, |B|), mean over the entries where both sets are non-empty")
for s in SIZES:
    w = DATA[s]["words"]
    parts = []
    for a, b in (("zs", "it"), ("fs", "it"), ("zs", "fs")):
        vals = [overlap(w[a][i], w[b][i]) for i in DATA[s]["E"] if w[a][i] and w[b][i]]
        parts.append(f"{COND[a]}/{COND[b]} {statistics.mean(vals):.3f} (n {len(vals)})")
    print(f"   {s:>4}: " + "; ".join(parts))
print("\n   The ten most used defining words per condition (number of records)")
for s in SIZES:
    for c in COND:
        count = collections.Counter(w for i in DATA[s]["E"] for w in DATA[s]["words"][c][i])
        ranked = sorted(count.items(), key=lambda kv: (-kv[1], kv[0]))  # ties alphabetical, so the output does not depend on hash order
        print(f"   {s:>4} {COND[c]:<10}" + ", ".join(f"{w} {n}" for w, n in ranked[:10]))

# ---------------------------------------------------------------------------------------------------------------------
print("\n3. (c3) RECOVERY OF THE INSTRUCT MUTUAL PAIRS AT EQUAL COVERAGE")
print("   T = mutual pairs of the instruct graph (whole word list) whose two words both have a surviving zero-shot entry.")
print("   zero-shot graph vs fsS graph (E3 limited to S, the same entries); sensitivity: the whole E3 graph.")
print(f"   {'size':>4}{'instruct pairs':>16}{'|T|':>6}{'zs':>5}{'r_zs':>8}{'95 % CP':>16}{'fsS':>6}{'r_fs':>8}{'95 % CP':>16}{'only fsS':>10}{'only zs':>9}{'McNemar p':>11}{'whole E3':>10}{'r':>7}")
tot = collections.Counter()
T_by, Z_by, F_by = {}, {}, {}
for s in SIZES:
    it = mutual_pairs(RES / "e2_filtered_default_main_32x" / "graphs" / f"main__Gemma3-{s}.json")
    zs = mutual_pairs(RES / "e2_filtered_default_main_32x" / "graphs" / f"main__Gemma3-{s}-pt.json")
    fs_all = mutual_pairs(RES / "e2_filtered_default_controls_32x" / "graphs" / f"e3__Gemma3-{s}-pt.json")
    fs_s = mutual_pairs(D029 / "graphs" / f"d029__fsS_{s}.json")
    covered = {DATA[s]["lemma"][i] for i in DATA[s]["S"]}
    T = {p for p in it if p[0] in covered and p[1] in covered}
    n = len(T)
    T_by[s], Z_by[s], F_by[s] = T, T & zs, T & fs_s
    x_zs, x_fs, x_all = len(T & zs), len(T & fs_s), len(T & fs_all)
    only_fs, only_zs = len((T & fs_s) - zs), len((T & zs) - fs_s)
    p = binomtest(min(only_fs, only_zs), only_fs + only_zs, 0.5).pvalue if only_fs + only_zs else 1.0
    lz, hz = cp(x_zs, n)
    lf, hf = cp(x_fs, n)
    print(f"   {s:>4}{len(it):16d}{n:6d}{x_zs:5d}{x_zs / n:8.3f}{'[%.3f, %.3f]' % (lz, hz):>16}{x_fs:6d}{x_fs / n:8.3f}{'[%.3f, %.3f]' % (lf, hf):>16}"
          f"{only_fs:10d}{only_zs:9d}{p:11.4f}{x_all:10d}{x_all / n:7.3f}")
    for k, v in (("n", n), ("x_zs", x_zs), ("x_fs", x_fs), ("x_all", x_all), ("only_fs", only_fs), ("only_zs", only_zs)):
        tot[k] += v
    print(f"        mutual pairs in the graph: zero-shot {len(zs)}, fsS {len(fs_s)}, whole E3 {len(fs_all)}; "
          f"of the zero-shot / fsS pairs, instruct pairs: {len(zs & it)} / {len(fs_s & it)}")

n = tot["n"]
p_pool = binomtest(min(tot["only_fs"], tot["only_zs"]), tot["only_fs"] + tot["only_zs"], 0.5).pvalue if tot["only_fs"] + tot["only_zs"] else 1.0
lz, hz = cp(tot["x_zs"], n)
lf, hf = cp(tot["x_fs"], n)
print(f"   pooled (descriptive: pairs recur across sizes) |T| {n}: zero-shot {tot['x_zs']} = {tot['x_zs'] / n:.3f} [{lz:.3f}, {hz:.3f}];"
      f" fsS {tot['x_fs']} = {tot['x_fs'] / n:.3f} [{lf:.3f}, {hf:.3f}]; only fsS {tot['only_fs']}, only zero-shot {tot['only_zs']}, exact McNemar p {p_pool:.2e};"
      f" whole E3 {tot['x_all']} = {tot['x_all'] / n:.3f}")

# ---------------------------------------------------------------------------------------------------------------------
print("\n4. THE READINGS OF D029, APPLIED")
ratios = {}
for s in SIZES:
    ratios[s] = C1[(s, "fs", "it")] / C1[(s, "zs", "it")] if C1[(s, "zs", "it")] > 0 else float("inf")
n15 = sum(1 for r in ratios.values() if r >= 1.5)
n125 = sum(1 for r in ratios.values() if r < 1.25)
v1 = "the zero-shot definitions use other defining words than the few-shot ones" if n15 >= 3 else (
    "no difference in the defining words between zero-shot and few-shot definitions" if n125 >= 3 else "mixed")
print("   (c1) mean J(few-shot, instruct) / mean J(zero-shot, instruct): " + ", ".join(f"{s} {r:.2f}" for s, r in ratios.items())
      + f"; sizes at 1.5 or more: {n15}, below 1.25: {n125}")
print(f"        -> {v1}")
r_zs, r_fs = tot["x_zs"] / n, tot["x_fs"] / n
if r_fs >= 2 * r_zs and p_pool < 0.05:
    v3 = "content differs"
elif r_fs < 1.25 * r_zs:
    v3 = "content does not differ"
else:
    v3 = "mixed"
print(f"   (c3) pooled r_fs / r_zs = {r_fs / r_zs if r_zs else float('inf'):.2f} (r_fs {r_fs:.3f}, r_zs {r_zs:.3f}), exact McNemar p {p_pool:.2e}")
print(f"        -> {v3}")

# ---------------------------------------------------------------------------------------------------------------------
print("\n5. RECURRENCE OF PAIRS ACROSS SIZES (added after sections 1-4 had been read; not part of D029; a check on the pooled test of section 3)")
all_t = set().union(*T_by.values())
rec_zs = set().union(*Z_by.values())
rec_fs = set().union(*F_by.values())
b5, c5 = len(rec_fs - rec_zs), len(rec_zs - rec_fs)
p5 = binomtest(min(b5, c5), b5 + c5, 0.5).pvalue if b5 + c5 else 1.0
print(f"   {tot['n']} pair-instances in the four T(s) are {len(all_t)} different pairs; recovered in a zero-shot graph at some size: {len(rec_zs)}; "
      f"in an fsS graph at some size: {len(rec_fs)}")
print(f"   each different pair counted once: recovered only by fsS {b5}, only by zero-shot {c5}, exact McNemar p {p5:.4f}")
print(f"   different pairs recovered only by fsS: {sorted(rec_fs - rec_zs)}")
print(f"   different pairs recovered in a zero-shot graph: {sorted(rec_zs)}")
