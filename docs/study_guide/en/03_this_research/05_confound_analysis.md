# Confound Analysis: sr_rate and Instruction Regime

**Time**: 45 min

---

## What is a Confound?

A **confound** (confounding variable) Z is a third variable that affects both X and Y, potentially creating a spurious correlation between them.

```
We want to measure:
  model_size (X) ──→ kernel_ratio (Y)

Potential confound:
  model_size (X) ──→ sr_rate (Z) ──→ kernel_ratio (Y)
  model_size (X) ──────────────────→ kernel_ratio (Y)  (direct effect)
```

If larger models also have higher sr_rate, and higher sr_rate inflates kernel_ratio, then the observed correlation X→Y might be indirect.

---

## sr_rate: The Instruction-Following Failure Rate

| Model | sr_rate | follow_rate |
|---|---|---|
| Qwen3.5-0.8B | 76.2% | 23.8% |
| Qwen3.5-2B | 92.2% | 7.8% |
| Qwen3.5-4B | 86.2% | 13.8% |
| Qwen3.5-9B | 75.9% | 24.1% |
| Qwen3.5-27B | 84.9% | 15.1% |
| Gemma-4-4B | **0.1%** | **99.9%** |
| Gemma-4-31B | **0.1%** | **99.9%** |

**Finding 1**: Within Qwen3.5, sr_rate has no monotone relationship with model size.
**Finding 2**: Gemma-4 belongs to a completely different instruction regime.

---

## Partial Correlation

**Partial correlation** r(X, Y | Z): the correlation between X and Y after removing Z's linear effect.

```python
import numpy as np

def partial_corr(x, y, z):
    def residual(a, b):
        B = np.column_stack([b, np.ones(len(b))])
        beta = np.linalg.lstsq(B, a, rcond=None)[0]
        return a - B @ beta
    return np.corrcoef(residual(x, z), residual(y, z))[0, 1]

r_raw = np.corrcoef(kern_all, log2_all)[0, 1]         # −0.757
r_partial = partial_corr(kern_all, log2_all, sr_all)   # −0.723
print(f"Δr = {r_partial - r_raw:.3f}")  # +0.034
```

**Δr = +0.034** — controlling for sr_rate barely changes the correlation.
The scale–kernel relationship is **not** an artifact of differential instruction-following.

---

## Structural Consequences of Instruction Regime

Comparing Qwen3.5-4B vs Gemma-4-4B (same parameter count, different regime):

| Metric | Qwen3.5-4B | Gemma-4-4B |
|---|---|---|
| sr_rate | 86.2% | 0.1% |
| n_edges | 6,844 | 5,025 |
| kern% | 10.8% | 7.3% |
| mset/k% | 17.1% | 23.3% |

Gemma-4 produces sparser graphs (fewer self-references) but its smaller kernel has denser cyclic structure.

---

## How to Report This in a Paper

```
"We treat sr_rate as an instruction-regime covariate in cross-family comparisons.
Partial correlation analysis shows Δr = +0.034 for kernel_ratio,
confirming that the scale–kernel relationship is not an artifact of
differential instruction-following. We recommend reporting sr_rate
alongside graph metrics in any cross-family comparison."
```

---

Next: `../04_future_plan/01_research_issues.md`
