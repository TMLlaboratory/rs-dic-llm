"""D029 (b) — does coverage explain the zero-shot gap? Null model on graphs restricted to the zero-shot survivors.

The zero-shot pretrained Gemma3 records lose 47-57 % of their entries to the non-definition filter (default filter,
first sentence), so their graphs are built on about half of the word list. This script asks what the few-shot (E3) and
the instruct graphs of the same size look like when they are limited to the same entries.

For each size s in 1B, 4B, 12B, 27B (the sizes that have a pretrained and an instruct model):

  S(s)   the entries (rows of the word list) whose zero-shot record has a valid status and is kept by the filter
  fsS    the E3 records of the entries in S(s); every other entry is treated as dropped
  itS    the instruct records of the entries in S(s)
  fsR1..fsR5   the E3 records of five random sets of entries of the size of S(s)
               (random.Random("d029|<s>|<k>").sample(range(3000), |S(s)|)): what a restriction to that many entries
               does to R by itself

A dropped entry keeps its node and adds no edge (D010); the node set is the fixed 2,750-lemma vocabulary. Each graph
goes through the null model of experiments/e1_full_null.py unchanged (nx.directed_edge_swap, 32 x edges swaps, at most
300 tries per swap, 100 replicates, seeds sha256('e1|<key>|<idx>')[:4]; the graph key here is d029__<kind>_<s>).

Before anything is run the script rebuilds the unrestricted default-filter graphs (zero-shot, E3, instruct) and checks
their snapshot hashes against the manifests of the earlier runs: a mismatch stops it, so the restriction starts from
the very graphs of the primary analysis. It also stops if the three record files do not hold the same entries in the
same order. The reading of the results is fixed in DECISION_LOG.md D029 and applied by
research/audit_scripts/27_survivor_restriction.py.

Usage (from the repo root):
    python -m experiments.d029_survivor_restriction --out results_2026-10-02_Local/d029_survivor_restriction --workers 12
    python -m experiments.d029_survivor_restriction --out /tmp/d029_smoke --smoke
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
N_ENTRIES = 3000
PATHS = {
    "zs": "data/definitions/Gemma3-{s}-pt_42.jsonl",
    "fs": e1.E_DIRS["e3"] + "/Gemma3-{s}-pt_42.jsonl",
    "it": "data/definitions/Gemma3-{s}_42.jsonl",
}
# keys of the same graphs in the earlier runs (primary analysis: default filter, first sentence, 32 x edges)
EARLIER = {
    "zs": ("results_2026-10-01_Local/e2_filtered_default_main_32x", "main__Gemma3-{s}-pt"),
    "fs": ("results_2026-10-01_Local/e2_filtered_default_controls_32x", "e3__Gemma3-{s}-pt"),
    "it": ("results_2026-10-01_Local/e2_filtered_default_main_32x", "main__Gemma3-{s}"),
}


def snapshot_hash(G: nx.DiGraph) -> str:
    """Same payload and hash as e1_full_null.write_snapshot."""
    payload = json.dumps({"nodes": sorted(G.nodes()), "edges": sorted(G.edges())}, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def set_hash(indices) -> str:
    return hashlib.sha256(json.dumps(sorted(indices)).encode("utf-8")).hexdigest()


def load_conditions(size: str) -> dict[str, list[dict]]:
    """Raw records of the three conditions; stops if they do not describe the same entries in the same order."""
    raw = {c: e1._load_jsonl(PATHS[c].format(s=size)) for c in PATHS}
    for c, records in raw.items():
        assert len(records) == N_ENTRIES, (size, c, len(records))
    for i in range(N_ENTRIES):
        ids = {(raw[c][i]["word"], raw[c][i]["pos"], raw[c][i]["lemma"]) for c in raw}
        assert len(ids) == 1, (size, i, ids)
    return raw


def filtered_conditions(raw: dict[str, list[dict]]) -> tuple[dict, dict]:
    from rs_dic_llm.filtered_definitions import filter_records

    out, stats = {}, {}
    for c, records in raw.items():
        out[c], stats[c] = filter_records(records, "default", "first_sentence", False)
    return out, stats


def survivors(zs_filtered: list[dict]) -> list[int]:
    """Entries whose zero-shot record has a valid status and is kept by the filter (non-empty first sentence)."""
    from rs_dic_llm.filtered_definitions import VALID_STATUSES

    return [i for i, r in enumerate(zs_filtered)
            if r.get("status", "ok") in VALID_STATUSES and r["definition"]]


def random_sets(size: str, n: int) -> list[list[int]]:
    return [sorted(random.Random(f"d029|{size}|{k}").sample(range(N_ENTRIES), n)) for k in range(1, N_RANDOM + 1)]


def restrict(filtered: list[dict], keep) -> list[dict]:
    """Copy of the filtered records in which every entry outside `keep` is dropped (empty definition)."""
    keep = set(keep)
    out = []
    for i, record in enumerate(filtered):
        new = dict(record)
        if i not in keep:
            new["definition"] = ""
        out.append(new)
    return out


def build(records: list[dict], vocabulary: set[str]) -> nx.DiGraph:
    from rs_dic_llm.graph_build import build_graph

    return build_graph(records, vocabulary=vocabulary)


def check_against_earlier_runs(size: str, filtered: dict, vocabulary: set[str]) -> dict:
    """Rebuild the unrestricted graphs and compare their hashes with the earlier runs' manifests."""
    checked = {}
    for c in ("zs", "fs", "it"):
        folder, key_fmt = EARLIER[c]
        key = key_fmt.format(s=size)
        manifest = json.loads((ROOT / folder / "graphs" / "manifest.json").read_text(encoding="utf-8"))
        want = manifest[key]["graph_sha256"]
        have = snapshot_hash(build(filtered[c], vocabulary))
        assert have == want, f"{size} {c}: rebuilt graph {have[:12]} differs from {folder}/{key} {want[:12]}"
        checked[c] = {"earlier_run": folder, "earlier_key": key, "graph_sha256": have}
    return checked


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, help="output folder (created if missing)")
    parser.add_argument("--reps", type=int, default=100)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--nswap-mult", type=int, default=32)
    parser.add_argument("--tries-mult", type=int, default=9600)
    parser.add_argument("--sizes", nargs="+", default=list(SIZES), choices=list(SIZES))
    parser.add_argument("--smoke", action="store_true", help="2 graphs x 3 replicates at 2 x edges swaps (code check only)")
    args = parser.parse_args(argv)
    if args.smoke:
        args.reps, args.nswap_mult, args.sizes = 3, 2, ["1B"]

    os.chdir(ROOT)
    out = Path(args.out)
    for sub in ("graphs", "replicates", "results"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    from rs_dic_llm.filtered_definitions import fixed_vocabulary
    from rs_dic_llm.sampling import load_word_list

    started = datetime.now().isoformat(timespec="seconds")
    vocabulary = fixed_vocabulary(load_word_list(e1.WORD_LIST))
    print(f"[d029] vocabulary {len(vocabulary)} lemmas; sizes {args.sizes}", flush=True)

    graphs: dict[str, dict] = {}
    sets_out: dict[str, dict] = {}
    for s in args.sizes:
        raw = load_conditions(s)
        filtered, stats = filtered_conditions(raw)
        fidelity = check_against_earlier_runs(s, filtered, vocabulary)
        S = survivors(filtered["zs"])
        rand = random_sets(s, len(S))
        sets_out[s] = {
            "n_entries": N_ENTRIES,
            "zero_shot_valid_status": stats["zs"]["n_valid_status"],
            "zero_shot_dropped_by_filter": stats["zs"]["n_dropped"],
            "zero_shot_dropped_share": stats["zs"]["dropped_share"],
            "survivors": len(S),
            "survivors_sha256": set_hash(S),
            "survivor_indices": S,
            "random_indices": {str(k): r for k, r in enumerate(rand, 1)},
            "random_sha256": {str(k): set_hash(r) for k, r in enumerate(rand, 1)},
            "e3_kept_in_survivors": sum(1 for i in S if filtered["fs"][i]["definition"]),
            "instruct_kept_in_survivors": sum(1 for i in S if filtered["it"][i]["definition"]),
            "fidelity_check": fidelity,
            "sources": {c: {"path": PATHS[c].format(s=s), "sha256": e1.sha256_file(PATHS[c].format(s=s))} for c in PATHS},
        }
        print(f"[d029] {s}: survivors {len(S)} of {N_ENTRIES} (zero-shot dropped {stats['zs']['n_dropped']} "
              f"= {100 * stats['zs']['dropped_share']:.1f} % of {stats['zs']['n_valid_status']} valid); "
              f"unrestricted graphs match the earlier runs", flush=True)

        wanted = [("fsS", "fs", S), ("itS", "it", S)] + [(f"fsR{k}", "fs", r) for k, r in enumerate(rand, 1)]
        for kind, cond, keep in wanted:
            key = f"d029__{kind}_{s}"
            records = restrict(filtered[cond], keep)
            G = build(records, vocabulary)
            graphs[key] = {"graph": G, "meta": {
                "dataset": "d029", "model": f"{kind}_{s}", "kind": kind, "size": s, "records_from": cond,
                "source": PATHS[cond].format(s=s), "n_entries_in_set": len(keep), "set_sha256": set_hash(keep),
                "n_records_with_text": sum(1 for r in records if r["definition"]),
                "filter": {"variant": "default", "unit": "first_sentence",
                           "quality_filter_sha256": e1.sha256_file("src/rs_dic_llm/quality_filter.py")},
            }}
        # a restriction can only remove edges
        full_it = build(filtered["it"], vocabulary)
        full_fs = build(filtered["fs"], vocabulary)
        assert set(graphs[f"d029__fsS_{s}"]["graph"].edges()) <= set(full_fs.edges())
        assert set(graphs[f"d029__itS_{s}"]["graph"].edges()) <= set(full_it.edges())

    (out / "restriction_sets.json").write_text(json.dumps(sets_out, indent=1), encoding="utf-8")
    if args.smoke:
        graphs = dict(list(graphs.items())[:2])

    print(f"[d029] {len(graphs)} graphs x {args.reps} replicates, {args.workers} workers", flush=True)
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
        print(f"[d029] {time.time() - t_start:7.0f}s  {key:22} E={res['n_edges']:>6} obs={res['observed']['cycles_2']:>4} "
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

    print(f"[d029] {len(tasks)} replicates to run ({sum(len(v) for v in done.values())} already done)", flush=True)
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
        "started": started,
        "finished": datetime.now().isoformat(timespec="seconds"),
        "args": vars(args),
        "python": sys.version.split()[0],
        "networkx": nx.__version__,
        "cycle_bound": e1.CYCLE_BOUND,
        "script_sha256": e1.sha256_file("experiments/d029_survivor_restriction.py"),
        "e1_full_null_sha256": e1.sha256_file("experiments/e1_full_null.py"),
        "note": "D029 (b): E3 and instruct graphs restricted to the zero-shot survivors, and five random restrictions of the same size; "
                "default filter, first sentence, fixed 2,750-lemma vocabulary; replicate seeds = sha256('e1|key|idx')[:4]",
    }, indent=1), encoding="utf-8")
    print(f"[d029] done in {time.time() - t_start:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
