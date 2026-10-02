"""D032: do the readings that rest on R survive a null that can break every mutual pair?

Reads the double-edge-swap null (results_2026-10-02_Local/d032_double_swap_null/results/, experiments/d032_double_swap_null.py: 88 graphs, 100 replicates each) and the
earlier results of the paper's null (networkx directed_edge_swap). R_d = observed pairs / max(null mean, 0.5); R'_d = observed pairs / null mean. Rules: DECISION_LOG.md D032.

  1. every key graph under both nulls
  2. (r1) coverage: rho_k = R'_d(random half) / R'_d(whole few-shot graph), entry-level halves (D029) and closed halves (D030)
  3. (r2) the zero-shot gap as built: instruct R_d / pretrained R_d, rule of D024
  4. (r3) equal coverage: R_d(itS) / R_d(zero-shot), rule of D029
  5. (r4) few-shot within a factor 2 of the instruct R_d, rule of D024
  6. (r5) scale: the labels and reading of D031 with R_d
  7. (r6) WordNet: the ranges of the instruct models against R_d of WordNet
Output is recorded in outputs/36_double_swap_readings.txt.
"""
import glob
import json
import math
import re
import statistics as st
import sys
from pathlib import Path

from scipy.stats import beta, chi2, spearmanr

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
PRIMARY = ROOT / "results_2026-10-01_Local"
NEW = ROOT / "results_2026-10-02_Local" / "d032_double_swap_null" / "results"
SIZES = ("1B", "4B", "12B", "27B")


def load_dir(folder):
    return {r["key"]: r for r in (json.loads(Path(p).read_text(encoding="utf-8")) for p in glob.glob(str(Path(folder) / "*.json")))}


new = load_dir(NEW)
if len(new) != 88:
    print(f"NOT FINISHED: {len(new)} of 88 results")
    sys.exit(0)
old = {**load_dir(PRIMARY / "e2_filtered_default_main_32x" / "results"), **load_dir(PRIMARY / "e2_filtered_default_controls_32x" / "results"),
       **load_dir(ROOT / "results_2026-10-02_Local" / "d029_survivor_restriction" / "results"), **load_dir(ROOT / "results_2026-10-02_Local" / "d030_closed_subdictionaries" / "results")}


def obs(r):
    return r["observed"]["cycles_2"]


def nul(r):
    return r["null_mean"]["cycles_2"]


def R(r):
    return obs(r) / max(nul(r), 0.5)


def Rp(r):
    return obs(r) / nul(r) if nul(r) > 0 else float("inf")


def poisson_ci(k, level=0.95):
    a = (1 - level) / 2
    return (0.0 if k == 0 else chi2.ppf(a, 2 * k) / 2), chi2.ppf(1 - a, 2 * (k + 1)) / 2


def r_range(r):
    lo, hi = poisson_ci(obs(r))
    e = max(nul(r), 0.5)
    return obs(r) / e, lo / e, hi / e


def ratio_ci(a, b, level=0.95):
    xa, xb, ea, eb = obs(a), obs(b), max(nul(a), 0.5), max(nul(b), 0.5)
    n = xa + xb
    al = (1 - level) / 2
    p_lo = beta.ppf(al, xa, n - xa + 1) if xa > 0 else 0.0
    p_hi = beta.ppf(1 - al, xa + 1, n - xa) if xb > 0 else 1.0
    odds = lambda p: p / (1 - p) if p < 1 else float("inf")
    return (xa / ea) / (xb / eb), odds(p_lo) * eb / ea, odds(p_hi) * eb / ea


inst = [k for k in new if k.startswith("main__") and not k.endswith("-pt") and k != "main__wordnet" and "270M" not in k]
pre = [k for k in new if k.startswith("main__") and k.endswith("-pt")]
fs = [k for k in new if k.startswith("e3__")]
assert len(inst) == 17 and len(pre) == 5 and len(fs) == 5, (len(inst), len(pre), len(fs))

