---
marp: true
theme: academic-tml
paginate: true
math: katex
---

<!-- _class: lead -->

# Controlled Scaling Study — Results
### rs-dic-llm · 17 Models · 3 Families · Uniform bf16

ロペスチャパホセ
2026-08-10

> Continuation of: *Model List, Hardware & Cost* (2026-07-28)
> Building on: Kumoi (2026), Vincent-Lamarre et al. (2016)

---

# Where We Left Off

## Two previous presentations

<div class="two-columns">
<div class="column">

**Cross-family replication** (deck.md)
11 models · 7 families · Together AI

- Scaling law r = −0.862 **does not generalize** across families
- sr_rate is a **training-recipe fingerprint**
- Out-degree (definitional style) drives topology, not parameter count

</div>
<div class="column">

**RunPod planning** (2026-07-28)
17 models · B200 · bf16 everywhere

- Proposed controlled re-run to address open issues raised by teacher
- Justified hardware, precision, seed + drift methodology

</div>
</div>

<div class="bubble">
This presentation reports what we actually found when we ran it.
</div>

---

# What the Teacher Asked to Justify

## Open issues from the last discussion

| Issue raised | Our answer |
|---|---|
| n=7 is too few data points | → Expanded to **17 models** across 3 families |
| Stochasticity unquantified (T=0.7) | → **Drift measurement** (see next section) |
| Mixed precision confounds results | → **Quantization study** + bf16 everywhere |
| sr_rate not experimentally controlled | → Controlled statistically; Qwen3 replaces Qwen3.5 |

> Each of these is addressed in a dedicated slide below.

---

<!-- _class: lead -->

# Part 1 — Experimental Setup

Justified decisions, one by one

---

# The 17 Models

## Three families, all bf16, all instruct

| Family | Sizes | Weight (bf16) | n |
|---|---|---|---|
| **Qwen2.5** | 0.5B · 1.5B · 3B · 7B · 14B · 32B · **72B** | 1.0–145 GB | 7 |
| **Qwen3** | 0.6B · 1.7B · 4B · 8B · **14B** | 1.2–28 GB | 5 |
| **Gemma3** | 270M · 1B · 4B · 12B · **27B** | 0.5–55 GB | 5 |

> All official HuggingFace checkpoints · All instruct · All **bf16** — no exceptions

WordNet baseline run through the identical pipeline.

---

# Word List Design

## n = 3,000 · POS 50/30/20 · seed 42

| Parameter | Value | Rationale |
|---|---|---|
| `n_words` | **3,000** | VL2016 used ~1,200 (French Robert) — 2.5× more for English WordNet density |
| POS split | **50% n · 30% v · 20% adj** | Mirrors VL2016 natural frequency structure |
| `word_sampling_seed` | **42** | One frozen list `word_list_3k_v1.json` — no word-selection confound |

- **Convergence:** Kernel/Core stabilize as vocabulary grows; 3,000 is past the convergence point
- **GPU budget:** 10–35 min/model × 17 models fits one 9-hour B200 pod session
- **Comparability:** all 17 models see the identical word list

<div class="bubble">
Cross-family study changed the word list between runs → 8pp swing on the deterministic WordNet baseline. This run fixes that.
</div>

---

# Generation Parameters

## Identical decoding across all 17 models

| Parameter | Value | Why |
|---|---|---|
| `temperature` | **0.7** | Mild stochasticity; validated by drift measurement → 1.64pp noise floor |
| `top_p` | **0.8** | Nucleus sampling — restricts to 80% cumulative probability mass |
| `top_k` | **20** | Hard candidate cap — combined with top_p, eliminates improbable tokens |
| `max_tokens` | **200** | Safety ceiling; ↑ from 80 after MLX pilots truncated thinking tokens before definition text |
| `generation_seed` | `base + word_index` | Per-word seed — any definition independently reproducible; crash-restarts are order-independent |

Mean definition length: **11–16 tokens** (max ~39). The 200-token ceiling is never approached.

<div class="bubble">
Identical decoding means observed metric differences must reflect model capability, not decoding strategy.
</div>

---

# Prompt Design — The Template

## Three deliberate clauses — each a methodological choice

```
Define the {pos} "{word}" in one short sentence.
Use only common English words.
Do not use the word itself in the definition.
```

