"""Is the analytic R (rs_dic_llm.metrics.scc.reciprocity_excess) just the rewiring R off by a factor 2?

Audit script (2026-10-01). Needs the graph cache from 1_build_graphs.py and the null means
recorded in outputs/2_compare_R.txt (20 replicates, nswap = 5 x edges).
"""
import os
import pickle
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "_cache" / "graphs"
EMPIRICAL_NULL_MEAN = {  # mean mutual pairs over 20 rewirings, from outputs/2_compare_R.txt
    "main__Gemma3-27B": 3.35, "main__Gemma3-27B-pt": 3.65, "main__Gemma3-4B-pt": 2.85,
    "main__Gemma3-4B": 2.2, "main__Qwen2.5-72B": 7.3, "main__wordnet": 2.5,
    "e3__Gemma3-27B-pt": 5.4, "e4__Gemma3-27B": 2.2, "e5__Qwen3-0.6B": 3.15,
}

print(f"{'graph':22}{'obs':>5}{'null_emp':>9}{'analytic_code':>14}{'analytic_half':>14}{'R_emp':>7}{'R_code':>7}{'R_2x':>7}")
for key, null_emp in EMPIRICAL_NULL_MEAN.items():
    with open(os.path.join(CACHE, key + ".pkl"), "rb") as fh:
        G = pickle.load(fh)
    E = G.number_of_edges()
    a = [G.out_degree(n) * G.in_degree(n) for n in G]
    code = (sum(a) ** 2 - sum(x * x for x in a)) / E ** 2  # value used by reciprocity_excess
    obs = sum(1 for u, v in G.edges() if G.has_edge(v, u)) // 2
    print(f"{key:22}{obs:>5}{null_emp:>9.2f}{code:>14.2f}{code / 2:>14.2f}"
          f"{obs / max(null_emp, .5):>7.1f}{obs / code:>7.1f}{obs / (code / 2):>7.1f}")
