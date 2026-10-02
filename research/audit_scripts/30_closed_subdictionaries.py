"""D030 (b): is R invariant when a graph is reduced to a closed sub-dictionary?

Reads results_2026-10-02_Local/d030_closed_subdictionaries/ (experiments/d030_closed_subdictionaries.py): for each size, the zero-shot, whole few-shot and whole
instruct graph induced on the lemmas W(s) that have a surviving zero-shot entry (zsC, fsC, itC), and the whole few-shot graph induced on five random lemma sets of the
same size (fsRC1..5). R' = observed mutual pairs / null mean, without the floor of 0.5 (R' = R wherever the null mean is at least 0.5); R is printed beside it.

  1. every graph: nodes, edges, observed pairs, null mean, R', R, exact Poisson range of R'
  2. reading (b1), invariance: rho_k = R'(fsRCk) / R'(whole few-shot graph); invariant if the median lies between 0.67 and 1.5 at three or four sizes, falls if it is
     below 0.5 at three or four sizes, otherwise mixed
  3. reading (b2), equal coverage on closed dictionaries: exact conditional range of R'(itC) / R'(zsC) (and fsC / zsC); shown if the range of itC / zsC excludes 1
     at three or four sizes, not shown if it includes 1 at three or four sizes, otherwise mixed
  4. descriptive (b3): spread of R' over the five random closed halves, and the same sizes in D029 (entries instead of words) for comparison

The rules are fixed in research/DECISION_LOG.md D030. Output is recorded in outputs/30_closed_subdictionaries.txt.
"""
import glob
import json
import statistics as st
import sys
from pathlib import Path

from scipy.stats import beta, chi2

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
PRIMARY = ROOT / "results_2026-10-01_Local"
D029 = ROOT / "results_2026-10-02_Local" / "d029_survivor_restriction" / "results"
D030 = ROOT / "results_2026-10-02_Local" / "d030_closed_subdictionaries"
SIZES = ("1B", "4B", "12B", "27B")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_dir(folder):
    return {r["key"]: r for r in (load(p) for p in glob.glob(str(folder / "results" / "*.json")))}


closed = load_dir(D030)
if len(closed) != 32:
    print(f"NOT FINISHED: {len(closed)} of 32 results")
    sys.exit(0)
e3 = {k: v for k, v in load_dir(PRIMARY / "e2_filtered_default_controls_32x").items() if k.startswith("e3__")}
d029 = {p.stem: load(p) for p in D029.glob("*.json")}


def obs(r):
    return r["observed"]["cycles_2"]


def nul(r):
    return r["null_mean"]["cycles_2"]


def rq(r):
    return obs(r) / nul(r)


def poisson_ci(k, level=0.95):
    a = (1 - level) / 2
    return (0.0 if k == 0 else chi2.ppf(a, 2 * k) / 2), chi2.ppf(1 - a, 2 * (k + 1)) / 2


def ratio_ci(a, b, level=0.95):
    """Exact conditional range of rate a / rate b; exposures are the null means (no floor, D030)."""
    xa, xb, ea, eb = obs(a), obs(b), nul(a), nul(b)
    n = xa + xb
    al = (1 - level) / 2
    p_lo = beta.ppf(al, xa, n - xa + 1) if xa > 0 else 0.0
    p_hi = beta.ppf(1 - al, xa + 1, n - xa) if xb > 0 else 1.0
    odds = lambda p: p / (1 - p) if p < 1 else float("inf")
    return (xa / ea) / (xb / eb), odds(p_lo) * eb / ea, odds(p_hi) * eb / ea


print("1. CLOSED SUB-DICTIONARIES (induced on the lemmas that have a surviving zero-shot entry; 100 replicates, 32 x edges)")
print("   R' = observed pairs / null mean without the floor; R = with the floor of 0.5; range = exact Poisson 95 % range of R'\n")
print(f"   {'size':>4} {'graph':<26}{'nodes':>6}{'edges':>7}{'obs':>5}{'null':>7}{'R':>7}{'R_prime':>9}{'range of R_prime':>19}")
for s in SIZES:
    whole = e3[f"e3__Gemma3-{s}-pt"]
    rows = [(f"{k}C", closed[f"d030c__{k}C_{s}"]) for k in ("zs", "fs", "it")] + [(f"fsRC{j}", closed[f"d030c__fsRC{j}_{s}"]) for j in range(1, 6)]
    for name, r in rows:
        lo, hi = poisson_ci(obs(r))
        flag = "  (floor)" if nul(r) < 0.5 else ""
        print(f"   {s:>4} {name:<26}{r['n_nodes']:>6}{r['n_edges']:>7}{obs(r):>5}{nul(r):>7.2f}{r['reciprocity_excess']:>7.1f}{rq(r):>9.1f}{'[%.1f, %.1f]' % (lo / nul(r), hi / nul(r)):>19}{flag}")
    lo, hi = poisson_ci(obs(whole))
    print(f"   {s:>4} {'whole few-shot (2750 nodes)':<26}{whole['n_nodes']:>6}{whole['n_edges']:>7}{obs(whole):>5}{nul(whole):>7.2f}{whole['reciprocity_excess']:>7.1f}{rq(whole):>9.1f}")
    print()

