# Scaling Laws and Knowledge Capacity

**Time**: 45 min | **Prerequisites**: `03_llm_basics.md`

---

## Chinchilla Scaling Laws (Hoffmann et al., 2022)

> Hoffmann, J., et al. (2022). Training compute-optimal large language models. *NeurIPS 2022*.

**Key insight**: there is an optimal ratio between model size N and training data D.

```
Optimal: N ≈ D / 20  (train on ~20× as many tokens as parameters)
```

Earlier work over-scaled models and under-trained them. Chinchilla showed a smaller, better-trained model often outperforms a larger, undertrained one at the same compute budget.

---

## Knowledge Capacity (arXiv:2404.05405)

Estimates the relationship between parameter count and memorisable factual knowledge.

**Conclusion**: ~2 bits of factual knowledge per parameter

| Model | Parameters | Estimated capacity |
|---|---|---|
| Qwen3.5-0.8B | 800M | ~200 MB equivalent |
| Qwen3.5-27B | 27B | ~6.75 GB equivalent |

**Connection to this research**: if knowledge capacity scales linearly with parameters, does *lexical efficiency* (smaller kernel = more knowledge packed into fewer anchor words) also scale?

---

## Emergence

Large models sometimes show **abrupt** jumps in capability at certain scale thresholds.

This research's mset/k ratio (r = +0.982, nearly linear with log-scale) suggests a **continuous** rather than emergent change in conceptual cycle structure across scales tested.

---

## How This Research Fits In

Existing scaling laws use **loss (perplexity)** or **benchmark scores** as the dependent variable.

This research adds:
- **Dictionary graph topology** as a new, architecture-agnostic measurement axis
- Does not require factual recall, only relational structure

```
Existing scaling laws:  parameters → loss
This research adds:     parameters → kernel topology (kernel ratio, mset/k)
```

---

Next: `../03_this_research/01_motivation.md`
