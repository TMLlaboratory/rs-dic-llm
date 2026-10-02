"""D030 (a) — where do the null model's mutual pairs come from?

Reruns the degree-preserving null of experiments/e1_full_null.py with the *stored seeds* for replicates 0-39 of 40 graphs and records, for every
replicate, which pairs of words are mutual. For each size s in 1B, 4B, 12B, 27B the graphs are

  the zero-shot, whole few-shot (E3) and whole instruct graph of the primary run (default filter, first sentence), and
  fsS, itS and fsR1..5 of D029 (results_2026-10-02_Local/d029_survivor_restriction).

Check (the script stops if it fails): the number of pairs of every rerun replicate equals the `cycles_2` stored for the same replicate in the run that
produced the graph, so that the rerun is the stored run and the pairs are the pairs that gave the stored null mean.
The readings are fixed in DECISION_LOG.md D030 and applied by research/audit_scripts/29_null_pairs.py.

Usage (from the repo root):
    python -m experiments.d030_null_pairs --out results_2026-10-02_Local/d030_null_pairs --workers 12
    python -m experiments.d030_null_pairs --out /tmp/d030a_smoke --smoke
"""

import argparse
import json
import os
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

SIZES = ("1B", "4B", "12B", "27B")
PRIMARY = "results_2026-10-01_Local"
D029 = "results_2026-10-02_Local/d029_survivor_restriction"
RUNS = {  # key pattern -> folder of the run that holds graphs/<key>.json and replicates/<key>.jsonl
    "main__Gemma3-{s}-pt": f"{PRIMARY}/e2_filtered_default_main_32x",
    "e3__Gemma3-{s}-pt": f"{PRIMARY}/e2_filtered_default_controls_32x",
    "main__Gemma3-{s}": f"{PRIMARY}/e2_filtered_default_main_32x",
    "d029__fsS_{s}": D029,
    "d029__itS_{s}": D029,
    **{f"d029__fsR{k}_{{s}}": D029 for k in range(1, 6)},
}
_CACHE: dict = {}


# Scheduling only (replicates are deterministic whatever the order): the graphs the reading of D030 (a) needs, the fsS graphs, come first, the slow whole graphs last.
ORDER = ("d029__fsS_{s}", "d029__itS_{s}", *(f"d029__fsR{k}_{{s}}" for k in range(1, 6)), "main__Gemma3-{s}-pt", "e3__Gemma3-{s}-pt", "main__Gemma3-{s}")


def graph_list() -> dict[str, str]:
    assert set(ORDER) == set(RUNS), "ORDER must list the same graph patterns as RUNS"
    return {pat.format(s=s): RUNS[pat] for pat in ORDER for s in SIZES}


def _load(key: str, folder: str) -> nx.DiGraph:
    if key not in _CACHE:
        data = json.loads((ROOT / folder / "graphs" / f"{key}.json").read_text(encoding="utf-8"))
        G = nx.DiGraph()
        G.add_nodes_from(data["nodes"])
        G.add_edges_from(data["edges"])
        _CACHE[key] = G
    return _CACHE[key]


def mutual_pairs(G: nx.DiGraph) -> list[list[str]]:
    return sorted([u, v] for u, v in {tuple(sorted((a, b))) for a, b in G.edges() if G.has_edge(b, a) and a != b})


def run_pairs(task: tuple) -> dict:
    key, folder, idx, nswap_mult, tries_mult = task
    G = _load(key, folder)
    H, failure = e1.rewire_checked(G, e1.seed_for(key, idx), nswap_mult, tries_mult)
    return {"key": key, "idx": idx, "swap_failure": failure, "pairs": mutual_pairs(H)}


def stored_cycles(key: str, folder: str) -> dict[int, int]:
    path = ROOT / folder / "replicates" / f"{key}.jsonl"
    return {rec["idx"]: rec["cycles_2"] for rec in e1._load_jsonl(str(path))}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--reps", type=int, default=40)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--nswap-mult", type=int, default=32)
    parser.add_argument("--tries-mult", type=int, default=9600)
    parser.add_argument("--smoke", action="store_true", help="2 graphs x 3 replicates (the check against the stored run still applies)")
    args = parser.parse_args(argv)

    os.chdir(ROOT)
    out = Path(args.out)
    (out / "pairs").mkdir(parents=True, exist_ok=True)
    started = datetime.now().isoformat(timespec="seconds")
    graphs = graph_list()
    if args.smoke:
        graphs = dict(list(graphs.items())[:2])
        args.reps = 3
    stored = {k: stored_cycles(k, f) for k, f in graphs.items()}
    print(f"[d030a] {len(graphs)} graphs x {args.reps} replicates, {args.workers} workers", flush=True)

    files = {k: out / "pairs" / f"{k}.jsonl" for k in graphs}
    done: dict[str, dict[int, dict]] = {}
    for k, p in files.items():
        done[k] = {}
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    done[k][rec["idx"]] = rec
    tasks = [(k, graphs[k], i, args.nswap_mult, args.tries_mult) for k in graphs for i in range(args.reps) if i not in done[k]]
    print(f"[d030a] {len(tasks)} replicates to run ({sum(len(v) for v in done.values())} already done)", flush=True)
    handles = {k: open(p, "a", encoding="utf-8") for k, p in files.items()}
    t0 = time.time()
    n_done = 0
    mismatches = 0
    try:
        with Pool(args.workers) as pool:
            for rec in pool.imap_unordered(run_pairs, tasks, chunksize=1):
                k, i = rec["key"], rec["idx"]
                rec["n_pairs"] = len(rec["pairs"])
                rec["stored_cycles_2"] = stored[k][i]
                rec["matches_stored"] = rec["n_pairs"] == rec["stored_cycles_2"]
                mismatches += not rec["matches_stored"]
                handles[k].write(json.dumps(rec) + "\n")
                handles[k].flush()
                done[k][i] = rec
                n_done += 1
                if n_done % 50 == 0 or not rec["matches_stored"]:
                    print(f"[d030a] {time.time() - t0:7.0f}s  {n_done}/{len(tasks)}  mismatches so far {mismatches}", flush=True)
    finally:
        for fh in handles.values():
            fh.close()
    bad = [(k, i) for k in graphs for i, r in done[k].items() if not r["matches_stored"]]
    (out / "run_info.json").write_text(json.dumps({
        "started": started, "finished": datetime.now().isoformat(timespec="seconds"), "args": vars(args),
        "graphs": graphs, "python": sys.version.split()[0], "networkx": nx.__version__,
        "script_sha256": e1.sha256_file("experiments/d030_null_pairs.py"),
        "replicates_checked": sum(len(v) for v in done.values()), "mismatches": len(bad),
        "note": "D030 (a): null pairs by node, stored seeds sha256('e1|key|idx')[:4], replicates 0-39",
    }, indent=1), encoding="utf-8")
    assert not bad, f"rerun differs from the stored run for {bad[:5]}"
    print(f"[d030a] done in {time.time() - t0:.0f}s; all {sum(len(v) for v in done.values())} replicates equal the stored ones -> {out}", flush=True)


if __name__ == "__main__":
    main()
