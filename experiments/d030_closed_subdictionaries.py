"""D030 (b) — closed sub-dictionaries: is R invariant when a graph is reduced to a set of words instead of a set of entries?

D029 limited graphs to a set of entries: the words without a definition stayed in the graph as nodes with no in-edges, and kept the out-edges
they had as defining words. Here the graph is *induced* on a set of words: the words outside the set and all their edges are removed, so that every
remaining word has a definition made of remaining words, a closed (smaller) dictionary.

For each size s in 1B, 4B, 12B, 27B, with W(s) the lemmas that have a surviving zero-shot entry (D029):

  zsC   the zero-shot graph induced on W(s)
  fsC   the whole few-shot (E3) graph induced on W(s)
  itC   the whole instruct graph induced on W(s)
  fsRC1..5   the whole few-shot graph induced on five random sets of lemmas of the size of W(s)
             (random.Random("d030|<s>|<k>").sample(sorted(lemmas), |W(s)|))

The graphs come from the snapshots of the primary run (results_2026-10-01_Local/e2_filtered_default_*) and go through the null model of
experiments/e1_full_null.py unchanged (32 x edges swaps, at most 300 tries per swap, 100 replicates, seeds sha256('e1|key|idx')[:4] with key d030c__<kind>_<s>).
The readings are fixed in DECISION_LOG.md D030 and applied by research/audit_scripts/30_closed_subdictionaries.py.

Usage (from the repo root):
    python -m experiments.d030_closed_subdictionaries --out results_2026-10-02_Local/d030_closed_subdictionaries --workers 12
    python -m experiments.d030_closed_subdictionaries --out /tmp/d030c_smoke --smoke
"""

import argparse
import hashlib
import json
import os
import random
import sys
import time
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path
from types import SimpleNamespace

import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from experiments import e1_full_null as e1  # noqa: E402

SIZES = ("1B", "4B", "12B", "27B")
N_RANDOM = 5
PRIMARY = "results_2026-10-01_Local"
SNAP = {
    "zs": f"{PRIMARY}/e2_filtered_default_main_32x/graphs/main__Gemma3-{{s}}-pt.json",
    "fs": f"{PRIMARY}/e2_filtered_default_controls_32x/graphs/e3__Gemma3-{{s}}-pt.json",
    "it": f"{PRIMARY}/e2_filtered_default_main_32x/graphs/main__Gemma3-{{s}}.json",
}
SETS = "results_2026-10-02_Local/d029_survivor_restriction/restriction_sets.json"


def load_snapshot(path: str) -> nx.DiGraph:
    """Same construction as e1_full_null._graph (sorted nodes, then sorted edges)."""
    data = json.loads((ROOT / path).read_text(encoding="utf-8"))
    G = nx.DiGraph()
    G.add_nodes_from(data["nodes"])
    G.add_edges_from(data["edges"])
    return G


def covered_lemmas(size: str, sets: dict) -> set[str]:
    """Lemmas of the entries whose zero-shot record survives the filter (the survivor list written by D029)."""
    records = e1._load_jsonl(f"data/definitions/Gemma3-{size}-pt_42.jsonl")
    return {records[i]["lemma"] for i in sets[size]["survivor_indices"]}


def induced(G: nx.DiGraph, words: set[str]) -> nx.DiGraph:
    H = G.subgraph(words).copy()
    assert set(H.nodes()) == set(words) and set(H.edges()) <= set(G.edges())
    return H


