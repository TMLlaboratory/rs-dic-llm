"""D034 — the prompt controls (E4: answers of 8 words or fewer; E5: no chat template) against the directed double-edge swap null of D032.

Section 4.3 of the draft gives the factor by which R moves when only the prompt changes; those ratios were computed against the paper's three-edge null. This script runs the
double-edge swap null of experiments/d032_double_swap_null.py (same functions, same seeds sha256('d032|key|idx')[:4], 64 x edges accepted swaps, 100 replicates) on the
default-filter graphs (first sentence, fixed 2,750-lemma node set) of the two controls of the 17 instruct models. The main-run graphs of the same models were run in D032.
Output per graph: results/<key>.json (same fields as D032). Comparison with the main run and with the three-edge null: research/audit_scripts/38_controls_double_swap.py.
Readings: DECISION_LOG.md D034.

Usage (repo root):
    python -m experiments.d034_controls_double_swap --out results_2026-10-02_Local/d034_controls_double_swap --workers 8
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from experiments.d032_double_swap_null import finalize, run_replicate, sha256_file  # noqa: E402

PRIMARY = ROOT / "results_2026-10-01_Local"
CONTROL_GRAPHS = PRIMARY / "e2_filtered_default_controls_32x" / "graphs"
MAIN_GRAPHS = PRIMARY / "e2_filtered_default_main_32x" / "graphs"


def control_paths() -> dict[str, Path]:
    models = sorted(p.stem[6:] for p in MAIN_GRAPHS.glob("main__*.json") if not p.stem.endswith("-pt") and not p.stem.endswith("wordnet"))
    assert len(models) == 17, models
    paths = {}
    for ds in ("e4", "e5"):
        for m in models:
            p = CONTROL_GRAPHS / f"{ds}__{m}.json"
            assert p.exists(), p
            paths[f"{ds}__{m}"] = p
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--swap-mult", type=int, default=64)
    ap.add_argument("--tries-mult", type=int, default=200)
    args = ap.parse_args(argv)
    os.chdir(ROOT)
    out = Path(args.out)
    for sub in ("replicates", "results"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    paths = control_paths()
    started = datetime.now().isoformat(timespec="seconds")
    print(f"[d034] {len(paths)} graphs x {args.reps} replicates, {args.workers} workers, {args.swap_mult} x edges accepted swaps", flush=True)
    files = {k: out / "replicates" / f"{k}.jsonl" for k in paths}
    done: dict[str, dict[int, dict]] = {k: {} for k in paths}
    for k, p in files.items():
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    done[k][rec["idx"]] = rec
    t0 = time.time()

    def fin(key):
        res = finalize(key, paths[key], [done[key][i] for i in sorted(done[key])], args)
        (out / "results" / f"{key}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(f"[d034] {time.time() - t0:7.0f}s  {key:28} E={res['n_edges']:>6} obs={res['observed']['cycles_2']:>4} null={res['null_mean']['cycles_2']:6.2f} "
              f"R={res['reciprocity_excess']:7.2f} kept={res['kept_observed_pairs_mean']:5.2f} budget_not_met={res['budget_not_met']}", flush=True)

    tasks = []
    for key in paths:
        if len(done[key]) >= args.reps and not (out / "results" / f"{key}.json").exists():
            fin(key)
        for idx in range(args.reps):
            if idx not in done[key]:
                tasks.append((key, str(paths[key]), idx, args.swap_mult, args.tries_mult))
    print(f"[d034] {len(tasks)} replicates to run ({sum(len(v) for v in done.values())} already done)", flush=True)
    handles = {k: open(p, "a", encoding="utf-8") for k, p in files.items()}
    try:
        with Pool(args.workers) as pool:
            for rec in pool.imap_unordered(run_replicate, tasks, chunksize=4):
                key = rec["key"]
                handles[key].write(json.dumps(rec) + "\n")
                handles[key].flush()
                done[key][rec["idx"]] = rec
                if len(done[key]) == args.reps:
                    fin(key)
    finally:
        for fh in handles.values():
            fh.close()
    (out / "run_info.json").write_text(json.dumps({
        "started": started, "finished": datetime.now().isoformat(timespec="seconds"), "args": vars(args), "python": sys.version.split()[0],
        "script_sha256": sha256_file(ROOT / "experiments" / "d034_controls_double_swap.py"),
        "d032_script_sha256": sha256_file(ROOT / "experiments" / "d032_double_swap_null.py"),
        "graphs": {k: str(v.relative_to(ROOT)) for k, v in paths.items()},
        "note": "D034: directed double-edge swap null (functions of D032) on the default-filter graphs of E4 and E5; seeds sha256('d032|key|idx')[:4]",
    }, indent=1), encoding="utf-8")
    print(f"[d034] done in {time.time() - t0:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
