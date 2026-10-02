"""Tables of manuscript/draft_v2.md (draft v1 and its tables, made by script 24, are kept unchanged).

What changed against v1: R is computed against the directed double-edge swap null (D032) and the values of the paper's first null (networkx `directed_edge_swap`, three-edge moves) sit
beside them; raw counts (observed mutual pairs / null mean) sit beside every R; the null itself (Section 4.3), the controls (D034), the scale tests (D031, D032) and the closed
sub-dictionaries (D030) have tables of their own; the five variants of the matched pairs (Table A2) are a first-null table in the appendix; the table of defining words moves to the
appendix. Numbering follows the order of appearance in v2:

   1  z-scores of kernel ratio and circulation rate, both nulls               (stored three-edge results; D033)
   2  mutual pairs and R by group, both nulls                                 (stored three-edge results; D032)
   3  cycle lengths, both nulls                                               (stored three-edge results; D033)
   4  pair types                                                              (script 24, parsed from outputs/20_pair_types.txt)
   5  the two nulls on eight graphs: pairs per replicate and observed pairs kept (D032 persistence run and D032 main run)
   6  coverage: R of random halves against the whole few-shot graph, both nulls (D029, D030, D032)
   7  the prompt controls, both nulls                                         (parsed from outputs/38_controls_double_swap.txt)
   8  scale: rank correlations within families, both nulls                    (parsed from outputs/31_scale_convergence.txt and 36_double_swap_readings.txt)
   9  matched Gemma 3 pairs as built, zero-shot                               (D032)
  10  the same entries                                                        (D029 graphs, D032)
  11  instruct pairs contained at equal coverage                              (parsed from outputs/28_defining_words.txt)
  12  few-shot prompt                                                         (D032)
  A1 per-graph results   A2 the five variants of Table 9 (first null; not re-run)   A3 defining words (parsed from outputs/28_defining_words.txt)   A4 closed sub-dictionaries (D030, D032)
  "Numbers quoted in the text" closes the output.

Output: outputs/33_manuscript_tables_v2.md. A table whose source run has not finished is replaced by a line "(Table N not printed: ...)".
"""
import glob
import json
import re
import statistics as st
import subprocess
import sys
from pathlib import Path

from scipy.stats import beta, chi2

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")
RES = ROOT / "results_2026-10-01_Local"
R2 = ROOT / "results_2026-10-02_Local"
OUT = ROOT / "research" / "audit_scripts" / "outputs"
SIZES = ("1B", "4B", "12B", "27B")
RUNS = {
    "unfiltered": ("e1d_null_unfiltered_32x", "e1d_null_unfiltered_32x_controls"),
    "default": ("e2_filtered_default_main_32x", "e2_filtered_default_controls_32x"),
    "strict": ("e2_filtered_strict_main_32x", "e2_filtered_strict_e3_32x"),
    "stored": ("e2_filtered_default_storedtext_main_32x", None),
    "frame": ("e2_frame_words_removed_default_main_32x", None),
}


def load_dir(folder):
    return {r["key"]: r for r in (json.loads(Path(p).read_text(encoding="utf-8")) for p in glob.glob(str(Path(folder) / "results" / "*.json")))}


def load_flat(folder):
    return {r["key"]: r for r in (json.loads(Path(p).read_text(encoding="utf-8")) for p in glob.glob(str(Path(folder) / "*.json")))}


DATA = {v: {**(load_dir(RES / a) if a else {}), **(load_dir(RES / b) if b else {})} for v, (a, b) in RUNS.items()}  # first null (three-edge moves)
X = load_dir(R2 / "d029_survivor_restriction")
assert len(X) == 28, len(X)
SETS = json.load(open(R2 / "d029_survivor_restriction" / "restriction_sets.json", encoding="utf-8"))
C3 = load_dir(R2 / "d030_closed_subdictionaries")
assert len(C3) == 32, len(C3)
NEW = load_flat(R2 / "d032_double_swap_null" / "results")  # double-edge swap null
assert len(NEW) == 88, len(NEW)
D33 = load_flat(R2 / "d033_double_swap_full_stats" / "results")
assert len(D33) == 23, len(D33)


def poisson_ci(k, level=0.95):
    a = (1 - level) / 2
    return (0.0 if k == 0 else chi2.ppf(a, 2 * k) / 2), chi2.ppf(1 - a, 2 * (k + 1)) / 2


obs = lambda rec: rec["observed"]["cycles_2"]
nul = lambda rec: rec["null_mean"]["cycles_2"]
Rf = lambda rec, floor=0.5: obs(rec) / max(nul(rec), floor)  # R with the floor
Rp = lambda rec: obs(rec) / nul(rec)  # R' without it


def r_range(rec, floor=0.5):
    lo, hi = poisson_ci(obs(rec))
    e = max(nul(rec), floor)
    return obs(rec) / e, lo / e, hi / e


def ratio_ci(a, b, level=0.95, floor=0.5):
    """Exact conditional range of rate a / rate b for two counts with known exposures (the null means, floored)."""
    xa, xb, ea, eb = obs(a), obs(b), max(nul(a), floor), max(nul(b), floor)
    n = xa + xb
    al = (1 - level) / 2
    p_lo = beta.ppf(al, xa, n - xa + 1) if xa > 0 else 0.0
    p_hi = beta.ppf(1 - al, xa + 1, n - xa) if xb > 0 else 1.0
    odds = lambda p: p / (1 - p) if p < 1 else float("inf")
    return (xa / ea) / (xb / eb), odds(p_lo) * eb / ea, odds(p_hi) * eb / ea