print("1. THE KEY GRAPHS UNDER BOTH NULLS (default filter, first sentence)")
print("   old = networkx directed_edge_swap (the paper's null); d = directed double-edge swap (D032); R with the floor of 0.5\n")
print(f"   {'graph':26}{'obs':>5}{'null old':>10}{'null d':>9}{'R old':>8}{'R d':>8}{'R d / R old':>13}{'kept d':>8}")
for k in sorted(inst, key=lambda x: (x.split('-')[0], float(re.search(r'-(\d+(?:\.\d+)?)B', x).group(1)))) + ["main__wordnet"] + sorted(pre) + sorted(fs):
    o, n = old[k], new[k]
    print(f"   {k:26}{obs(n):>5}{nul(o):>10.2f}{nul(n):>9.2f}{R(o):>8.1f}{R(n):>8.1f}{R(n) / R(o):>13.2f}{n['kept_observed_pairs_mean']:>8.2f}")
for label, keys in (("17 instruct", inst), ("5 zero-shot pretrained", pre), ("5 few-shot pretrained", fs)):
    ratios = [R(new[k]) / R(old[k]) for k in keys]
    print(f"   {label}: R d / R old median {st.median(ratios):.2f}, range {min(ratios):.2f}-{max(ratios):.2f}; R d range {min(R(new[k]) for k in keys):.1f}-{max(R(new[k]) for k in keys):.1f} (old {min(R(old[k]) for k in keys):.1f}-{max(R(old[k]) for k in keys):.1f})")
wn_old, wn_new = old["main__wordnet"], new["main__wordnet"]
print(f"   WordNet: R old {R(wn_old):.1f} (null {nul(wn_old):.2f}), R d {R(wn_new):.1f} (null {nul(wn_new):.2f}), range of R d [{r_range(wn_new)[1]:.1f}, {r_range(wn_new)[2]:.1f}]")
rho_models, _ = spearmanr([R(old[k]) for k in inst], [R(new[k]) for k in inst])
print(f"   rank correlation of R old and R d over the 17 instruct models: {rho_models:+.2f}")

print("\n2. (r1) COVERAGE under the double-edge swap null: rho_k = R'_d(half k) / R'_d(whole few-shot graph)")
print(f"   {'size':>4}{'whole R_d_prime':>16}{'entry-level halves (D029): rho 1..5':>44}{'median':>8}{'closed halves (D030): rho 1..5':>40}{'median':>8}")
lab_e, lab_c = [], []
for s in SIZES:
    whole = Rp(new[f"e3__Gemma3-{s}-pt"])
    re_ = [Rp(new[f"d029__fsR{j}_{s}"]) / whole for j in range(1, 6)]
    rc_ = [Rp(new[f"d030c__fsRC{j}_{s}"]) / whole for j in range(1, 6)]
    me, mc = st.median(re_), st.median(rc_)
    lab = lambda m: "falls" if m < 0.5 else ("invariant" if 0.67 <= m <= 1.5 else "neither")
    lab_e.append(lab(me))
    lab_c.append(lab(mc))
    print(f"   {s:>4}{whole:16.1f}{'  '.join('%.2f' % x for x in re_):>44}{me:8.2f}{'  '.join('%.2f' % x for x in rc_):>40}{mc:8.2f}   {lab(me)} / {lab(mc)}")


def verdict(labels):
    return "R DEPENDS ON COVERAGE" if labels.count("falls") >= 3 else ("R DOES NOT DEPEND ON COVERAGE" if labels.count("invariant") >= 3 else "MIXED")


print(f"   entry-level halves: {', '.join(lab_e)} -> {verdict(lab_e)}")
print(f"   closed halves:      {', '.join(lab_c)} -> {verdict(lab_c)}")
print("   for comparison, the same median rho under the paper's null: entry-level " + ", ".join(
    f"{st.median([Rp(old[f'd029__fsR{j}_{s}']) / Rp(old[f'e3__Gemma3-{s}-pt']) for j in range(1, 6)]):.2f}" for s in SIZES) + "; closed " + ", ".join(
    f"{st.median([Rp(old[f'd030c__fsRC{j}_{s}']) / Rp(old[f'e3__Gemma3-{s}-pt']) for j in range(1, 6)]):.2f}" for s in SIZES))

