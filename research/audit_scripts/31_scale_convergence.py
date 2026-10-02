"""D031: does R approach WordNet's with model size?

The 17 instruct models of the primary run (default filter, first sentence, 32 x edges swaps; results and graph snapshots in
results_2026-10-01_Local/e2_filtered_default_main_32x). Within each family (Gemma3, Qwen2.5, Qwen3) the Spearman correlation with the parameter count of

  S1  d = |ln R - ln R_WordNet|              (distance in R; R_WordNet = 15.7)
  S2  J = Jaccard(model's mutual pairs, WordNet's mutual pairs)

Qwen3-4B-Instruct-2507, a later checkpoint at the size of Qwen3-4B, is left out of the trend and added in a sensitivity row. Labels, reading and limits are
fixed in research/DECISION_LOG.md D031. Descriptive, no reading: raw mutual pairs, null mean, and the kernel-ratio distance d_k = |kernel ratio - WordNet's|.
Output is recorded in outputs/31_scale_convergence.txt.
"""
import json
import math
import re
import sys
from pathlib import Path

from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
RUN = ROOT / "results_2026-10-01_Local" / "e2_filtered_default_main_32x"
FAMILIES = ("Gemma3", "Qwen2.5", "Qwen3")
LATER_CHECKPOINT = "Qwen3-4B-Instruct-2507"


def load(key):
    return json.loads((RUN / "results" / f"{key}.json").read_text(encoding="utf-8"))


def pairs(key):
    g = json.loads((RUN / "graphs" / f"{key}.json").read_text(encoding="utf-8"))
    edges = {tuple(e) for e in g["edges"]}
    return {tuple(sorted((u, v))) for (u, v) in edges if (v, u) in edges and u != v}


def size_b(name):
    m = re.search(r"-(\d+(?:\.\d+)?)B", name)
    return float(m.group(1))


wn = load("main__wordnet")
R_WN, K_WN = wn["reciprocity_excess"], wn["observed"]["kernel_ratio"]
P_WN = pairs("main__wordnet")
assert round(R_WN, 1) == 15.7 and len(P_WN) == 27, (R_WN, len(P_WN))

rows = []
for p in sorted((RUN / "results").glob("main__*.json")):
    key = p.stem
    name = key[6:]
    if name.endswith("-pt") or name == "wordnet" or name.startswith("Gemma3-270M"):
        continue
    r = load(key)
    P = pairs(key)
    shared = len(P & P_WN)
    rows.append({
        "name": name, "family": name.split("-")[0], "size": size_b(name), "R": r["reciprocity_excess"], "pairs": r["observed"]["cycles_2"],
        "null": r["null_mean"]["cycles_2"], "d": abs(math.log(r["reciprocity_excess"]) - math.log(R_WN)), "shared": shared,
        "J": shared / len(P | P_WN), "kernel": r["observed"]["kernel_ratio"], "dk": abs(r["observed"]["kernel_ratio"] - K_WN),
        "kz": r["z"]["kernel_ratio"],
    })
assert len(rows) == 17 and {r["family"] for r in rows} == set(FAMILIES), (len(rows), {r["family"] for r in rows})

print("1. THE 17 INSTRUCT MODELS (default filter, first sentence)")
print(f"   WordNet: R {R_WN:.1f}, {len(P_WN)} mutual pairs, kernel ratio {K_WN:.4f}")
print(f"   {'model':24}{'size B':>7}{'R':>7}{'pairs':>6}{'null':>7}{'d=|ln R/R_WN|':>15}{'shared':>7}{'J':>7}{'kernel':>8}{'d_k':>8}{'kernel z':>9}")
for fam in FAMILIES:
    for r in sorted((x for x in rows if x["family"] == fam), key=lambda x: (x["size"], x["name"])):
        flag = "  (left out of the trend)" if r["name"] == LATER_CHECKPOINT else ""
        print(f"   {r['name']:24}{r['size']:7.1f}{r['R']:7.1f}{r['pairs']:6d}{r['null']:7.2f}{r['d']:15.2f}{r['shared']:7d}{r['J']:7.3f}{r['kernel']:8.4f}{r['dk']:8.4f}{r['kz']:9.2f}{flag}")


def rho(sel, stat):
    xs = [x["size"] for x in sel]
    ys = [x[stat] for x in sel]
    if len(set(ys)) < 2:
        return float("nan"), float("nan")
    return spearmanr(xs, ys)


def label(stat, value):
    toward = value <= -0.6 if stat == "d" else value >= 0.6
    away = value >= 0.6 if stat == "d" else value <= -0.6
    return "toward" if toward else ("away" if away else "none")


def analyse(title, include_later):
    print(f"\n{title}")
    print(f"   {'family':9}{'n':>3}   {'S1 rho (d)':>11}{'p':>6}  {'label':7}   {'S2 rho (J)':>11}{'p':>6}  {'label':7}")
    labels = {"d": [], "J": []}
    for fam in FAMILIES:
        sel = [x for x in rows if x["family"] == fam and (include_later or x["name"] != LATER_CHECKPOINT)]
        out = []
        for stat in ("d", "J"):
            rv, pv = rho(sel, stat)
            lab = label(stat, rv) if rv == rv else "none"
            labels[stat].append(lab)
            out.append((rv, pv, lab))
        print(f"   {fam:9}{len(sel):3d}   {out[0][0]:+11.2f}{out[0][1]:6.2f}  {out[0][2]:7}   {out[1][0]:+11.2f}{out[1][1]:6.2f}  {out[1][2]:7}")
    supported = all(sum(l == "toward" for l in labels[s]) >= 2 and "away" not in labels[s] for s in ("d", "J"))
    contradicted = all(sum(l == "away" for l in labels[s]) >= 2 for s in ("d", "J"))
    verdict = "CONVERGENCE WITH SIZE IS SUPPORTED" if supported else ("CONVERGENCE IS CONTRADICTED" if contradicted else "NO CONSISTENT APPROACH")
    print(f"   S1 labels {labels['d']}, S2 labels {labels['J']}  ->  {verdict}")
    return verdict


print()
v_main = analyse("2. THE READING OF D031 (trend with Qwen3-4B-Instruct-2507 left out)", include_later=False)
v_sens = analyse("3. SENSITIVITY: Qwen3-4B-Instruct-2507 included", include_later=True)

print("\n4. DESCRIPTIVE (no reading): rank correlation with parameter count within each family (2507 left out)")
print(f"   {'family':9}{'n':>3}   {'R':>8}{'pairs':>8}{'null':>8}{'d_k':>8}{'kernel':>8}{'kernel z':>9}")
for fam in FAMILIES:
    sel = [x for x in rows if x["family"] == fam and x["name"] != LATER_CHECKPOINT]
    print(f"   {fam:9}{len(sel):3d}   " + "".join(f"{rho(sel, s)[0]:+8.2f}" for s in ("R", "pairs", "null", "dk", "kernel")) + f"{rho(sel, 'kz')[0]:+9.2f}")
print("   (R is a ratio of the observed pairs to the null mean; where R and the pairs move differently, the null mean explains it.)")
print(f"\n5. SHARED PAIRS WITH WORDNET: {sorted(r['shared'] for r in rows)} (of {len(P_WN)}); models with 0 shared pairs: {sum(r['shared'] == 0 for r in rows)}")
