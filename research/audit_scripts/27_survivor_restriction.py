"""D029 (b): does coverage explain the zero-shot gap? R of the E3 and instruct graphs limited to the zero-shot survivors.

Reads the 28 null-model results of results_2026-10-02_Local/d029_survivor_restriction/ (experiments/d029_survivor_restriction.py)
and the primary results of results_2026-10-01_Local (default filter, first sentence, 32 x edges swaps), prints

  1. per size: the primary R of the zero-shot, whole-E3 and whole-instruct graphs; R of fsS (E3 limited to S), itS (instruct limited
     to S) and of the five random restrictions fsR1..5 of the same size, with observed pairs, null mean and the exact 95 % Poisson
     range of R (observed count over null mean, floor 0.5 as in R)
  2. the reading of D029 (b), applied mechanically to the point estimates, and at how many sizes the range of R(fsS) contains g(s)
  3. R(itS) against the whole-instruct R (no reading of its own)
  4. flags: null mean below the floor, swap failures, replicates
  5. added after sections 1-4 had been read, and not part of D029: the zero-shot, fsS and itS graphs are built from the same
     entries, so their R can be compared at equal coverage; ratios with the exact conditional range used in scripts 19 and 24

The reading is fixed in research/DECISION_LOG.md D029. Output is recorded in outputs/27_survivor_restriction.txt.
"""
import json
import math
import sys
from pathlib import Path

from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
PRIMARY = ROOT / "results_2026-10-01_Local"
D029 = ROOT / "results_2026-10-02_Local" / "d029_survivor_restriction" / "results"
SIZES = ("1B", "4B", "12B", "27B")
N_RANDOM = 5


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def poisson_ci(k, level=0.95):
    a = (1 - level) / 2
    return (0.0 if k == 0 else chi2.ppf(a, 2 * k) / 2), chi2.ppf(1 - a, 2 * (k + 1)) / 2


def summarize(rec):
    obs, null = rec["observed"]["cycles_2"], rec["null_mean"]["cycles_2"]
    lo, hi = poisson_ci(obs)
    floor = max(null, 0.5)
    return {"obs": obs, "null": null, "R": obs / floor, "lo": lo / floor, "hi": hi / floor, "floor": null < 0.5,
            "edges": rec["n_edges"], "fail": rec["swap_failures"], "reps": rec["replicates"]}


missing = [f"d029__{k}_{s}" for s in SIZES for k in ["fsS", "itS"] + [f"fsR{j}" for j in range(1, N_RANDOM + 1)]
           if not (D029 / f"d029__{k}_{s}.json").exists()]
if missing:
    print(f"NOT FINISHED: {len(missing)} of 28 results missing, first {missing[:3]}")
    sys.exit(0)

P, X = {}, {}
for s in SIZES:
    P[s] = {
        "zs": summarize(load(PRIMARY / "e2_filtered_default_main_32x" / "results" / f"main__Gemma3-{s}-pt.json")),
        "fs": summarize(load(PRIMARY / "e2_filtered_default_controls_32x" / "results" / f"e3__Gemma3-{s}-pt.json")),
        "it": summarize(load(PRIMARY / "e2_filtered_default_main_32x" / "results" / f"main__Gemma3-{s}.json")),
    }
    X[s] = {k: summarize(load(D029 / f"d029__{k}_{s}.json")) for k in ["fsS", "itS"] + [f"fsR{j}" for j in range(1, N_RANDOM + 1)]}

print("1. R OF THE RESTRICTED GRAPHS (default filter, first sentence; 100 replicates, 32 x edges swaps)")
print("   R = observed mutual pairs / max(null mean, 0.5); range = exact 95 % Poisson range of the observed count over the same denominator\n")
print(f"   {'size':>4} {'graph':<22}{'edges':>7}{'obs':>5}{'null':>7}{'R':>7}{'range':>16}")
for s in SIZES:
    rows = [("zero-shot (primary)", P[s]["zs"]), ("whole E3 (primary)", P[s]["fs"]), ("whole instruct (primary)", P[s]["it"]),
            ("fsS: E3 in S", X[s]["fsS"])] + [(f"fsR{j}: E3, random set", X[s][f"fsR{j}"]) for j in range(1, N_RANDOM + 1)] + [("itS: instruct in S", X[s]["itS"])]
    for name, r in rows:
        print(f"   {s:>4} {name:<22}{r['edges']:>7}{r['obs']:>5}{r['null']:>7.2f}{r['R']:>7.1f}{'[%.1f, %.1f]' % (r['lo'], r['hi']):>16}{'  (floor)' if r['floor'] else ''}")
    print()

