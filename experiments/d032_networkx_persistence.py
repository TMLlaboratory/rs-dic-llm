"""D032 validation, second half — how many observed mutual pairs does a replicate of the paper's null (networkx `directed_edge_swap`) still contain?

Reruns the first `--reps` stored replicates (stored seeds, so the run is the stored run: every rerun replicate must equal the stored `cycles_2`, or the script stops) for the
eight graphs of experiments/d032_convergence.py, and records for each replicate the number of mutual pairs and how many of the observed pairs it still contains. The same
quantity for the double-edge swap null is in the output of d032_convergence.py. Output: <out>/persistence.jsonl and <out>/summary.txt.

Usage: python -m experiments.d032_networkx_persistence --out results_2026-10-02_Local/d032_networkx_persistence --workers 8
"""

import argparse
import json
import os
import statistics as st
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from experiments import e1_full_null as e1  # noqa: E402
from experiments.d032_convergence import GRAPHS  # noqa: E402
from experiments.d032_double_swap_null import SOURCES, graph_paths  # noqa: E402

_CACHE: dict = {}


def run_one(task: tuple) -> dict:
    key, path, idx = task
    if key not in _CACHE:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        G = nx.DiGraph()
        G.add_nodes_from(data["nodes"])
        G.add_edges_from(data["edges"])
        _CACHE[key] = G
    G = _CACHE[key]
    obs = {tuple(sorted((u, v))) for u, v in G.edges() if G.has_edge(v, u) and u != v}
    H, failure = e1.rewire_checked(G, e1.seed_for(key, idx), 32, 9600)
    p = {tuple(sorted((u, v))) for u, v in H.edges() if H.has_edge(v, u) and u != v}
    return {"key": key, "idx": idx, "pairs": len(p), "kept": len(p & obs), "swap_failure": failure}


def stored_cycles(key: str) -> dict[int, int]:
    prefix = next(p for p in SOURCES if key.startswith(p))
    path = ROOT / SOURCES[prefix] / "replicates" / f"{key}.jsonl"
    return {rec["idx"]: rec["cycles_2"] for rec in e1._load_jsonl(str(path))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args(argv)
    os.chdir(ROOT)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    paths = graph_paths()
    tasks = [(k, str(paths[k]), i) for k in GRAPHS for i in range(args.reps)]
    stored = {k: stored_cycles(k) for k in GRAPHS}
    recs = []
    t0 = time.time()
    with open(out / "persistence.jsonl", "w", encoding="utf-8") as fh, Pool(args.workers) as pool:
        for n, rec in enumerate(pool.imap_unordered(run_one, tasks, chunksize=1), start=1):
            rec["matches_stored"] = rec["pairs"] == stored[rec["key"]][rec["idx"]]
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            recs.append(rec)
            if n % 20 == 0:
                print(f"[d032p] {time.time() - t0:6.0f}s  {n}/{len(tasks)}", flush=True)
    bad = [r for r in recs if not r["matches_stored"]]
    lines = ["D032 validation: observed mutual pairs still present in a replicate of the paper's null (networkx directed_edge_swap, 32 x edges; stored seeds; "
             f"{args.reps} replicates per graph; {len(recs) - len(bad)} of {len(recs)} equal the stored replicate)\n",
             f"{'graph':22}{'observed pairs':>16}{'null pairs (mean)':>19}{'observed pairs kept (mean)':>28}{'kept / null mean':>18}"]
    for key in GRAPHS:
        data = json.loads(Path(paths[key]).read_text(encoding="utf-8"))
        edges = {tuple(e) for e in data["edges"]}
        obs = len({tuple(sorted((u, v))) for (u, v) in edges if (v, u) in edges and u != v})
        rs = [r for r in recs if r["key"] == key]
        pm, km = st.mean(r["pairs"] for r in rs), st.mean(r["kept"] for r in rs)
        lines.append(f"{key:22}{obs:>16}{pm:>19.2f}{km:>28.2f}{km / pm if pm else float('nan'):>18.2f}")
    (out / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    assert not bad, f"rerun differs from the stored run for {len(bad)} replicates"


if __name__ == "__main__":
    main()
