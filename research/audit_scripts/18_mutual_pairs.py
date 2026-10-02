"""What are the mutual definitions? (the 2-cycles behind R), on the primary graphs (default filter, first sentence).

Reads the graph snapshots of results_2026-10-01_Local/e2_filtered_default_main_32x and lists, for every
graph, the pairs of words that each appear in the definition of the other. Prints: the number of pairs
per graph and how many of them WordNet also has; the pairs of WordNet and of two instruct models; how
many instruct models share each pair. Output is recorded in outputs/18_mutual_pairs.txt.
"""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
GRAPHS = ROOT / "results_2026-10-01_Local" / "e2_filtered_default_main_32x" / "graphs"


def pairs(key):
    g = json.load(open(GRAPHS / f"{key}.json", encoding="utf-8"))
    edges = {tuple(e) for e in g["edges"]}
    return {tuple(sorted((u, v))) for (u, v) in edges if (v, u) in edges and u != v}


keys = [p.stem for p in sorted(GRAPHS.glob("main__*.json"))]
P = {k: pairs(k) for k in keys}
wn = P["main__wordnet"]
is_base = lambda k: k.endswith("-pt")
instruct = [k for k in keys if not is_base(k) and k != "main__wordnet"]
base = [k for k in keys if is_base(k)]

print("1. MUTUAL PAIRS PER GRAPH, and how many are also WordNet pairs")
for k in sorted(keys, key=lambda k: -len(P[k])):
    print(f"   {k[6:]:26} {len(P[k]):4} pairs; also in WordNet: {len(P[k] & wn)}")

print(f"\n2. WORDNET'S {len(wn)} PAIRS\n   {sorted(wn)}")
for k in ("main__Gemma3-27B", "main__Qwen2.5-72B"):
    print(f"\n3. {k[6:]}: {len(P[k])} pairs, the first 40 alphabetically\n   {sorted(P[k])[:40]}")
a, b = P["main__Gemma3-27B"], P["main__Qwen2.5-72B"]
print(f"\n   shared by Gemma3-27B and Qwen2.5-72B: {len(a & b)} ({100 * len(a & b) / len(a):.0f} % of Gemma3-27B's, {100 * len(a & b) / len(b):.0f} % of Qwen2.5-72B's)")

count = collections.Counter(p for k in instruct for p in P[k])
total = sum(len(P[k]) for k in instruct)
print(f"\n4. SHARING AMONG THE {len(instruct)} INSTRUCT MODELS: {len(count)} different pairs, {total} pair occurrences")
print(f"   pairs found in at least 2 models: {sum(1 for c in count.values() if c >= 2)} of {len(count)}; "
      f"occurrences that are shared with another model: {sum(c for c in count.values() if c >= 2)} of {total} "
      f"({100 * sum(c for c in count.values() if c >= 2) / total:.0f} %)")
print("   most common pairs (number of instruct models):", count.most_common(15))
print(f"   pairs of the instruct models that WordNet also has: {sum(1 for p in count if p in wn)} of {len(count)} different pairs")

print("\n5. THE BASE MODELS' PAIRS")
for k in base:
    shared = sum(1 for p in P[k] if p in count)
    print(f"   {k[6:]:16} {len(P[k]):3} pairs, {shared} of them also found in an instruct model: {sorted(P[k])}")