def conservative(a, b):
    ra, alo, ahi = r_range(a)
    rb, blo, bhi = r_range(b)
    return ra / rb, alo / bhi, (ahi / blo if blo > 0 else float("inf"))


# self-check against values recorded in the registry (first null) and in outputs/36 (double-edge null)
chk = ratio_ci(DATA["default"]["main__Gemma3-4B"], DATA["default"]["main__Gemma3-4B-pt"])
assert [round(x, 1) for x in chk] == [3.3, 1.7, 7.1], chk
chk = ratio_ci(DATA["default"]["main__Gemma3-1B"], DATA["default"]["e3__Gemma3-1B-pt"])
assert [round(x, 2) for x in chk] == [1.91, 1.13, 3.24], chk
chk = ratio_ci(NEW["main__Gemma3-1B"], NEW["main__Gemma3-1B-pt"])
assert [round(x, 1) for x in chk] == [6.4, 2.0, 32.8], chk
assert round(Rf(NEW["main__wordnet"]), 1) == 18.1

cell = lambda rec: f"{Rf(rec):.1f} ({obs(rec)} / {nul(rec):.2f})"
cell_rng = lambda rec: (lambda r: f"{r[0]:.1f} [{r[1]:.1f}, {r[2]:.1f}] ({obs(rec)} / {nul(rec):.2f})")(r_range(rec))
fmt_range = lambda lo, hi: f"[{lo:.1f}, {hi:.1f}]"
size_b = lambda key: float(re.search(r"-(\d+(?:\.\d+)?)([MB])", key).group(1)) * (0.001 if re.search(r"-(\d+(?:\.\d+)?)([MB])", key).group(2) == "M" else 1.0)
family = lambda key: key[6:].split("-")[0]
is_base = lambda k: k.endswith("-pt")
is_wn = lambda k: k.endswith("__wordnet")
main_keys = sorted(k for k in DATA["default"] if k.startswith("main__"))
instruct = [k for k in main_keys if not is_base(k) and not is_wn(k)]
base = [k for k in main_keys if is_base(k)]
fewshot = sorted(k for k in DATA["default"] if k.startswith("e3__"))
assert len(instruct) == 17 and len(base) == 5 and len(fewshot) == 5, (len(instruct), len(base), len(fewshot))
groups = (("17 instruct models", instruct), ("5 pretrained models", base), ("WordNet", ["main__wordnet"]))

# ----------------------------------------------------------------------------- Table 1: kernel ratio and circulation rate
print("**Table 1.** z-scores of the kernel ratio and the circulation rate against the degree-preserving null, by group (median, with the number of graphs below 0 / beyond -2 / beyond +2). "
      "Three-edge null: the null of our first analysis, 100 replicates, three filter variants; double-edge null: 20 replicates, default filter (D033).\n")
print("| Measure | Group | n | Three-edge null: unfiltered | Three-edge null: default filter | Three-edge null: strict filter | Double-edge null: default filter |")
print("|---|---|---:|---|---|---|---|")
zc = lambda z: f"{st.median(z):+.2f} ({sum(x < 0 for x in z)} / {sum(x < -2 for x in z)} / {sum(x > 2 for x in z)})"
for label, key in (("Kernel ratio", "kernel_ratio"), ("Circulation rate", "circulation_rate")):
    for gname, keys in groups:
        cells = [zc([DATA[v][k]["z"][key] for k in keys]) for v in ("unfiltered", "default", "strict")] + [zc([D33[k]["z"][key] for k in keys])]
        print(f"| {label} | {gname} | {len(keys)} | " + " | ".join(cells) + " |")

# ----------------------------------------------------------------------------- Table 2: cycle lengths
print("\n**Table 3.** Cycle lengths in the default-filter graphs: observed number of cycles / mean number in the null, summed over the graphs of a group, against the three-edge null (100 replicates) "
      "and the double-edge null (20 replicates, D033).\n")
print("| Group | Null | 2 | 3 | 4 | 5 | 6 | 7 |")
print("|---|---|---:|---:|---:|---:|---:|---:|")
for gname, keys in groups:
    for tag, data in (("three-edge", DATA["default"]), ("double-edge", D33)):
        cells = []
        for L in range(2, 8):
            o = sum(data[k]["cycle_hist_observed_vs_null"][str(L)]["observed"] for k in keys)
            n = sum(data[k]["cycle_hist_observed_vs_null"][str(L)]["null_mean"] for k in keys)
            cells.append(f"{o} / {n:.0f} = {o / max(n, 1e-9):.2f}x")
        print(f"| {gname} | {tag} | " + " | ".join(cells) + " |")

# ----------------------------------------------------------------------------- Table 3: R by group under both nulls
print("\n**Table 2.** Mutual pairs and R by group (default filter, first sentence, 2,750-lemma node set): the range over the graphs of a group, with the median in brackets. R = observed pairs / null mean "
      "(floor 0.5). Three-edge null: 100 replicates of 32 x |E| swaps; double-edge null: 100 replicates of 64 x |E| swaps (D032). The last column is the ratio of the double-edge R to the three-edge R of the same graph.\n")
