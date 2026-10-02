"""Tables of the manuscript draft (manuscript/draft_v0.md), computed from the per-graph results of the null-model runs.

Reads the same result folders as scripts 17 and 19 (unfiltered E1d, default filter, strict filter, stored text, frame words
removed) and, for the pair-type table, the recorded output of script 20. Prints Markdown tables and, at the end, the
numbers the text quotes. The interval formulas are those of script 19 (exact Poisson range of an observed count divided by
the null mean, floor 0.5; exact conditional range of a ratio of two such rates, null means taken as known), and the script
checks itself against values recorded in the registry before it prints anything.
Output: outputs/24_manuscript_tables.md
"""
import glob
import json
import re
import statistics as st
import sys
from pathlib import Path

from scipy.stats import beta, chi2

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
RES = ROOT / "results_2026-10-01_Local"
OUT20 = ROOT / "research" / "audit_scripts" / "outputs" / "20_pair_types.txt"
RUNS = {
    "unfiltered": ("e1d_null_unfiltered_32x", "e1d_null_unfiltered_32x_controls"),
    "default": ("e2_filtered_default_main_32x", "e2_filtered_default_controls_32x"),
    "strict": ("e2_filtered_strict_main_32x", "e2_filtered_strict_e3_32x"),
    "stored": ("e2_filtered_default_storedtext_main_32x", None),
    "frame": ("e2_frame_words_removed_default_main_32x", None),
}
SIZES = ("1B", "4B", "12B", "27B")


def load(folder):
    out = {}
    if folder:
        for p in glob.glob(str(RES / folder / "results" / "*.json")):
            r = json.load(open(p, encoding="utf-8"))
            out[r["key"]] = r
    return out


DATA = {v: {**load(a), **load(b)} for v, (a, b) in RUNS.items()}


def poisson_ci(k, level=0.95):
    a = (1 - level) / 2
    return (0.0 if k == 0 else chi2.ppf(a, 2 * k) / 2), chi2.ppf(1 - a, 2 * (k + 1)) / 2


def r_range(rec):
    obs, null = rec["observed"]["cycles_2"], max(rec["null_mean"]["cycles_2"], 0.5)
    lo, hi = poisson_ci(obs)
    return obs / null, lo / null, hi / null


def ratio_ci(a, b, level=0.95):
    """Exact conditional range of rate a / rate b for two counts with known exposures (the null means, floor 0.5)."""
    xa, xb = a["observed"]["cycles_2"], b["observed"]["cycles_2"]
    ea, eb = max(a["null_mean"]["cycles_2"], 0.5), max(b["null_mean"]["cycles_2"], 0.5)
    n = xa + xb
    alpha = (1 - level) / 2
    p_lo = beta.ppf(alpha, xa, n - xa + 1) if xa > 0 else 0.0
    p_hi = beta.ppf(1 - alpha, xa + 1, n - xa) if xb > 0 else 1.0
    odds = lambda p: p / (1 - p) if p < 1 else float("inf")
    scale = eb / ea
    return (xa / ea) / (xb / eb), odds(p_lo) * scale, odds(p_hi) * scale


def conservative(a, b):
    ra, alo, ahi = r_range(a)
    rb, blo, bhi = r_range(b)
    return ra / rb, alo / bhi, (ahi / blo if blo > 0 else float("inf"))


# --- self-check against values recorded in the registry (default filter) -------------------------------------------
chk = ratio_ci(DATA["default"]["main__Gemma3-4B"], DATA["default"]["main__Gemma3-4B-pt"])
assert [round(x, 1) for x in chk] == [3.3, 1.7, 7.1], chk
chk = ratio_ci(DATA["default"]["main__Gemma3-1B"], DATA["default"]["e3__Gemma3-1B-pt"])
assert [round(x, 2) for x in chk] == [1.91, 1.13, 3.24], chk
chk = r_range(DATA["default"]["main__Gemma3-27B-pt"])
assert [round(x, 1) for x in chk] == [4.9, 2.7, 8.2], chk