| Clause | Purpose |
|---|---|
| `{pos}` label | POS disambiguation — "run" noun ≠ "run" verb |
| **one short sentence** | Prevents multi-sentence output and meta-commentary; matches VL2016 format |
| **common English words** | Graph density — rare synonyms are out-of-vocabulary and produce no graph edges |
| **do not use the word itself** | Prevents uninformative self-loops |

---

# Prompt Design — Self-Reference Handling

## What happens when the model violates clause 3?

Violations are **expected** at T=0.7 — not pipeline errors. Handled in three steps:

1. Record flagged as `status = "self_referential"` in the JSONL output
2. Self-loop edge removed during graph construction
3. Word still participates via its other valid edges

**Why this matters — `sr_rate` as a behavioral metric:**

> A model with high `sr_rate` is producing definitional shortcuts rather than genuine semantic decomposition. Larger models tend to self-reference less — so `sr_rate` tracks instruction-following quality and becomes a confound variable analyzed in Part 2.

<div class="bubble">
Self-reference is a symptom, not just noise. This is why the teacher flagged sr_rate as an uncontrolled variable.
</div>

---

# Why Not Qwen3.5? → Qwen3

## Discovered during weight download on the CPU pod

The previous study used **Qwen3.5** (0.8B–27B). We tried to replicate that.

**What went wrong:**

> All Qwen3.5-\*-Instruct model IDs return **404 on HuggingFace**.

After investigation: Qwen3.5 is a **multimodal vision-language model** (VLM).
It requires `AutoModelForMultimodalLM`, not `AutoModelForCausalLM`.
Our pipeline is text-only — it is **architecturally incompatible**.

**What we replaced it with:**

**Qwen3** — the text-only LLM family from the same vendor, 5 sizes (0.6B→14B).
Critically: Qwen3 also has **much lower sr_rate** than Qwen3.5,
which removes one of the confounds the teacher flagged.

<div class="bubble">
Qwen3.5 was never a valid choice for this pipeline. Qwen3 is a cleaner experimental design.
</div>

---

# Drift Measurement

## Teacher's question: is T=0.7 introducing noise larger than our effects?

**Design:** run one model twice with different generation seeds; compare kernel\_ratio.

### First attempt: n=300 — **invalid**

```
kernel_ratio = 0.0%  (both runs)
```

300 words is too sparse — not enough definitions to form any cycles at all.

### Second attempt: n=1,000 — **valid**

```
Run A kernel_ratio = X%
Run B kernel_ratio = X + 1.64pp
```

**Drift = 1.64 percentage points.**

<div class="bubble">
1.64pp is our noise floor. Any measured effect larger than this is real.
T=0.7 is acceptable. The full experiment ran at n=3,000.
</div>

---

# Quantization Study

## Teacher's question: does precision level change the graph metrics?

**Design:** Qwen2.5-32B and Qwen2.5-72B × {bf16, int8, int4} · n=500

| Model | Precision | kern% | circ% | sr% |
|---|---|---|---|---|
| Qwen2.5-32B | bf16 | 1.4% | 1.0% | 49.8% |
| Qwen2.5-32B | int8 | 1.4% | 1.0% | 49.8% |
| Qwen2.5-32B | int4 | 1.4% | 1.0% | 49.8% |
| Qwen2.5-72B | bf16 | 1.0% | 0.8% | 11.2% |
| Qwen2.5-72B | int8 | 1.0% | 0.8% | 11.2% |
| Qwen2.5-72B | int4 | 1.0% | 0.8% | 11.2% |

**H₀: < 1pp difference from bf16** → **Confirmed.** All differences = 0.0pp.

<div class="two-columns">
<div class="column">

← **Prior** (Qwen3.5-27B, MLX):
bf16=8.6% · 8bit=9.4% · 4bit=8.7%
Δ up to 0.8pp — borderline acceptable

</div>
<div class="column">

**New** (Qwen2.5, B200):
All precisions **identical** — bf16 is
conservative, not strictly necessary.

</div>
</div>

---

<!-- _class: lead -->

# Part 2 — Results

What we found

---

# Main Result: Family Identity Dominates

## The scaling law does not generalize — confirmed again, with more data

**Prior result** (Qwen3.5, n=5): kern% fell 17.9% → 8.6% across 0.8B–27B — r = **−0.862**

**New result — 17 models, 3 families — r = +0.382 (weak, positive):**