print("| Group | n | Mutual pairs | Three-edge null: null mean | Three-edge null: R | Double-edge null: null mean | Double-edge null: R | R double / R three-edge: median (range) |")
print("|---|---:|---|---|---|---|---|---|")
rng = lambda xs, f="{:.1f}": f"{f.format(min(xs))} to {f.format(max(xs))} ({f.format(st.median(xs))})"
for gname, keys in (("17 instruct models", instruct), ("5 pretrained models, zero-shot", base), ("5 pretrained models, few-shot", fewshot), ("WordNet", ["main__wordnet"])):
    ratios = [Rf(NEW[k]) / Rf(DATA["default"][k]) for k in keys]
    pairs_ = [obs(NEW[k]) for k in keys]
    if len(keys) == 1:
        k = keys[0]
        print(f"| {gname} | 1 | {obs(NEW[k])} | {nul(DATA['default'][k]):.2f} | {Rf(DATA['default'][k]):.1f} | {nul(NEW[k]):.2f} | {Rf(NEW[k]):.1f} | {ratios[0]:.2f} |")
    else:
        print(f"| {gname} | {len(keys)} | {min(pairs_)} to {max(pairs_)} | {rng([nul(DATA['default'][k]) for k in keys], '{:.2f}')} | {rng([Rf(DATA['default'][k]) for k in keys])} | "
              f"{rng([nul(NEW[k]) for k in keys], '{:.2f}')} | {rng([Rf(NEW[k]) for k in keys])} | {st.median(ratios):.2f} ({min(ratios):.2f} to {max(ratios):.2f}) |")

# ----------------------------------------------------------------------------- Table 4: pair types, from script 24 (null-free)
t24 = subprocess.run([sys.executable, str(ROOT / "research" / "audit_scripts" / "24_manuscript_tables.py")], capture_output=True, text=True, encoding="utf-8", cwd=ROOT).stdout
assert "**Table A1.**" in t24, "script 24 did not run"
m3 = re.search(r"\*\*Table 3\.\*\*[^\n]*\n\n(?:\|[^\n]*\n)+", t24)
assert m3
print("\n" + m3.group(0).rstrip("\n").replace("**Table 3.**", "**Table 4.**").replace("Few-shot pretrained (E3)", "Few-shot pretrained"))

# ----------------------------------------------------------------------------- Table 5: the two nulls on eight graphs
PERS = R2 / "d032_networkx_persistence" / "persistence.jsonl"
recs = [json.loads(l) for l in PERS.read_text(encoding="utf-8").splitlines() if l.strip()] if PERS.exists() else []
if len(recs) == 160:
    from experiments.d032_convergence import GRAPHS, independent_edge_estimate
    from experiments.d032_double_swap_null import graph_paths

    gp = graph_paths()
    print("\n**Table 5.** The two nulls on eight graphs (default filter): mutual pairs in a replicate and how many of them are pairs of the observed graph. Three-edge null: the first 20 stored replicates "
          "(32 x |E| swaps, stored seeds); double-edge null: 100 replicates (64 x |E| swaps, D032). Independent-edge estimate: the expected number of mutual pairs if every edge u -> v were present with "
          "probability min(1, d_out(u) d_in(v) / |E|) independently.\n")
    print("| Graph | Observed pairs | Independent-edge estimate | Three-edge null: pairs | of them observed pairs | Double-edge null: pairs | of them observed pairs |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    NAMES5 = {"e3__Gemma3-4B-pt": "Gemma 3 4B pretrained, few-shot", "main__Gemma3-1B": "Gemma 3 1B instruct", "main__Gemma3-12B": "Gemma 3 12B instruct", "main__wordnet": "WordNet",
              "main__Gemma3-12B-pt": "Gemma 3 12B pretrained, zero-shot", "d029__fsS_4B": "4B few-shot, entries of the zero-shot survivors", "d030c__fsRC3_4B": "4B few-shot, closed on a random half of the words",
              "d030c__itC_1B": "1B instruct, closed on the survivors' words"}
    for key in GRAPHS:
        rs = [r for r in recs if r["key"] == key]
        assert len(rs) == 20, (key, len(rs))
        o = obs(NEW[key])
        print(f"| {NAMES5[key]} | {o} | {independent_edge_estimate(gp[key]):.2f} | {st.mean(r['pairs'] for r in rs):.2f} | {st.mean(r['kept'] for r in rs):.2f} | {nul(NEW[key]):.2f} | {NEW[key]['kept_observed_pairs_mean']:.2f} |")
else:
    print(f"\n(Table 5 not printed: the persistence run has {len(recs)} of 160 replicates.)")

# ----------------------------------------------------------------------------- Table 6: coverage under both nulls
print("\n**Table 6.** Does R depend on coverage? rho = R' of the few-shot graph limited to a random half of the entries (D029) or induced on a random half of the words (closed, D030) divided by R' of the "
      "whole few-shot graph (R' = observed pairs / null mean, no floor); median of five halves, with the smallest and the largest in brackets. A value near 1 means that the half has the same R' as the whole graph.\n")
print("| Size | Whole few-shot graph: R' three-edge | R' double-edge | Entry-level halves: rho three-edge | rho double-edge | Closed halves: rho three-edge | rho double-edge |")
print("|---|---:|---:|---|---|---|---|")
for s in SIZES:
    wo, wn_ = Rp(DATA["default"][f"e3__Gemma3-{s}-pt"]), Rp(NEW[f"e3__Gemma3-{s}-pt"])
    ent_o = [Rp(X[f"d029__fsR{j}_{s}"]) / wo for j in range(1, 6)]
    ent_n = [Rp(NEW[f"d029__fsR{j}_{s}"]) / wn_ for j in range(1, 6)]
    clo_o = [Rp(C3[f"d030c__fsRC{j}_{s}"]) / wo for j in range(1, 6)]
    clo_n = [Rp(NEW[f"d030c__fsRC{j}_{s}"]) / wn_ for j in range(1, 6)]
    f2 = lambda v: f"{st.median(v):.2f} ({min(v):.2f} to {max(v):.2f})"
    print(f"| {s} | {wo:.1f} | {wn_:.1f} | {f2(ent_o)} | {f2(ent_n)} | {f2(clo_o)} | {f2(clo_n)} |")

