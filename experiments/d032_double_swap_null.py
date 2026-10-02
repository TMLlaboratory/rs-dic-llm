"""D032 — a degree-preserving null that can break every mutual pair: directed double-edge swaps.

The null of the paper (experiments/e1_full_null.py, networkx `directed_edge_swap`, a three-edge move) cannot move the edges of a mutual pair whose words have
few other links (D030): such pairs stay in every replicate, add the same number to the observed count and to the null mean, and pull R toward 1, more so in sparse
graphs. This script runs the standard directed double-edge swap instead (Maslov-Sneppen): pick two distinct edges (a->b) and (c->d) uniformly at random, propose
(a->d) and (c->b), and accept unless it makes a self-loop (a = d or c = b), a multi-edge (a->d or c->b exists) or is a no-op (a = c or b = d). Every node keeps its in-
and out-degree. Proposals are symmetric, so the stationary distribution is uniform over the graphs reachable from the observed one.

Per graph: `--reps` replicates (default 100) of `--swap-mult` x edges accepted swaps (default 32); replicate seeds sha256('d032|key|idx')[:4]. Recorded per replicate: the
number of mutual pairs and how many of the observed pairs it still contains. Per graph: observed pairs, null mean and SD, R = observed / max(null mean, 0.5), R' = observed /
null mean, exact Poisson range, bootstrap range of R (null replicates only), mean observed pairs kept.

Graphs (snapshots written by the earlier runs, default filter, first sentence): the 23 main graphs (17 instruct, 5 pretrained, WordNet), the 5 few-shot graphs, the 28 graphs of D029 and the 32
closed sub-dictionaries of D030. Readings: DECISION_LOG.md D032; applied by research/audit_scripts/36_double_swap_readings.py.

Usage (repo root):
    python -m experiments.d032_double_swap_null --out results_2026-10-02_Local/d032_double_swap_null --workers 12
    python -m experiments.d032_double_swap_null --out /tmp/d032_smoke --smoke
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

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

PRIMARY = "results_2026-10-01_Local"
SOURCES = {  # folder with graphs/<key>.json, key prefix
    "main__": f"{PRIMARY}/e2_filtered_default_main_32x",
    "e3__": f"{PRIMARY}/e2_filtered_default_controls_32x",
    "d029__": "results_2026-10-02_Local/d029_survivor_restriction",
    "d030c__": "results_2026-10-02_Local/d030_closed_subdictionaries",
}
BOOTSTRAP_B = 10_000
R_FLOOR = 0.5


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def graph_paths() -> dict[str, Path]:
    out = {}
    for prefix, folder in SOURCES.items():
        for p in sorted((ROOT / folder / "graphs").glob(f"{prefix}*.json")):
            out[p.stem] = p
    return out


def seed_for(key: str, idx: int) -> int:
    return int.from_bytes(hashlib.sha256(f"d032|{key}|{idx}".encode()).digest()[:4], "big")


def mutual(S: set) -> set:
    return {(u, v) for (u, v) in S if u < v and (v, u) in S}


def double_swap(edges: list, nswap: int, rng: random.Random, max_tries: int):
    E = list(edges)
    S = set(E)
    m = len(E)
    done = tries = 0
    while done < nswap and tries < max_tries:
        tries += 1
        i, j = rng.randrange(m), rng.randrange(m)
        if i == j:
            continue
        a, b = E[i]
        c, d = E[j]
        if a == c or b == d or a == d or c == b:
            continue
        if (a, d) in S or (c, b) in S:
            continue
        S.remove((a, b))
        S.remove((c, d))
        S.add((a, d))
        S.add((c, b))
        E[i] = (a, d)
        E[j] = (c, b)
        done += 1
    return S, done, tries


_CACHE: dict = {}


def _load(key: str, path: str):
    if key not in _CACHE:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        edges = [tuple(e) for e in data["edges"]]
        _CACHE[key] = (edges, mutual(set(edges)))
    return _CACHE[key]


def run_replicate(task: tuple) -> dict:
    key, path, idx, mult, tries_mult = task
    edges, obs_pairs = _load(key, path)
    rng = random.Random(seed_for(key, idx))
    t0 = time.time()
    S, done, tries = double_swap(edges, mult * len(edges), rng, tries_mult * mult * len(edges))
    p = mutual(S)
    return {"key": key, "idx": idx, "pairs": len(p), "kept": len(p & obs_pairs), "accepted": done, "tries": tries,
            "budget_met": done >= mult * len(edges), "sec": round(time.time() - t0, 2)}


def poisson_ci(k: int, level: float = 0.95):
    from scipy.stats import chi2

    a = (1 - level) / 2
    return (0.0 if k == 0 else chi2.ppf(a, 2 * k) / 2), chi2.ppf(1 - a, 2 * (k + 1)) / 2


def finalize(key: str, path: Path, reps: list[dict], args) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    edges = [tuple(e) for e in data["edges"]]
    obs = len(mutual(set(edges)))
    null = [r["pairs"] for r in reps]
    mean, sd = st.mean(null), st.pstdev(null)
    rng = np.random.default_rng(0)
    arr = np.asarray(null, dtype=float)
    means = rng.choice(arr, size=(BOOTSTRAP_B, len(arr)), replace=True).mean(axis=1)
    r_boot = obs / np.maximum(means, R_FLOOR)
    lo, hi = poisson_ci(obs)
    return {
        "key": key, "n_nodes": len(data["nodes"]), "n_edges": len(edges), "snapshot_sha256": sha256_file(path),
        "observed": {"cycles_2": obs}, "null_mean": {"cycles_2": mean}, "null_sd": {"cycles_2": sd},
        "reciprocity_excess": obs / max(mean, R_FLOOR), "R_prime": (obs / mean) if mean > 0 else None,
        "R_floor_applied": mean < R_FLOOR, "R_ci95": [float(np.percentile(r_boot, 2.5)), float(np.percentile(r_boot, 97.5))],
        "R_poisson_range": [lo / max(mean, R_FLOOR), hi / max(mean, R_FLOOR)],
        "replicates": len(reps), "swap_mult": args.swap_mult, "budget_not_met": sum(not r["budget_met"] for r in reps),
        "kept_observed_pairs_mean": st.mean(r["kept"] for r in reps), "accepted_mean": st.mean(r["accepted"] for r in reps),
        "tries_mean": st.mean(r["tries"] for r in reps),
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--reps", type=int, default=100)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--swap-mult", type=int, default=32)
    parser.add_argument("--tries-mult", type=int, default=200, help="try limit = tries-mult x accepted swaps asked for")
    parser.add_argument("--smoke", action="store_true", help="3 graphs x 3 replicates")
    args = parser.parse_args(argv)

    os.chdir(ROOT)
    out = Path(args.out)
    for sub in ("replicates", "results"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    started = datetime.now().isoformat(timespec="seconds")
    paths = graph_paths()
    if args.smoke:
        paths = dict(list(paths.items())[:3])
        args.reps = 3
    print(f"[d032] {len(paths)} graphs x {args.reps} replicates, {args.workers} workers, {args.swap_mult} x edges accepted swaps", flush=True)

    files = {k: out / "replicates" / f"{k}.jsonl" for k in paths}
    done: dict[str, dict[int, dict]] = {}
    for k, p in files.items():
        done[k] = {}
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    done[k][rec["idx"]] = rec
    t0 = time.time()
    results: dict[str, dict] = {}

    def maybe_finalize(key: str) -> None:
        reps = [done[key][i] for i in sorted(done[key])]
        res = finalize(key, paths[key], reps, args)
        results[key] = res
        (out / "results" / f"{key}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(f"[d032] {time.time() - t0:7.0f}s  {key:26} E={res['n_edges']:>6} obs={res['observed']['cycles_2']:>4} null={res['null_mean']['cycles_2']:6.2f} "
              f"R={res['reciprocity_excess']:7.2f} kept={res['kept_observed_pairs_mean']:5.2f} budget_not_met={res['budget_not_met']}", flush=True)

    tasks = []
    for key in paths:
        res_path = out / "results" / f"{key}.json"
        if len(done[key]) >= args.reps and not res_path.exists():
            maybe_finalize(key)
        elif res_path.exists() and len(done[key]) >= args.reps:
            results[key] = json.loads(res_path.read_text(encoding="utf-8"))
        for idx in range(args.reps):
            if idx not in done[key]:
                tasks.append((key, str(paths[key]), idx, args.swap_mult, args.tries_mult))
    print(f"[d032] {len(tasks)} replicates to run ({sum(len(v) for v in done.values())} already done)", flush=True)
    handles = {k: open(p, "a", encoding="utf-8") for k, p in files.items()}
    try:
        with Pool(args.workers) as pool:
            for rec in pool.imap_unordered(run_replicate, tasks, chunksize=4):
                key = rec["key"]
                handles[key].write(json.dumps(rec) + "\n")
                handles[key].flush()
                done[key][rec["idx"]] = rec
                if len(done[key]) == args.reps:
                    maybe_finalize(key)
    finally:
        for fh in handles.values():
            fh.close()
    (out / "run_info.json").write_text(json.dumps({
        "started": started, "finished": datetime.now().isoformat(timespec="seconds"), "args": vars(args), "python": sys.version.split()[0],
        "script_sha256": sha256_file(ROOT / "experiments" / "d032_double_swap_null.py"),
        "graphs": {k: str(v.relative_to(ROOT)) for k, v in paths.items()},
        "note": "D032: directed double-edge swap null; seeds sha256('d032|key|idx')[:4]",
    }, indent=1), encoding="utf-8")
    print(f"[d032] done in {time.time() - t0:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