| Family | Sizes | kern% range | Direction |
|---|---|---|---|
| Qwen2.5 | 0.5B → 72B | 7.0–13.9% | ↑↓↑↓ — **no monotone** |
| Qwen3 | 0.6B → 14B | 3.4–12.2% | ↑↓↑ — **no monotone** |
| Gemma3 | 270M → 27B | 0.0–12.5% | ↑ monotone ✅ |

<div class="bubble">
Family membership predicts graph structure better than parameter count.
The old r = −0.862 was a Qwen3.5-only pattern — not a law of scale.
</div>

---

# Gemma3 — Convergence Toward WordNet

## The one family that shows clean monotone scaling

| Size | kern% | |
|---|---|---|
| Gemma3-270M | 0.0% | ← too small to form cycles |
| Gemma3-1B | 5.9% | |
| Gemma3-4B | 8.7% | |
| Gemma3-12B | 11.9% | |
| Gemma3-27B | 12.5% | |
| **WordNet** | **15.5%** | ← human-curated ceiling |

Gemma3 is the **only family in either study** to show a clean monotone increase
that converges toward the WordNet baseline.

<div class="bubble">
Larger Gemma3 models produce definitional graphs that structurally resemble WordNet.
New finding — not present in the prior study (which used Gemma-4, a different generation).
</div>

> ← Prior Gemma-4 (4B bf16 → 31B **8bit**): 7.3% → 8.1% — confounded by mixed precision

---

# Qwen Families — No Monotone Trend

## Model size is not a reliable predictor within either Qwen family

**Qwen2.5** (7 sizes) — ↑↓↑↓ no monotone

| 0.5B | 1.5B | 3B | 7B | 14B | 32B | 72B |
|---|---|---|---|---|---|---|
| 13.9% | 8.4% | 10.7% | 13.6% | 7.8% | 7.0% | 9.7% |

**Qwen3** (5 sizes) — ↑↓↑ no monotone

| 0.6B | 1.7B | 4B | 8B | 14B |
|---|---|---|---|---|
| 3.4% | 12.2% | 7.0% | 8.7% | 8.8% |

Both families hover in the 7–14% range with no directional trend.
The apparent trend in Qwen3.5 (prior study) was specific to that architecture's training recipe.

---

# Kernel Stability: What Words Are Universally Central?

## How many words appear in every model's kernel?

<div class="two-columns">
<div class="column">

← **Prior study** (Qwen3.5, 5 models):
**92 words** in all 5 kernels
→ Interpreted as "universal kernel"

← **Cross-family replication** (11 models):
**38 words** in all 11 kernels
→ Weakened: family, not universal

</div>
<div class="column">

**New** (17 models, 3 families):
**0 words** in all 17 kernels
**13 words** in 16/17 kernels

*number · group · point · place · person*
*idea · begin · take · start · action*
*people · use · different*

**12/13 also in WordNet kernel ✅**

</div>
</div>

<div class="bubble">
The "universal kernel" shrinks as the model set grows. What survives — 13 near-universal words — are high-generality abstract anchors. Cross-system agreement with WordNet on these 13 is strong.
</div>

---

# Core ≠ NSM Primitives

## Do LLM definitional cores recover Wierzbicka's semantic primes?

**NSM** (Natural Semantic Metalanguage): 65 theoretical primitives — *do, want, know, feel, this, same, big, small…*

| Model | NSM overlap | Core words (sample) |
|---|---|---|
| Qwen2.5-3B | 9.2% | *action, become, choose, feel, energy…* |
| Qwen3-4B | 6.2% | *action, allow, feel, force, bad…* |
| Gemma3-4B | 4.6% | *action, force, finish, bad, body…* |
| All models | **0–9.2%** | |

LLMs converge on a consistent set — *action, force, desire, different, energy, body* —
but these are **not** Wierzbicka's primes.

<div class="bubble">
LLMs develop their own "semantic bedrock" through training.
It is consistent across families but distinct from theoretically-motivated primitives.
</div>

---

# Confound Analysis: SR Rate

## Teacher's question: is the kernel–size correlation an artefact of instruction-following?

**sr_rate** = fraction of definitions where the model uses the word itself.
Larger models tend to do this less.

| Metric | r raw | r partial (controlling sr) | Δr |
|---|---|---|---|
| kernel\_ratio | +0.382 | +0.275 | −0.107 |
| mset/k ratio | +0.638 | +0.410 | −0.228 |

