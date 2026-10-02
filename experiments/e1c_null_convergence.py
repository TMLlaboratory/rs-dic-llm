"""E1c — How many edge swaps does the degree-preserving null need? (decision D020, option b)

E1 used 5 x edges swaps and E1b 15 x; R rose by a median 13 % from one to the other and 10 of
24 graphs exhausted the try budget at 15 x. This run follows ONE long swap chain per
replicate and records the null statistics at checkpoints up to 128 x E (cumulative swaps in units of the
number of edges E), so the relaxation curve shows where the null mean stops falling, and
counts the tries each segment needs, so the budget can be set from the measured acceptance.

The chain is an instrumented copy of nx.directed_edge_swap (networkx 3.6.1) that also counts
tries; with the same seed it gives the same graph as networkx (checked in the smoke test).
Graphs are the snapshots E1 saved, so they are the graphs of the E1 results.

Usage (repo root):
    python -m experiments.e1c_null_convergence --out results_2026-10-01_Local/e1c_null_convergence
    python -m experiments.e1c_null_convergence --out ... --summary-only
    python -m experiments.e1c_null_convergence --out /tmp/e1c_smoke --smoke
Resumable: finished chains are appended to chains.jsonl and skipped on re-run.
"""
import argparse
import hashlib
import json
import math
import os
import random
import statistics
import subprocess
import sys
import time
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from experiments.null_model import compute_kernel  # noqa: E402

GRAPH_DIR = "results_2026-10-01_Local/e1_null_unfiltered/graphs"
DEFAULT_GRAPHS = ["main__wordnet", "main__Gemma3-1B", "main__Qwen2.5-32B",
                  "main__Qwen3-14B", "main__Gemma3-27B-pt", "main__Qwen2.5-72B"]
DEFAULT_CHECKPOINTS = [1, 2, 4, 8, 16, 24, 32, 48, 64, 96, 128]  # cumulative swaps / E
TRIES_PER_SWAP = 1000  # try limit of a segment = 1000 x the swaps it asks for (never meant to bind)
R_FLOOR = 0.5  # as in null_model.analyse


