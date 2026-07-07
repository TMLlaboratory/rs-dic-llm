"""Full experiment: Qwen3.5 × 5 model sizes × 3000 words.

Skips models whose definition JSONL already exists (0.8B and 27B from pilot).

Research perspective:
    Smaller models reuse common vocabulary → higher edge density → more cycles.
    We track edge_density and mean_out_degree alongside Kernel/Core/SCC metrics
    to disentangle "conceptual circularity" from "vocabulary sparsity."

Prerequisites:
    python ~/mlx-proxy/mlx_proxy.py   # in a separate terminal

Usage:
    uv run python -m experiments.run_full [--seed 42]

Outputs:
    data/definitions/{model_short}_{seed}.jsonl   (per model)
    results/metrics/{model_short}_{seed}.json     (per model)
    results/metrics/wordnet_{seed}.json           (shared baseline)
    results/full_summary.json                     (all models combined)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import ExperimentConfig, FULL_MODELS
from rs_dic_llm.sampling import load_word_list
from rs_dic_llm.generation import generate_definitions, load_definitions
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.analysis import compute_all_metrics, save_metrics
from rs_dic_llm.wordnet_baseline import build_wordnet_graph


def _model_short(model_id: str) -> str:
    return model_id.split("/")[-1]


def _self_ref_rate(jsonl_path: str) -> float:
    lines = Path(jsonl_path).read_text(encoding="utf-8").strip().splitlines()
    recs = [json.loads(l) for l in lines]
    sr = sum(1 for r in recs if r.get("status") == "self_referential")
    return sr / len(recs) if recs else 0.0


def run(config: ExperimentConfig) -> None:
    words = load_word_list(config.word_list_path)
    print(f"[full] {len(words)} words loaded from {config.word_list_path}")

    all_metrics: list[dict] = []

    for model_id in config.models:
        short = _model_short(model_id)
        def_path = f"data/definitions/{short}_{config.seed}.jsonl"
        metrics_path = f"{config.output_dir}/metrics/{short}_{config.seed}.json"

        if Path(metrics_path).exists():
            print(f"\n[full] {short}: metrics already exist, loading ...")
            with open(metrics_path) as f:
                metrics = json.load(f)
            all_metrics.append(metrics)
            _print_summary(metrics, def_path if Path(def_path).exists() else None)
            continue

        if not Path(def_path).exists():
            print(f"\n[full] generating definitions — {short}")
            definitions = generate_definitions(words, model_id, config, output_path=def_path)
        else:
            print(f"\n[full] loading existing definitions: {def_path}")
            definitions = load_definitions(def_path)

        print(f"[full] building graph — {short}")
        G = build_graph(definitions)

        print(f"[full] computing metrics — {short}")
        metrics = compute_all_metrics(G, model_id=model_id)
        save_metrics(metrics, metrics_path)
        all_metrics.append(metrics)
        _print_summary(metrics, def_path)

    # WordNet baseline
    wn_path = f"{config.output_dir}/metrics/wordnet_{config.seed}.json"
    if Path(wn_path).exists():
        print("\n[full] WordNet baseline: loading existing metrics ...")
        with open(wn_path) as f:
            wn_metrics = json.load(f)
    else:
        print("\n[full] computing WordNet baseline ...")
        wn_G, _ = build_wordnet_graph(words)
        wn_metrics = compute_all_metrics(wn_G, model_id="wordnet")
        save_metrics(wn_metrics, wn_path)

    _print_summary(wn_metrics, None)

    # Combined summary table
    _print_table(all_metrics, wn_metrics)

    summary_path = f"{config.output_dir}/full_summary.json"
    Path(summary_path).parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({"models": all_metrics, "wordnet": wn_metrics}, f,
                  ensure_ascii=False, indent=2)
    print(f"\n[full] summary saved to {summary_path}")


def _print_summary(metrics: dict, def_path: str | None) -> None:
    short = metrics["model"].split("/")[-1] if "/" in metrics["model"] else metrics["model"]
    sr_str = ""
    if def_path and Path(def_path).exists():
        sr = _self_ref_rate(def_path)
        sr_str = f"  self_ref_rate  : {sr:.1%}"
    print(f"\n  --- {short} ---")
    print(f"  nodes          : {metrics.get('n_nodes')}")
    print(f"  edges          : {metrics.get('n_edges')}")
    print(f"  mean_out_degree: {metrics.get('mean_out_degree', 0):.3f}")
    print(f"  circulation    : {metrics.get('circulation_rate', 0):.4f}")
    print(f"  kernel_ratio   : {metrics.get('kernel_ratio', 0):.4f}")
    print(f"  core_size      : {metrics.get('core_size')}")
    print(f"  core/kernel    : {metrics.get('core_kernel_ratio', 0):.4f}")
    print(f"  minset         : {metrics.get('minset_size')}")
    if sr_str:
        print(sr_str)


def _print_table(model_metrics: list[dict], wn_metrics: dict) -> None:
    print("\n" + "=" * 80)
    print("FULL EXPERIMENT SUMMARY")
    print("=" * 80)
    hdr = f"{'model':30} {'edges':>7} {'out_deg':>7} {'circ%':>6} {'kern%':>6} {'c/k%':>6} {'minset':>6}"
    print(hdr)
    print("-" * 80)
    for m in model_metrics:
        short = m["model"].split("/")[-1] if "/" in m["model"] else m["model"]
        print(
            f"{short:30} "
            f"{m.get('n_edges',0):>7} "
            f"{m.get('mean_out_degree',0):>7.2f} "
            f"{m.get('circulation_rate',0)*100:>6.1f} "
            f"{m.get('kernel_ratio',0)*100:>6.1f} "
            f"{m.get('core_kernel_ratio',0)*100:>6.1f} "
            f"{str(m.get('minset_size','-')):>6}"
        )
    print("-" * 80)
    wn = wn_metrics
    print(
        f"{'wordnet (baseline)':30} "
        f"{wn.get('n_edges',0):>7} "
        f"{wn.get('mean_out_degree',0):>7.2f} "
        f"{wn.get('circulation_rate',0)*100:>6.1f} "
        f"{wn.get('kernel_ratio',0)*100:>6.1f} "
        f"{wn.get('core_kernel_ratio',0)*100:>6.1f} "
        f"{str(wn.get('minset_size','-')):>6}"
    )
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--models", nargs="+", default=FULL_MODELS)
    args = parser.parse_args()

    cfg = ExperimentConfig(
        n_words=3000,
        seed=args.seed,
        models=args.models,
    )
    run(cfg)