print("2. READING (b1): is R' invariant under random closed restriction?  rho_k = R'(fsRCk) / R'(whole few-shot graph)")
print(f"   {'size':>4}{'whole R_prime':>14}{'rho_1..5':>44}{'median':>9}  label")
n_inv = n_fall = 0
for s in SIZES:
    whole = rq(e3[f"e3__Gemma3-{s}-pt"])
    rhos = [rq(closed[f"d030c__fsRC{j}_{s}"]) / whole for j in range(1, 6)]
    med = st.median(rhos)
    lab = "invariant" if 0.67 <= med <= 1.5 else ("falls" if med < 0.5 else "neither")
    n_inv += lab == "invariant"
    n_fall += lab == "falls"
    print(f"   {s:>4}{whole:14.1f}{'  '.join('%.2f' % x for x in rhos):>44}{med:9.2f}  {lab}")
v1 = "R IS APPROXIMATELY INVARIANT" if n_inv >= 3 else ("R FALLS WITH RANDOM CLOSED RESTRICTION" if n_fall >= 3 else "MIXED")
print(f"   sizes invariant: {n_inv} of 4; sizes where it falls: {n_fall} of 4  ->  {v1}")

print("\n3. READING (b2): equal coverage on closed dictionaries, exact conditional range of the ratio of R'")
print(f"   {'size':>4}{'itC / zsC':>28}{'includes 1':>12}{'fsC / zsC':>28}{'includes 1':>12}")
n_it_excl = n_it_incl = 0
for s in SIZES:
    zc, fc, ic = (closed[f"d030c__{k}C_{s}"] for k in ("zs", "fs", "it"))
    ri, rf = ratio_ci(ic, zc), ratio_ci(fc, zc)
    inc_i, inc_f = ri[1] <= 1 <= ri[2], rf[1] <= 1 <= rf[2]
    n_it_incl += inc_i
    n_it_excl += not inc_i
    print(f"   {s:>4}{'%.2f [%.2f, %.2f]' % ri:>28}{'yes' if inc_i else 'no':>12}{'%.2f [%.2f, %.2f]' % rf:>28}{'yes' if inc_f else 'no':>12}")
v2 = "A DIFFERENCE AT EQUAL COVERAGE IS SHOWN" if n_it_excl >= 3 else ("A DIFFERENCE IS NOT SHOWN" if n_it_incl >= 3 else "MIXED")
print(f"   instruct / zero-shot range excludes 1 at {n_it_excl} of 4 sizes, includes 1 at {n_it_incl} of 4  ->  {v2}")

print("\n4. DESCRIPTIVE (b3): spread of R' over the five random halves, closed (this entry) against the entry-level halves of D029")
print(f"   {'size':>4}{'closed: smallest':>18}{'largest':>9}{'max/min':>9}{'null range':>14}   {'D029 entry-level: smallest':>28}{'largest':>9}{'max/min':>9}{'null range':>14}")
for s in SIZES:
    c = [closed[f"d030c__fsRC{j}_{s}"] for j in range(1, 6)]
    d = [d029[f"d029__fsR{j}_{s}"] for j in range(1, 6)]
    cq, dq = [rq(x) for x in c], [rq(x) for x in d]
    cn, dn = [nul(x) for x in c], [nul(x) for x in d]
    print(f"   {s:>4}{min(cq):18.1f}{max(cq):9.1f}{max(cq) / min(cq):9.1f}{'%.2f-%.2f' % (min(cn), max(cn)):>14}   {min(dq):28.1f}{max(dq):9.1f}{max(dq) / min(dq):9.1f}{'%.2f-%.2f' % (min(dn), max(dn)):>14}")
print("\n5. FLAGS: graphs with a null mean below the floor of 0.5 or swap failures: " +
      (", ".join(f"{k}" for k, r in closed.items() if nul(r) < 0.5 or r["swap_failures"]) or "none"))