print("\n3. (r2) THE ZERO-SHOT GAP AS BUILT: instruct R_d / pretrained R_d, exact conditional range (rule of D024: at least 2 for three of four pairs)")
print(f"   {'size':>4}{'instruct R_d':>14}{'pretrained R_d':>16}{'ratio d [range]':>26}{'ratio old':>11}")
above2 = below2 = 0
for s in SIZES:
    i, p = new[f"main__Gemma3-{s}"], new[f"main__Gemma3-{s}-pt"]
    rt = ratio_ci(i, p)
    ro = ratio_ci(old[f"main__Gemma3-{s}"], old[f"main__Gemma3-{s}-pt"])
    above2 += rt[0] >= 2
    below2 += rt[0] < 2
    print(f"   {s:>4}{R(i):>14.1f}{R(p):>16.1f}{'%.1f [%.1f, %.1f]' % rt:>26}{ro[0]:>11.1f}")
v2 = "THE GAP IS PRESENT" if above2 >= 3 else ("THE GAP IS ABSENT" if below2 >= 2 else "MIXED")
print(f"   pairs at 2 or more: {above2} of 4; below 2: {below2} of 4  ->  {v2}")

print("\n4. (r3) EQUAL COVERAGE: R_d(itS) / R_d(zero-shot), exact conditional range (rule of D029)")
print(f"   {'size':>4}{'zero-shot R_d':>15}{'fsS R_d':>9}{'itS R_d':>9}{'itS / zero-shot':>26}{'includes 1':>12}{'fsS / zero-shot':>26}{'itS / fsS':>24}")
n_excl = n_incl = 0
for s in SIZES:
    z, f, i = new[f"main__Gemma3-{s}-pt"], new[f"d029__fsS_{s}"], new[f"d029__itS_{s}"]
    rz, rf, ri = ratio_ci(i, z), ratio_ci(f, z), ratio_ci(i, f)
    inc = rz[1] <= 1 <= rz[2]
    n_incl += inc
    n_excl += not inc
    print(f"   {s:>4}{R(z):>15.1f}{R(f):>9.1f}{R(i):>9.1f}{'%.2f [%.2f, %.2f]' % rz:>26}{'yes' if inc else 'no':>12}{'%.2f [%.2f, %.2f]' % rf:>26}{'%.2f [%.2f, %.2f]' % ri:>24}")
v3 = "A DIFFERENCE IS SHOWN" if n_excl >= 3 else ("A DIFFERENCE IS NOT SHOWN" if n_incl >= 3 else "MIXED")
print(f"   range of itS / zero-shot excludes 1 at {n_excl} of 4 sizes, includes 1 at {n_incl} of 4  ->  {v3}")

print("\n5. (r4) FEW-SHOT: is the few-shot pretrained R_d within a factor 2 of the instruct R_d?")
n_in = 0
for s in SIZES:
    f, i = new[f"e3__Gemma3-{s}-pt"], new[f"main__Gemma3-{s}"]
    a, b = R(f), R(i)
    fac = max(a, b) / min(a, b)
    n_in += fac <= 2
    rt = ratio_ci(i, f)
    print(f"   {s:>4}  few-shot {a:6.1f}  instruct {b:6.1f}  factor {fac:5.2f}  instruct / few-shot {rt[0]:.2f} [{rt[1]:.2f}, {rt[2]:.2f}]  (paper's null: {R(old[f'e3__Gemma3-{s}-pt']):.1f} / {R(old[f'main__Gemma3-{s}']):.1f})")
print(f"   within a factor 2 at {n_in} of 4 sizes  ->  {'THE FEW-SHOT R REACHES THE INSTRUCT RANGE' if n_in >= 3 else 'NOT REACHED'}")

print("\n6. (r5) SCALE (D031 with R_d): distance |ln R_d - ln R_d(WordNet)| and Jaccard overlap of the pairs with WordNet's, rank correlation with size within families")


def pairs_of(key):
    folder = PRIMARY / "e2_filtered_default_main_32x" / "graphs" / f"{key}.json"
    g = json.loads(folder.read_text(encoding="utf-8"))
    e = {tuple(x) for x in g["edges"]}
    return {tuple(sorted((u, v))) for (u, v) in e if (v, u) in e and u != v}


size_b = lambda k: float(re.search(r"-(\d+(?:\.\d+)?)B", k).group(1))
P_WN = pairs_of("main__wordnet")
rows, rows_with_2507 = [], []
for k in inst:
    P = pairs_of(k)
    row = {"fam": k[6:].split("-")[0], "size": size_b(k), "d": abs(math.log(R(new[k])) - math.log(R(wn_new))), "J": len(P & P_WN) / len(P | P_WN), "pairs": obs(new[k]), "null": nul(new[k])}
    rows_with_2507.append(row)
    if "2507" not in k:
        rows.append(row)
