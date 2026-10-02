"""E3 few-shot outputs: do the base models copy the three examples in the prompt? (D023 item 5)

E3 gave each base model a prompt with three worked examples (book, walk, large) before the target
word (experiments/e3_fewshot_base.py). A base model can answer a new word by repeating an example
definition or by repeating the same sentence for many words; either would put template words into
the graph. This script counts, per E3 model, over the stored definitions (first sentence, as used by
the filter):
  - copies:   the text, lower-cased and without punctuation, equals an example definition, or shares
              a run of 6 or more consecutive words with one;
  - repeats:  the same normalized text given to two or more different words;
  - the share of records the filter (D023) drops, for comparison.
Output: outputs/16_e3_copy_check.txt.
"""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")
from rs_dic_llm.extraction import first_sentence  # noqa: E402
from rs_dic_llm.quality_filter import classify  # noqa: E402

EXAMPLES = {
    "book": "A set of printed or written pages bound together between covers.",
    "walk": "To move forward by placing one foot in front of the other at a steady pace.",
    "large": "Having a size or amount that is greater than normal or average.",
}
MODELS = ["Gemma3-270M-pt", "Gemma3-1B-pt", "Gemma3-4B-pt", "Gemma3-12B-pt", "Gemma3-27B-pt"]
PATH = "results_2026-09-09_Runpod/results_e3 (fewshot)/definitions/{}_42.jsonl"
RUN = 6


def words(text):
    return re.findall(r"[a-z]+", text.lower())


def shares_run(tokens, example_tokens, n=RUN):
    grams = {tuple(example_tokens[i:i + n]) for i in range(len(example_tokens) - n + 1)}
    return any(tuple(tokens[i:i + n]) in grams for i in range(len(tokens) - n + 1))


ex_tokens = {k: words(v) for k, v in EXAMPLES.items()}
print(f"{'model':16}{'records':>8}{'exact copy':>12}{'6-word run':>12}{'repeated text':>15}{'records in repeats':>20}{'dropped by filter':>19}")
details = {}
for model in MODELS:
    recs = [json.loads(line) for line in open(ROOT / PATH.format(model), encoding="utf-8") if line.strip()]
    texts = [(r["word"], first_sentence(r.get("definition") or "")) for r in recs]
    exact = runs = 0
    by_text = collections.defaultdict(set)
    dropped = 0
    for word, text in texts:
        toks = words(text)
        if not toks:
            continue
        if any(toks == t for t in ex_tokens.values()):
            exact += 1
        if any(shares_run(toks, t) for t in ex_tokens.values()):
            runs += 1
        by_text[" ".join(toks)].add(str(word).lower())
        dropped += not classify(text, word).keep
    repeated = {t: ws for t, ws in by_text.items() if len(ws) >= 2}
    in_repeats = sum(len(ws) for ws in repeated.values())
    details[model] = sorted(repeated.items(), key=lambda kv: -len(kv[1]))[:4]
    print(f"{model:16}{len(recs):>8}{exact:>12}{runs:>12}{len(repeated):>15}{in_repeats:>20}{dropped:>19}")
print("\nmost repeated texts (number of different words that received the same text):")
for model, items in details.items():
    for text, ws in items:
        print(f"   {model:16} x{len(ws):<3} {text[:100]!r}")
