"""Stage 1: Generate definitions for a list of words via mlx-proxy."""

import json
import re
import sys
import time
from pathlib import Path

from tqdm import tqdm

from . import mlx_client
from .config import ExperimentConfig

_POS_LABEL = {"n": "noun", "v": "verb", "a": "adjective"}

_PROMPT_TEMPLATE = (
    'Define the {pos} "{word}" in one short sentence. '
    "Use only common English words. "
    "Do not use the word itself in the definition."
)


def _first_sentence(text: str) -> str:
    """Return the first sentence of text (split on '. ' or '\n')."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    for sep in (".\n", "\n", ". "):
        idx = text.find(sep)
        if idx != -1:
            return text[: idx + 1].strip()
    return text.strip()


def _is_self_referential(definition: str, word: str) -> bool:
    return word.lower() in definition.lower().split()


def generate_definitions(
    words: list[dict],
    model_id: str,
    config: ExperimentConfig,
    output_path: str | None = None,
) -> list[dict]:
    """Generate definitions for each word using the loaded mlx-proxy model.

    Writes results incrementally to output_path (JSONL) if provided.
    Returns list of result dicts with keys:
        word, pos, model, definition, status, tokens_approx, latency_ms
    """
    mlx_client.load_model(model_id)

    out_file = None
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        out_file = open(output_path, "w", encoding="utf-8")

    results: list[dict] = []
    n_failed = 0

    try:
        for entry in tqdm(words, desc=f"generate [{model_id.split('/')[-1]}]"):
            word = entry["lemma"]
            pos = entry["pos"]
            pos_label = _POS_LABEL.get(pos, pos)
            prompt = _PROMPT_TEMPLATE.format(word=word, pos=pos_label)

            status = "ok"
            definition = ""
            t0 = time.time()

            try:
                raw = mlx_client.generate(
                    prompt,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    top_k=config.top_k,
                    max_tokens=config.max_tokens,
                    max_retries=config.max_retries,
                )
                definition = _first_sentence(raw)

                if not definition:
                    status = "empty"
                elif "<think>" in raw:
                    status = "thinking_leak"
                elif _is_self_referential(definition, word):
                    status = "self_referential"

            except Exception as e:
                print(f"  [generation] failed for '{word}': {e}", file=sys.stderr)
                status = "failed"
                n_failed += 1

            latency_ms = int((time.time() - t0) * 1000)
            record = {
                "word": word,
                "lemma": word,
                "pos": pos,
                "model": model_id,
                "definition": definition,
                "status": status,
                "tokens_approx": len(definition.split()),
                "latency_ms": latency_ms,
            }
            results.append(record)

            if out_file:
                out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                out_file.flush()

    finally:
        if out_file:
            out_file.close()

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"  [generation] done: {ok}/{len(results)} ok, {n_failed} failed")
    if n_failed / max(len(results), 1) > 0.2:
        print("  [generation] WARNING: failure rate > 20% — consider few-shot prompt",
              file=sys.stderr)

    return results


def load_definitions(path: str) -> list[dict]:
    """Load a JSONL definition file."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
