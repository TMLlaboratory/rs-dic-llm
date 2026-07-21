# Large Language Models and Scaling Laws

**Time**: 60 min | **Prerequisites**: basic probability

---

## What is an LLM?

An LLM (Large Language Model) is a probabilistic model trained on massive text corpora. It generates text by predicting "what word comes next?"

```
Input: "Define the noun 'cat':"
P("a" | input) = 0.12
P("an" | input) = 0.08
...
→ sample or pick the highest-probability word, repeat
```

**Parameter count** = number of learned weights.
0.8B = 800 million, 27B = 27 billion parameters.

---

## Temperature

The `temperature` parameter controls output diversity:

```
temperature → 0.0: always picks the single most likely word (greedy decoding)
temperature = 0.7: samples proportionally to probability (moderate diversity)
temperature = 2.0: nearly random
```

> **This research uses temperature = 0.7** (Qwen3.5 official recommendation for non-thinking mode).
> At temperature = 0.0, self-referential definitions (cat = "a cat-like...") surged to ~85% — confirmed experimentally.

---

## Model Families

Multiple sizes of the same architecture trained on the same data = a **family**.

Used in this research:
- **Qwen3.5**: 0.8B, 2B, 4B, 9B, 27B (same architecture, different scale)
- **Gemma-4**: 4B, 31B (Google DeepMind)

Different families can exhibit fundamentally different behaviours for the same prompt — Gemma-4 follows the "don't use the word itself" instruction; Qwen3.5 largely ignores it.

---

## Scaling Laws

```
Loss ≈ C × N^{-α}   where N = parameter count
```

**Chinchilla (Hoffmann et al., 2022)**: optimal training ratio is ~20 tokens per parameter.

**Knowledge capacity (arXiv:2404.05405)**: ~2 bits of factual knowledge per parameter.

| Model | Params | Est. knowledge |
|---|---|---|
| 0.8B | 800M | ~200 MB |
| 27B | 27B | ~6.75 GB |

**This research asks**: if knowledge capacity scales with parameters, does *how concepts are organised in definitions* also scale?

---

## Instruction Following

LLM prompts can include instructions:

```
"Do not use the word itself in the definition."
```

**Finding**: instruction-following rate is a **family-level property**, not a scale property:
- Qwen3.5: 76–92% of definitions violate the instruction (self-referential)
- Gemma-4: 99.9% of definitions follow the instruction

This difference is the key confound in cross-family analysis.

---

Next: `../02_key_papers/01_vincent_lamarre_2016.md`
