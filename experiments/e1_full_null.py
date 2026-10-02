"""E1 — Degree-preserving null model at full scale, on the unfiltered graphs.

Runs the audited null model from experiments/null_model.py over every graph the paper
needs, with the additions a 100-replicate run requires:

  * explicit graph sets (main 23 + WordNet, E3, E4, E5) instead of globbing
    data/definitions, which also holds Qwen3.5 / Gemma-4 files that are not part of
    the paper
  * replicate-level multiprocessing with deterministic per-replicate seeds
  * swap-failure flags: nx.directed_edge_swap raises NetworkXAlgorithmError when it
    cannot complete the requested swaps; null_model.rewire silently keeps the partly
    randomised graph, here every such replicate is recorded
  * full cycle-length histogram, raw replicate values, bootstrap 95% CI on R
  * snapshots of every graph (edge lists) and the sha256 of every source file
  * resumable: replicates are appended to one JSONL per graph

summarize() and compute_kernel() are the ones in null_model.py (a startup check asserts
summarize_full() agrees with summarize()). R keeps the definition used there:
    R = observed 2-cycles / max(null mean 2-cycles, 0.5)
The bootstrap CI resamples the null replicates only; it does not include sampling
variance of the generated definitions themselves.

By default this is the UNFILTERED run (the "before" column of the E2 before/after table). With
--filter default|strict the graphs are rebuilt from the records the non-definition filter keeps
(D023, D024): the decision is made on the first sentence of the stored text; --unit says whether a
kept record contributes its first sentence (primary, D009) or its stored text (sensitivity); a dropped
record keeps its node and adds no edge, and every filtered graph has the same fixed 2,750-lemma node
set (D010). --drop-imperatives also drops bare imperatives built on the headword (D023 item 4).

Usage (from the repo root):
    python -m experiments.e1_full_null --out results_2026-10-01_Local/e1_null_unfiltered
    python -m experiments.e1_full_null --out ... --sets main --reps 100 --workers 10
    python -m experiments.e1_full_null --out ... --filter default --unit first_sentence \
        --nswap-mult 32 --tries-mult 9600
    python -m experiments.e1_full_null --out /tmp/e1_smoke --smoke
"""

import argparse
import csv
import hashlib
import json
import os
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

from experiments.null_model import CYCLE_BOUND, compute_kernel, summarize  # noqa: E402

WORD_LIST = "data/sample_words/word_list_3k_v1.json"
E_DIRS = {
    "e3": "results_2026-09-09_Runpod/results_e3 (fewshot)/definitions",
    "e4": "results_2026-09-09_Runpod/results_e4 (lenght)/definitions",
    "e5": "results_2026-09-09_Runpod/results_e5 (no template)/definitions",
}
METRICS = ("kernel_ratio", "circulation_rate", "cycles_total", "cycles_2", "cycles_long")
BOOTSTRAP_B = 10_000
R_FLOOR = 0.5  # same floor as null_model.analyse


