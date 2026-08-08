"""Quantization side study: does precision level affect definition-graph metrics?

Design justification:
    Models : Qwen2.5-27B and Qwen2.5-72B
    Why    : Same family — isolates precision from family/architecture effects.
             Two sizes — checks whether the precision effect is consistent across
             scales (quantization error may differ for larger models).
             Both are the *largest* models in the main experiment and therefore
             the ones most at risk of precision-related confounds.
    Levels : bf16, int8, int4 — the three standard levels in the HuggingFace /
             bitsandbytes ecosystem. 6-bit is not supported in bitsandbytes and
             was excluded to ensure reproducibility by other researchers.
    n_words: 300 — fast (~2h total), stable enough for metric comparison.
             Not 3000 because this is a controlled side study, not a full run.

Hypothesis:
    H0: quantization does not change kernel_ratio or sr_rate meaningfully
        (< 1pp difference vs bf16)
    H1: lower precision causes measurable changes (>= 1pp in kernel_ratio or
        >= 3pp in sr_rate)

Interpretation:
    If H1 confirmed → controls for precision in main experiment are justified
    If H0 holds    → bf16 constraint is conservative but still valid methodology

Usage:
    python experiments/quantization_study.py
    python experiments/quantization_study.py --n-words 500
    python experiments/quantization_study.py --model-size 27B   # one model only
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import ExperimentConfig
from rs_dic_llm.sampling import load_word_list
from rs_dic_llm.generation import generate_definitions
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.analysis import compute_all_metrics
from rs_dic_llm import hf_client

# The two models chosen for the side study (see justification above)
STUDY_MODELS = {
    "27B": "Qwen/Qwen2.5-27B-Instruct",
    "72B": "Qwen/Qwen2.5-72B-Instruct",
}
PRECISIONS = ["bf16", "int8", "int4"]
GEN_SEED = 0   # fixed; same seed used for every combination → differences are pure precision effect


def _run_one(model_id: str, precision: str, words: list, config: ExperimentConfig) -> dict:
    hf_client.load_model(model_id, quantization=precision)
    cfg = ExperimentConfig(
        models=[model_id],
        n_words=len(words),
        seed=config.seed,
        generation_seed=GEN_SEED,
        temperature=config.temperature,
        top_p=config.top_p,
        top_k=config.top_k,
        max_tokens=config.max_tokens,
    )
    defs = generate_definitions(words, model_id, cfg, output_path=None)
    G = build_graph(defs)
    metrics = compute_all_metrics(G, model_id=model_id, run_minset=False)
    n = len(defs) or 1
    metrics["sr_rate"] = sum(1 for r in defs if r.get("status") == "self_referential") / n
    metrics["precision"] = precision
    metrics["n_ok"] = sum(1 for r in defs if r.get("status") in ("ok", "self_referential"))
    return metrics


def main(n_words: int = 300, model_sizes: list[str] | None = None) -> None:
    if model_sizes is None:
        model_sizes = list(STUDY_MODELS.keys())

    config = ExperimentConfig()
    words = load_word_list(config.word_list_path)[:n_words]

    print(f"\n[quantization study] {n_words} words × {len(model_sizes)} models "
          f"× {len(PRECISIONS)} precision levels = "
          f"{n_words * len(model_sizes) * len(PRECISIONS):,} generation calls")
    print(f"  temperature : {config.temperature}   (same as main experiment)")
    print(f"  gen_seed    : {GEN_SEED}           (fixed — differences = pure precision effect)")
    print()

    results: list[dict] = []
    for size in model_sizes:
        model_id = STUDY_MODELS[size]
        model_short = model_id.split("/")[1]
        for precision in PRECISIONS:
            print(f"--- {model_short} [{precision}] ---")
            try:
                m = _run_one(model_id, precision, words, config)
                results.append({
                    "model": model_short, "size": size,
                    "precision": precision,
                    "kernel_ratio": m["kernel_ratio"],
                    "circulation_rate": m["circulation_rate"],
                    "mean_out_degree": m["mean_out_degree"],
                    "sr_rate": m["sr_rate"],
                    "n_ok": m["n_ok"],
                })
                print(f"  kern={m['kernel_ratio']*100:.1f}%  "
                      f"circ={m['circulation_rate']*100:.1f}%  "
                      f"sr={m['sr_rate']*100:.0f}%  "
                      f"ok={m['n_ok']}/{n_words}")
                hf_client.unload_model()
            except Exception as e:
                print(f"  FAILED: {e}", file=sys.stderr)
                results.append({
                    "model": model_short, "size": size,
                    "precision": precision, "error": str(e),
                })

    _print_summary(results, model_sizes)
    _interpret(results, model_sizes)
    _save(results, n_words)


def _print_summary(results: list, model_sizes: list) -> None:
    print("\n" + "=" * 82)
    print("QUANTIZATION SIDE STUDY — RESULTS TABLE")
    print("=" * 82)
    hdr = f"  {'model':28} {'prec':6} {'kern%':>7} {'circ%':>7} {'out_deg':>8} {'sr%':>5} {'ok':>6}"
    print(hdr)
    print("  " + "-" * 70)

    for size in model_sizes:
        for precision in PRECISIONS:
            r = next((x for x in results
                      if x.get("size") == size and x.get("precision") == precision), None)
            if r is None:
                continue
            if "error" in r:
                print(f"  {r['model']:28} {precision:6}  ERROR")
            else:
                marker = "←bf16" if precision == "bf16" else ""
                print(f"  {r['model']:28} {precision:6} "
                      f"{r['kernel_ratio']*100:>7.1f} "
                      f"{r['circulation_rate']*100:>7.1f} "
                      f"{r['mean_out_degree']:>8.2f} "
                      f"{r['sr_rate']*100:>5.0f} "
                      f"{r['n_ok']:>6}  {marker}")
        print()


def _interpret(results: list, model_sizes: list) -> None:
    print("=" * 82)
    print("INTERPRETATION (relative to bf16 baseline)")
    print("=" * 82)
    any_h1 = False
    for size in model_sizes:
        size_rows = [r for r in results if r.get("size") == size and "error" not in r]
        bf16 = next((r for r in size_rows if r["precision"] == "bf16"), None)
        if not bf16:
            continue
        model_name = bf16["model"]
        print(f"\n  {model_name}:")
        for r in size_rows:
            if r["precision"] == "bf16":
                continue
            dkr = (r["kernel_ratio"] - bf16["kernel_ratio"]) * 100
            dsr = (r["sr_rate"] - bf16["sr_rate"]) * 100
            verdict = "H0 (< 1pp, acceptable)" if abs(dkr) < 1.0 else "H1 — SIGNIFICANT EFFECT"
            if abs(dkr) >= 1.0:
                any_h1 = True
            print(f"    {r['precision']:6} vs bf16: "
                  f"kernel_ratio {dkr:+.1f}pp  "
                  f"sr_rate {dsr:+.1f}pp  → {verdict}")

    print()
    if any_h1:
        print("  CONCLUSION: Quantization significantly alters definition-graph metrics.")
        print("  This confirms that precision level is a confound variable that must be")
        print("  controlled. The main experiment's constraint of uniform bf16 precision")
        print("  across all 17 models is methodologically necessary, not just conservative.")
    else:
        print("  CONCLUSION: Quantization does not significantly alter key graph metrics")
        print("  at the n=300 scale. The bf16 constraint in the main experiment is")
        print("  conservative and ensures reproducibility, even if not strictly required.")


def _save(results: list, n_words: int) -> None:
    out = Path("results/quantization_study.json")
    out.parent.mkdir(exist_ok=True)
    payload = {
        "design": {
            "models": STUDY_MODELS,
            "precisions": PRECISIONS,
            "n_words": n_words,
            "gen_seed": GEN_SEED,
            "hypothesis": {
                "H0": "quantization does not change kernel_ratio by >= 1pp vs bf16",
                "H1": "lower precision causes >= 1pp change in kernel_ratio",
            },
        },
        "results": results,
    }
    out.write_text(json.dumps(payload, indent=2))
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n-words", type=int, default=300,
                        help="Words per model/precision combination (default: 300)")
    parser.add_argument("--model-size", choices=["27B", "72B"],
                        help="Run only one model size (default: both)")
    args = parser.parse_args()

    sizes = [args.model_size] if args.model_size else None
    main(args.n_words, sizes)