print("2. THE READING OF D029 (b), applied to the point estimates")
print(f"   {'size':>4}{'R zero-shot':>13}{'R whole E3':>12}{'g(s)':>7}{'R fsS':>8}{'smallest fsRk':>15}{'range of fsS':>16}{'<= g':>6}{'< min fsRk':>12}{'g in range':>12}   per-size reading")
yes_n = no_n = in_range = 0
for s in SIZES:
    g = math.sqrt(P[s]["zs"]["R"] * P[s]["fs"]["R"])
    r = X[s]["fsS"]
    rmin = min(X[s][f"fsR{j}"]["R"] for j in range(1, N_RANDOM + 1))
    c1, c2 = r["R"] <= g, r["R"] < rmin
    yes_s, no_s = c1 and c2, (not c1) and (not c2)
    yes_n += yes_s
    no_n += no_s
    contains = r["lo"] <= g <= r["hi"]
    in_range += contains
    print(f"   {s:>4}{P[s]['zs']['R']:13.1f}{P[s]['fs']['R']:12.1f}{g:7.1f}{r['R']:8.1f}{rmin:15.1f}{'[%.1f, %.1f]' % (r['lo'], r['hi']):>16}"
          f"{'yes' if c1 else 'no':>6}{'yes' if c2 else 'no':>12}{'yes' if contains else 'no':>12}   {'explains' if yes_s else ('does not' if no_s else 'neither')}")
verdict = ("COVERAGE EXPLAINS MOST OF THE GAP" if yes_n >= 3 else ("COVERAGE DOES NOT EXPLAIN IT" if no_n >= 3 else "MIXED"))
print(f"   sizes that satisfy 'explains' (R fsS <= g and below the smallest fsRk): {yes_n} of 4; 'does not explain' (R fsS > g and not below it): {no_n} of 4")
print(f"   sizes at which the exact range of R(fsS) contains g(s): {in_range} of 4 (the reading itself uses the point estimates)")
print(f"   -> {verdict}")

print("\n3. WHAT A RESTRICTION TO THE SURVIVORS DOES TO THE OTHER GRAPHS (no reading of its own)")
print(f"   {'size':>4}{'R whole instruct':>18}{'R itS':>8}{'itS / whole':>13}{'R whole E3':>12}{'R fsS':>8}{'fsS / whole':>13}{'fsR mean':>10}{'fsR / whole':>13}")
for s in SIZES:
    rm = sum(X[s][f"fsR{j}"]["R"] for j in range(1, N_RANDOM + 1)) / N_RANDOM
    print(f"   {s:>4}{P[s]['it']['R']:18.1f}{X[s]['itS']['R']:8.1f}{X[s]['itS']['R'] / P[s]['it']['R']:13.2f}{P[s]['fs']['R']:12.1f}{X[s]['fsS']['R']:8.1f}"
          f"{X[s]['fsS']['R'] / P[s]['fs']['R']:13.2f}{rm:10.1f}{rm / P[s]['fs']['R']:13.2f}")

print("\n4. FLAGS")
flag = [(s, k, r) for s in SIZES for k, r in X[s].items() if r["floor"] or r["fail"] or r["reps"] != 100]
print("   graphs with null mean below the floor of 0.5, swap failures, or other than 100 replicates: " + (
    ", ".join(f"{k}_{s} (floor {r['floor']}, failures {r['fail']}, replicates {r['reps']})" for s, k, r in flag) if flag else "none"))

# ---------------------------------------------------------------------------------------------------------------------
from scipy.stats import beta  # noqa: E402


def ratio_ci(a, b, level=0.95):
    """Exact conditional range of rate a / rate b for two counts with known exposures (the null means, floor 0.5), as in script 19."""
    xa, xb = a["obs"], b["obs"]
    ea, eb = max(a["null"], 0.5), max(b["null"], 0.5)
    n = xa + xb
    alpha = (1 - level) / 2
    p_lo = beta.ppf(alpha, xa, n - xa + 1) if xa > 0 else 0.0
    p_hi = beta.ppf(1 - alpha, xa + 1, n - xa) if xb > 0 else 1.0
    odds = lambda p: p / (1 - p) if p < 1 else float("inf")
    scale = eb / ea
    return (xa / ea) / (xb / eb), odds(p_lo) * scale, odds(p_hi) * scale


chk = ratio_ci(summarize(load(PRIMARY / "e2_filtered_default_main_32x" / "results" / "main__Gemma3-4B.json")),
               summarize(load(PRIMARY / "e2_filtered_default_main_32x" / "results" / "main__Gemma3-4B-pt.json")))
assert [round(x, 1) for x in chk] == [3.3, 1.7, 7.1], chk  # the value recorded for the 4B pair in scripts 19 and 24