# ── graph collection ──────────────────────────────────────────────────────────

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_jsonl(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def collect_graphs(sets: list[str], flt: dict | None = None, only: list[str] | None = None,
                   drop_words: list[str] | None = None) -> dict[str, dict]:
    """Return {key: {"graph": DiGraph, "meta": dict}} for the requested sets.

    flt=None builds the unfiltered graphs as before. flt = {"variant", "unit", "drop_imperatives", ...}
    applies rs_dic_llm.filtered_definitions.filter_records and builds every graph on the fixed
    2,750-lemma vocabulary (D010). `only` restricts the work to these graph keys. `drop_words` removes
    these lemmas, with their edges, from every graph, WordNet included (D025).
    """
    from rs_dic_llm.config import MODEL_REGISTRY
    from rs_dic_llm.filtered_definitions import filter_records, fixed_vocabulary
    from rs_dic_llm.graph_build import build_graph, drop_nodes
    from rs_dic_llm.sampling import load_word_list
    from rs_dic_llm.wordnet_baseline import build_wordnet_graph

    word_list = load_word_list(WORD_LIST)
    vocabulary = fixed_vocabulary(word_list) if flt else None
    out: dict[str, dict] = {}

    def wanted(key: str) -> bool:
        return only is None or key in only

    def add(dataset: str, name: str, path: str) -> None:
        key = f"{dataset}__{name}"
        if not wanted(key):
            return
        records = _load_jsonl(path)
        meta = {
            "dataset": dataset,
            "model": name,
            "is_base": name.endswith("-pt"),
            "source": path,
            "source_sha256": sha256_file(path),
            "n_records": len(records),
        }
        if flt:
            records, stats = filter_records(records, flt["variant"], flt["unit"], flt["drop_imperatives"])
            meta["filter"] = {**flt, **stats, "vocabulary_size": len(vocabulary)}
        G = build_graph(records, vocabulary=vocabulary)
        if drop_words:
            meta["removed_nodes"] = drop_nodes(G, drop_words)
        out[key] = {"graph": G, "meta": meta}

    if "main" in sets:
        for display, *_ in MODEL_REGISTRY:
            add("main", display, f"data/definitions/{display}_42.jsonl")
        if wanted("main__wordnet"):
            G, _ = build_wordnet_graph(word_list)
            wn_removed = drop_nodes(G, drop_words) if drop_words else None
            out["main__wordnet"] = {
                "graph": G,
                "meta": {
                    "dataset": "main",
                    "model": "wordnet",
                    "is_base": False,
                    "source": WORD_LIST,
                    "source_sha256": sha256_file(WORD_LIST),
                    "n_records": G.number_of_nodes(),
                    "removed_nodes": wn_removed,
                },
            }
    for dataset, folder in E_DIRS.items():
        if dataset in sets:
            for path in sorted(Path(folder).glob("*_42.jsonl")):
                add(dataset, path.name[: -len("_42.jsonl")], str(path))
    return out


def write_snapshot(key: str, G: nx.DiGraph, graph_dir: Path) -> str:
    payload = json.dumps(
        {"nodes": sorted(G.nodes()), "edges": sorted(G.edges())}, ensure_ascii=False
    )
    (graph_dir / f"{key}.json").write_text(payload, encoding="utf-8")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ── worker side ───────────────────────────────────────────────────────────────

_GRAPHS: dict[str, nx.DiGraph] = {}
_GRAPH_DIR = ""


def _init_worker(graph_dir: str) -> None:
    global _GRAPH_DIR
    _GRAPH_DIR = graph_dir


def _graph(key: str) -> nx.DiGraph:
    if key not in _GRAPHS:
        with open(os.path.join(_GRAPH_DIR, f"{key}.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        G = nx.DiGraph()
        G.add_nodes_from(data["nodes"])
        G.add_edges_from(data["edges"])
        _GRAPHS[key] = G
    return _GRAPHS[key]


def seed_for(key: str, idx: int) -> int:
    digest = hashlib.sha256(f"e1|{key}|{idx}".encode()).digest()
    return int.from_bytes(digest[:4], "big")


def summarize_full(G: nx.DiGraph, n_nodes: int) -> dict:
    """Same quantities as null_model.summarize, plus the cycle-length histogram."""
    hist: dict[int, int] = {}
    for cycle in nx.simple_cycles(G, length_bound=CYCLE_BOUND):
        hist[len(cycle)] = hist.get(len(cycle), 0) + 1
    sccs = [c for c in nx.strongly_connected_components(G) if len(c) > 1]
    return {
        "kernel_ratio": len(compute_kernel(G)) / n_nodes,
        "circulation_rate": sum(len(c) for c in sccs) / n_nodes,
        "cycles_total": sum(hist.values()),
        "cycles_2": hist.get(2, 0),
        "cycles_long": sum(v for k, v in hist.items() if k >= 5),
        "cycle_hist": {str(k): v for k, v in sorted(hist.items())},
    }


def rewire_checked(G: nx.DiGraph, seed: int, nswap_mult: int, tries_mult: int):
    """Same call as null_model.rewire, but reports whether the swap budget was met."""
    H = G.copy()
    n_edges = H.number_of_edges()
    try:
        nx.directed_edge_swap(
            H, nswap=nswap_mult * n_edges, max_tries=tries_mult * n_edges, seed=seed
        )
        return H, None
    except nx.NetworkXAlgorithmError:
        return H, "max_tries"
    except nx.NetworkXError as exc:
        return H, f"error: {exc}"


def run_replicate(task: tuple) -> dict:
    key, idx, nswap_mult, tries_mult = task
    t0 = time.time()
    G = _graph(key)
    H, failure = rewire_checked(G, seed_for(key, idx), nswap_mult, tries_mult)
    record = summarize_full(H, G.number_of_nodes())
    record.update(key=key, idx=idx, swap_failure=failure, sec=round(time.time() - t0, 2))
    return record


# ── statistics ────────────────────────────────────────────────────────────────

def bootstrap_r_ci(obs_c2: int, null_c2: list[int]) -> list[float]:
    rng = np.random.default_rng(0)
    arr = np.asarray(null_c2, dtype=float)
    means = rng.choice(arr, size=(BOOTSTRAP_B, len(arr)), replace=True).mean(axis=1)
    r = obs_c2 / np.maximum(means, R_FLOOR)
    return [float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))]


def _null_stats(rows: list[dict]) -> tuple[dict, dict]:
    mean = {m: statistics.mean(r[m] for r in rows) for m in METRICS}
    sd = {m: statistics.pstdev([r[m] for r in rows]) for m in METRICS}
    return mean, sd


def finalize(key: str, meta: dict, G: nx.DiGraph, reps: list[dict], args) -> dict:
    from rs_dic_llm.metrics.scc import reciprocity_excess as r_analytic

    n = G.number_of_nodes()
    obs_full = summarize_full(G, n)
    obs = {m: obs_full[m] for m in METRICS}
    null_mean, null_sd = _null_stats(reps)
    complete = [r for r in reps if r["swap_failure"] is None]

    hist_ratio = {}
    for length in range(2, CYCLE_BOUND + 1):
        null_len = statistics.mean(r["cycle_hist"].get(str(length), 0) for r in reps)
        hist_ratio[str(length)] = {
            "observed": obs_full["cycle_hist"].get(str(length), 0),
            "null_mean": null_len,
        }

    result = {
        "key": key,
        "meta": meta,
        "n_nodes": n,
        "n_edges": G.number_of_edges(),
        "observed": obs,
        "null_mean": null_mean,
        "null_sd": null_sd,
        "z": {m: (obs[m] - null_mean[m]) / (null_sd[m] or 1e-9) for m in METRICS},
        "replicates": len(reps),
        "swap_failures": len(reps) - len(complete),
        "nswap_mult": args.nswap_mult,
        "reciprocity_excess": obs["cycles_2"] / max(null_mean["cycles_2"], R_FLOOR),
        "R_ci95": bootstrap_r_ci(obs["cycles_2"], [r["cycles_2"] for r in reps]),
        "R_floor_applied": null_mean["cycles_2"] < R_FLOOR,
        "cycle_hist_observed_vs_null": hist_ratio,
        "R_analytic_rs_dic_llm": r_analytic(G),
    }
    if len(complete) >= 10:
        mean_c, _ = _null_stats(complete)
        result["R_complete_replicates_only"] = obs["cycles_2"] / max(mean_c["cycles_2"], R_FLOOR)
    return result


# ── driver ────────────────────────────────────────────────────────────────────

def _read_done(path: Path) -> dict[int, dict]:
    done: dict[int, dict] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                done[rec["idx"]] = rec
    return done


def _write_summary(results: list[dict], out: Path) -> None:
    (out / "null_model_all.json").write_text(
        json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    cols = ["key", "n_nodes", "n_edges", "obs_pairs", "null_mean_pairs", "null_sd_pairs",
            "R", "R_ci_lo", "R_ci_hi", "R_analytic", "kernel_obs", "kernel_null",
            "kernel_z", "swap_failures", "replicates"]
    with open(out / "summary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in results:
            w.writerow([
                r["key"], r["n_nodes"], r["n_edges"], r["observed"]["cycles_2"],
                round(r["null_mean"]["cycles_2"], 3), round(r["null_sd"]["cycles_2"], 3),
                round(r["reciprocity_excess"], 3), round(r["R_ci95"][0], 3),
                round(r["R_ci95"][1], 3), round(r["R_analytic_rs_dic_llm"], 3),
                round(r["observed"]["kernel_ratio"], 5), round(r["null_mean"]["kernel_ratio"], 5),
                round(r["z"]["kernel_ratio"], 3), r["swap_failures"], r["replicates"],
            ])


def _git_head() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT
        ).stdout.strip()
    except OSError:
        return "unknown"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, help="output folder (created if missing)")
    parser.add_argument("--sets", nargs="+", default=["main", "e3", "e4", "e5"],
                        choices=["main", "e3", "e4", "e5"])
    parser.add_argument("--reps", type=int, default=100)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--nswap-mult", type=int, default=5,
                        help="swaps per edge (null_model.py uses 5)")
    parser.add_argument("--tries-mult", type=int, default=300,
                        help="max swap attempts per edge (null_model.py uses 300)")
    parser.add_argument("--only", nargs="+", default=None, help="restrict to these graph keys")
    parser.add_argument("--filter", choices=["none", "default", "strict", "extract"], default="none",
                        help="build the graphs from the records the non-definition filter keeps (D023, D024); "
                             "extract = first sentence only, nothing dropped")
    parser.add_argument("--unit", choices=["first_sentence", "stored"], default="first_sentence",
                        help="text a kept record contributes: its first sentence (primary) or the stored text")
    parser.add_argument("--drop-imperatives", action="store_true",
                        help="also drop bare imperatives built on the headword (D023 item 4; needs --filter)")
    parser.add_argument("--drop-words", nargs="+", default=None,
                        help="remove these lemmas, with their edges, from every graph (D025: frame words)")
    parser.add_argument("--smoke", action="store_true", help="2 graphs x 3 replicates")
    args = parser.parse_args(argv)

    os.chdir(ROOT)
    out = Path(args.out)
    for sub in ("graphs", "replicates", "results"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    flt = None
    if args.filter != "none":
        flt = {
            "variant": args.filter,
            "unit": args.unit,
            "drop_imperatives": args.drop_imperatives,
            "quality_filter_sha256": sha256_file("src/rs_dic_llm/quality_filter.py"),
            "quality_filter_strict_sha256": (sha256_file("src/rs_dic_llm/quality_filter_strict.py")
                                             if args.filter == "strict" else None),
        }
    elif args.drop_imperatives:
        parser.error("--drop-imperatives needs --filter default or strict")

    started = datetime.now().isoformat(timespec="seconds")
    print(f"[e1] collecting graphs for sets {args.sets}, filter {args.filter} ...", flush=True)
    graphs = collect_graphs(args.sets, flt, args.only, args.drop_words)
    if args.only:
        graphs = {k: v for k, v in graphs.items() if k in args.only}
    if args.smoke:
        graphs = dict(list(graphs.items())[:2])
        args.reps = 3
    print(f"[e1] {len(graphs)} graphs x {args.reps} replicates, {args.workers} workers", flush=True)

    snapshots = {}
    for key, item in graphs.items():
        item["meta"]["graph_sha256"] = write_snapshot(key, item["graph"], out / "graphs")
        item["meta"]["n_nodes"] = item["graph"].number_of_nodes()
        item["meta"]["n_edges"] = item["graph"].number_of_edges()
        snapshots[key] = item["meta"]
    (out / "graphs" / "manifest.json").write_text(
        json.dumps(snapshots, indent=1, ensure_ascii=False), encoding="utf-8")

    # fidelity check: summarize_full must agree with the audited null_model.summarize
    probe_key = next(iter(graphs))
    probe = graphs[probe_key]["graph"]
    a = summarize(probe, probe.number_of_nodes())
    b = summarize_full(probe, probe.number_of_nodes())
    assert all(a[m] == b[m] for m in METRICS), f"summarize mismatch on {probe_key}"

    replicate_files = {k: out / "replicates" / f"{k}.jsonl" for k in graphs}
    done = {k: _read_done(p) for k, p in replicate_files.items()}
    results: dict[str, dict] = {}
    t_start = time.time()

    def maybe_finalize(key: str) -> None:
        reps = [done[key][i] for i in sorted(done[key])]
        res = finalize(key, graphs[key]["meta"], graphs[key]["graph"], reps, args)
        results[key] = res
        (out / "results" / f"{key}.json").write_text(
            json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        lo, hi = res["R_ci95"]
        print(f"[e1] {time.time() - t_start:7.0f}s  {key:34} E={res['n_edges']:>6} "
              f"obs={res['observed']['cycles_2']:>4} null={res['null_mean']['cycles_2']:6.2f} "
              f"R={res['reciprocity_excess']:6.2f} [{lo:6.2f},{hi:6.2f}] "
              f"swap_fail={res['swap_failures']}/{res['replicates']}", flush=True)

    tasks = []
    for key in graphs:
        if len(done[key]) >= args.reps and not (out / "results" / f"{key}.json").exists():
            maybe_finalize(key)
        elif (out / "results" / f"{key}.json").exists() and len(done[key]) >= args.reps:
            results[key] = json.loads((out / "results" / f"{key}.json").read_text(encoding="utf-8"))
        for idx in range(args.reps):
            if idx not in done[key]:
                tasks.append((key, idx, args.nswap_mult, args.tries_mult))

    print(f"[e1] {len(tasks)} replicates to run "
          f"({sum(len(v) for v in done.values())} already done)", flush=True)
    handles = {k: open(p, "a", encoding="utf-8") for k, p in replicate_files.items()}
    try:
        with Pool(args.workers, initializer=_init_worker,
                  initargs=(str(out / "graphs"),)) as pool:
            for rec in pool.imap_unordered(run_replicate, tasks, chunksize=1):
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
    _write_summary(ordered, out)
    (out / "run_info.json").write_text(json.dumps({
        "started": started,
        "finished": datetime.now().isoformat(timespec="seconds"),
        "args": vars(args),
        "git_head": _git_head(),
        "python": sys.version.split()[0],
        "networkx": nx.__version__,
        "cycle_bound": CYCLE_BOUND,
        "filter": flt,
        "note": ("unfiltered graphs; " if flt is None else
                 f"filtered graphs ({flt['variant']} filter, unit {flt['unit']}, fixed 2,750-lemma vocabulary); ")
                + (f"nodes removed from every graph: {', '.join(args.drop_words)}; " if args.drop_words else "")
                + "replicate seeds = sha256('e1|key|idx')[:4]",
    }, indent=1), encoding="utf-8")
    print(f"[e1] done in {time.time() - t_start:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
