"""Measure output drift from temperature=0.7 before committing to the full run.

Runs one small model twice with different generation seeds and compares
kernel_ratio, sr_rate, and circulation_rate. If drift > effect sizes we
expect to measure, switch to greedy (temperature=0).

Recommendation from Vincent-Lamarre 2016: the kernel ratio typically spans
~10-30% across model sizes. Any drift comparable to that range means T=0.7
is introducing noise that drowns the signal.

Usage:
    python -m experiments.drift_measurement
    python -m experiments.drift_measurement --model Qwen2.5-3B --n-words 300
    python -m experiments.drift_measurement --seeds 0 1 2   # 3-way comparison
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import ExperimentConfig, MODEL_DISPLAY, MODEL_REGISTRY
from rs_dic_llm.sampling import load_word_list
from rs_dic_llm.generation import generate_definitions
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.analysis import compute_all_metrics
from rs_dic_llm.metrics.kernel_core import compute_kernel


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def run_one(model_id: str, words: list[dict], config: ExperimentConfig,
            seed: int) -> tuple[dict, set]:
    """Generate + compute metrics for one seed. Returns (metrics, kernel_set)."""
    cfg = ExperimentConfig(
        models=[model_id],
        n_words=len(words),
        seed=config.seed,
        generation_seed=seed,
        temperature=config.temperature,
        top_p=config.top_p,
        top_k=config.top_k,
        max_tokens=config.max_tokens,
    )
    defs = generate_definitions(words, model_id, cfg, output_path=None)
    G = build_graph(defs)
    metrics = compute_all_metrics(G, model_id=model_id, run_minset=False)
    metrics["sr_rate"] = sum(1 for r in defs if r.get("status") == "self_referential") / len(defs)
    kernel = compute_kernel(G)
    return metrics, kernel


def run(model_id: str, seeds: list[int], n_words: int) -> None:
    config = ExperimentConfig()
    words = load_word_list(config.word_list_path)[:n_words]
    display = MODEL_DISPLAY.get(model_id, model_id.split("/")[-1])

    print(f"\n[drift] model    : {display}")
    print(f"[drift] n_words  : {n_words}")
    print(f"[drift] seeds    : {seeds}")
    print(f"[drift] temperature: {config.temperature}")
    print()

    results = []
    for seed in seeds:
        print(f"--- seed {seed} ---")
        metrics, kernel = run_one(model_id, words, config, seed)
        results.append({"seed": seed, "metrics": metrics, "kernel": kernel})

    # ── Metric drift table ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"DRIFT REPORT: {display} — {n_words} words × {len(seeds)} seeds")
    print("=" * 70)
    metric_keys = ["kernel_ratio", "circulation_rate", "mean_out_degree", "sr_rate"]
    print(f"  {'metric':20}" + "".join(f"  seed={s}" for s in seeds) +
          "    range    %range")
    print("  " + "-" * 65)
    for key in metric_keys:
        vals = [r["metrics"].get(key, 0.0) for r in results]
        rng = max(vals) - min(vals)
        pct_range = rng / (np.mean(vals) + 1e-9) * 100
        row = f"  {key:20}" + "".join(f"  {v*100:6.2f}%" for v in vals)
        row += f"   {rng*100:5.2f}pp  {pct_range:5.1f}%"
        print(row)

    # ── Kernel Jaccard across seed pairs ─────────────────────────────────────
    if len(results) >= 2:
        print(f"\n  Kernel Jaccard similarity (1.0 = identical):")
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                j_score = jaccard(results[i]["kernel"], results[j]["kernel"])
                print(f"    seed {seeds[i]} vs seed {seeds[j]}: {j_score:.4f}")

    # ── Recommendation ────────────────────────────────────────────────────────
    kr_vals = [r["metrics"].get("kernel_ratio", 0.0) for r in results]
    kr_range_pp = (max(kr_vals) - min(kr_vals)) * 100
    print(f"\n  kernel_ratio drift: {kr_range_pp:.2f}pp")

    if kr_range_pp < 1.0:
        print("  VERDICT: drift < 1pp — T=0.7 with fixed seed is acceptable.")
        print("           Proceed with the full run.")
    elif kr_range_pp < 3.0:
        print("  VERDICT: drift 1–3pp — marginal. Report as noise floor in paper.")
        print("           Consider whether effects of interest are > 3pp.")
    else:
        print("  VERDICT: drift > 3pp — comparable to expected effect sizes.")
        print("           Switch to greedy decoding (temperature=0) for the full run.")

    # ── Save report ───────────────────────────────────────────────────────────
    out = {
        "model": display,
        "n_words": n_words,
        "seeds": seeds,
        "temperature": config.temperature,
        "results": [
            {
                "seed": r["seed"],
                "kernel_ratio": r["metrics"].get("kernel_ratio"),
                "circulation_rate": r["metrics"].get("circulation_rate"),
                "mean_out_degree": r["metrics"].get("mean_out_degree"),
                "sr_rate": r["metrics"].get("sr_rate"),
                "kernel_size": r["metrics"].get("kernel_size"),
            }
            for r in results
        ],
    }
    out_path = Path("results") / f"drift_{display}_n{n_words}.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\n  Report saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", type=str, default="Qwen2.5-3B",
        help="Display name of model to use (default: Qwen2.5-3B)"
    )
    parser.add_argument(
        "--n-words", type=int, default=300,
        help="Word count (300 is fast and sufficient for drift estimate)"
    )
    parser.add_argument(
        "--seeds", type=int, nargs="+", default=[0, 1],
        help="Generation seeds to compare (default: 0 1)"
    )
    args = parser.parse_args()

    # Resolve display name → hf model id
    match = [hf for _, hf, _, _ in MODEL_REGISTRY if MODEL_DISPLAY[hf] == args.model]
    if not match:
        print(f"Unknown model: {args.model}", file=sys.stderr)
        print(f"Valid names: {[d for d,_,_,_ in MODEL_REGISTRY]}")
        sys.exit(1)

    run(match[0], args.seeds, args.n_words)
