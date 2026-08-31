"""Stage 5: Build the WordNet baseline definition graph.

Uses the same normalize → build_graph pipeline as the LLM definitions,
but sourced from WordNet synset.definition() instead of model output.
"""

from .graph_build import build_graph
from .sampling import _ensure_nltk


def wordnet_definitions(words: list[dict]) -> list[dict]:
    """Return definition records for each word using WordNet.

    Uses the definition of the matching synset (stored in word_list_v1.json).
    Falls back to the first synset for the given POS if the stored synset
    is not found.
    """
    _ensure_nltk()
    from nltk.corpus import wordnet as wn

    records: list[dict] = []
    for entry in words:
        lemma = entry["lemma"]
        pos = entry["pos"]
        synset_name = entry.get("synset")
        definition = ""

        if synset_name:
            try:
                definition = wn.synset(synset_name).definition()
            except Exception:
                pass

        if not definition:
            synsets = wn.synsets(lemma, pos=pos)
            if synsets:
                definition = synsets[0].definition()

        records.append({
            "lemma": lemma,
            "pos": pos,
            "model": "wordnet",
            "definition": definition,
            "status": "ok" if definition else "failed",
        })

    return records


def build_wordnet_graph(words: list[dict]):
    """Build and return a DiGraph from WordNet definitions of the given word list."""
    definitions = wordnet_definitions(words)
    return build_graph(definitions), definitions
