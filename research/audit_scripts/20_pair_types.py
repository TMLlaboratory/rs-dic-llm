"""What kind of word pairs are the mutual definitions, and do base models given examples produce the same ones?

Descriptive analysis on the primary graphs (default filter, first sentence) and the E3 graphs of the same run.
1. Every mutual pair (u, v) is typed with WordNet, over all senses of both words and without part of speech:
   synonym (a shared synset), antonym, derived form (derivationally related lemmas), hypernym (one word's synset is a
   direct hypernym of the other's), coordinate (a shared direct hypernym), other. The first match in that order
   decides. "Other" holds associates (eat-mouth, bicycle-ride) and anything WordNet does not link.
2. Overlap of pair sets: few-shot base models (E3) against the instruct models, zero-shot base models against the
   instruct models, with the overlap between two instruct models as the yardstick (Jaccard index).
3. (added 2026-10-02) WordNet's pairs against each instruct model (shared pairs, Jaccard index).
4. (added 2026-10-02) Within-family yardsticks for section 2, which mixes families: Gemma3 against Gemma3, and the
   few-shot base models against the Gemma3 and the non-Gemma instruct models.
Output: outputs/20_pair_types.txt. Exploratory: no reading was fixed in advance.
"""
import collections
import json
import statistics as st
import sys
from pathlib import Path

from nltk.corpus import wordnet as wn

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
RES = ROOT / "results_2026-10-01_Local"
MAIN = RES / "e2_filtered_default_main_32x" / "graphs"
CTRL = RES / "e2_filtered_default_controls_32x" / "graphs"
SIZES = ("1B", "4B", "12B", "27B")


def pairs(path):
    g = json.load(open(path, encoding="utf-8"))
    edges = {tuple(e) for e in g["edges"]}
    return {tuple(sorted((u, v))) for (u, v) in edges if (v, u) in edges and u != v}


def lemma_links(word, kind):
    out = set()
    for s in wn.synsets(word):
        for lem in s.lemmas():
            if lem.name().lower() == word:
                rel = lem.antonyms() if kind == "antonym" else lem.derivationally_related_forms()
                out |= {x.name().lower() for x in rel}
    return out


def relation(u, v):
    su, sv = set(wn.synsets(u)), set(wn.synsets(v))
    if not su or not sv:
        return "not in WordNet"
    if su & sv:
        return "synonym"
    if v in lemma_links(u, "antonym") or u in lemma_links(v, "antonym"):
        return "antonym"
    if v in lemma_links(u, "derived") or u in lemma_links(v, "derived"):
        return "derived form"
    if any(set(s.hypernyms()) & sv for s in su) or any(set(t.hypernyms()) & su for t in sv):
        return "hypernym"
    if any(set(s.hypernyms()) & set(t.hypernyms()) for s in su for t in sv):
        return "coordinate"
    return "other"


ORDER = ["synonym", "antonym", "derived form", "hypernym", "coordinate", "other", "not in WordNet"]
cache = {}


def typed(ps):
    return collections.Counter(cache.setdefault(p, relation(*p)) for p in ps)


def show(label, counter):
    n = sum(counter.values())
    cells = "  ".join(f"{k} {counter[k]} ({100 * counter[k] / n:.0f} %)" for k in ORDER if counter[k])
    print(f"   {label:34} n={n:4}  {cells}")


P = {p.stem: pairs(p) for p in sorted(MAIN.glob("main__*.json"))}
E3 = {p.stem: pairs(p) for p in sorted(CTRL.glob("e3__*.json"))}
wordnet = P["main__wordnet"]
instruct = [k for k in P if not k.endswith("-pt") and k != "main__wordnet"]
base = [k for k in P if k.endswith("-pt")]
union_instruct = set().union(*(P[k] for k in instruct))

print("1. TYPES OF MUTUAL PAIRS (WordNet relation, all senses, no part of speech)")
show("WordNet graph", typed(wordnet))
show("instruct models: distinct pairs", typed(union_instruct))
occurrences = collections.Counter()
for k in instruct:
    occurrences += typed(P[k])
show("instruct models: occurrences", occurrences)
shared = {p for p in union_instruct if sum(p in P[k] for k in instruct) >= 5}
show("pairs found in 5+ instruct models", typed(shared))
occ_base = collections.Counter()
for k in base:
    occ_base += typed(P[k])
show("zero-shot base: occurrences", occ_base)
occ_e3 = collections.Counter()
for k in E3:
    occ_e3 += typed(E3[k])
show("few-shot base (E3): occurrences", occ_e3)

print("\n   examples (most widely shared instruct pairs of each type):")
count = collections.Counter(p for k in instruct for p in P[k])
for kind in ORDER[:6]:
    ranked = sorted(count.items(), key=lambda kv: (-kv[1], kv[0]))  # ties broken alphabetically, so the output is reproducible
    ex = [f"{u}-{v} ({n})" for (u, v), n in ranked if cache.setdefault((u, v), relation(u, v)) == kind][:6]
    print(f"   {kind:13} {', '.join(ex)}")
