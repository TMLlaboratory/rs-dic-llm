"""D032 validation: may the directed double-edge swap null be used? (rules V1 and V2 of DECISION_LOG.md D032)

Reads results_2026-10-02_Local/d032_convergence/chains.jsonl (experiments/d032_convergence.py: 30 chains on each of eight graphs, checkpoints of 1 to 128 x edges accepted swaps)
and results_2026-10-02_Local/d032_networkx_persistence/persistence.jsonl (experiments/d032_networkx_persistence.py: the paper's null on the same graphs, stored seeds).

  V1  the null is settled at 32 x edges if on every graph the mean number of pairs at 32 x lies within 10 % or two standard errors (of the difference) of the mean at 128 x
  V2  the mean number of observed pairs still present at 32 x is below 5 % of the observed pairs on every graph
  and, descriptive, the independent-edge estimate beside the means of both nulls, and the observed pairs that the paper's null keeps.

Output is recorded in outputs/35_double_swap_validation.txt.
"""
import json
import math
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from experiments.d032_convergence import CHECKPOINTS, GRAPHS, independent_edge_estimate  # noqa: E402
from experiments.d032_double_swap_null import graph_paths  # noqa: E402

conv = [json.loads(line) for line in (ROOT / "results_2026-10-02_Local" / "d032_convergence" / "chains.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
pers_path = ROOT / "results_2026-10-02_Local" / "d032_networkx_persistence" / "persistence.jsonl"
pers = [json.loads(line) for line in pers_path.read_text(encoding="utf-8").splitlines() if line.strip()] if pers_path.exists() else []
paths = graph_paths()
i32, i128 = CHECKPOINTS.index(32), CHECKPOINTS.index(128)


def observed(key):
    data = json.loads(Path(paths[key]).read_text(encoding="utf-8"))
    edges = {tuple(e) for e in data["edges"]}
    return len({tuple(sorted((u, v))) for (u, v) in edges if (v, u) in edges and u != v})


print("1. THE DOUBLE-EDGE SWAP NULL: mean mutual pairs by accepted swaps per edge (30 chains per graph); independent-edge estimate; observed pairs still present")
print(f"   {'graph':22}{'obs':>5}{'indep.':>8}" + "".join(f"{k:>7}x" for k in CHECKPOINTS) + f"{'kept at 32x':>13}")
v1_ok, v2_ok = [], []
for key in GRAPHS:
    cs = [c for c in conv if c["key"] == key]
    obs = observed(key)
    means = [st.mean(c["rows"][i]["pairs"] for c in cs) for i in range(len(CHECKPOINTS))]
    kept32 = st.mean(c["rows"][i32]["kept"] for c in cs)
    a = [c["rows"][i32]["pairs"] for c in cs]
    b = [c["rows"][i128]["pairs"] for c in cs]
    se = math.sqrt(st.pvariance(a) / len(a) + st.pvariance(b) / len(b))
    diff = abs(st.mean(a) - st.mean(b))
    ok1 = diff <= 0.10 * st.mean(b) or diff <= 2 * se
    ok2 = kept32 < 0.05 * obs
    v1_ok.append(ok1)
    v2_ok.append(ok2)
    print(f"   {key:22}{obs:>5}{independent_edge_estimate(paths[key]):>8.2f}" + "".join(f"{m:>8.2f}" for m in means) + f"{kept32:>13.2f}   V1 {'ok' if ok1 else 'FAILS'}, V2 {'ok' if ok2 else 'FAILS'}")
print(f"\n   V1 (settled at 32 x edges): {'met on all eight graphs' if all(v1_ok) else 'NOT met on ' + ', '.join(g for g, o in zip(GRAPHS, v1_ok) if not o)}")
print(f"   V2 (the null can break the observed pairs): {'met on all eight graphs' if all(v2_ok) else 'NOT met on ' + ', '.join(g for g, o in zip(GRAPHS, v2_ok) if not o)}")
if not all(v1_ok):
    for k in [c for c in CHECKPOINTS if c > 32]:  # D032: "the multiplier is raised to the smallest checkpoint that passes"
        ok = True
        j = CHECKPOINTS.index(k)
        for key in GRAPHS:
            cs = [c for c in conv if c["key"] == key]
            a = [c["rows"][j]["pairs"] for c in cs]
            b = [c["rows"][i128]["pairs"] for c in cs]
            se = math.sqrt(st.pvariance(a) / len(a) + st.pvariance(b) / len(b))
            d = abs(st.mean(a) - st.mean(b))
            ok &= d <= 0.10 * st.mean(b) or d <= 2 * se
        if ok:
            print(f"   smallest checkpoint that passes V1 on all graphs: {k} x edges")
            break

print("\n2. THE PAPER'S NULL (networkx directed_edge_swap, 32 x edges, stored seeds): observed pairs still present in a replicate")
if pers:
    print(f"   {'graph':22}{'obs':>5}{'null pairs (mean)':>19}{'observed pairs kept (mean)':>28}{'kept / null':>13}{'reps':>6}{'equal stored':>14}")
    for key in GRAPHS:
        rs = [r for r in pers if r["key"] == key]
        pm, km = st.mean(r["pairs"] for r in rs), st.mean(r["kept"] for r in rs)
        print(f"   {key:22}{observed(key):>5}{pm:>19.2f}{km:>28.2f}{km / pm if pm else float('nan'):>13.2f}{len(rs):>6}{sum(r['matches_stored'] for r in rs):>14}")
else:
    print("   (not run yet)")
