"""E3, E4 and E5 at the converged null (E1d setting) against the main graphs.

Audit script (2026-10-01). Reads E1d (23 main graphs), the controls run (40 graphs) and the stored
definitions, and prints R for every condition with its 95 % interval, the changes the controls make
to R, the mean definition length of each condition, and how R moves with definition length.
Output is recorded in outputs/13_controls_vs_main.txt.
"""
import glob
import json
import math
import statistics as st
import sys
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
MAIN = {r["key"]: r for r in json.load(open(ROOT / "results_2026-10-01_Local/e1d_null_unfiltered_32x/null_model_all.json", encoding="utf-8"))}
CTRL = {}
for p in glob.glob(str(ROOT / "results_2026-10-01_Local/e1d_null_unfiltered_32x_controls/results/*.json")):
    r = json.load(open(p, encoding="utf-8"))
    CTRL[r["key"]] = r
ALL = {**MAIN, **CTRL}
PATHS = {
    "main": "data/definitions/{}_42.jsonl",
    "e3": "results_2026-09-09_Runpod/results_e3 (fewshot)/definitions/{}_42.jsonl",
    "e4": "results_2026-09-09_Runpod/results_e4 (lenght)/definitions/{}_42.jsonl",
    "e5": "results_2026-09-09_Runpod/results_e5 (no template)/definitions/{}_42.jsonl",
}


def words(key: str) -> float:
    ds, name = key.split("__")
    recs = [json.loads(l) for l in open(ROOT / PATHS[ds].format(name), encoding="utf-8") if l.strip()]
    w = [len((r.get("definition") or "").split()) for r in recs if (r.get("definition") or "").strip()]
    return sum(w) / len(w)


R = lambda k: ALL[k]["reciprocity_excess"]
ci = lambda k: "[%.1f, %.1f]" % tuple(ALL[k]["R_ci95"])
flag = lambda k: "*" if ALL[k]["swap_failures"] else " "
print(f"graphs: main {len(MAIN)}, controls {len(CTRL)}; swap failures in the controls: "
      f"{[(k, ALL[k]['swap_failures']) for k in CTRL if ALL[k]['swap_failures']]}")

print("\n1. E3: BASE MODELS, ZERO-SHOT vs FEW-SHOT, WITH THE INSTRUCT MODEL OF THE SAME SIZE (R [95 % CI]; mean words per definition)")
print(f"   {'size':6}{'zero-shot':>17}{'few-shot E3':>19}{'instruct':>19}   words: zero / few / instruct")
for s in ("270M", "1B", "4B", "12B", "27B"):
    z, f, i = f"main__Gemma3-{s}-pt", f"e3__Gemma3-{s}-pt", f"main__Gemma3-{s}"
    inst = f"{R(i):5.1f} {ci(i)}" if i in MAIN else "--"
    iw = f"{words(i):.1f}" if i in MAIN else "--"
    print(f"   {s:6}{R(z):>6.1f} {ci(z):>10}{R(f):>8.1f} {ci(f):>10}   {inst:>17}   {words(z):.1f} / {words(f):.1f} / {iw}")
    if i in MAIN:
        lo_f, hi_f = ALL[f]["R_ci95"]; lo_i, hi_i = ALL[i]["R_ci95"]
        rel = "above" if lo_f > hi_i else "below" if hi_f < lo_i else "overlapping with"
        print(f"          few-shot base is {rel} the instruct model (intervals)")

print("\n2. E4: 8-WORD CAP, per instruct model (R at 32 x; mean words)")
print(f"   {'model':24}{'main R':>8}{'E4 R':>8}{'ratio':>7}   {'words main':>10}{'E4':>6}")
rows4 = []
for k in sorted(k for k in CTRL if k.startswith("e4__")):
    m = "main__" + k[4:]
    if m not in MAIN:
        continue
    rows4.append((k, R(m), R(k), R(k) / R(m), words(m), words(k)))
    print(f"   {k[4:]:24}{R(m):>8.1f}{R(k):>7.1f}{flag(k)}{R(k) / R(m):>7.2f}   {words(m):>10.1f}{words(k):>6.1f}")
rat = [r[3] for r in rows4]
print(f"   ratio E4/main: median {st.median(rat):.2f}, range {min(rat):.2f}-{max(rat):.2f}; R higher under the cap in {sum(x > 1 for x in rat)} of {len(rat)} models")
print(f"   mean words main {st.mean(r[4] for r in rows4):.1f} -> E4 {st.mean(r[5] for r in rows4):.1f}")
factor = lambda xs: [max(x, 1 / x) for x in xs]
f4 = factor(rat)
print(f"   size of the change: median factor {st.median(f4):.2f}, largest {max(f4):.2f}; within a factor 2 in {sum(f < 2 for f in f4)} of {len(f4)} models")

print("\n3. E5: NO CHAT TEMPLATE, per instruct model (R at 32 x; mean words of the stored text)")
print(f"   {'model':24}{'main R':>8}{'E5 R':>8}{'ratio':>7}   {'words main':>10}{'E5':>6}")
rows5 = []
for k in sorted(k for k in CTRL if k.startswith("e5__")):
    m = "main__" + k[4:]
    if m not in MAIN:
        continue
    rows5.append((k, R(m), R(k), R(k) / R(m), words(m), words(k)))
    print(f"   {k[4:]:24}{R(m):>8.1f}{R(k):>7.1f}{flag(k)}{R(k) / R(m):>7.2f}   {words(m):>10.1f}{words(k):>6.1f}")
rat5 = [r[3] for r in rows5]
print(f"   ratio E5/main: median {st.median(rat5):.2f}, range {min(rat5):.2f}-{max(rat5):.2f}; higher in {sum(x > 1 for x in rat5)} of {len(rat5)}")
f5 = factor(rat5)
print(f"   size of the change: median factor {st.median(f5):.2f}, largest {max(f5):.2f}; within a factor 2 in {sum(f < 2 for f in f5)} of {len(f5)} models")

print("\n4. HOW R MOVES WITH DEFINITION LENGTH (all converged graphs without swap failures)")
pts = [(k, R(k), words(k)) for k in ALL if not ALL[k]["swap_failures"] and R(k) > 0 and "wordnet" not in k]
rho, p = stats.spearmanr([w for _, _, w in pts], [r for _, r, _ in pts])
print(f"   all {len(pts)} graphs: Spearman rho(mean words, R) = {rho:+.2f} (p = {p:.3g})")
for lab, test in (("instruct, main + E4", lambda k: k.split('__')[0] in ('main', 'e4') and not k.endswith('-pt') and 'wordnet' not in k),
                  ("base, zero-shot + few-shot", lambda k: k.endswith('-pt'))):
    sub = [(r, w) for k, r, w in pts if test(k)]
    rho, p = stats.spearmanr([w for _, w in sub], [r for r, _ in sub])
    print(f"   {lab:28} n={len(sub):2}: rho = {rho:+.2f} (p = {p:.3g})")
dl = [(math.log(r[2] / r[1]), math.log(r[5] / r[4])) for r in rows4]
rho, p = stats.spearmanr([b for _, b in dl], [a for a, _ in dl])
print(f"   within a model, E4 against main (n={len(dl)}): rho(change in log words, change in log R) = {rho:+.2f} (p = {p:.3g})")
