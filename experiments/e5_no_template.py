"""E5 — Instruction-tuned models without the chat template.

Research question: Is reciprocity excess R caused by the chat template wrapping
(system prompts, special tokens, generation hints), or by the underlying
instruction-tuning of the weights?

Design:
  - Models: all instruct models (same 17 as main experiment)
  - Same prompt text as main experiment (_PROMPT_TEMPLATE)
  - use_template=False: raw prompt text sent directly to the model
    (no system prompt, no BOS/EOS special tokens from the chat template)
  - Outputs: data/definitions/e5_notemplate/{display}_42.jsonl
             results/e5_notemplate/metrics_{display}_42.json
             results/e5_notemplate/summary.json

Interpretation:
  - If R stays in instruct range (>= 8.9) → the template is NOT the cause;
    instruction tuning of the weights creates the structure.
  - If R drops toward base range → the template formatting is part of the mechanism.

Note: without a chat template, instruct models may produce less coherent output.
The ok-rate and definition quality will likely drop. What matters is the graph
structure of whatever definitions ARE produced.

Usage:
    python -m experiments.e5_no_template
    python -m experiments.e5_no_template --smoke
    python -m experiments.e5_no_template --model Gemma3-4B
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import ExperimentConfig, MODEL_DISPLAY, MODEL_REGISTRY, INSTRUCT_MODELS
from rs_dic_llm.sampling import load_word_list
from rs_dic_llm.generation import generate_definitions, _PROMPT_TEMPLATE
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.analysis import compute_all_metrics, save_metrics
from rs_dic_llm import hf_client

OUTPUT_DIR = "results/e5_notemplate"
DEF_DIR = "data/definitions/e5_notemplate"


def _print_row(m: dict) -> None:
    display = m.get("display", m.get("model", "?"))
    R = m.get("reciprocity_excess", 0.0)
    sr = m.get("sr_rate", 0.0)
    ok_rate = m.get("ok_rate", 0.0)
    print(
        f"  {display:22}  "
        f"edges={m.get('n_edges', 0):6}  "
        f"R={R:6.2f}  "
        f"kern={m.get('kernel_ratio', 0) * 100:.1f}%  "
        f"ok={ok_rate:.0%}  "
        f"sr={sr:.0%}"
    )


def run(smoke: bool = False, model_filter: str | None = None) -> None:
    config = ExperimentConfig(word_list_path="data/sample_words/word_list_3k_v1.json")
    words = load_word_list(config.word_list_path)
    if smoke:
        words = words[:10]
        print("[e5] SMOKE TEST — 10 words only")

    models = INSTRUCT_MODELS
    if model_filter:
        match = [hf for _, hf, _, _ in MODEL_REGISTRY if MODEL_DISPLAY[hf] == model_filter]
        if not match:
            print(f"Unknown model: {model_filter}")
            sys.exit(1)
        models = match

    print(f"[e5] {len(words)} words × {len(models)} instruct models  (NO chat template)")
    all_metrics: list[dict] = []

    for model_id in models:
        display = MODEL_DISPLAY.get(model_id, model_id.split("/")[-1])
        def_path = f"{DEF_DIR}/{display}_42.jsonl"
        met_path = f"{OUTPUT_DIR}/metrics_{display}_42.json"

        if Path(met_path).exists() and not smoke:
            print(f"\n[e5] {display}: already done, skipping")
            with open(met_path) as f:
                metrics = json.load(f)
            all_metrics.append(metrics)
            _print_row(metrics)
            continue

        print(f"\n[e5] generating — {display}  (raw prompt, no template)")
        defs = generate_definitions(
            words,
            model_id,
            config,
            output_path=def_path if not smoke else None,
            use_template=False,          # THE KEY ABLATION: bypass chat template
            prompt_template=_PROMPT_TEMPLATE,
        )

        G = build_graph(defs)
        metrics = compute_all_metrics(G, model_id=model_id, run_minset=False)
        metrics["display"] = display
        metrics["experiment"] = "e5_notemplate"
        n_defs = max(len(defs), 1)
        metrics["sr_rate"] = sum(1 for r in defs if r.get("status") == "self_referential") / n_defs
        metrics["ok_rate"] = sum(1 for r in defs if r.get("status") in ("ok", "self_referential")) / n_defs

        all_metrics.append(metrics)
        if not smoke:
            save_metrics(metrics, met_path)
        _print_row(metrics)

        hf_client.unload_model()

    # Summary
    print("\n" + "=" * 76)
    print("E5 SUMMARY — Instruct models WITHOUT chat template")
    print("Reference: main experiment R (same models, with template)")
    print("=" * 76)
    print(f"  {'model':22}  {'R':>6}  {'kern%':>6}  {'ok%':>6}  {'edges':>6}")
    print("  " + "-" * 62)
    for m in sorted(all_metrics, key=lambda x: (x.get("family", ""), x.get("param_b", 0))):
        R = m.get("reciprocity_excess", 0.0)
        tag = " ← ≥8.9" if R >= 8.9 else ""
        print(
            f"  {m.get('display', '?'):22}  {R:6.2f}  "
            f"{m.get('kernel_ratio', 0) * 100:6.1f}  "
            f"{m.get('ok_rate', 0) * 100:6.1f}  "
            f"{m.get('n_edges', 0):6}{tag}"
        )

    if not smoke:
        out = Path(OUTPUT_DIR) / "summary.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"experiment": "e5_notemplate", "models": all_metrics}, indent=2))
        print(f"\n[e5] saved → {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--smoke", action="store_true", help="10 words, no files written")
    parser.add_argument("--model", type=str, default=None,
                        help="Run one model by display name (e.g. Gemma3-4B)")
    args = parser.parse_args()
    run(smoke=args.smoke, model_filter=args.model)