# ----------------------------------------------------------------------------- Table 7: the prompt controls (script 38)
p38 = OUT / "38_controls_double_swap.txt"
if p38.exists() and "NOT FINISHED" not in p38.read_text(encoding="utf-8"):
    t38 = p38.read_text(encoding="utf-8")
    pat = re.compile(r"^\s+(three-edge|double-edge)\s+n=\s*(\d+) median ratio\s+([\d.]+) range ([\d.]+)-([\d.]+); median size of the change x([\d.]+), largest x([\d.]+); within a factor 2 in (\d+) of (\d+); control R higher in (\d+) of (\d+)\s*$", re.M)
    blocks = t38.split("E5 (no chat template)")
    rows = {}
    for ds, blk in (("E4", blocks[0]), ("E5", blocks[1].split("READING OF D034")[0])):
        for m in pat.finditer(blk):
            rows[(ds, m.group(1))] = m.groups()[1:]
    assert len(rows) == 4, rows
    print("\n**Table 7.** The prompt controls: R of the control divided by R of the same instruct model in the main run (default filter), for the models where both graphs hold a mutual pair. "
          "Size of the change = the larger of the ratio and its inverse. Length cap: answers of 8 words or fewer; no chat template: the original prompt without the chat template.\n")
    print("| Control | Null | Models | Median ratio (range) | Median size of the change (largest) | Within a factor 2 | Control R higher |")
    print("|---|---|---:|---|---|---:|---:|")
    for ds, name in (("E4", "Length cap"), ("E5", "No chat template")):
        for tag in ("three-edge", "double-edge"):
            n, med, lo, hi, fac, big, w2, wn_, hi_n, _ = rows[(ds, tag)]
            print(f"| {name} | {tag} | {n} | {med} ({lo} to {hi}) | {fac} ({big}) | {w2} of {wn_} | {hi_n} of {n} |")
else:
    print("\n(Table 7 not printed: outputs/38_controls_double_swap.txt is missing or not finished.)")

# ----------------------------------------------------------------------------- Table 8: scale (D031 and D032)
t31 = (OUT / "31_scale_convergence.txt").read_text(encoding="utf-8")
sec2 = t31.split("2. THE READING OF D031")[1].split("3. SENSITIVITY")[0]
old_rows = re.findall(r"^\s+(Gemma3|Qwen2\.5|Qwen3)\s+(\d+)\s+([+-]\d\.\d\d)\s+(\d\.\d\d)\s+(toward|away|none)\s+([+-]\d\.\d\d)\s+(\d\.\d\d)\s+(toward|away|none)", sec2, re.M)
verdict_old = re.search(r"->\s+(NO CONSISTENT APPROACH|CONVERGENCE WITH SIZE IS SUPPORTED|CONVERGENCE IS CONTRADICTED)", sec2).group(1)
t36 = (OUT / "36_double_swap_readings.txt").read_text(encoding="utf-8")
sec6 = t36.split("6. (r5) SCALE")[1].split("7. (r6) WORDNET")[0]
new_rows = re.findall(r"^\s+(Gemma3|Qwen2\.5|Qwen3)\s+(\d+)\s+([+-]\d\.\d\d)\s+(toward|away|none)\s+([+-]\d\.\d\d)\s+(toward|away|none)\s+([+-]\d\.\d\d)\s+([+-]\d\.\d\d)\s*$", sec6, re.M)
verdict_new = re.search(r"->\s+(NO CONSISTENT APPROACH|CONVERGENCE WITH SIZE IS SUPPORTED|CONVERGENCE IS CONTRADICTED)", sec6).group(1)
assert len(old_rows) == 3 and len(new_rows) == 3 and verdict_old == verdict_new == "NO CONSISTENT APPROACH", (old_rows, new_rows, verdict_old, verdict_new)
print("\n**Table 8.** Does R approach WordNet's with model size? Spearman rank correlation with the parameter count within each family, 17 instruct models (default filter; Qwen3-4B-Instruct-2507 left out of the "
      "trends). Labels fixed in advance (D031): the distance |ln R - ln R_WordNet| is *toward* if the correlation is -0.6 or lower, *away* if it is +0.6 or higher; the Jaccard index of the model's mutual pairs "
      "with WordNet's 27 pairs is *toward* if it is +0.6 or higher, *away* if -0.6 or lower. The overlap does not depend on the null. The last two columns are descriptive.\n")
print("| Family | n | Distance in R, three-edge null | Label | Distance in R, double-edge null | Label | Overlap with WordNet's pairs | Label | Observed pairs | Null mean, double-edge |")
print("|---|---:|---:|---|---:|---|---:|---|---:|---:|")
for (fam, n, d1, _p, l1, j1, _p2, lj), (fam2, n2, d2, l2, j2, lj2, pr, nr) in zip(old_rows, new_rows):
    assert fam == fam2 and n == n2 and j1 == j2 and lj == lj2, (fam, j1, j2)
    print(f"| {fam} | {n} | {d1} | {l1} | {d2} | {l2} | {j1} | {lj} | {pr} | {nr} |")
