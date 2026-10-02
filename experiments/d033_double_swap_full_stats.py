"""D033 — kernel ratio, circulation rate and cycle profile against the directed double-edge swap null.

The statistics of Section 4.1 (kernel ratio, circulation rate) and of the cycle-length profile were computed against the three-edge null of the paper (D030 and D032 show that this null
cannot break some mutual pairs). This script computes the same statistics (`e1_full_null.summarize_full`: kernel ratio, circulation rate, simple cycles up to length 7 with their histogram)
for replicates of the double-edge swap null of experiments/d032_double_swap_null.py: the 23 main graphs (17 instruct, 5 pretrained, WordNet; default filter, first sentence), 20 replicates each,
64 x edges accepted swaps, seeds sha256('d033|key|idx')[:4]. Per graph: observed values, null mean and SD (population SD, as in the paper), z-scores, null mean number of cycles of each length.
Readings: DECISION_LOG.md D033; applied by research/audit_scripts/37_double_swap_claim1.py.

Usage: python -m experiments.d033_double_swap_full_stats --out results_2026-10-02_Local/d033_double_swap_full_stats --workers 12
"""

import argparse
import hashlib
import json
import os
import random
import statistics as st
import sys
import time
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from experiments import e1_full_null as e1  # noqa: E402
from experiments.d032_double_swap_null import double_swap  # noqa: E402

GRAPH_DIR = ROOT / "results_2026-10-01_Local" / "e2_filtered_default_main_32x" / "graphs"
METRICS = ("kernel_ratio", "circulation_rate", "cycles_total", "cycles_2", "cycles_long")
_CACHE: dict = {}


def seed_for(key: str, idx: int) -> int:
    return int.from_bytes(hashlib.sha256(f"d033|{key}|{idx}".encode()).digest()[:4], "big")


def _load(key: str):
    if key not in _CACHE:
        data = json.loads((GRAPH_DIR / f"{key}.json").read_text(encoding="utf-8"))
        _CACHE[key] = (data["nodes"], [tuple(e) for e in data["edges"]])
    return _CACHE[key]


def run_replicate(task: tuple) -> dict:
    key, idx, mult = task
    nodes, edges = _load(key)
    rng = random.Random(seed_for(key, idx))
    t0 = time.time()
    S, done, tries = double_swap(edges, mult * len(edges), rng, 200 * mult * len(edges))
    H = nx.DiGraph()
    H.add_nodes_from(nodes)
    H.add_edges_from(S)
    rec = e1.summarize_full(H, len(nodes))
    rec.update(key=key, idx=idx, accepted=done, budget_met=done >= mult * len(edges), sec=round(time.time() - t0, 1))
    return rec


def finalize(key: str, reps: list[dict]) -> dict:
    nodes, edges = _load(key)
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    obs = e1.summarize_full(G, len(nodes))
    mean = {m: st.mean(r[m] for r in reps) for m in METRICS}
    sd = {m: st.pstdev([r[m] for r in reps]) for m in METRICS}
    hist = {}
    for length in range(2, e1.CYCLE_BOUND + 1):
        hist[str(length)] = {"observed": obs["cycle_hist"].get(str(length), 0),
                             "null_mean": st.mean(r["cycle_hist"].get(str(length), 0) for r in reps)}
    return {"key": key, "n_nodes": len(nodes), "n_edges": len(edges), "replicates": len(reps),
            "observed": {m: obs[m] for m in METRICS}, "null_mean": mean, "null_sd": sd,
            "z": {m: (obs[m] - mean[m]) / (sd[m] or 1e-9) for m in METRICS}, "cycle_hist_observed_vs_null": hist,
            "budget_not_met": sum(not r["budget_met"] for r in reps)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--swap-mult", type=int, default=64)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)
    os.chdir(ROOT)
    out = Path(args.out)
    for sub in ("replicates", "results"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    keys = sorted(p.stem for p in GRAPH_DIR.glob("main__*.json"))
    if args.smoke:
        keys, args.reps = keys[:2], 2
    assert args.smoke or len(keys) == 23, len(keys)
    files = {k: out / "replicates" / f"{k}.jsonl" for k in keys}
    done = {k: {} for k in keys}
    for k, p in files.items():
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    done[k][r["idx"]] = r
    started = datetime.now().isoformat(timespec="seconds")
    t0 = time.time()
    tasks = [(k, i, args.swap_mult) for k in keys for i in range(args.reps) if i not in done[k]]
    print(f"[d033] {len(keys)} graphs x {args.reps} replicates, {len(tasks)} to run, {args.workers} workers", flush=True)

    def fin(k):
        res = finalize(k, [done[k][i] for i in sorted(done[k])])
        (out / "results" / f"{k}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(f"[d033] {time.time() - t0:6.0f}s  {k:28} kernel z {res['z']['kernel_ratio']:+6.2f}  circulation z {res['z']['circulation_rate']:+6.2f}  2-cycles obs {res['observed']['cycles_2']} null {res['null_mean']['cycles_2']:.2f}", flush=True)

    for k in keys:
        if len(done[k]) >= args.reps and not (out / "results" / f"{k}.json").exists():
            fin(k)
    handles = {k: open(p, "a", encoding="utf-8") for k, p in files.items()}
    try:
        with Pool(args.workers) as pool:
            for rec in pool.imap_unordered(run_replicate, tasks, chunksize=1):
                k = rec["key"]
                handles[k].write(json.dumps(rec) + "\n")
                handles[k].flush()
                done[k][rec["idx"]] = rec
                if len(done[k]) == args.reps:
                    fin(k)
    finally:
        for fh in handles.values():
            fh.close()
    (out / "run_info.json").write_text(json.dumps({"started": started, "finished": datetime.now().isoformat(timespec="seconds"), "args": vars(args), "python": sys.version.split()[0],
                                                   "networkx": nx.__version__, "script_sha256": e1.sha256_file("experiments/d033_double_swap_full_stats.py")}, indent=1), encoding="utf-8")
    print(f"[d033] done in {time.time() - t0:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
