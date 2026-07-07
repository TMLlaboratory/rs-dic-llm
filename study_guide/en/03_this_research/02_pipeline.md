# Experiment Pipeline

**Time**: 60 min

---

## Overview

```
Stage 0: Word sampling       3,000 words from WordNet + Brown Corpus
    ↓
Stage 1: Definition generation  Each LLM generates 1 definition per word
    ↓
Stage 2: Preprocessing          Lemmatize, remove stop words
    ↓
Stage 3: Graph construction     Build nx.DiGraph
    ↓
Stage 4: Metrics                Kernel / Core / MinSet / sr_rate
    ↓
Stage 5: WordNet baseline       WordNet definitions through the same pipeline
    ↓
Stage 6: Analysis               Scaling correlations, confound analysis, universal kernel
```

---

## Stage 0: Why 3,000 Words?

**Preliminary experiment with 300 words produced ~0 edges (even in WordNet baseline).**

Reasoning: with 300 words, if "cat" is defined using "animal", "animal" has only a ~0.3% chance of being in the sampled vocabulary — most cross-references are lost.

With 3,000 words (Brown Corpus frequency ≥ 5), most common English words that appear in definitions are in the vocabulary, so edges can be captured.

Composition: 1,500 nouns + 900 verbs + 600 adjectives, seed = 42.

---

## Stage 1: Prompt and Parameters

```python
PROMPT = (
    'Define the {pos} "{word}" in one short sentence. '
    "Use only common English words. "
    "Do not use the word itself in the definition."
)
```

| Parameter | Value | Reason |
|---|---|---|
| temperature | 0.7 | Qwen3.5 official recommendation |
| top_p | 0.8 | official recommendation |
| top_k | 20 | official recommendation |
| max_tokens | 80 | keep to one sentence |
| enable_thinking | False | required (True takes minutes) |

Definition status labels:

| status | Meaning |
|---|---|
| `ok` | Clean definition |
| `self_referential` | Defined word appears in the definition |
| `failed` | 3 consecutive generation failures |

---

## Stage 2–3: Preprocessing and Graph Construction

```python
def build_graph(definitions, vocab):
    G = nx.DiGraph()
    G.add_nodes_from(vocab)
    for rec in definitions:
        if rec["status"] not in {"ok", "self_referential"}:
            continue
        target = rec["word"]
        for raw in rec["definition"].split():
            token = raw.lower().strip(".,;:!?\"'")
            if not token.isalpha() or token in STOP_WORDS:
                continue
            source = lemmatize(token)
            if source in vocab and source != target:
                G.add_edge(source, target)   # source is used to define target
    return G
```

> **Why include `self_referential`?** Excluding them makes Qwen3.5 graphs artificially sparse. We remove only self-loops (source == target); other valid edges are kept.

---

## Graph Scale (actual measurements)

| Model | Nodes | Edges | Mean out-degree |
|---|---|---|---|
| Qwen3.5-0.8B | 2,750 | 10,259 | 3.73 |
| Qwen3.5-27B | 2,750 | 6,927 | 2.52 |
| Gemma-4-4B | 2,750 | 5,025 | 1.83 |
| WordNet | — | — | 1.67 |

Smaller models produce more edges (because they use a smaller repetitive vocabulary).

---

Next: `03_metrics.md`