def size_b(key):
    m = re.search(r"-(\d+(?:\.\d+)?)([MB])", key)
    return float(m.group(1)) * (0.001 if m.group(2) == "M" else 1.0)


def family(key):
    return key[6:].split("-")[0]


is_base = lambda k: k.endswith("-pt")
is_wn = lambda k: k.endswith("__wordnet")
main_keys = [k for k in DATA["default"] if k.startswith("main__")]
instruct = [k for k in main_keys if not is_base(k) and not is_wn(k)]
base = [k for k in main_keys if is_base(k)]
assert len(instruct) == 17 and len(base) == 5, (len(instruct), len(base))
R = lambda v, k: DATA[v][k]["reciprocity_excess"]
fmt_range = lambda lo, hi: f"[{lo:.1f}, {hi:.1f}]"

# --- Table 1 -------------------------------------------------------------------------------------------------------------
print("\n**Table 1.** Claim 1: z-scores of the kernel ratio and the circulation rate against the degree-preserving null, by group (median, with the number of graphs "
      "below 0 / beyond -2 / beyond +2).\n")
print("| Measure | Group | n | Unfiltered | Default filter | Strict filter |")
print("|---|---|---:|---|---|---|")
groups = (("17 instruct models", instruct), ("5 pretrained models", base), ("WordNet", ["main__wordnet"]))
for label, key in (("Kernel ratio", "kernel_ratio"), ("Circulation rate", "circulation_rate")):
    for gname, keys in groups:
        cells = []
        for v in ("unfiltered", "default", "strict"):
            z = [DATA[v][k]["z"][key] for k in keys]
            cells.append(f"{st.median(z):+.2f} ({sum(x < 0 for x in z)} / {sum(x < -2 for x in z)} / {sum(x > 2 for x in z)})")
        print(f"| {label} | {gname} | {len(keys)} | " + " | ".join(cells) + " |")

# --- Table 2 -------------------------------------------------------------------------------------------------------------
print("\n**Table 2.** Cycle lengths in the default-filter graphs: observed number of cycles / mean number in the null, summed over the graphs of a group.\n")
print("| Group | 2 | 3 | 4 | 5 | 6 | 7 |")
print("|---|---:|---:|---:|---:|---:|---:|")
for gname, keys in (("17 instruct models", instruct), ("5 pretrained models", base), ("WordNet", ["main__wordnet"])):
    cells = []
    for L in range(2, 8):
        o = sum(DATA["default"][k]["cycle_hist_observed_vs_null"][str(L)]["observed"] for k in keys)
        n = sum(DATA["default"][k]["cycle_hist_observed_vs_null"][str(L)]["null_mean"] for k in keys)
        cells.append(f"{o} / {n:.0f} = {o / max(n, 1e-9):.2f}x")
    print(f"| {gname} | " + " | ".join(cells) + " |")

# --- Table 3 (parsed from the recorded output of script 20) ------------------------------------------------------------
text20 = OUT20.read_text(encoding="utf-8")
cats = ["synonym", "hypernym", "coordinate", "antonym", "derived form", "other"]


def parse(label):
    line = next(l for l in text20.splitlines() if l.strip().startswith(label))
    n = int(re.search(r"n=\s*(\d+)", line).group(1))
    vals = {}
    for c in cats:
        m = re.search(rf"{c} (\d+) \((\d+) %\)", line)
        vals[c] = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    return n, vals


print("\n**Table 3.** Mutual pairs by WordNet relation (all senses, no part of speech; the first match in the order of the columns decides). Counts, with shares of the "
      "pair occurrences in brackets.\n")
print("| Source | Pair occurrences | Synonym | Hypernym | Sister term | Antonym | Derived form | No direct link |")
print("|---|---:|---:|---:|---:|---:|---:|---:|")
for label, name in (("WordNet graph", "WordNet"), ("instruct models: occurrences", "17 instruct models"),
                    ("few-shot base (E3): occurrences", "Few-shot pretrained (E3)"), ("zero-shot base: occurrences", "Zero-shot pretrained")):
    n, vals = parse(label)
    print(f"| {name} | {n} | " + " | ".join(f"{vals[c][0]} ({vals[c][1]} %)" for c in cats) + " |")

