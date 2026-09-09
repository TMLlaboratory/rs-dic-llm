"""Stage 1: Generate definitions for a list of words via HuggingFace transformers."""

import json
import re
import sys
import time
from pathlib import Path

from tqdm import tqdm

from . import hf_client
from .config import ExperimentConfig

_POS_LABEL = {"n": "noun", "v": "verb", "a": "adjective"}
_BATCH_SIZE = 16

_PROMPT_TEMPLATE = (
    'Define the {pos} "{word}" in one short sentence. '
    "Use only common English words. "
    "Do not use the word itself in the definition."
)


def _first_sentence(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    for sep in (".\n", "\n", ". "):
        idx = text.find(sep)
        if idx != -1:
            return text[: idx + 1].strip()
    return text.strip()


def _is_self_referential(definition: str, word: str) -> bool:
    # re.findall strips punctuation so "happiness." correctly matches "happiness"
    tokens = re.findall(r"[a-zA-Z'-]+", definition.lower())
    return word.lower() in tokens


def _write_manifest(path: str, model_id: str, config: ExperimentConfig) -> None:
    """Save generation parameters beside the JSONL file for full reproducibility."""
    manifest = {
        "model_id": model_id,
        "generation_seed": config.generation_seed,
        "temperature": config.temperature,
        "top_p": config.top_p,
        "top_k": config.top_k,
        "max_tokens": config.max_tokens,
        "n_words": config.n_words,
        "word_list_path": config.word_list_path,
        "seed_formula": "generation_seed + word_index",
    }
    Path(path).write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


def generate_definitions(
    words: list[dict],
    model_id: str,
    config: ExperimentConfig,
    output_path: str | None = None,
    use_template: bool = True,
    prompt_template: str | None = None,
    extract_fn=None,
) -> list[dict]:
    """Generate definitions for each word using the loaded HF model.

    Per-word seed = config.generation_seed + word_index, so any individual
    word's output is reproducible independently of list order.

    Writes results incrementally to output_path (JSONL) if provided.
    Also writes a companion .manifest.json with all generation parameters.

    Args:
        use_template: if False, skip apply_chat_template (for E5 / raw base model runs).
        prompt_template: override the default prompt. Must have {word} and {pos} slots.
        extract_fn: override _first_sentence for custom output parsing (e.g. E3 few-shot).

    Returns list of result dicts with keys:
        word, pos, model, definition, status, tokens_approx, latency_ms,
        generation_seed (the per-word seed used)
    """
    hf_client.load_model(model_id)

    template = prompt_template or _PROMPT_TEMPLATE
    _extract = extract_fn or _first_sentence

    out_file = None
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        out_file = open(output_path, "w", encoding="utf-8")
        manifest_path = output_path.replace(".jsonl", ".manifest.json")
        _write_manifest(manifest_path, model_id, config)

    results: list[dict] = []
    n_failed = 0
    short_name = model_id.split("/")[-1]

    try:
        with tqdm(total=len(words), desc=f"generate [{short_name}]") as pbar:
            for batch_start in range(0, len(words), _BATCH_SIZE):
                batch = words[batch_start: batch_start + _BATCH_SIZE]
                batch_seed = config.generation_seed + batch_start

                prompts = []
                for entry in batch:
                    pos_label = _POS_LABEL.get(entry["pos"], entry["pos"])
                    prompts.append(template.format(word=entry["lemma"], pos=pos_label))

                t0 = time.time()
                try:
                    raws = hf_client.generate_batch(
                        prompts,
                        temperature=config.temperature,
                        top_p=config.top_p,
                        top_k=config.top_k,
                        max_tokens=config.max_tokens,
                        seed=batch_seed,
                        use_template=use_template,
                    )
                except Exception as e:
                    print(f"  [generation] batch failed at {batch_start}: {e}", file=sys.stderr)
                    raws = [""] * len(batch)
                    n_failed += len(batch)

                batch_latency_ms = int((time.time() - t0) * 1000)

                for j, (entry, raw) in enumerate(zip(batch, raws)):
                    word = entry["lemma"]
                    word_seed = config.generation_seed + batch_start + j
                    definition = _extract(raw) if raw else ""

                    if not raw:
                        status = "failed"
                    elif not definition:
                        status = "empty"
                    elif "<think>" in raw:
                        status = "thinking_leak"
                    elif _is_self_referential(definition, word):
                        status = "self_referential"
                    else:
                        status = "ok"

                    record = {
                        "word": word,
                        "lemma": word,
                        "pos": entry["pos"],
                        "model": model_id,
                        "definition": definition,
                        "status": status,
                        "tokens_approx": len(definition.split()),
                        "latency_ms": batch_latency_ms // len(batch),
                        "generation_seed": word_seed,
                    }
                    results.append(record)

                    if out_file:
                        out_file.write(json.dumps(record, ensure_ascii=False) + "\n")

                if out_file:
                    out_file.flush()

                pbar.update(len(batch))

    finally:
        if out_file:
            out_file.close()

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"  [generation] done: {ok}/{len(results)} ok, {n_failed} failed")
    if n_failed / max(len(results), 1) > 0.2:
        print(
            "  [generation] WARNING: failure rate > 20% — check model loading",
            file=sys.stderr,
        )

    return results


def load_definitions(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
