"""Stage 0: Sample words from WordNet for the dictionary-graph experiment.

Sampling strategy:
  - POS split: noun 50%, verb 30%, adjective 20%  (mirrors VL2016 roughly)
  - Filter to synsets whose Brown-corpus frequency > 0 (content words only)
  - Take the first lemma of the first (most frequent) synset per POS
  - Deduplicate, then random-sample with a fixed seed
"""

import json
import random
from pathlib import Path


def _ensure_nltk() -> None:
    import nltk
    for resource in ("wordnet", "omw-1.4", "brown", "universal_tagset"):
        try:
            nltk.data.find(f"corpora/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)


def _brown_freq() -> dict[str, int]:
    """Return {lemma: count} from Brown corpus for frequency filtering."""
    from nltk.corpus import brown
    from collections import Counter
    return Counter(w.lower() for w in brown.words())


def sample_words(
    n_total: int = 300,
    seed: int = 42,
    output_path: str | None = None,
    min_freq: int = 5,
) -> list[dict]:
    """Return a list of {lemma, pos, synset} dicts.

    POS quotas: noun=50%, verb=30%, adj=20% (rounded).
    Only words appearing >= min_freq times in the Brown corpus are kept,
    so sampled words tend to be common enough to reference each other in
    definitions (sparse rare-word graphs have ~0 edges).
    Saves JSON to output_path if provided.
    """
    _ensure_nltk()
    from nltk.corpus import wordnet as wn

    freq = _brown_freq()

    quotas = {
        "n": round(n_total * 0.50),
        "v": round(n_total * 0.30),
        "a": n_total - round(n_total * 0.50) - round(n_total * 0.30),
    }

    rng = random.Random(seed)
    result: list[dict] = []

    for pos, quota in quotas.items():
        candidates: list[dict] = []
        seen_lemmas: set[str] = set()
        for synset in wn.all_synsets(pos=pos):
            lemma = synset.lemmas()[0].name().replace("_", " ").lower()
            if lemma in seen_lemmas:
                continue
            if not synset.definition():
                continue
            if freq.get(lemma, 0) < min_freq:
                continue
            seen_lemmas.add(lemma)
            candidates.append({
                "lemma": lemma,
                "pos": pos,
                "synset": synset.name(),
                "definition_wn": synset.definition(),
                "brown_freq": freq.get(lemma, 0),
            })
        sampled = rng.sample(candidates, min(quota, len(candidates)))
        result.extend(sampled)

    rng.shuffle(result)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {"version": "v1", "seed": seed, "n_total": len(result), "words": result},
                f, ensure_ascii=False, indent=2,
            )
        print(f"  [sampling] saved {len(result)} words to {output_path}")

    return result


def load_word_list(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)["words"]