# --- Table 4 ------------------------------------------------------------------------------------------------------------
print("\n**Table 4.** Matched Gemma3 pairs under a zero-shot prompt: R of the instruct model / R of the pretrained model, with the exact conditional 95 % range "
      "of the ratio, under five variants of the analysis.\n")
print("| Size | Instruct R | Pretrained R | Default filter | Unfiltered | Strict filter | Whole stored text | Six frame words removed |")
print("|---|---:|---:|---|---|---|---|---|")
excl1 = excl2 = total = 0
for s in SIZES:
    cells = []
    for v in ("default", "unfiltered", "strict", "stored", "frame"):
        i, b = DATA[v].get(f"main__Gemma3-{s}"), DATA[v].get(f"main__Gemma3-{s}-pt")
        ratio, lo, hi = ratio_ci(i, b)
        total += 1
        excl1 += (lo > 1 or hi < 1)
        excl2 += (lo >= 2 or hi < 2)
        cells.append(f"{ratio:.1f} [{lo:.1f}, {hi:.1f}]")
    i, b = DATA["default"][f"main__Gemma3-{s}"], DATA["default"][f"main__Gemma3-{s}-pt"]
    print(f"| {s} | {R('default', f'main__Gemma3-{s}'):.1f} | {R('default', f'main__Gemma3-{s}-pt'):.1f} | " + " | ".join(cells) + " |")
print(f"\nOver the {total} pair-by-variant comparisons the range excludes 1 in {excl1} and excludes 2 in {excl2}.")

# --- Table 5 ------------------------------------------------------------------------------------------------------------
print("\n**Table 5.** The three-example prompt (E3): R of the pretrained Gemma3 models given three example definitions, against the zero-shot "
      "pretrained model and the instruct model of the same size (default filter). The ratio is instruct R / few-shot R; the exact range is the "
      "conditional range, the conservative range combines the two ends of the Poisson ranges.\n")
print("| Size | Zero-shot pretrained R | Few-shot pretrained R (95 % range) | Instruct R | Instruct / few-shot | Exact range | Conservative range |")
print("|---|---:|---:|---:|---:|---|---|")
g = DATA["default"]["e3__Gemma3-270M-pt"]
rg, lg, hg = r_range(g)
print(f"| 270M | {R('default', 'main__Gemma3-270M-pt'):.1f} | {rg:.1f} {fmt_range(lg, hg)} | no cycles (D011) | -- | -- | -- |")
e3_rows = {}
for s in SIZES:
    f, i = DATA["default"][f"e3__Gemma3-{s}-pt"], DATA["default"][f"main__Gemma3-{s}"]
    rf, lf, hf = r_range(f)
    ratio, lo, hi = ratio_ci(i, f)
    cr, clo, chi = conservative(i, f)
    e3_rows[s] = (ratio, lo, hi, clo, chi)
    print(f"| {s} | {R('default', f'main__Gemma3-{s}-pt'):.1f} | {rf:.1f} {fmt_range(lf, hf)} | {R('default', f'main__Gemma3-{s}'):.1f} | {ratio:.2f} | "
          f"[{lo:.2f}, {hi:.2f}] | [{clo:.2f}, {chi:.2f}] |")

# --- Tables 6-8 (D029: equal coverage and defining words) -------------------------------------------------------------
D029_RES = ROOT / "results_2026-10-02_Local" / "d029_survivor_restriction"
SETS = json.load(open(D029_RES / "restriction_sets.json", encoding="utf-8"))
X = {}
for p in glob.glob(str(D029_RES / "results" / "*.json")):
    r = json.load(open(p, encoding="utf-8"))
    X[r["key"]] = r
assert len(X) == 28, len(X)

