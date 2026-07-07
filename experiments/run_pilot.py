"""Pilot experiment: Qwen3.5-0.8B and Qwen3.5-27B × 3000 words.

300 words proved too sparse for graph structure to emerge (0 edges even in WordNet
baseline). 3000 words is the minimum for meaningful Kernel/Core/SCC metrics.

Prerequisites:
    python ~/mlx-proxy/mlx_proxy.py   # in a separate terminal

Usage:
    uv run python -m experiments.run_pilot [--n-words 3000] [--seed 42]

Outputs:
    data/sample_words/word_list_3k_v1.json
    data/definitions/{model_short}_{seed}.jsonl
    results/metrics/{model_short}_{seed}.json
"""

import argparse
import sys
from pathlib import Path

# make sure src/ is on the path when run as a script
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import ExperimentConfig, PILOT_MODELS
from rs_dic_llm.sampling import sample_words, load_word_list
from rs_dic_llm.generation import generate_definitions
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.analysis import compute_all_metrics, save_metrics
from rs_dic_llm import mlx_client


def _model_short(model_id: str) -> str:
    return model_id.split("/")[-1]


def run(config: ExperimentConfig) -> None:
    # ------------------------------------------------------------------ #
    # Stage 0: word sampling
    # ------------------------------------------------------------------ #
    word_list_path = config.word_list_path
    if not Path(word_list_path).exists():
        print(f"[pilot] sampling {config.n_words} words (seed={config.seed}) ...")
        words = sample_words(
            n_total=config.n_words,
            seed=config.seed,
            output_path=word_list_path,
        )
    else:
        print(f"[pilot] loading existing word list: {word_list_path}")
        words = load_word_list(word_list_path)

    # ------------------------------------------------------------------ #
    # Stage 1-4: per-model loop
    # ------------------------------------------------------------------ #
    for model_id in config.models:
        short = _model_short(model_id)
        def_path = f"data/definitions/{short}_{config.seed}.jsonl"
        metrics_path = f"{config.output_dir}/metrics/{short}_{config.seed}.json"

        # Stage 1: generate (or reload if already done)
        if not Path(def_path).exists():
            print(f"\n[pilot] generating definitions — {short}")
            definitions = generate_definitions(
                words, model_id, config, output_path=def_path
            )
        else:
            from rs_dic_llm.generation import load_definitions
            print(f"\n[pilot] loading existing definitions: {def_path}")
            definitions = load_definitions(def_path)

        # Stage 2-3: graph construction
        print(f"[pilot] building graph ...")
        G = build_graph(definitions)

        # Stage 4-5: metrics
        print(f"[pilot] computing metrics ...")
        metrics = compute_all_metrics(G, model_id=model_id)
        save_metrics(metrics, metrics_path)

        # Print pilot summary
        print(f"\n  --- {short} ---")
        print(f"  nodes       : {metrics['n_nodes']}")
        print(f"  circulation : {metrics['circulation_rate']:.3f}")
        print(f"  kernel_ratio: {metrics['kernel_ratio']:.3f}")
        print(f"  core/kernel : {metrics['core_kernel_ratio']:.3f}")
        print(f"  minset_ratio: {metrics['minset_ratio']}")
        print(f"  cycle_dist  : {metrics['cycle_length_dist']}")

    # ------------------------------------------------------------------ #
    # WordNet baseline
    # ------------------------------------------------------------------ #
    from rs_dic_llm.wordnet_baseline import build_wordnet_graph
    print("\n[pilot] computing WordNet baseline ...")
    wn_G, _ = build_wordnet_graph(words)
    wn_metrics = compute_all_metrics(wn_G, model_id="wordnet")
    save_metrics(wn_metrics, f"{config.output_dir}/metrics/wordnet_{config.seed}.json")

    print(f"\n  --- WordNet baseline ---")
    print(f"  nodes       : {wn_metrics['n_nodes']}")
    print(f"  circulation : {wn_metrics['circulation_rate']:.3f}")
    print(f"  kernel_ratio: {wn_metrics['kernel_ratio']:.3f}")
    print(f"  core/kernel : {wn_metrics['core_kernel_ratio']:.3f}")

    # ------------------------------------------------------------------ #
    # Pilot GO/NO-GO check
    # ------------------------------------------------------------------ #
    print("\n[pilot] GO/NO-GO check:")
    model_metrics = []
    for model_id in config.models:
        short = _model_short(model_id)
        mp = f"{config.output_dir}/metrics/{short}_{config.seed}.json"
        if Path(mp).exists():
            import json
            with open(mp) as f:
                model_metrics.append(json.load(f))

    if len(model_metrics) >= 2:
        rates = [m["circulation_rate"] for m in model_metrics]
        diff = max(rates) - min(rates)
        print(f"  circulation rate range: {min(rates):.3f} – {max(rates):.3f}  (diff={diff:.3f})")
        print(f"  criterion 1 (diff >= 0.10): {'PASS' if diff >= 0.10 else 'FAIL'}")

    wn_kr = wn_metrics["kernel_ratio"]
    print(f"  WordNet kernel ratio: {wn_kr:.3f}")
    print(f"  criterion 3 (5-20%): {'PASS' if 0.05 <= wn_kr <= 0.20 else 'FAIL'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-words", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--models", nargs="+", default=PILOT_MODELS)
    args = parser.parse_args()

    cfg = ExperimentConfig(
        n_words=args.n_words,
        seed=args.seed,
        models=args.models,
    )
    run(cfg)