print(f"\nReading fixed in advance: {verdict_old.lower()} under both nulls.")

# ----------------------------------------------------------------------------- Table 9: matched pairs as built (R, double-edge null)
print("\n**Table 9.** Matched Gemma3 pairs under a zero-shot prompt, as built (the pretrained graphs cover about half of the entries; Section 4.6.2): R against the double-edge null with the observed mutual pairs "
      "and the null mean in brackets, and instruct R / pretrained R with the exact conditional 95 % range of the ratio. The last column is the ratio against the three-edge null (our first analysis). "
      "The strict filter and the other variants were not re-run with the double-edge null (Table A2).\n")
print("| Size | Instruct R (pairs / null mean) | Pretrained R (pairs / null mean) | Instruct / pretrained | Same ratio, three-edge null |")
print("|---|---:|---:|---|---|")
for s in SIZES:
    i, b = NEW[f"main__Gemma3-{s}"], NEW[f"main__Gemma3-{s}-pt"]
    r_n = ratio_ci(i, b)
    r_o = ratio_ci(DATA["default"][f"main__Gemma3-{s}"], DATA["default"][f"main__Gemma3-{s}-pt"])
    print(f"| {s} | {cell(i)} | {cell(b)} | {r_n[0]:.1f} [{r_n[1]:.1f}, {r_n[2]:.1f}] | {r_o[0]:.1f} [{r_o[1]:.1f}, {r_o[2]:.1f}] |")

# ----------------------------------------------------------------------------- Table 10: the same entries (D029 graphs, double-edge null)
print("\n**Table 10.** The same entries (D029 graphs, double-edge null): R of the zero-shot pretrained graph and of the few-shot and instruct graphs limited to the entries whose zero-shot record survived the filter, "
      "with the exact Poisson 95 % range, the observed mutual pairs and the null mean in brackets, and the exact conditional range of instruct / zero-shot. The last two columns give the range over five random sets "
      "of entries of the same size for the few-shot graph.\n")
print("| Size | Entries kept (of 3,000) | Zero-shot pretrained | Few-shot, same entries | Instruct, same entries | Instruct / zero-shot (exact range) | Five random halves: R | Five random halves: null mean |")
print("|---|---:|---|---|---|---|---|---|")
n_incl = 0
for s in SIZES:
    z, f, i = NEW[f"main__Gemma3-{s}-pt"], NEW[f"d029__fsS_{s}"], NEW[f"d029__itS_{s}"]
    ratio, lo, hi = ratio_ci(i, z)
    n_incl += (lo <= 1 <= hi)
    halves = [NEW[f"d029__fsR{k}_{s}"] for k in range(1, 6)]
    rr, nn = sorted(Rf(h) for h in halves), sorted(nul(h) for h in halves)
    print(f"| {s} | {SETS[s]['survivors']:,} | {cell_rng(z)} | {cell_rng(f)} | {cell_rng(i)} | {ratio:.2f} [{lo:.2f}, {hi:.2f}] | {rr[0]:.1f} to {rr[-1]:.1f} | {nn[0]:.2f} to {nn[-1]:.2f} |")
print(f"\nThe exact range of instruct / zero-shot includes 1 at {n_incl} of 4 sizes.")

# ----------------------------------------------------------------------------- Table 11: instruct pairs contained at equal coverage (null-free)
t28 = (OUT / "28_defining_words.txt").read_text(encoding="utf-8")
c3_rows = re.findall(r"^\s+(\d+B)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+\[[\d., ]+\]\s+(\d+)\s+([\d.]+)\s+\[[\d., ]+\]\s+(\d+)\s+(\d+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s*$", t28, re.M)
assert [r[0] for r in c3_rows] == list(SIZES), c3_rows
pool = re.search(r"pooled .*\|T\| (\d+): zero-shot (\d+) = ([\d.]+) \[([\d.]+), ([\d.]+)\]; fsS (\d+) = ([\d.]+) \[([\d.]+), ([\d.]+)\]; only fsS (\d+), only zero-shot (\d+), exact McNemar p ([\d.e+-]+)", t28)
dist = re.search(r"are (\d+) different pairs; recovered in a zero-shot graph at some size: (\d+); in an fsS graph at some size: (\d+)", t28)
dist_p = re.search(r"recovered only by fsS (\d+), only by zero-shot (\d+), exact McNemar p ([\d.]+)", t28)
assert pool and dist and dist_p
print("\n**Table 11.** Mutual pairs of the instruct graph that the other graphs contain, at equal coverage (D029; the pairs do not depend on the null). At risk: mutual pairs of the instruct graph (whole word list) whose two "
      "words both have a surviving zero-shot entry. Zero-shot: the zero-shot graph; few-shot: the few-shot graph limited to the same entries. Exact McNemar test on the pairs found in one graph and not in the other.\n")
print("| Size | Instruct pairs | At risk | Zero-shot | Few-shot, same entries | Only few-shot | Only zero-shot | Exact McNemar p |")
print("|---|---:|---:|---|---|---:|---:|---:|")
for (s, n_it, n_t, x_zs, r_zs, x_fs, r_fs, o_fs, o_zs, p_, x_all, r_all) in c3_rows:
    print(f"| {s} | {n_it} | {n_t} | {x_zs} ({100 * float(r_zs):.0f} %) | {x_fs} ({100 * float(r_fs):.0f} %) | {o_fs} | {o_zs} | {float(p_):.3f} |")