print("\n**Table 6.** Equal coverage (D029). R of the zero-shot pretrained graph and of the few-shot and instruct graphs limited to the entries whose "
      "zero-shot record survived the filter (the same entries), with the exact Poisson 95 % range, and the exact conditional range of instruct / zero-shot. "
      "The last three columns are the few-shot graph limited to five random sets of entries of the same size (smallest to largest R) and the graphs of the whole word list.\n")
print("| Size | Entries kept (of 3,000) | Zero-shot pretrained | Few-shot, same entries | Instruct, same entries | Instruct / zero-shot (exact range) | Few-shot, five random halves | Few-shot, whole list | Instruct, whole list |")
print("|---|---:|---|---|---|---|---|---:|---:|")
n_incl = 0
for s in SIZES:
    z, f, i = DATA["default"][f"main__Gemma3-{s}-pt"], X[f"d029__fsS_{s}"], X[f"d029__itS_{s}"]
    (rz, zlo, zhi), (rf, flo, fhi), (ri, ilo, ihi) = r_range(z), r_range(f), r_range(i)
    ratio, lo, hi = ratio_ci(i, z)
    n_incl += (lo <= 1 <= hi)
    rands = sorted(X[f"d029__fsR{k}_{s}"]["reciprocity_excess"] for k in range(1, 6))
    print(f"| {s} | {SETS[s]['survivors']:,} | {rz:.1f} {fmt_range(zlo, zhi)} ({z['observed']['cycles_2']} pairs) | {rf:.1f} {fmt_range(flo, fhi)} ({f['observed']['cycles_2']}) | "
          f"{ri:.1f} {fmt_range(ilo, ihi)} ({i['observed']['cycles_2']}) | {ratio:.2f} [{lo:.2f}, {hi:.2f}] | {rands[0]:.1f} to {rands[-1]:.1f} | "
          f"{R('default', f'e3__Gemma3-{s}-pt'):.1f} | {R('default', f'main__Gemma3-{s}'):.1f} |")
print(f"\nThe exact range of instruct / zero-shot includes 1 at {n_incl} of 4 sizes.")

OUT28 = ROOT / "research" / "audit_scripts" / "outputs" / "28_defining_words.txt"
t28 = OUT28.read_text(encoding="utf-8")
c3_rows = re.findall(r"^\s+(\d+B)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+\[[\d., ]+\]\s+(\d+)\s+([\d.]+)\s+\[[\d., ]+\]\s+(\d+)\s+(\d+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s*$", t28, re.M)
assert [r[0] for r in c3_rows] == list(SIZES), c3_rows
pool = re.search(r"pooled .*\|T\| (\d+): zero-shot (\d+) = ([\d.]+) \[([\d.]+), ([\d.]+)\]; fsS (\d+) = ([\d.]+) \[([\d.]+), ([\d.]+)\]; only fsS (\d+), only zero-shot (\d+), exact McNemar p ([\d.e+-]+)", t28)
dist = re.search(r"are (\d+) different pairs; recovered in a zero-shot graph at some size: (\d+); in an fsS graph at some size: (\d+)", t28)
dist_p = re.search(r"recovered only by fsS (\d+), only by zero-shot (\d+), exact McNemar p ([\d.]+)", t28)
assert pool and dist and dist_p

print("\n**Table 7.** Mutual pairs of the instruct graph that the other graphs contain, at equal coverage (D029). At risk: mutual pairs of the instruct graph "
      "(whole word list) whose two words both have a surviving zero-shot entry. Zero-shot: the zero-shot graph; few-shot: the few-shot graph limited to the "
      "same entries. Exact McNemar test on the pairs found in one graph and not in the other.\n")
print("| Size | Instruct pairs | At risk | Zero-shot | Few-shot, same entries | Only few-shot | Only zero-shot | Exact McNemar p |")
print("|---|---:|---:|---|---|---:|---:|---:|")
for (s, n_it, n_t, x_zs, r_zs, x_fs, r_fs, o_fs, o_zs, p_, x_all, r_all) in c3_rows:
    print(f"| {s} | {n_it} | {n_t} | {x_zs} ({100 * float(r_zs):.0f} %) | {x_fs} ({100 * float(r_fs):.0f} %) | {o_fs} | {o_zs} | {float(p_):.3f} |")
