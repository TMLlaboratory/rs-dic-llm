"""E4 — Length-controlled definitions on instruction-tuned models.

Research question: Is reciprocity excess R a byproduct of definition verbosity
(longer definitions reference more vocabulary words → more edges → more 2-cycles),
or does it survive when definition length is constrained?

Design:
  - Models: all instruct models (same 17 as main experiment)
  - Prompt: hard word-count constraint — "in 8 words or fewer"
    (targets the instruct model mean of ~8 words to level the playing field)
  - Same pipeline (chat template, same graph build, same null correction)
  - Outputs: data/definitions/e4_length/{display}_42.jsonl
             results/e4_length/metrics_{display}_42.json
             results/e4_length/summary.json

Interpretation:
  - If R stays >= 8.9 under length constraint → R is real structure, not verbosity.
  - If R drops toward base range → part of R is driven by definition length.

Usage:
    python -m experiments.e4_length_control
    python -m experiments.e4_length_control --smoke
    python -m experiments.e4_length_control --model Gemma3-4B
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import ExperimentConfig, MODEL_DISPLAY, MODEL_REGISTRY, INSTRUCT_MODELS
from rs_dic_llm.sampling import load_word_list
from rs_dic_llm.generation import generate_definitions
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.analysis import compute_all_metrics, save_metrics
from rs_dic_llm import hf_client

# ── Length-constrained prompt ──────────────────────────────────────────────────
# 8 words matches the mean definition length of the 270M–1B instruct models,
# bringing the verbosity distribution in line with smaller models and base models.
_LENGTH_PROMPT = (
    'Define the {pos} "{word}" in 8 words or fewer. '
    "Use only common English words. "
    "Do not use the word itself in the definition."
)

OUTPUT_DIR = "results/e4_length"
DEF_DIR = "data/definitions/e4_length"


def _print_row(m: dict) -> None:
    display = m.get("display", m.get("model", "?"))
    R = m.get("reciprocity_excess", 0.0)
    sr = m.get("sr_rate", 0.0)
    mean_len = m.get("mean_def_words", 0.0)
    print(
        f"  {display:22}  "
        f"edges={m.get('n_edges', 0):6}  "
        f"R={R:6.2f}  "
        f"kern={m.get('kernel_ratio', 0) * 100:.1f}%  "
        f"len={mean_len:.1f}w  "
        f"sr={sr:.0%}"
    )


def run(smoke: bool = False, model_filter: str | None = None) -> None:
    config = ExperimentConfig(word_list_path="data/sample_words/word_list_3k_v1.json")
    words = load_word_list(config.word_list_path)
    if smoke:
        words = words[:10]
        print("[e4] SMOKE TEST — 10 words only")

    models = INSTRUCT_MODELS
    if model_filter:
        match = [hf for _, hf, _, _ in MODEL_REGISTRY if MODEL_DISPLAY[hf] == model_filter]
        if not match:
            print(f"Unknown model: {model_filter}")
            sys.exit(1)
        models = match

    print(f"[e4] {len(words)} words × {len(models)} instruct models  (8-word constraint)")
    all_metrics: list[dict] = []

    for model_id in models:
        display = MODEL_DISPLAY.get(model_id, model_id.split("/")[-1])
        def_path = f"{DEF_DIR}/{display}_42.jsonl"
        met_path = f"{OUTPUT_DIR}/metrics_{display}_42.json"

        if Path(met_path).exists() and not smoke:
            print(f"\n[e4] {display}: already done, skipping")
            with open(met_path) as f:
                metrics = json.load(f)
            all_metrics.append(metrics)
            _print_row(metrics)
            continue

        print(f"\n[e4] generating — {display}")
        defs = generate_definitions(
            words,
            model_id,
            config,
            output_path=def_path if not smoke else None,
            use_template=True,           # instruct models: apply chat template normally
            prompt_template=_LENGTH_PROMPT,
        )

        G = build_graph(defs)
        metrics = compute_all_metrics(G, model_id=model_id, run_minset=False)
        metrics["display"] = display
        metrics["experiment"] = "e4_length"
        n_ok = sum(1 for r in defs if r["status"] in ("ok", "self_referential"))
        metrics["sr_rate"] = sum(1 for r in defs if r.get("status") == "self_referential") / max(len(defs), 1)
        metrics["mean_def_words"] = (
            sum(len(r["definition"].split()) for r in defs if r["definition"])
            / max(n_ok, 1)
        )

        all_metrics.append(metrics)
        if not smoke:
            save_metrics(metrics, met_path)
        _print_row(metrics)

        hf_client.unload_model()

    # Summary
    print("\n" + "=" * 72)
    print("E4 SUMMARY — Length-controlled instruct models  (8-word constraint)")
    print("Reference: main experiment R (same models, unconstrained)")
    print("=" * 72)
    print(f"  {'model':22}  {'R':>6}  {'kern%':>6}  {'mean_len':>8}  {'edges':>6}")
    print("  " + "-" * 62)
    for m in sorted(all_metrics, key=lambda x: (x.get("family", ""), x.get("param_b", 0))):
        R = m.get("reciprocity_excess", 0.0)
        tag = " ← ≥8.9" if R >= 8.9 else ""
        print(
            f"  {m.get('display', '?'):22}  {R:6.2f}  "
            f"{m.get('kernel_ratio', 0) * 100:6.1f}  "
            f"{m.get('mean_def_words', 0):8.1f}  "
            f"{m.get('n_edges', 0):6}{tag}"
        )

    if not smoke:
        out = Path(OUTPUT_DIR) / "summary.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"experiment": "e4_length", "models": all_metrics}, indent=2))
        print(f"\n[e4] saved → {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--smoke", action="store_true", help="10 words, no files written")
    parser.add_argument("--model", type=str, default=None,
                        help="Run one model by display name (e.g. Gemma3-4B)")
    args = parser.parse_args()
    run(smoke=args.smoke, model_filter=args.model)
