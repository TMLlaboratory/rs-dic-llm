"""Run the full 17-model experiment on RunPod B200.

All models run sequentially on one B200 (180 GB), bf16, same settings.
Skips any model whose metrics JSON already exists (safe to resume).

Usage:
    python -m experiments.run_experiment                    # all 17 models
    python -m experiments.run_experiment --smoke            # 3 models × 10 words
    python -m experiments.run_experiment --model Qwen2.5-7B # one model by display name
    python -m experiments.run_experiment --gen-seed 0       # override generation seed

Outputs per model:
    data/definitions/{display}_{seed}.jsonl
    data/definitions/{display}_{seed}.manifest.json
    results/metrics/{display}_{seed}.json
    results/full_summary.json  (updated after each model completes)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import (
    ExperimentConfig, FULL_MODELS, SMOKE_MODELS,
    MODEL_REGISTRY, MODEL_DISPLAY, MODEL_PARAM_B, MODEL_FAMILY,
)
from rs_dic_llm.sampling import load_word_list
from rs_dic_llm.generation import generate_definitions, load_definitions
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.analysis import compute_all_metrics, save_metrics
from rs_dic_llm.wordnet_baseline import build_wordnet_graph


def run(config: ExperimentConfig, smoke: bool = False) -> None:
    words = load_word_list(config.word_list_path)
    if smoke:
        words = words[:10]
        print(f"[experiment] SMOKE TEST — using first 10 words only")
    print(f"[experiment] {len(words)} words, {len(config.models)} models")

    all_metrics: list[dict] = []

    for model_id in config.models:
        display = MODEL_DISPLAY.get(model_id, model_id.split("/")[-1])
        def_path     = f"data/definitions/{display}_{config.seed}.jsonl"
        metrics_path = f"{config.output_dir}/metrics/{display}_{config.seed}.json"

        if Path(metrics_path).exists() and not smoke:
            print(f"\n[experiment] {display}: already done, loading ...")
            with open(metrics_path) as f:
                metrics = json.load(f)
            all_metrics.append(metrics)
            _print_row(metrics)
            continue

        if not Path(def_path).exists() or smoke:
            print(f"\n[experiment] generating — {display}")
            definitions = generate_definitions(
                words, model_id, config, output_path=def_path if not smoke else None
            )
        else:
            print(f"\n[experiment] loading existing definitions: {def_path}")
            definitions = load_definitions(def_path)
            if len(definitions) < len(words):
                print(
                    f"  [experiment] WARNING: {def_path} has only "
                    f"{len(definitions)}/{len(words)} records — incomplete from a prior "
                    f"interrupted run. Regenerating ...",
                    file=sys.stderr,
                )
                definitions = generate_definitions(
                    words, model_id, config, output_path=def_path
                )

        print(f"[experiment] building graph + metrics — {display}")
        G = build_graph(definitions)
        metrics = compute_all_metrics(G, model_id=model_id)

        # Annotate with registry metadata for downstream analysis
        metrics["display"] = display
        metrics["param_b"] = MODEL_PARAM_B.get(model_id)
        metrics["family"]  = MODEL_FAMILY.get(model_id)
        metrics["sr_rate"] = _sr_rate(definitions)

        all_metrics.append(metrics)

        if not smoke:
            save_metrics(metrics, metrics_path)
            _save_summary(all_metrics, config)

        _print_row(metrics)

    # WordNet baseline
    wn_path = f"{config.output_dir}/metrics/wordnet_{config.seed}.json"
    if Path(wn_path).exists() and not smoke:
        print("\n[experiment] WordNet baseline: loading ...")
        with open(wn_path) as f:
            wn_metrics = json.load(f)
    else:
        print("\n[experiment] computing WordNet baseline ...")
        wn_G, _ = build_wordnet_graph(words)
        wn_metrics = compute_all_metrics(wn_G, model_id="wordnet")
        wn_metrics["display"] = "wordnet"
        if not smoke:
            save_metrics(wn_metrics, wn_path)

    _print_table(all_metrics, wn_metrics)

    if not smoke:
        _save_summary(all_metrics, config, wn_metrics)
        print(f"\n[experiment] complete — {config.output_dir}/full_summary.json")


def _sr_rate(definitions: list[dict]) -> float:
    if not definitions:
        return 0.0
    sr = sum(1 for r in definitions if r.get("status") == "self_referential")
    return sr / len(definitions)


def _save_summary(
    model_metrics: list[dict],
    config: ExperimentConfig,
    wn_metrics: dict | None = None,
) -> None:
    summary = {"models": model_metrics}
    if wn_metrics:
        summary["wordnet"] = wn_metrics
    path = f"{config.output_dir}/full_summary.json"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def _print_row(m: dict) -> None:
    display = m.get("display", m.get("model", "?"))
    ks = m.get("kernel_size", 0) or 1
    ms = m.get("minset_size") or 0
    sr = m.get("sr_rate", 0.0)
    print(
        f"  {display:20}  "
        f"edges={m.get('n_edges',0):6}  "
        f"circ={m.get('circulation_rate',0)*100:.1f}%  "
        f"kern={m.get('kernel_ratio',0)*100:.1f}%  "
        f"mset/k={ms/ks*100:.1f}%  "
        f"sr={sr:.0%}"
    )


def _print_table(model_metrics: list[dict], wn_metrics: dict) -> None:
    print("\n" + "=" * 90)
    print("EXPERIMENT SUMMARY")
    print("=" * 90)
    hdr = (f"{'display':22} {'fam':8} {'B':>5}  "
           f"{'edges':>7} {'out_deg':>7} {'circ%':>6} {'kern%':>6} "
           f"{'c/k%':>6} {'mset':>5} {'sr%':>5}")
    print(hdr)
    print("-" * 90)
    for m in sorted(model_metrics, key=lambda x: (x.get("family",""), x.get("param_b", 0))):
        display = m.get("display", m.get("model", "?"))
        ks = m.get("kernel_size", 0) or 1
        ms = m.get("minset_size") or 0
        sr = m.get("sr_rate", 0.0)
        print(
            f"{display:22} {m.get('family','?'):8} {m.get('param_b', 0):>5.1f}  "
            f"{m.get('n_edges',0):>7} "
            f"{m.get('mean_out_degree',0):>7.2f} "
            f"{m.get('circulation_rate',0)*100:>6.1f} "
            f"{m.get('kernel_ratio',0)*100:>6.1f} "
            f"{m.get('core_kernel_ratio',0)*100:>6.1f} "
            f"{str(ms):>5} "
            f"{sr*100:>5.1f}"
        )
    print("-" * 90)
    wn = wn_metrics
    ks = wn.get("kernel_size", 0) or 1
    ms = wn.get("minset_size") or 0
    print(
        f"{'wordnet (baseline)':22} {'---':8} {'---':>5}  "
        f"{wn.get('n_edges',0):>7} "
        f"{wn.get('mean_out_degree',0):>7.2f} "
        f"{wn.get('circulation_rate',0)*100:>6.1f} "
        f"{wn.get('kernel_ratio',0)*100:>6.1f} "
        f"{wn.get('core_kernel_ratio',0)*100:>6.1f} "
        f"{str(ms):>5} "
        f"{'---':>5}"
    )
    print("=" * 90)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke",    action="store_true",
                        help="Smoke test: 3 models × 10 words, no files written")
    parser.add_argument("--model",    type=str, default=None,
                        help="Run a single model by display name (e.g. Qwen2.5-7B)")
    parser.add_argument("--seed",     type=int, default=42,
                        help="Word-sampling seed (default 42)")
    parser.add_argument("--gen-seed", type=int, default=0,
                        help="Base generation seed (default 0)")
    args = parser.parse_args()

    # Resolve --model by display name
    if args.model:
        match = [hf for _, hf, _, _ in MODEL_REGISTRY
                 if MODEL_DISPLAY[hf] == args.model]
        if not match:
            print(f"Unknown model display name: {args.model}", file=sys.stderr)
            print(f"Valid names: {[d for d,_,_,_ in MODEL_REGISTRY]}")
            sys.exit(1)
        models = match
    elif args.smoke:
        models = SMOKE_MODELS
    else:
        models = FULL_MODELS

    cfg = ExperimentConfig(
        models=models,
        n_words=10 if args.smoke else 3000,
        seed=args.seed,
        generation_seed=args.gen_seed,
    )
    run(cfg, smoke=args.smoke)
