# Open Research Issues

**Time**: 30 min

---

## Priority-Sorted Issue List

### 🔴 High Priority (must address before submission)

**Too few data points**
- Current: Qwen3.5 n=5, all models n=7
- Problem: correlation coefficients from 5–7 points have low statistical power
- Fix: add Llama-4, Phi-4, Mistral families → target n ≥ 15

**Single seed only**
- Current: seed=42 only (T=0.7 introduces stochasticity)
- Problem: variance in graph metrics from generation randomness is not reported
- Fix: run seeds 42, 123, 456; report mean ± std for each metric

**sr_rate not experimentally controlled**
- Current: partial correlation analysis only
- Problem: Gemma-4 vs Qwen3.5 comparison is fundamentally confounded
- Fix: few-shot prompt with 3 non-self-referential examples → reduce Qwen3.5 sr_rate

---

### 🟠 Medium Priority

**No curated human dictionary baseline**
- Current: WordNet only
- Problem: cannot directly replicate Vincent-Lamarre et al. (2016) benchmarks
- Fix: investigate LDOCE licensing; even a 3k-word subset would suffice

**MinSet completeness uncertainty**
- Current: lazy constraint ILP (short cycles as seed)
- Problem: may not enumerate all cycles for convergence guarantee
- Fix: add formal convergence check; compare against brute-force on small graphs

---

### 🟡 Low Priority (future extensions)

- English only → multilingual extension (Japanese, Chinese)
- 3,000 words → larger vocabulary (10,000+)
- Static analysis → dynamic (metrics at each training checkpoint)

---

## Target Venues

| Venue | Notes | Fit |
|---|---|---|
| Topics in Cognitive Science | Same journal as original paper | ★★★ |
| Minds and Machines | Language & AI philosophy | ★★★ |
| ACL / EMNLP Findings | Top NLP venues | ★★ (n=7 too small) |
| COLING | Applied NLP & resources | ★★ |

---

Next: `02_experiment_plan.md`