n_t, x_zs, r_zs, zlo, zhi, x_fs, r_fs, flo, fhi, o_fs, o_zs, p_ = pool.groups()
print(f"| Pooled (descriptive: pairs recur across sizes) | -- | {n_t} | {x_zs} ({100 * float(r_zs):.0f} %; 95 % range {100 * float(zlo):.0f}-{100 * float(zhi):.0f} %) | "
      f"{x_fs} ({100 * float(r_fs):.0f} %; {100 * float(flo):.0f}-{100 * float(fhi):.0f} %) | {o_fs} | {o_zs} | {float(p_):.4f} |")
print(f"| Each different pair once ({dist.group(1)} pairs) | -- | {dist.group(1)} | {dist.group(2)} | {dist.group(3)} | {dist_p.group(1)} | {dist_p.group(2)} | {float(dist_p.group(3)):.3f} |")

# ----------------------------------------------------------------------------- Table 12: few-shot prompt (double-edge null)
print("\n**Table 12.** The few-shot prompt (three worked examples): R of the pretrained Gemma3 models given three example definitions, against the zero-shot pretrained model and the instruct model of the same size "
      "(default filter, double-edge null), with the observed mutual pairs and the null mean in brackets. The ratio is instruct R / few-shot R; the exact range is the conditional range, the conservative range "
      "combines the two ends of the Poisson ranges. The last column is the few-shot R against the three-edge null.\n")
print("| Size | Zero-shot pretrained R | Few-shot pretrained R (95 % range) | Instruct R | Instruct / few-shot | Exact range | Conservative range | Few-shot R, three-edge null |")
print("|---|---:|---|---:|---:|---|---|---:|")
g = NEW["e3__Gemma3-270M-pt"]
print(f"| 270M | {cell(NEW['main__Gemma3-270M-pt'])} | {cell_rng(g)} | no cycles (D011) | -- | -- | -- | {Rf(DATA['default']['e3__Gemma3-270M-pt']):.1f} |")
e3_rows = {}
for s in SIZES:
    f, i, z = NEW[f"e3__Gemma3-{s}-pt"], NEW[f"main__Gemma3-{s}"], NEW[f"main__Gemma3-{s}-pt"]
    ratio, lo, hi = ratio_ci(i, f)
    cr_, clo, chi_ = conservative(i, f)
    e3_rows[s] = (ratio, lo, hi, clo, chi_)
    print(f"| {s} | {cell(z)} | {cell_rng(f)} | {cell(i)} | {ratio:.2f} | [{lo:.2f}, {hi:.2f}] | [{clo:.2f}, {chi_:.2f}] | {Rf(DATA['default'][f'e3__Gemma3-{s}-pt']):.1f} |")
print("\n- Few-shot ranges of instruct / few-shot include 1: " + "; ".join(f"{s}: exact {'yes' if e3_rows[s][1] <= 1 <= e3_rows[s][2] else 'no'}, conservative {'yes' if e3_rows[s][3] <= 1 <= e3_rows[s][4] else 'no'}" for s in SIZES))

# ----------------------------------------------------------------------------- Appendix tables
print("\n**Table A1.** Definition graphs of the 23 analysed sources (default filter, first sentence; 2,750-lemma node set). Null mean and R against the three-edge null (100 replicates, 32 x |E| swaps) and against the "
      "double-edge null (100 replicates, 64 x |E| swaps); R = observed mutual pairs / null mean (floor 0.5); the 95 % range is the exact Poisson range of the observed number of mutual pairs divided by the null mean "
      "of the double-edge null; the last column is R of the unfiltered graphs (stored text; three-edge null only). The zero-shot pretrained graphs cover about half of the entries (Section 4.6.2).\n")
print("| Source | Edges | Mutual pairs | Three-edge null: mean | R | Double-edge null: mean | R | 95 % range of R | R unfiltered (three-edge) |")
print("|---|---:|---:|---:|---:|---:|---:|---|---:|")
order = []
for fam, label in (("Gemma3", "Gemma3 instruct"), ("Qwen2.5", "Qwen2.5 instruct"), ("Qwen3", "Qwen3 instruct")):
    order.append((label, sorted((k for k in instruct if family(k) == fam), key=lambda k: (size_b(k), k))))
order.append(("Gemma3 pretrained (zero-shot)", sorted(base, key=size_b)))
order.append(("Gemma3 pretrained (few-shot)", sorted(fewshot, key=size_b)))
order.append(("Reference", ["main__wordnet"]))
for label, keys in order:
    print(f"| *{label}* | | | | | | | | |")
    for k in keys:
        o_, n_ = DATA["default"][k], NEW[k]
        r, lo, hi = r_range(n_)
        unf = DATA["unfiltered"].get(k)
        print(f"| {k.split('__')[1]} | {n_['n_edges']} | {obs(n_)} | {nul(o_):.2f} | {Rf(o_):.1f} | {nul(n_):.2f} | {r:.1f} | {fmt_range(lo, hi)} | " + (f"{unf['reciprocity_excess']:.1f} |" if unf else "-- |"))

print("\n**Table A2.** Matched Gemma3 pairs under a zero-shot prompt, against the three-edge null (our first analysis; these variants were not re-run with the double-edge null): R of the instruct model / R of the "
      "pretrained model, with the exact conditional 95 % range of the ratio, under five variants of the analysis.\n")