def load_graph(key: str, graph_dir: str) -> nx.DiGraph:
    with open(os.path.join(graph_dir, f"{key}.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    G = nx.DiGraph()
    G.add_nodes_from(data["nodes"])
    G.add_edges_from(data["edges"])
    return G


def swap_counting(G: nx.DiGraph, nswap: int, rng: random.Random, max_tries: int):
    """Copy of nx.directed_edge_swap (3.6.1) that returns (swaps, tries, reached_target)."""
    keys, degrees = zip(*G.degree())
    cdf = nx.utils.cumulative_distribution(degrees)
    discrete_sequence = nx.utils.discrete_sequence
    tries = swaps = 0
    while swaps < nswap:
        start = keys[discrete_sequence(1, cdistribution=cdf, seed=rng)[0]]
        tries += 1
        if tries > max_tries:
            return swaps, tries, False
        if G.out_degree(start) == 0:
            continue
        second = rng.choice(list(G.succ[start]))
        if start == second:
            continue
        if G.out_degree(second) == 0:
            continue
        third = rng.choice(list(G.succ[second]))
        if second == third:
            continue
        if G.out_degree(third) == 0:
            continue
        fourth = rng.choice(list(G.succ[third]))
        if third == fourth:
            continue
        if third not in G.succ[start] and fourth not in G.succ[second] and second not in G.succ[third]:
            G.add_edge(start, third)
            G.add_edge(third, second)
            G.add_edge(second, fourth)
            G.remove_edge(start, second)
            G.remove_edge(second, third)
            G.remove_edge(third, fourth)
            swaps += 1
    return swaps, tries, True


def metrics(G: nx.DiGraph) -> dict:
    n = G.number_of_nodes()
    return {
        "mutual_pairs": sum(1 for u, v in G.edges() if G.has_edge(v, u)) // 2,
        "kernel_ratio": len(compute_kernel(G)) / n,
        "circulation_rate": sum(len(c) for c in nx.strongly_connected_components(G) if len(c) > 1) / n,
    }


def seed_for(key: str, rep: int) -> int:
    return int.from_bytes(hashlib.sha256(f"e1c|{key}|{rep}".encode()).digest()[:8], "big")


_CACHE: dict = {}


def run_chain(task: tuple) -> dict:
    key, rep, checkpoints, graph_dir = task
    if key not in _CACHE:
        _CACHE[key] = load_graph(key, graph_dir)
    G = _CACHE[key].copy()
    edges = G.number_of_edges()
    rng = random.Random(seed_for(key, rep))
    record = {"key": key, "rep": rep, "edges": edges, "checkpoints": []}
    done, t0 = 0, time.time()
    for k in checkpoints:
        segment = k * edges - done
        swaps, tries, reached = swap_counting(G, segment, rng, TRIES_PER_SWAP * max(segment, 1))
        done += swaps
        record["checkpoints"].append({"k": k, "swaps": done, "segment_swaps": swaps, "segment_tries": tries,
                                      "reached": reached, **metrics(G)})
        if not reached:
            break
    record["seconds"] = round(time.time() - t0, 1)
    return record


def summarize(out: Path, graph_dir: str) -> None:
    from scipy.optimize import curve_fit

    chains = [json.loads(line) for line in open(out / "chains.jsonl", encoding="utf-8") if line.strip()]
    by_key: dict = {}
    for c in chains:
        by_key.setdefault(c["key"], []).append(c)
    lines = []
    recommend_k, worst_acc = [], 1.0
    for key, cs in by_key.items():
        G = load_graph(key, graph_dir)
        obs = metrics(G)
        edges = G.number_of_edges()
        ks = sorted({cp["k"] for c in cs for cp in c["checkpoints"]})
        table = []
        for k in ks:
            cps = [cp for c in cs for cp in c["checkpoints"] if cp["k"] == k and cp["reached"]]
            if len(cps) < 3:
                continue
            m = [cp["mutual_pairs"] for cp in cps]
            mean, sd = statistics.mean(m), statistics.pstdev(m)
            kz = (obs["kernel_ratio"] - statistics.mean(cp["kernel_ratio"] for cp in cps)) / (
                statistics.pstdev([cp["kernel_ratio"] for cp in cps]) or 1e-9)
            cz = (obs["circulation_rate"] - statistics.mean(cp["circulation_rate"] for cp in cps)) / (
                statistics.pstdev([cp["circulation_rate"] for cp in cps]) or 1e-9)
            acc = sum(cp["segment_swaps"] for cp in cps) / max(sum(cp["segment_tries"] for cp in cps), 1)
            table.append(dict(k=k, n=len(cps), mean=mean, se=sd / math.sqrt(len(cps)),
                              R=obs["mutual_pairs"] / max(mean, R_FLOOR), kz=kz, cz=cz, acceptance=acc))
        if not table:
            continue
        ref_rows = table[-max(3, len(table) // 3):]  # the last third of the checkpoints
        ref = statistics.mean(r["mean"] for r in ref_rows)
        settled = None
        for i, r in enumerate(table):
            if all(abs(x["mean"] - ref) <= max(2 * x["se"], 0.05 * ref) for x in table[i:]):
                settled = r["k"]
                break
        fit = ""
        try:
            xs = [r["k"] for r in table]
            ys = [r["mean"] for r in table]
            sig = [max(r["se"], 1e-3) for r in table]
            popt, pcov = curve_fit(lambda x, a, b, tau: a + b * np.exp(-x / tau), xs, ys, sigma=sig,
                                   p0=[ys[-1], ys[0] - ys[-1], 4.0], maxfev=20000)
            fit = (f"exponential fit: limit {popt[0]:.2f} +/- {math.sqrt(pcov[0][0]):.2f}, "
                   f"time constant {popt[2]:.1f} x E  ->  R(limit) = {obs['mutual_pairs'] / max(popt[0], R_FLOOR):.1f}")
        except Exception:  # noqa: BLE001
            fit = "exponential fit: did not converge"
        lines.append(f"\n{key}  (E={edges}, observed mutual pairs {obs['mutual_pairs']}, {len(cs)} chains)")
        lines.append(f"  {'swaps/E':>8}{'chains':>7}{'null mean':>11}{'SE':>7}{'R':>8}{'kernel z':>10}{'circ z':>8}{'accept %':>10}")
        for r in table:
            lines.append(f"  {r['k']:>8}{r['n']:>7}{r['mean']:>11.2f}{r['se']:>7.2f}{r['R']:>8.1f}{r['kz']:>10.2f}{r['cz']:>8.2f}{100 * r['acceptance']:>10.2f}")
        lines.append(f"  reference (mean of swaps/E >= {ref_rows[0]['k']}): {ref:.2f}; mean within 5 % (or 2 SE) of it from swaps/E = {settled}")
        lines.append(f"  {fit}")
        done = sorted({c["checkpoints"][-1]["k"] for c in cs})
        lines.append(f"  chains stopped early (try limit hit): {sum(1 for c in cs if not c['checkpoints'][-1]['reached'])}; last checkpoint reached by chains: {done}")
        if settled:
            recommend_k.append(settled)
        worst_acc = min(worst_acc, min(r["acceptance"] for r in table))
    if recommend_k:
        k_rec = max(recommend_k)
        safe = 2 ** math.ceil(math.log2(max(k_rec * 2, 1)))
        lines.append(f"\nRECOMMENDATION (indicative, for the researcher to decide): the null mean has settled by "
                     f"{k_rec} x E on every graph listed; use {safe} x E (a factor 2 margin, rounded to a power of 2) and a try "
                     f"limit of {math.ceil(3 / worst_acc)} x the requested swaps (3 / the lowest measured acceptance of "
                     f"{100 * worst_acc:.2f} %).")
    text = "\n".join(lines)
    (out / "summary.txt").write_text(text, encoding="utf-8")
    print(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--graphs", nargs="+", default=DEFAULT_GRAPHS)
    parser.add_argument("--graph-dir", default=GRAPH_DIR)
    parser.add_argument("--reps", type=int, default=30)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--checkpoints", nargs="+", type=int, default=DEFAULT_CHECKPOINTS)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--smoke", action="store_true", help="2 graphs x 2 chains x checkpoints 1 2 4")
    args = parser.parse_args(argv)
    os.chdir(ROOT)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.smoke:
        args.graphs, args.reps, args.checkpoints = args.graphs[:2], 2, [1, 2, 4]
        # exactness check against networkx, same seed
        G0 = load_graph(args.graphs[0], args.graph_dir)
        A = G0.copy()
        nx.directed_edge_swap(A, nswap=3000, max_tries=10 ** 7, seed=12345)
        B = G0.copy()
        swap_counting(B, 3000, random.Random(12345), 10 ** 7)
        assert set(A.edges()) == set(B.edges()), "instrumented swap differs from networkx"
        print("smoke: instrumented swap reproduces networkx")
    path = out / "chains.jsonl"
    if not args.summary_only:
        done = set()
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    done.add((rec["key"], rec["rep"]))
        tasks = [(k, r, args.checkpoints, args.graph_dir) for r in range(args.reps) for k in args.graphs
                 if (k, r) not in done]
        print(f"[e1c] {len(tasks)} chains to run ({len(done)} done), checkpoints {args.checkpoints}, "
              f"{args.workers} workers", flush=True)
        started, t0 = datetime.now().isoformat(timespec="seconds"), time.time()
        with open(path, "a", encoding="utf-8") as fh, Pool(args.workers) as pool:
            for n, rec in enumerate(pool.imap_unordered(run_chain, tasks, chunksize=1), start=1):
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                last = rec["checkpoints"][-1]
                print(f"[e1c] {time.time() - t0:7.0f}s  chain {n}/{len(tasks)}  {rec['key']:24} rep {rec['rep']:2}  "
                      f"reached {last['k']} x E  mutual pairs {last['mutual_pairs']}  {rec['seconds']}s", flush=True)
        (out / "run_info.json").write_text(json.dumps({
            "started": started, "finished": datetime.now().isoformat(timespec="seconds"),
            "args": vars(args), "tries_per_swap_limit": TRIES_PER_SWAP,
            "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip(),
            "networkx": nx.__version__}, indent=1), encoding="utf-8")
    summarize(out, args.graph_dir)


if __name__ == "__main__":
    main()
