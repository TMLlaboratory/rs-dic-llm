"""D032 validation — does the directed double-edge swap null settle, can it break the observed pairs, and does it agree with the independent-edge estimate?

For eight graphs (dense and sparse) this follows `--chains` swap chains per graph and records the number of mutual pairs and the number of observed pairs still present at
checkpoints of 1, 2, 4, 8, 16, 32, 64 and 128 x edges accepted swaps. It also computes the independent-edge (configuration-model) estimate of the expected number of mutual
pairs, sum over node pairs of min(1, d_out(u) d_in(v) / m) x min(1, d_out(v) d_in(u) / m), which is what a null that mixes freely should approach in sparse graphs.
The rules for accepting the null are in DECISION_LOG.md D032 (V1, V2). Output: <out>/chains.jsonl and <out>/summary.txt.

Usage: python -m experiments.d032_convergence --out results_2026-10-02_Local/d032_convergence --workers 12
"""

import argparse
import json
import os
import random
import statistics as st
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from experiments.d032_double_swap_null import graph_paths, mutual, seed_for  # noqa: E402

GRAPHS = ["e3__Gemma3-4B-pt", "main__Gemma3-1B", "main__Gemma3-12B", "main__wordnet", "main__Gemma3-12B-pt", "d029__fsS_4B", "d030c__fsRC3_4B", "d030c__itC_1B"]
CHECKPOINTS = [1, 2, 4, 8, 16, 32, 64, 128]


def chain(task: tuple) -> dict:
    key, path, rep = task
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    E = [tuple(e) for e in data["edges"]]
    S = set(E)
    obs = mutual(S)
    m = len(E)
    rng = random.Random(seed_for("conv|" + key, rep))
    done, rows = 0, []
    for k in CHECKPOINTS:
        target = k * m
        tries = 0
        while done < target and tries < 400 * target:
            tries += 1
            i, j = rng.randrange(m), rng.randrange(m)
            if i == j:
                continue
            a, b = E[i]
            c, d = E[j]
            if a == c or b == d or a == d or c == b or (a, d) in S or (c, b) in S:
                continue
            S.remove((a, b))
            S.remove((c, d))
            S.add((a, d))
            S.add((c, b))
            E[i], E[j] = (a, d), (c, b)
            done += 1
        p = mutual(S)
        rows.append({"k": k, "pairs": len(p), "kept": len(p & obs)})
    return {"key": key, "rep": rep, "rows": rows}


def independent_edge_estimate(path) -> float:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    idx = {w: i for i, w in enumerate(data["nodes"])}
    n = len(idx)
    dout, din = np.zeros(n), np.zeros(n)
    for u, v in data["edges"]:
        dout[idx[u]] += 1
        din[idx[v]] += 1
    m = len(data["edges"])
    P = np.minimum(1.0, np.outer(dout, din) / m)  # P[u, v]: probability of u -> v
    np.fill_diagonal(P, 0.0)
    return float((np.triu(P * P.T, 1)).sum())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--chains", type=int, default=30)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args(argv)
    os.chdir(ROOT)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    paths = graph_paths()
    path = out / "chains.jsonl"
    done = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["key"], r["rep"]))
    tasks = [(k, str(paths[k]), r) for r in range(args.chains) for k in GRAPHS if (k, r) not in done]
    print(f"[d032c] {len(tasks)} chains to run ({len(done)} done), checkpoints {CHECKPOINTS} x edges", flush=True)
    t0 = time.time()
    with open(path, "a", encoding="utf-8") as fh, Pool(args.workers) as pool:
        for n, rec in enumerate(pool.imap_unordered(chain, tasks, chunksize=1), start=1):
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            if n % 20 == 0:
                print(f"[d032c] {time.time() - t0:6.0f}s  {n}/{len(tasks)}", flush=True)
    recs = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    lines = ["D032 validation of the directed double-edge swap null (accepted swaps per edge; mean over chains; SE = SD / sqrt(chains))\n"]
    for key in GRAPHS:
        cs = [r for r in recs if r["key"] == key]
        obs = len(mutual({tuple(e) for e in json.loads(Path(paths[key]).read_text(encoding="utf-8"))["edges"]}))
        lines.append(f"{key}  (observed pairs {obs}, {len(cs)} chains; independent-edge estimate {independent_edge_estimate(paths[key]):.2f})")
        lines.append(f"   {'swaps/E':>8}{'null mean':>11}{'SE':>7}{'observed pairs kept':>21}")
        for i, k in enumerate(CHECKPOINTS):
            pairs = [r["rows"][i]["pairs"] for r in cs]
            kept = [r["rows"][i]["kept"] for r in cs]
            lines.append(f"   {k:>8}{st.mean(pairs):>11.2f}{st.pstdev(pairs) / max(len(pairs), 1) ** 0.5:>7.2f}{st.mean(kept):>21.2f}")
        lines.append("")
    (out / "summary.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