print("| Size | Instruct R | Pretrained R | Default filter | Unfiltered | Strict filter | Whole stored text | Six frame words removed |")
print("|---|---:|---:|---|---|---|---|---|")
excl1 = excl2 = total = 0
for s in SIZES:
    cells = []
    for v in ("default", "unfiltered", "strict", "stored", "frame"):
        ratio, lo, hi = ratio_ci(DATA[v][f"main__Gemma3-{s}"], DATA[v][f"main__Gemma3-{s}-pt"])
        total += 1
        excl1 += (lo > 1 or hi < 1)
        excl2 += (lo >= 2 or hi < 2)
        cells.append(f"{ratio:.1f} [{lo:.1f}, {hi:.1f}]")
    print(f"| {s} | {Rf(DATA['default'][f'main__Gemma3-{s}']):.1f} | {Rf(DATA['default'][f'main__Gemma3-{s}-pt']):.1f} | " + " | ".join(cells) + " |")
print(f"\nOver the {total} pair-by-variant comparisons the range excludes 1 in {excl1} and excludes 2 in {excl2}.")

c1 = {(m[0], m[3]): (float(m[4]), float(m[5])) for m in re.findall(r"^\s+(\d+B)\s+(\d+)\s+(\d+)\s+(zero-shot / instruct|few-shot / instruct|zero-shot / few-shot)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s*$", t28, re.M)}
c2 = {(m[0], m[1]): m[2:] for m in re.findall(r"^\s+(\d+B) (zero-shot|few-shot|instruct)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s*$", t28, re.M)}
assert len(c1) == 12 and len(c2) == 12, (len(c1), len(c2))
c1_ratio = re.search(r"mean J\(few-shot, instruct\) / mean J\(zero-shot, instruct\): 1B ([\d.]+), 4B ([\d.]+), 12B ([\d.]+), 27B ([\d.]+)", t28)
assert c1_ratio
c1_ratio = dict(zip(SIZES, (float(x) for x in c1_ratio.groups())))
print("\n**Table A3.** Defining words of the same entries in the three conditions (D029 (c); entries kept in all three conditions; the defining words of an entry are the in-vocabulary lemmas of its first sentence, "
      "the headword excluded). Jaccard index of the defining-word sets with the instruct definition of the same entry (mean); share of records that contain one of six frame words (define, mean, refer, describe, "
      "phrase, use); share of all defining-word occurrences carried by the five most used words.\n")
print("| Size | Mean Jaccard with instruct: zero-shot | few-shot | few-shot / zero-shot | Frame word: zero-shot | few-shot | instruct | Top-5 words: zero-shot | few-shot | instruct |")
print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for s in SIZES:
    jz, jf = c1[(s, "zero-shot / instruct")][0], c1[(s, "few-shot / instruct")][0]
    fr = [100 * float(c2[(s, c)][5]) for c in ("zero-shot", "few-shot", "instruct")]
    tp = [100 * float(c2[(s, c)][4]) for c in ("zero-shot", "few-shot", "instruct")]
    print(f"| {s} | {jz:.3f} | {jf:.3f} | {c1_ratio[s]:.2f} | {fr[0]:.0f} % | {fr[1]:.0f} % | {fr[2]:.0f} % | {tp[0]:.0f} % | {tp[1]:.0f} % | {tp[2]:.0f} % |")

print("\n**Table A4.** Closed sub-dictionaries (D030, double-edge null): the zero-shot graph, the whole few-shot graph and the whole instruct graph induced on the words that have a surviving zero-shot entry "
      "(the other words and their edges removed), and the whole few-shot graph induced on five random sets of words of the same size. R' = observed pairs / null mean without the floor; brackets: the exact Poisson "
      "95 % range of R', then the observed pairs and the null mean. Instruct / zero-shot: exact conditional range without the floor. rho = R' of a random half / R' of the whole few-shot graph (median of five).\n")
print("| Size | Words | Zero-shot | Few-shot | Instruct | Instruct / zero-shot | Few-shot / zero-shot | Whole few-shot R' | Random halves: R' | rho (median) |")
print("|---|---:|---|---|---|---|---|---:|---|---:|")


def cell_c(rec):
    o_, nm = obs(rec), nul(rec)
    lo, hi = poisson_ci(o_)
    return f"{o_ / nm:.1f} [{lo / nm:.1f}, {hi / nm:.1f}] ({o_} / {nm:.2f})"


for s in SIZES:
    zc_, fc, ic = (NEW[f"d030c__{k}C_{s}"] for k in ("zs", "fs", "it"))
    r_it, r_fs = ratio_ci(ic, zc_, floor=0.0), ratio_ci(fc, zc_, floor=0.0)
    whole = Rp(NEW[f"e3__Gemma3-{s}-pt"])
    halves = [Rp(NEW[f"d030c__fsRC{k}_{s}"]) for k in range(1, 6)]
    print(f"| {s} | {zc_['n_nodes']:,} | {cell_c(zc_)} | {cell_c(fc)} | {cell_c(ic)} | {r_it[0]:.2f} [{r_it[1]:.2f}, {r_it[2]:.2f}] | {r_fs[0]:.2f} [{r_fs[1]:.2f}, {r_fs[2]:.2f}] | "
          f"{whole:.1f} | {min(halves):.1f} to {max(halves):.1f} | {st.median(halves) / whole:.2f} |")

