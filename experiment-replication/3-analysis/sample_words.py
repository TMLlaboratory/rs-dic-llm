"""
Stage 0: sample 3,000 words (1,500 nouns / 900 verbs / 600 adjectives)
from WordNet, filtered by Brown Corpus frequency >= 5, seed 42.

Deterministic given the same nltk data version (candidates are sorted
before sampling). Output: words.json  [{word, pos}, ...]

Usage: python sample_words.py [--out words.json]
"""

import argparse
import json
import random

import nltk

for pkg in ["wordnet", "brown", "omw-1.4"]:
    try:
        nltk.data.find(f"corpora/{pkg}")
    except LookupError:
        nltk.download(pkg, quiet=True)

from nltk.corpus import brown, wordnet as wn

SEED = 42
QUOTA = {"noun": (wn.NOUN, 1500), "verb": (wn.VERB, 900), "adjective": (wn.ADJ, 600)}
MIN_FREQ = 5


def main(out_path: str):
    freq = nltk.FreqDist(w.lower() for w in brown.words() if w.isalpha())

    rng = random.Random(SEED)
    sampled = []
    for pos_label, (wn_pos, quota) in QUOTA.items():
        candidates = set()
        for synset in wn.all_synsets(wn_pos):
            for lemma in synset.lemma_names():
                w = lemma.lower()
                if w.isalpha() and "_" not in lemma and freq[w] >= MIN_FREQ:
                    candidates.add(w)
        candidates = sorted(candidates)          # determinism
        picked = rng.sample(candidates, quota)
        sampled += [{"word": w, "pos": pos_label} for w in picked]
        print(f"{pos_label}: {len(candidates)} candidates -> {quota} sampled")

    # A word can be sampled under two POS (e.g. noun+verb); the paper treats
    # entries as (word,pos) prompts but the graph vocabulary is the word set.
    vocab = {e["word"] for e in sampled}
    print(f"total entries: {len(sampled)}, unique vocab: {len(vocab)}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sampled, f, indent=1)
    print(f"saved {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="words.json")
    main(ap.parse_args().out)