def set_hash(words) -> str:
    return hashlib.sha256(json.dumps(sorted(words), ensure_ascii=False).encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--reps", type=int, default=100)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--nswap-mult", type=int, default=32)
    parser.add_argument("--tries-mult", type=int, default=9600)
    parser.add_argument("--smoke", action="store_true", help="2 graphs x 3 replicates at 2 x edges swaps (code check only)")
    args = parser.parse_args(argv)
    if args.smoke:
        args.reps, args.nswap_mult = 3, 2

    os.chdir(ROOT)
    out = Path(args.out)
    for sub in ("graphs", "replicates", "results"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    started = datetime.now().isoformat(timespec="seconds")
    sets = json.loads((ROOT / SETS).read_text(encoding="utf-8"))

    graphs: dict[str, dict] = {}
    info: dict[str, dict] = {}
    for s in SIZES:
        whole = {c: load_snapshot(SNAP[c].format(s=s)) for c in SNAP}
        pool_lemmas = sorted(whole["fs"].nodes())
        W = covered_lemmas(s, sets)
        assert W <= set(pool_lemmas), s
        info[s] = {"covered_lemmas": len(W), "covered_sha256": set_hash(W), "lemma_pool": len(pool_lemmas),
                   "snapshots": {c: {"path": SNAP[c].format(s=s), "sha256": e1.sha256_file(SNAP[c].format(s=s))} for c in SNAP}}
        wanted = [("zsC", "zs", W), ("fsC", "fs", W), ("itC", "it", W)]
        for k in range(1, N_RANDOM + 1):
            wk = set(random.Random(f"d030|{s}|{k}").sample(pool_lemmas, len(W)))
            wanted.append((f"fsRC{k}", "fs", wk))
        for kind, cond, words in wanted:
            key = f"d030c__{kind}_{s}"
            G = induced(whole[cond], words)
            graphs[key] = {"graph": G, "meta": {
                "dataset": "d030c", "model": f"{kind}_{s}", "kind": kind, "size": s, "induced_from": cond,
                "source": SNAP[cond].format(s=s), "n_words_in_set": len(words), "set_sha256": set_hash(words),
                "source_graph_edges": whole[cond].number_of_edges()}}
        print(f"[d030c] {s}: {len(W)} covered lemmas of {len(pool_lemmas)}; edges of the whole graphs zs/fs/it "
              f"{whole['zs'].number_of_edges()}/{whole['fs'].number_of_edges()}/{whole['it'].number_of_edges()}; "
              f"closed zsC/fsC/itC {graphs[f'd030c__zsC_{s}']['graph'].number_of_edges()}/{graphs[f'd030c__fsC_{s}']['graph'].number_of_edges()}/"
              f"{graphs[f'd030c__itC_{s}']['graph'].number_of_edges()}", flush=True)
    (out / "sets_info.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    if args.smoke:
        graphs = dict(list(graphs.items())[:2])

    print(f"[d030c] {len(graphs)} graphs x {args.reps} replicates, {args.workers} workers", flush=True)
    snapshots = {}
    for key, item in graphs.items():
        item["meta"]["graph_sha256"] = e1.write_snapshot(key, item["graph"], out / "graphs")
        item["meta"]["n_nodes"] = item["graph"].number_of_nodes()
        item["meta"]["n_edges"] = item["graph"].number_of_edges()
        snapshots[key] = item["meta"]
    (out / "graphs" / "manifest.json").write_text(json.dumps(snapshots, indent=1, ensure_ascii=False), encoding="utf-8")

    probe = graphs[next(iter(graphs))]["graph"]
    a, b = e1.summarize(probe, probe.number_of_nodes()), e1.summarize_full(probe, probe.number_of_nodes())
    assert all(a[m] == b[m] for m in e1.METRICS), "summarize mismatch"

    replicate_files = {k: out / "replicates" / f"{k}.jsonl" for k in graphs}
    done = {k: e1._read_done(p) for k, p in replicate_files.items()}
    results: dict[str, dict] = {}
    t_start = time.time()
    fin_args = SimpleNamespace(nswap_mult=args.nswap_mult)

    def maybe_finalize(key: str) -> None:
        reps = [done[key][i] for i in sorted(done[key])]
        res = e1.finalize(key, graphs[key]["meta"], graphs[key]["graph"], reps, fin_args)
        results[key] = res
        (out / "results" / f"{key}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        lo, hi = res["R_ci95"]
        print(f"[d030c] {time.time() - t_start:7.0f}s  {key:22} N={res['n_nodes']:>5} E={res['n_edges']:>6} obs={res['observed']['cycles_2']:>4} "
              f"null={res['null_mean']['cycles_2']:6.2f} R={res['reciprocity_excess']:6.2f} [{lo:6.2f},{hi:6.2f}] "
              f"swap_fail={res['swap_failures']}/{res['replicates']}", flush=True)

    tasks = []
    for key in graphs:
        res_path = out / "results" / f"{key}.json"
        if len(done[key]) >= args.reps and not res_path.exists():
            maybe_finalize(key)
        elif res_path.exists() and len(done[key]) >= args.reps:
            results[key] = json.loads(res_path.read_text(encoding="utf-8"))
        for idx in range(args.reps):
            if idx not in done[key]:
                tasks.append((key, idx, args.nswap_mult, args.tries_mult))
    print(f"[d030c] {len(tasks)} replicates to run ({sum(len(v) for v in done.values())} already done)", flush=True)
    handles = {k: open(p, "a", encoding="utf-8") for k, p in replicate_files.items()}
    try:
        with Pool(args.workers, initializer=e1._init_worker, initargs=(str(out / "graphs"),)) as pool:
            for rec in pool.imap_unordered(e1.run_replicate, tasks, chunksize=1):
                key = rec["key"]
                handles[key].write(json.dumps(rec) + "\n")
                handles[key].flush()
                done[key][rec["idx"]] = rec
                if len(done[key]) == args.reps:
                    maybe_finalize(key)
    finally:
        for fh in handles.values():
            fh.close()

    ordered = [results[k] for k in graphs if k in results]
    e1._write_summary(ordered, out)
    (out / "run_info.json").write_text(json.dumps({
        "started": started, "finished": datetime.now().isoformat(timespec="seconds"), "args": vars(args),
        "python": sys.version.split()[0], "networkx": nx.__version__, "cycle_bound": e1.CYCLE_BOUND,
        "script_sha256": e1.sha256_file("experiments/d030_closed_subdictionaries.py"),
        "e1_full_null_sha256": e1.sha256_file("experiments/e1_full_null.py"),
        "note": "D030 (b): graphs induced on the covered lemmas W(s) and on five random lemma sets of the same size; "
                "snapshots of the primary run (default filter, first sentence); replicate seeds = sha256('e1|key|idx')[:4]",
    }, indent=1), encoding="utf-8")
    print(f"[d030c] done in {time.time() - t_start:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