labels = {"d": [], "J": []}
print(f"   {'family':9}{'n':>3}{'S1 rho (d)':>12}{'label':>8}{'S2 rho (J)':>12}{'label':>8}{'pairs rho':>11}{'null rho':>10}")
for fam in ("Gemma3", "Qwen2.5", "Qwen3"):
    sel = [r for r in rows if r["fam"] == fam]
    out = []
    for stat in ("d", "J"):
        rv = spearmanr([r["size"] for r in sel], [r[stat] for r in sel])[0]
        toward = rv <= -0.6 if stat == "d" else rv >= 0.6
        away = rv >= 0.6 if stat == "d" else rv <= -0.6
        lab = "toward" if toward else ("away" if away else "none")
        labels[stat].append(lab)
        out.append((rv, lab))
    pr = spearmanr([r["size"] for r in sel], [r["pairs"] for r in sel])[0]
    nr = spearmanr([r["size"] for r in sel], [r["null"] for r in sel])[0]
    print(f"   {fam:9}{len(sel):>3}{out[0][0]:>+12.2f}{out[0][1]:>8}{out[1][0]:>+12.2f}{out[1][1]:>8}{pr:>+11.2f}{nr:>+10.2f}")
supported = all(sum(l == "toward" for l in labels[s]) >= 2 and "away" not in labels[s] for s in ("d", "J"))
contradicted = all(sum(l == "away" for l in labels[s]) >= 2 for s in ("d", "J"))
print(f"   S1 labels {labels['d']}, S2 labels {labels['J']}  ->  {'CONVERGENCE WITH SIZE IS SUPPORTED' if supported else ('CONVERGENCE IS CONTRADICTED' if contradicted else 'NO CONSISTENT APPROACH')}")
# Added 2026-10-02 (after the first recording): the sensitivity of D031 with Qwen3-4B-Instruct-2507 included, for the double-edge null
print("\n   sensitivity, Qwen3-4B-Instruct-2507 included (descriptive):")
for fam in ("Gemma3", "Qwen2.5", "Qwen3"):
    sel = [r for r in rows_with_2507 if r["fam"] == fam]
    out = []
    for stat in ("d", "J"):
        rv = spearmanr([r["size"] for r in sel], [r[stat] for r in sel])[0]
        toward = rv <= -0.6 if stat == "d" else rv >= 0.6
        away = rv >= 0.6 if stat == "d" else rv <= -0.6
        out.append((rv, "toward" if toward else ("away" if away else "none")))
    print(f"   {fam:9}{len(sel):>3}{out[0][0]:>+12.2f}{out[0][1]:>8}{out[1][0]:>+12.2f}{out[1][1]:>8}")

print("\n7. (r6) WORDNET: the exact Poisson range of each instruct model's R_d against R_d of WordNet")
wn = R(wn_new)
above = [k for k in inst if r_range(new[k])[1] > wn]
below = [k for k in inst if r_range(new[k])[2] < wn]
print(f"   R_d of WordNet {wn:.1f} [{r_range(wn_new)[1]:.1f}, {r_range(wn_new)[2]:.1f}]; instruct models entirely above: {len(above)}, entirely below: {len(below)}, containing it: {17 - len(above) - len(below)}; "
      f"point estimates above: {sum(R(new[k]) > wn for k in inst)} of 17")
wn_o = R(wn_old)
above_o = [k for k in inst if r_range(old[k])[1] > wn_o]
below_o = [k for k in inst if r_range(old[k])[2] < wn_o]
print(f"   (paper's null: R of WordNet {wn_o:.1f}; above {len(above_o)}, below {len(below_o)}, containing {17 - len(above_o) - len(below_o)}; point estimates above {sum(R(old[k]) > wn_o for k in inst)} of 17)")
print(f"   instruct R_d median {st.median(R(new[k]) for k in inst):.1f} (paper's null {st.median(R(old[k]) for k in inst):.1f}); zero-shot pretrained R_d median {st.median(R(new[k]) for k in pre):.1f} ({st.median(R(old[k]) for k in pre):.1f})")