# ----------------------------------------------------------------------------- numbers quoted in the text
print("\n**Numbers quoted in the text**\n")
wn_new, wn_old = NEW["main__wordnet"], DATA["default"]["main__wordnet"]
for tag, data in (("double-edge", NEW), ("three-edge", DATA["default"])):
    wn = Rf(data["main__wordnet"])
    above = [k for k in instruct if r_range(data[k])[1] > wn]
    below = [k for k in instruct if r_range(data[k])[2] < wn]
    cont = [k for k in instruct if k not in above and k not in below]
    print(f"- {tag} null: WordNet R {wn:.1f} {fmt_range(*r_range(data['main__wordnet'])[1:])}, null mean {nul(data['main__wordnet']):.2f}; instruct models with the range entirely above {len(above)}, entirely below {len(below)} "
          f"({', '.join(k[6:] for k in below) or 'none'}), containing it {len(cont)}; point estimates above WordNet's: {sum(Rf(data[k]) > wn for k in instruct)} of 17")
    lo_i = min(instruct, key=lambda k: Rf(data[k]))
    hi_b = max(base, key=lambda k: Rf(data[k]))
    print(f"  lowest instruct {lo_i[6:]} {Rf(data[lo_i]):.1f} {fmt_range(*r_range(data[lo_i])[1:])}; highest zero-shot pretrained {hi_b[6:]} {Rf(data[hi_b]):.1f} {fmt_range(*r_range(data[hi_b])[1:])}")
    print(f"  instruct: R {min(Rf(data[k]) for k in instruct):.1f}-{max(Rf(data[k]) for k in instruct):.1f} (median {st.median(Rf(data[k]) for k in instruct):.1f}); zero-shot pretrained "
          f"{min(Rf(data[k]) for k in base):.1f}-{max(Rf(data[k]) for k in base):.1f} (median {st.median(Rf(data[k]) for k in base):.1f}); few-shot pretrained {min(Rf(data[k]) for k in fewshot):.1f}-{max(Rf(data[k]) for k in fewshot):.1f}")
from scipy.stats import spearmanr  # noqa: E402

for tag, data in (("double-edge", NEW), ("three-edge", DATA["default"])):
    wn_rec = data["main__wordnet"]
    rr = {k: ratio_ci(data[k], wn_rec) for k in instruct}
    print(f"- {tag} null: exact conditional range of instruct R / WordNet R excludes 1 above for {sum(r[1] > 1 for r in rr.values())} of 17 models, below for {sum(r[2] < 1 for r in rr.values())}, "
          f"includes 1 for {sum(r[1] <= 1 <= r[2] for r in rr.values())}; instruct ranges above the upper end of WordNet's range ({r_range(wn_rec)[2]:.1f}): {sum(r_range(data[k])[1] > r_range(wn_rec)[2] for k in instruct)}")
    print(f"  rank correlation over the 17 instruct models: mutual pairs with R {spearmanr([obs(data[k]) for k in instruct], [Rf(data[k]) for k in instruct])[0]:+.2f}; null mean with R "
          f"{spearmanr([nul(data[k]) for k in instruct], [Rf(data[k]) for k in instruct])[0]:+.2f}")
print(f"- rank correlation of R (three-edge) and R (double-edge) over the 17 instruct models: {spearmanr([Rf(DATA['default'][k]) for k in instruct], [Rf(NEW[k]) for k in instruct])[0]:+.2f}; "
      f"R double-edge / R three-edge below 1.11 for {sum(Rf(NEW[k]) / Rf(DATA['default'][k]) < 1.11 for k in instruct)} models, at least 1.7 for {sum(Rf(NEW[k]) / Rf(DATA['default'][k]) >= 1.7 for k in instruct)}")
print(f"- zero-shot pretrained graphs, double-edge null: null means {', '.join(f'{nul(NEW[k]):.2f}' for k in sorted(base, key=size_b))} (below the floor of 0.5 in "
      f"{sum(nul(NEW[k]) < 0.5 for k in base)} of 5); R' without the floor {', '.join(f'{Rp(NEW[k]):.1f}' for k in sorted(base, key=size_b))}; observed pairs {', '.join(str(obs(NEW[k])) for k in sorted(base, key=size_b))}")
print(f"- graphs under the double-edge null whose null mean is below the floor: main and few-shot graphs {sorted(k for k in NEW if nul(NEW[k]) < 0.5 and k.split(chr(95) * 2)[0] in ('main', 'e3'))}; "
      f"restricted graphs of D029 and D030: {sum(nul(NEW[k]) < 0.5 for k in NEW if k.startswith(('d029__', 'd030c__')))} of {sum(k.startswith(('d029__', 'd030c__')) for k in NEW)}")
gz = {s: D33[f"main__Gemma3-{s}"]["z"]["kernel_ratio"] for s in SIZES}
print("- Gemma 3 instruct kernel-ratio z, double-edge null: " + ", ".join(f"{s} {gz[s]:+.2f}" for s in SIZES) + "; three-edge null: " + ", ".join(f"{s} {DATA['default'][f'main__Gemma3-{s}']['z']['kernel_ratio']:+.2f}" for s in SIZES))
print(f"- observed mutual pairs: instruct {min(obs(NEW[k]) for k in instruct)}-{max(obs(NEW[k]) for k in instruct)}, zero-shot pretrained {sorted(obs(NEW[k]) for k in base)}, few-shot pretrained "
      f"{sorted(obs(NEW[k]) for k in fewshot)}, WordNet {obs(wn_new)}")
print(f"- observed pairs kept in a double-edge replicate (mean over replicates), largest over the 88 graphs: {max(NEW[k]['kept_observed_pairs_mean'] for k in NEW):.2f}")
print(f"- replicates short of the swap budget (double-edge null): {sum(NEW[k]['budget_not_met'] for k in NEW)}")