← Prior cross-family study: Δr = +0.034 (sr barely mattered across 7 families)
**New** (17 models): Δr = −0.107 to −0.228 — sr inflates correlations more noticeably.

**But the partial correlations remain positive** — sr_rate does not fully explain the trend.

<div class="bubble">
The kernel–size correlations are real but partially inflated by instruction-following differences.
Reporting partial correlations alongside raw values is now standard in this analysis.
</div>

---

# Regression: Definition Style Encodes Model Size

## Can graph metrics predict how large a model is?

**Design:** predict log₂(params) from graph + text metrics, LOO cross-validation.

| Features | R² | Q²\_loo |
|---|---|---|
| kernel\_ratio alone | 0.15 | **−0.17** (worse than mean) |
| minset/kernel alone | 0.41 | +0.19 |
| **out\_degree + OOV\_rate + tokens/word** | **0.86** | **+0.71** |

**Best predictors are text-style features, not graph metrics directly.**

Larger models write:
- **longer** definitions (more tokens/word)
- **fewer** out-of-vocabulary words (lower OOV rate)
- **higher** out-degree (more references per definition)

<div class="bubble">
Definitional style is a fingerprint of model scale — consistent with the prior finding that
out-degree, not parameter count directly, drives graph topology.
</div>

---

<!-- _class: lead -->

# Part 3 — Synthesis

What changed, what stands, what is new

---

# Verdict 1/2 — Prior Scaling Claims

## How our new results update the original four claims

| Claim | Prior verdict | New verdict |
|---|---|---|
| Kernel ratio ↓ with scale | Family trait (Qwen3.5 only) | Not universal — **Gemma3 goes ↑** |
| MinSet/K ↑ with scale | Inverts in gpt-oss & Gemma-4 | **No monotone in Qwen2.5 or Qwen3** |
| Universal kernel (92 words) | Weakened to 38 across 11 families | **Further weakened: 0 in 17, 13 in 16/17** |
| sr_rate = recipe fingerprint | Confirmed, generation-level | **Confirmed. Qwen3 varies 15–85% by size** |

<div class="bubble">
No prior scaling claim survives as a universal law. All are family-level traits.
</div>

---

# Verdict 2/2 — New Questions Answered

## Four open questions from the RunPod planning slides — now resolved

| Question | Status before | Answer now |
|---|---|---|
| Does Gemma scale cleanly? | Untestable (mixed precision) | **Yes** — Gemma3 monotone ↑ → converges to WordNet |
| What drives topology? | Out-degree r=+0.75 (11 models) | **Confirmed** — definitional style is the best predictor |
| Is bf16 strictly necessary? | Open question | **No** — H₀ confirmed; bf16 is conservative best practice |
| Is T=0.7 acceptable? | Unquantified | **Yes** — 1.64pp drift at n=1,000 |

<div class="bubble">
Both methodological questions (precision, stochasticity) and one new empirical result (Gemma3 convergence) are answered by this run.
</div>

---

# Limitations & Next Steps

## What this study still cannot answer

- **Single seed** — drift quantified (1.64pp), but multi-seed error bars not yet computed
- **sr_rate not experimentally eliminated** — statistical control only; few-shot prompting pending
- **Gemma3 above 27B unknown** — does the monotone trend continue past 27B?
- **Word-list sensitivity** — single frozen list; bootstrap sampling not yet done

## Highest-priority next steps

1. **Multi-seed** (seeds 42/123/456) — add error bars to every metric
2. **Few-shot prompt** — force sr_rate ≈ 0 across all families; re-run Qwen2.5-7B as a pilot
3. **Gemma3 extrapolation** — if 27B = 12.5% and WordNet = 15.5%, does a larger model reach it?
4. **Style-intervention** — change prompt verbosity, verify out-degree moves, verify metrics follow

---

<!-- _class: lead -->

# Bottom Line

## Family identity > model size, for definition-graph topology

<div class="rule"></div>

**Gemma3** is the only family converging toward WordNet structure.
**Qwen families** show no monotone trend — definitional style dominates.
**Quantization** does not affect metrics — bf16 constraint is validated.
**Drift** at T=0.7 is 1.64pp — real effects are distinguishable from noise.

情報経営システム工学 4年 · ロペスチャパホセ

> Data: `results/full_summary.json` · Definitions: `data/definitions/*.jsonl`
> Scripts: `experiments/analyse_results.py`, `regress_model_size.py`, `analyse_confound.py`
