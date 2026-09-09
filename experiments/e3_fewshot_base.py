"""E3 — Few-shot prompting on base (pretrained) models.

Research question: Does few-shot prompting push base model reciprocity excess R
into the instruction-tuned range (>= 8.9), or does it stay in the base range (1.5–7.3)?

Both outcomes make a publishable claim:
  - R rises  → format compliance, not training, creates the structure.
  - R stays low → instruction tuning causes a qualitative change, not just format.

Design:
  - Models: all 5 Gemma3-pt base models (matched pairs with Gemma3-it)
  - Prompt: 3 Q/A-format few-shot examples + target word
  - use_template=False: raw text to the model (base models have no chat template)
  - Outputs: data/definitions/e3_fewshot/{display}_42.jsonl
             results/e3_fewshot/metrics_{display}_42.json
             results/e3_fewshot/summary.json

Usage:
    python -m experiments.e3_fewshot_base
    python -m experiments.e3_fewshot_base --smoke
    python -m experiments.e3_fewshot_base --model Gemma3-4B-pt
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import ExperimentConfig, MODEL_DISPLAY, MODEL_REGISTRY, BASE_MODELS
from rs_dic_llm.sampling import load_word_list
from rs_dic_llm.generation import generate_definitions
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.analysis import compute_all_metrics, save_metrics
from rs_dic_llm import hf_client

# ── Few-shot prompt ────────────────────────────────────────────────────────────
# Q/A format helps base models identify the correct continuation pattern.
# Examples chosen so none of their definition words overlap with target vocabulary
# (they use very common words unlikely to be in the 3000-word sample).
_FEWSHOT_HEADER = """\
Below are example word definitions. Each definition is one sentence, uses only simple English words, and does not repeat the word being defined.

Q: Define the noun "book".
A: A set of printed or written pages bound together between covers.

Q: Define the verb "walk".
A: To move forward by placing one foot in front of the other at a steady pace.

Q: Define the adjective "large".
A: Having a size or amount that is greater than normal or average.

Q: Define the {pos} "{word}".
A:"""

_POS_LABEL = {"n": "noun", "v": "verb", "a": "adjective"}


def _extract_fewshot_definition(raw: str) -> str:
    """Extract the first sentence from a base model continuation.

    After the few-shot prompt ends with 'A:', the model outputs the definition
    (possibly followed by further Q/A pairs it hallucinates). We take only the
    first complete sentence.
    """
    if not raw:
        return ""
    # Strip any <think> blocks (Qwen3 reasoning models)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    # Stop at the next 'Q:' — model continuing the few-shot pattern
    raw = re.split(r"\nQ:", raw)[0].strip()
    # Take first sentence
    for sep in (".\n", ". ", ".\t", "\n"):
        idx = raw.find(sep)
        if 0 < idx < 300:
            return raw[: idx + 1].strip()
    return raw.strip()


OUTPUT_DIR = "results/e3_fewshot"
DEF_DIR = "data/definitions/e3_fewshot"


def _print_row(m: dict) -> None:
    display = m.get("display", m.get("model", "?"))
    R = m.get("reciprocity_excess", 0.0)
    sr = m.get("sr_rate", 0.0)
    print(
        f"  {display:22}  "
        f"edges={m.get('n_edges', 0):6}  "
        f"R={R:6.2f}  "
        f"kern={m.get('kernel_ratio', 0) * 100:.1f}%  "
        f"circ={m.get('circulation_rate', 0) * 100:.1f}%  "
        f"sr={sr:.0%}"
    )


def run(smoke: bool = False, model_filter: str | None = None) -> None:
    config = ExperimentConfig(word_list_path="data/sample_words/word_list_3k_v1.json")
    words = load_word_list(config.word_list_path)
    if smoke:
        words = words[:10]
        print("[e3] SMOKE TEST — 10 words only")

    models = BASE_MODELS
    if model_filter:
        match = [hf for _, hf, _, _ in MODEL_REGISTRY if MODEL_DISPLAY[hf] == model_filter]
        if not match:
            print(f"Unknown model: {model_filter}")
            sys.exit(1)
        models = match

    print(f"[e3] {len(words)} words × {len(models)} base models  (few-shot prompting)")
    all_metrics: list[dict] = []

    for model_id in models:
        display = MODEL_DISPLAY.get(model_id, model_id.split("/")[-1])
        def_path = f"{DEF_DIR}/{display}_42.jsonl"
        met_path = f"{OUTPUT_DIR}/metrics_{display}_42.json"

        if Path(met_path).exists() and not smoke:
            print(f"\n[e3] {display}: already done, skipping")
            with open(met_path) as f:
                metrics = json.load(f)
            all_metrics.append(metrics)
            _print_row(metrics)
            continue

        print(f"\n[e3] generating — {display}")
        defs = generate_definitions(
            words,
            model_id,
            config,
            output_path=def_path if not smoke else None,
            use_template=False,          # base models: send raw text
            prompt_template=_FEWSHOT_HEADER,
            extract_fn=_extract_fewshot_definition,
        )

        G = build_graph(defs)
        metrics = compute_all_metrics(G, model_id=model_id, run_minset=False)
        metrics["display"] = display
        metrics["experiment"] = "e3_fewshot"
        metrics["sr_rate"] = sum(1 for r in defs if r.get("status") == "self_referential") / max(len(defs), 1)

        all_metrics.append(metrics)
        if not smoke:
            save_metrics(metrics, met_path)
        _print_row(metrics)

        hf_client.unload_model()

    # Summary
    print("\n" + "=" * 70)
    print("E3 SUMMARY — Few-shot base models   (reference: instruct R ≥ 8.9)")
    print("=" * 70)
    print(f"  {'model':22}  {'R':>6}  {'kern%':>6}  {'circ%':>6}  {'edges':>6}")
    print("  " + "-" * 60)
    for m in all_metrics:
        R = m.get("reciprocity_excess", 0.0)
        tag = " ← IN INSTRUCT RANGE" if R >= 8.9 else ""
        print(
            f"  {m.get('display', '?'):22}  {R:6.2f}  "
            f"{m.get('kernel_ratio', 0) * 100:6.1f}  "
            f"{m.get('circulation_rate', 0) * 100:6.1f}  "
            f"{m.get('n_edges', 0):6}{tag}"
        )

    if not smoke:
        out = Path(OUTPUT_DIR) / "summary.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"experiment": "e3_fewshot", "models": all_metrics}, indent=2))
        print(f"\n[e3] saved → {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--smoke", action="store_true", help="10 words, no files written")
    parser.add_argument("--model", type=str, default=None,
                        help="Run one model by display name (e.g. Gemma3-4B-pt)")
    args = parser.parse_args()
    run(smoke=args.smoke, model_filter=args.model)
