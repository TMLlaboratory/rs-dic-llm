# How to Read the Results

**Time**: 60 min

---

## Big Picture

```
Qwen3.5 (same architecture, varying scale):
  kernel%:  17.9 → 11.1 → 10.8 → 10.1 → 8.6   (monotone ↓, r=−0.862)
  mset/k%:  14.4 → 16.7 → 17.1 → 18.1 → 20.3  (monotone ↑, r=+0.982)

Gemma-4 (different architecture):
  sr_rate ≈ 0.1% (vs. Qwen3.5's 76–92%)
  kernel%: 7.3 (4B), 8.1 (31B) ← lower than same-size Qwen3.5
  mset/k%: 23.3 (4B), 16.2 (31B) ← higher density in smaller kernel
```

---

## Pearson Correlation: Key Values

```
r = +1.0: perfect positive correlation
r =  0.0: no correlation
r = −1.0: perfect negative correlation
```

| Metric vs log2(params) | Within Qwen3.5 | All 7 models |
|---|---|---|
| kernel_ratio | −0.862 | −0.757 |
| mset/k | **+0.982** | +0.318 |
| circ | −0.675 | — |

An r = +0.982 with only 5 data points is exceptionally strong. It means the mset/k values fall nearly on a straight line when plotted against log2(params).

---

## Scatter Plot (Text)

```
kernel_ratio vs log2(params):

18% │ ●  (0.8B)
    │
12% │    ●  (2B)
    │       ●  (4B)
    │          ●  (9B)
 9% │              ●  (27B)
    └────────────────────────
       -0.3  1.0  2.0  3.2  4.8  ← log2(params)

Slope ≈ −0.0165 (every doubling of params → −1.65 pp kernel ratio)
```

---

## WordNet Comparison

WordNet kernel ratio = 15.5%, higher than any LLM.
Vincent-Lamarre et al. (2016) found ~10% for curated human dictionaries.
WordNet's higher value reflects its synset-based (rather than prose) definitions.

The largest LLM (Qwen3.5-27B at 8.6%) has entered the range of curated dictionaries.

---

## Quantization Results

```
Qwen3.5-27B quantization comparison:
       bf16  8-bit  6-bit  4-bit
kern%:  8.6   9.4    8.2    8.7
mset/k: 20.3  15.9   19.1   20.2
```

4-bit is closest to bf16 (Δkern = +0.1pp). 8-bit deviates most on mset/k (−4.4pp), possibly an artifact of MLX's 8-bit scheme.

**Practical implication**: 4-bit quantisation reduces inference cost dramatically with minimal impact on graph metrics.

---

Next: `05_confound_analysis.md`