n_t, x_zs, r_zs, zlo, zhi, x_fs, r_fs, flo, fhi, o_fs, o_zs, p_ = pool.groups()
print(f"| Pooled (descriptive: pairs recur across sizes) | -- | {n_t} | {x_zs} ({100 * float(r_zs):.0f} %; 95 % range {100 * float(zlo):.0f}-{100 * float(zhi):.0f} %) | "
      f"{x_fs} ({100 * float(r_fs):.0f} %; {100 * float(flo):.0f}-{100 * float(fhi):.0f} %) | {o_fs} | {o_zs} | {float(p_):.4f} |")
print(f"| Each different pair once ({dist.group(1)} pairs) | -- | {dist.group(1)} | {dist.group(2)} | {dist.group(3)} | {dist_p.group(1)} | {dist_p.group(2)} | {float(dist_p.group(3)):.3f} |")

c1 = {(m[0], m[3]): (float(m[4]), float(m[5])) for m in re.findall(r"^\s+(\d+B)\s+(\d+)\s+(\d+)\s+(zero-shot / instruct|few-shot / instruct|zero-shot / few-shot)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s*$", t28, re.M)}
c2 = {(m[0], m[1]): m[2:] for m in re.findall(r"^\s+(\d+B) (zero-shot|few-shot|instruct)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s*$", t28, re.M)}
assert len(c1) == 12 and len(c2) == 12, (len(c1), len(c2))
c1_ratio = re.search(r"mean J\(few-shot, instruct\) / mean J\(zero-shot, instruct\): 1B ([\d.]+), 4B ([\d.]+), 12B ([\d.]+), 27B ([\d.]+)", t28)
assert c1_ratio
c1_ratio = dict(zip(SIZES, (float(x) for x in c1_ratio.groups())))  # the ratios of script 28, from unrounded means
print("\n**Table 8.** Defining words of the same entries in the three conditions (D029 (c); entries kept in all three conditions; the defining words of an entry are the "
      "in-vocabulary lemmas of its first sentence, the headword excluded). Jaccard index of the defining-word sets with the instruct definition of the same entry (mean); "
      "share of records that contain one of six frame words (define, mean, refer, describe, phrase, use); share of all defining-word occurrences carried by the five most used words.\n")
print("| Size | Mean Jaccard with instruct: zero-shot | few-shot | few-shot / zero-shot | Frame word: zero-shot | few-shot | instruct | Top-5 words: zero-shot | few-shot | instruct |")
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for s in SIZES:
    jz, jf = c1[(s, "zero-shot / instruct")][0], c1[(s, "few-shot / instruct")][0]
    fr = [100 * float(c2[(s, c)][5]) for c in ("zero-shot", "few-shot", "instruct")]
    tp = [100 * float(c2[(s, c)][4]) for c in ("zero-shot", "few-shot", "instruct")]
    print(f"| {s} | {jz:.3f} | {jf:.3f} | {c1_ratio[s]:.2f} | {fr[0]:.0f} % | {fr[1]:.0f} % | {fr[2]:.0f} % | {tp[0]:.0f} % | {tp[1]:.0f} % | {tp[2]:.0f} % |")

# --- Table A1 ------------------------------------------------------------------------------------------------------------
print("\n**Table A1.** Definition graphs of the 23 analysed sources (default filter, first sentence; 2,750-lemma node set). "
      "R = observed mutual pairs / null mean (floor 0.5); the 95 % range is the exact Poisson range of the observed number of mutual pairs "
      "divided by the null mean; the last column is R of the unfiltered graphs (stored text). "
      "The zero-shot pretrained graphs cover about half of the entries (Section 4.3.5), which lowers their R.\n")
