"""Do the words of the three E3 few-shot examples (book, walk, large) appear in the E3 graphs? (audit F25)

experiments/e3_fewshot_base.py (lines 45-46) says the examples were chosen so that their words are unlikely to be in the
3,000-word sample. This script checks it on the E3 graphs of the default-filter re-run (first sentence):
1. whether the three headwords and the words of the three example definitions are nodes of the 2,750-lemma vocabulary
   (the definitions are read from the script itself and reduced to vocabulary lemmas with the same normalizer as the graphs);
2. per few-shot base model: how many edges start at one of these words, and how many mutual pairs involve one, beside the same
   counts for the matched Gemma3 instruct model, which was not shown the examples (the yardstick for how often these words
   appear anyway).
Descriptive only. Output: outputs/23_e3_example_words.txt.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")
from rs_dic_llm.normalize import normalize  # noqa: E402

RES = ROOT / "results_2026-10-01_Local"
E3 = RES / "e2_filtered_default_controls_32x" / "graphs"
MAIN = RES / "e2_filtered_default_main_32x" / "graphs"
SOURCE = (ROOT / "experiments" / "e3_fewshot_base.py").read_text(encoding="utf-8")
EXAMPLES = re.findall(r'Q: Define the \w+ "(\w+)"\.\r?\nA: (.+)', SOURCE)
assert len(EXAMPLES) == 3, EXAMPLES


def load(path):
    g = json.load(open(path, encoding="utf-8"))
    edges = {tuple(e) for e in g["edges"]}
    return set(g["nodes"]), edges


vocab, _ = load(E3 / "e3__Gemma3-1B-pt.json")
print(f"1. THE EXAMPLES AND THE VOCABULARY ({len(vocab)} lemmas)")
words = set()
for head, text in EXAMPLES:
    inside = sorted(set(normalize(text, vocab)))
    words |= set(inside)
    if head in vocab:
        words.add(head)
    print(f"   {head:6} headword in the vocabulary: {'yes' if head in vocab else 'no':3} | its definition has {len(inside)} words in the vocabulary: {', '.join(inside)}")
heads = {h for h, _ in EXAMPLES if h in vocab}
print(f"   headwords in the vocabulary: {sorted(heads)}; all example words in the vocabulary ({len(words)}): {sorted(words)}")


def involved(edges, subset):
    pairs = {tuple(sorted((u, v))) for (u, v) in edges if (v, u) in edges and u != v}
    return sorted(p for p in pairs if set(p) & subset), len(pairs)


print("\n2. EDGES FROM THE EXAMPLE WORDS AND MUTUAL PAIRS THAT INVOLVE THEM (few-shot base model | matched Gemma3 instruct model)")
for size in ("270M", "1B", "4B", "12B", "27B"):
    row = []
    for label, path in (("E3 base", E3 / f"e3__Gemma3-{size}-pt.json"), ("instruct", MAIN / f"main__Gemma3-{size}.json")):
        if not path.exists():
            row.append(f"{label}: no graph")
            continue
        _, edges = load(path)
        from_words = sum(1 for (u, v) in edges if u in words)
        pairs_all, total_pairs = involved(edges, words)
        pairs_head, _ = involved(edges, heads)
        row.append(f"{label}: edges from the words {from_words} of {len(edges)} ({100 * from_words / len(edges):.1f} %); mutual pairs involving a word "
                   f"{len(pairs_all)} of {total_pairs}, a headword {len(pairs_head)}")
    print(f"   Gemma3-{size:4} " + " | ".join(row))

print("\n   the mutual pairs of the few-shot base models that involve an example word:")
for size in ("270M", "1B", "4B", "12B", "27B"):
    _, edges = load(E3 / f"e3__Gemma3-{size}-pt.json")
    pairs_all, _ = involved(edges, words)
    print(f"   Gemma3-{size}-pt: " + (", ".join("-".join(p) for p in pairs_all) if pairs_all else "none"))