sets = load(D029.parent / "restriction_sets.json")
manifest = load(D029.parent / "graphs" / "manifest.json")
print("\n5. AT EQUAL COVERAGE (added after sections 1-4 had been read; not part of D029)")
print("   The zero-shot graph, fsS and itS are built from the same entries of the word list (the survivors S), so their R can be compared directly.")
print(f"   {'size':>4}{'entries':>9}{'with text: zero-shot / fsS / itS':>36}")
for s in SIZES:
    print(f"   {s:>4}{sets[s]['survivors']:>9}{'%d / %d / %d' % (sets[s]['survivors'], manifest[f'd029__fsS_{s}']['n_records_with_text'], manifest[f'd029__itS_{s}']['n_records_with_text']):>36}")
print(f"\n   {'size':>4}{'zero-shot R (obs)':>20}{'fsS R (obs)':>16}{'itS R (obs)':>16}   {'itS / zero-shot':>26}{'fsS / zero-shot':>26}{'itS / fsS':>26}")
n_inc = {"it_zs": 0, "fs_zs": 0, "it_fs": 0}
for s in SIZES:
    z, f, i = P[s]["zs"], X[s]["fsS"], X[s]["itS"]
    cells = []
    for tag, (a, b) in (("it_zs", (i, z)), ("fs_zs", (f, z)), ("it_fs", (i, f))):
        r, lo, hi = ratio_ci(a, b)
        n_inc[tag] += lo <= 1 <= hi
        cells.append(f"{r:5.2f} [{lo:5.2f}, {hi:6.2f}]")
    print(f"   {s:>4}{'%.1f (%d)' % (z['R'], z['obs']):>20}{'%.1f (%d)' % (f['R'], f['obs']):>16}{'%.1f (%d)' % (i['R'], i['obs']):>16}   {cells[0]:>26}{cells[1]:>26}{cells[2]:>26}")
print(f"   exact ranges that include 1: itS / zero-shot {n_inc['it_zs']} of 4, fsS / zero-shot {n_inc['fs_zs']} of 4, itS / fsS {n_inc['it_fs']} of 4")
print("\n   For comparison, the whole graphs (Table 4 and Table 5 of the draft): instruct R / zero-shot R, and whole instruct R / whole E3 R")
for s in SIZES:
    r1 = ratio_ci(P[s]["it"], P[s]["zs"])
    r2 = ratio_ci(P[s]["it"], P[s]["fs"])
    print(f"   {s:>4}  whole instruct / zero-shot {r1[0]:5.2f} [{r1[1]:5.2f}, {r1[2]:6.2f}]    whole instruct / whole E3 {r2[0]:5.2f} [{r2[1]:5.2f}, {r2[2]:5.2f}]")
print("\n   Share of the whole graph's mutual pairs and null mean that remain in fsS (the observed pairs need both words defined):")
for s in SIZES:
    w, f = P[s]["fs"], X[s]["fsS"]
    share = sets[s]["survivors"] / 3000
    print(f"   {s:>4}  entries kept {share:.3f} (squared {share ** 2:.3f}); observed pairs {w['obs']} -> {f['obs']} (x{f['obs'] / w['obs']:.2f}); null mean {w['null']:.2f} -> {f['null']:.2f} (x{f['null'] / w['null']:.2f}); R {w['R']:.1f} -> {f['R']:.1f}")

print("\n6. RATIOS TO THE WHOLE-LIST R USED IN THE DRAFT (added after an outside review of draft v1; descriptive, not part of D029)")
print("   v1 said 'between 0.07 and 0.35 of its whole-list value, whichever half'; the figures below are the ones the draft v2 states\n")
print(f"   {'size':>4}{'whole few-shot R':>18}{'survivors':>11}{'single random halves (5)':>28}{'max / min of the halves':>25}{'instruct survivors / whole':>28}")
all_halves, all_fsS, all_itS, all_mean = [], [], [], []
for s in SIZES:
    whole = P[s]["fs"]["R"]
    halves = [X[s][f"fsR{j}"]["R"] / whole for j in range(1, N_RANDOM + 1)]
    fs_s = X[s]["fsS"]["R"] / whole
    it_s = X[s]["itS"]["R"] / P[s]["it"]["R"]
    rr = [X[s][f"fsR{j}"]["R"] for j in range(1, N_RANDOM + 1)]
    all_halves += halves
    all_fsS.append(fs_s)
    all_itS.append(it_s)
    all_mean.append(sum(halves) / len(halves))
    print(f"   {s:>4}{whole:18.1f}{fs_s:11.2f}{'%.2f to %.2f' % (min(halves), max(halves)):>28}{max(rr) / min(rr):25.1f}{it_s:28.2f}")
print(f"\n   few-shot graph on the survivors: {min(all_fsS):.2f}-{max(all_fsS):.2f} of its whole-list R; mean of the five random halves: {min(all_mean):.2f}-{max(all_mean):.2f}; "
      f"instruct graph on the survivors: {min(all_itS):.2f}-{max(all_itS):.2f}; the 20 single random halves: {min(all_halves):.2f}-{max(all_halves):.2f}")