print("| Source | Edges | Mutual pairs | Null mean | R | 95 % range | R unfiltered |")
print("|---|---:|---:|---:|---:|---|---:|")
order = []
for fam, label in (("Gemma3", "Gemma3 instruct"), ("Qwen2.5", "Qwen2.5 instruct"), ("Qwen3", "Qwen3 instruct")):
    keys = sorted((k for k in instruct if family(k) == fam), key=lambda k: (size_b(k), k))
    order.append((label, keys))
order.append(("Gemma3 pretrained (zero-shot)", sorted(base, key=size_b)))
order.append(("Human baseline", ["main__wordnet"]))
for label, keys in order:
    print(f"| *{label}* | | | | | | |")
    for k in keys:
        rec = DATA["default"][k]
        r, lo, hi = r_range(rec)
        unf = DATA["unfiltered"].get(k)
        print(f"| {k[6:]} | {rec['n_edges']} | {rec['observed']['cycles_2']} | {rec['null_mean']['cycles_2']:.2f} | {r:.1f} | {fmt_range(lo, hi)} | "
              f"{unf['reciprocity_excess']:.1f} |" if unf else f"| {k[6:]} | {rec['n_edges']} | {rec['observed']['cycles_2']} | {rec['null_mean']['cycles_2']:.2f} | {r:.1f} | {fmt_range(lo, hi)} | -- |")

# --- numbers quoted in the text -------------------------------------------------------------------------------------------
print("\n**Numbers quoted in the text** (default filter unless stated)\n")
for v in ("unfiltered", "default", "strict"):
    ri = [R(v, k) for k in instruct]
    rb = [R(v, k) for k in base]
    wn = R(v, "main__wordnet")
    above = sum(x > wn for x in ri)
    print(f"- {v}: instruct R {min(ri):.1f}-{max(ri):.1f} (median {st.median(ri):.1f}); pretrained {min(rb):.1f}-{max(rb):.1f} (median {st.median(rb):.1f}); "
          f"WordNet {wn:.1f}; instruct models above WordNet: {above} of 17")
lo_i = min(instruct, key=lambda k: R("default", k))
hi_b = max(base, key=lambda k: R("default", k))
print(f"- default: lowest instruct {lo_i[6:]} {R('default', lo_i):.1f} {fmt_range(*r_range(DATA['default'][lo_i])[1:])}; highest pretrained {hi_b[6:]} {R('default', hi_b):.1f} "
      f"{fmt_range(*r_range(DATA['default'][hi_b])[1:])}")
wn_r = R("default", "main__wordnet")
above = [k for k in instruct if r_range(DATA["default"][k])[1] > wn_r]
below = [k for k in instruct if r_range(DATA["default"][k])[2] < wn_r]
print(f"- default: instruct models whose 95 % range lies entirely above WordNet's R ({wn_r:.1f}): {len(above)} ({', '.join(k[6:] for k in above)}); "
      f"entirely below: {len(below)} ({', '.join(k[6:] for k in below)}); the other {17 - len(above) - len(below)} ranges contain it")
print(f"- mutual pairs of the filtered pretrained graphs: {sorted(DATA['default'][k]['observed']['cycles_2'] for k in base)}; edges {sorted(DATA['default'][k]['n_edges'] for k in base)}")
print(f"- mutual pairs of the instruct graphs: {min(DATA['default'][k]['observed']['cycles_2'] for k in instruct)}-{max(DATA['default'][k]['observed']['cycles_2'] for k in instruct)}; "
      f"WordNet {DATA['default']['main__wordnet']['observed']['cycles_2']}")
print(f"- E3 few-shot R by size (270M, 1B, 4B, 12B, 27B): " + ", ".join(f"{R('default', f'e3__Gemma3-{s}-pt'):.1f}" for s in ("270M",) + SIZES))
print("- E3 conservative / exact ranges include 1 at 4B, 12B, 27B: " + ", ".join(f"{s}: exact {'yes' if e3_rows[s][1] <= 1 <= e3_rows[s][2] else 'no'}, "
      f"conservative {'yes' if e3_rows[s][3] <= 1 <= e3_rows[s][4] else 'no'}" for s in SIZES))
