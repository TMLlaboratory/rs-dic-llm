# Research Motivation

**Time**: 30 min

---

## The Core Intuition

> **"Do smaller models define concepts in circular ways more often?"**

Example: a 0.8B model (hypothetical)
```
cat  → "a cat-like animal with fur"   (uses "cat" to define "cat"!)
dog  → "an animal like a dog"
```

A larger model:
```
cat  → "a small domesticated carnivore kept as a pet or for pest control"
dog  → "a domesticated mammal of the genus Canis"
```

Larger models appear to use richer vocabulary and fewer self-references. **Can we measure this quantitatively?**

---

## Research Map

```
LLM capability evaluation
    │
    ├── Benchmarks (MMLU, etc.) ── task performance
    ├── Perplexity ────────────── language modelling
    └── [This work] Definition graphs ── conceptual organisation (NEW axis)
                    │
                    ├── kernel ratio (lexical efficiency)
                    ├── mset/k (cyclic density of core)
                    └── circulation_rate (overall circularity)
```

---

## Three Research Questions

| RQ | Question | Answer (preview) |
|---|---|---|
| RQ1 | Does kernel ratio correlate with model size? | r = −0.862 within Qwen3.5 |
| RQ2 | How does sr_rate confound cross-family comparison? | Family-level covariate; controlled via partial correlation |
| RQ3 | Is there a universal kernel across all models? | 92 words (10 overlap with NSM) |

---

Next: `02_pipeline.md`