print("   WordNet's own pairs by type:")
for kind in ORDER[:6]:
    print(f"   {kind:13} {', '.join(f'{u}-{v}' for u, v in sorted(wordnet) if cache.setdefault((u, v), relation(u, v)) == kind)}")

print("\n2. OVERLAP OF PAIR SETS")
jac = lambda a, b: len(a & b) / len(a | b) if a | b else 0.0
inst_inst = [jac(P[a], P[b]) for i, a in enumerate(instruct) for b in instruct[i + 1:]]
print(f"   yardstick: Jaccard index between two instruct models, median {st.median(inst_inst):.2f} (range {min(inst_inst):.2f}-{max(inst_inst):.2f}, {len(inst_inst)} pairs of models)")
print(f"   {'few-shot base (E3)':22}{'pairs':>6}{'in an instruct model':>24}{'in the matched instruct':>26}{'Jaccard matched':>17}{'median Jaccard, 17 instruct':>29}")
for s in SIZES:
    e = E3.get(f"e3__Gemma3-{s}-pt")
    m = P.get(f"main__Gemma3-{s}")
    if e is not None and m is not None:
        in_any = len(e & union_instruct)
        print(f"   {'Gemma3-' + s + '-pt':22}{len(e):6}{str(in_any) + ' (' + format(100 * in_any / len(e), '.0f') + ' %)':>24}"
              f"{str(len(e & m)) + ' (' + format(100 * len(e & m) / len(e), '.0f') + ' %)':>26}{jac(e, m):17.2f}{st.median(jac(e, P[k]) for k in instruct):29.2f}")
print(f"\n   {'zero-shot base':22}{'pairs':>6}{'in an instruct model':>24}{'in WordNet':>14}")
for k in base:
    in_any = len(P[k] & union_instruct)
    print(f"   {k[6:]:22}{len(P[k]):6}{str(in_any) + ' (' + (format(100 * in_any / len(P[k]), '.0f') if P[k] else '0') + ' %)':>24}{len(P[k] & wordnet):14}")
print(f"\n   few-shot base pairs that are WordNet pairs: " + ", ".join(f"{k[10:]} {len(E3[k] & wordnet)} of {len(E3[k])}" for k in E3))

# Added 2026-10-02 after a review: WordNet against each instruct model, and within-family yardsticks (the median of section 2
# mixes model families).
print("\n3. WORDNET AGAINST EACH INSTRUCT MODEL (mutual pairs shared with WordNet's pairs)")
rows = sorted(((jac(P[k], wordnet), k[6:], len(P[k]), len(P[k] & wordnet)) for k in instruct), reverse=True)
for j, name, n, inter in rows:
    print(f"   {name:18} pairs {n:3}  shared with WordNet {inter}  Jaccard {j:.3f}")
print(f"   Jaccard index with WordNet: {min(r[0] for r in rows):.3f}-{max(r[0] for r in rows):.3f}; shared pairs {min(r[3] for r in rows)}-{max(r[3] for r in rows)} of WordNet's {len(wordnet)}")

family = lambda k: k[6:].split("-")[0]
print("\n4. YARDSTICKS BY FAMILY: Jaccard index between two instruct models")
within, across = collections.defaultdict(list), []
for i, a in enumerate(instruct):
    for b in instruct[i + 1:]:
        (within[family(a)] if family(a) == family(b) else across).append(jac(P[a], P[b]))
for fam, v in sorted(within.items()):
    print(f"   within {fam:8} {len(v):3} pairs of models  median {st.median(v):.2f}  range {min(v):.2f}-{max(v):.2f}")
print(f"   across families {len(across):3} pairs of models  median {st.median(across):.2f}  range {min(across):.2f}-{max(across):.2f}")
gemma = [k for k in instruct if family(k) == "Gemma3"]
print("\n   few-shot base (E3) against the instruct models: its matched Gemma3 instruct model, the other Gemma3 instruct models, the non-Gemma instruct models")
for s in SIZES:
    e, matched = E3.get(f"e3__Gemma3-{s}-pt"), P.get(f"main__Gemma3-{s}")
    if e is None or matched is None:
        continue
    others = [jac(e, P[k]) for k in gemma if k != f"main__Gemma3-{s}"]
    non_gemma = [jac(e, P[k]) for k in instruct if family(k) != "Gemma3"]
    print(f"   Gemma3-{s}-pt  matched {jac(e, matched):.2f} | other Gemma3 instruct: median {st.median(others):.2f} (range {min(others):.2f}-{max(others):.2f}) | "
          f"non-Gemma instruct: median {st.median(non_gemma):.2f} (range {min(non_gemma):.2f}-{max(non_gemma):.2f})")
