---
marp: true
theme: academic-tml
paginate: true
math: katex
---

<!-- _class: lead -->

# Definitional Graphs as Structural Probes of LLM Lexical Knowledge

### Style Over Topology

José Leal
Nagaoka University of Technology
August 2025

---

# A 72B Model Writes the Same Definition as a 14B Model

## The observation that motivates this study

| Model | Parameters | Definition of *"action"* |
|-------|-----------|--------------------------|
| Qwen2.5-14B | 14 B | *"To do something."* |
| Qwen2.5-72B | 72 B | *"To do something."* |

Same output. **58 billion parameters** of difference.

- If model scale doesn't change how a model defines words, what does?
- And if style is already fixed at 14B — what are the extra parameters doing for definition quality?

<div class="bubble">
Definition style can stabilize well before maximum scale — the training recipe, not parameter count, determines it
</div>

---

# The rs-dic-llm Pipeline

## An unsupervised structural probe — no labels, no benchmarks

**Step 1 — Generate**
A fixed set of 3,000 common English words is given to an LLM.
The model produces one definition per word. No examples, no gold standard.

**Step 2 — Build the graph**
Each definition is scanned for words that appear in the 3,000-word vocabulary.
Every such occurrence becomes a directed edge: *defined word → referenced word*

> *"Force"* → *"To make someone do something against their will"*
> edges: force→make, force→someone, force→something, force→will

**Step 3 — Compute metrics**
Graph and sentence-level metrics are extracted from the resulting network.

<div class="bubble">
The same pipeline runs on any model, any language — no task-specific tuning required
</div>

---

# What the Pipeline Measures

## Two levels of analysis

## Sentence-level — computed per definition

| Metric | What it captures |
|--------|-----------------|
| **tokens/word** (tpw) | Average definition length in words |
| **out-degree** | Average in-vocabulary references per definition |
| **OOV rate** | Fraction of unique words outside the 3k vocabulary |
| **sr\_rate** | Fraction of definitions using the target word itself |

## Graph-level — computed from the full 3,000-definition network

| Metric | What it captures |
|--------|-----------------|
| **kernel ratio** | Fraction of vocabulary in the cyclic self-sufficient core |
| **minset ratio** | Minimum set of words that can reach the entire kernel |
| **NSM overlap** | Overlap with Wierzbicka's 65 semantic primitives |

<div class="bubble">
Style metrics are readable from any single definition. Graph metrics emerge only after all 3,000 definitions are generated.
</div>

---

# Graph 1 — Kernel Ratio vs. Parameter Count

## Does the semantic core grow with model scale?

| Model | Kernel ratio | | Model | Kernel ratio |
|-------|-------------|---|-------|-------------|
| Gemma3-270M | **0.0%** ← collapse | | Qwen2.5-0.5B | 13.9% |
| Gemma3-1B | 5.9% | | Qwen2.5-1.5B | 8.4% |
| Gemma3-4B | 8.7% | | Qwen2.5-3B | 10.7% |
| Gemma3-12B | 11.9% | | Qwen2.5-7B | 13.6% |
| Gemma3-27B | **12.5%** | | Qwen2.5-14B | 7.8% |
| | | | Qwen2.5-32B | 7.0% |
| Qwen3-0.6B | 3.4% | | Qwen2.5-72B | 9.7% |
| Qwen3-1.7B | **12.2%** ← anomaly | | | |
| Qwen3-4B | 7.0% | | **WordNet** | **15.45%** |
| Qwen3-14B | 8.8% | | | |

> Predictive power of kernel ratio alone: $Q^2_{loo} = -0.17$

---

# Graph 1 — What Kernel Ratio Tells Us and Doesn't

## What it reveals

- **Gemma3 is the only family with monotone growth** — every size step increases the kernel
- **Gemma3-27B converges toward WordNet** (12.5% vs 15.45%)
- **Gemma3-270M is a total outlier** — kernel = 0% because out-degree is so low (0.54) that the graph forms almost no cycles

## What it fails to reveal

- Kernel ratio alone <span class="marker">cannot predict model size</span> ($Q^2_{loo} = -0.17$, worse than guessing the mean)
- The same kernel value (≈12%) could be Gemma3-27B, Qwen3-1.7B, or Qwen2.5-7B
- Qwen3-1.7B reaches 12.2% — higher than Qwen3-14B (8.8%) — despite being smaller

<div class="bubble">
Kernel ratio is an emergent property accumulated across 3,000 definitions — too compressed to serve as a reliable fingerprint
</div>

---

# Graph 2 — Out-Degree vs. Parameter Count

## Average in-vocabulary references per definition

| Family | Smallest | → | Largest | WordNet ref. | Trend |
|--------|----------|---|---------|--------------|-------|
| Gemma3 | 0.54 (270M) | → | **2.88** (27B) | 1.67 | ↑ monotone, exceeds WN at 4B |
| Qwen2.5 | 2.55 (0.5B) | → | 1.85 (72B) | 1.67 | ↓ then plateau |
| Qwen3 | 1.80 (0.6B) | → | 2.14 (14B) | 1.67 | irregular |

## Key observations

- Gemma3 grows continuously — 270M barely references any in-vocabulary words (0.54); 27B references nearly three (2.88)
- Qwen2.5-0.5B **starts above WordNet** (2.55) then drops sharply to 1.85 at 1.5B and holds there
- Qwen3-1.7B anomaly: out-degree 2.58 — **highest in the Qwen3 family**, despite being the second-smallest model

<div class="bubble">
Out-degree is the primary driver of graph edge density and therefore kernel size
</div>

---

# Graphs 3 & 4 — Tokens/Word and Out-Degree Are the Same Graph

## A structural relationship explains why

$$\text{out\_degree} \approx c \times \text{tokens\_per\_word}, \quad c \approx 0.20\text{–}0.26$$

The fraction of in-vocabulary words per definition (**OOV density**) is approximately constant across all 17 models — roughly 1 in-vocabulary word for every 4–5 total words.

## The data confirms it

| Model | tpw | out-degree | Ratio (od/tpw) |
|-------|-----|------------|----------------|
| Gemma3-270M | 3.4 | 0.54 | 0.16 |
| Gemma3-27B | 12.3 | 2.88 | 0.23 |
| Qwen2.5-72B | 7.0 | 1.85 | 0.26 |
| Qwen3-1.7B | 13.0 | 2.58 | 0.20 |

**Implication:** Definition <span class="marker">length is upstream of connectivity</span>. A model that writes longer definitions mechanically produces more in-vocabulary references, more graph edges, and a larger kernel — not because it knows more, but because it writes more.

---

# Graph 5 — OOV Rate vs. Parameter Count

## Fraction of unique definition words outside the 3,000-word vocabulary

| Family | Range | Pattern |
|--------|-------|---------|
| Gemma3 | 27.1% (270M) – 73.8% (1B) | Rises sharply at 1B; stable above that |
| Qwen2.5 | 49.7% (32B) – 70.2% (3B) | No monotone trend; Qwen2.5-32B unusually low |
| Qwen3 | 50.9% (0.6B) – 74.6% (14B) | Irregular; no family-level pattern |

## What OOV rate captures

- **High OOV:** model draws on rich vocabulary beyond the target 3k list — specialized, varied word choice
- **Low OOV:** model relies on in-vocabulary words when defining — compact, self-referential network
- Individually: $Q^2_{loo} = -0.137$ — **worse than the mean alone**

## Why it still matters

OOV rate provides the **third dimension** of the style fingerprint — the constraint that disambiguates when tpw and out-degree cannot.

<div class="bubble">
OOV rate is uninformative alone; it becomes essential as the third triangulation axis
</div>

---

# Definition Comparison: *"force"* — Gemma3

## Monotone quality improvement at every size step

| Model | Definition |
|-------|-----------|
| 270M | *"Force is a **force** that causes something to change."* |
| 1B | *"To exert power or influence."* |
| 4B | *"To make something happen, **often** against someone's will."* |
| 12B | *"To make someone or something do something against their will or resistance."* |
| 27B | *"To compel someone or something to do something against their will, often with strength."* |
| **WordNet 3.1** | *"to cause someone to do something through pressure or necessity, by physical, moral or intellectual means"* |

- **270M:** circular self-reference — "force" defined using "force"
- **4B:** correct but hedged — "often against" instead of "against"
- **27B:** correct and precise — but still omits the mechanism specification WordNet provides ("physical, moral or intellectual")
- **WordNet** length (≈14 words) matches Gemma3-27B's global average tpw (12.3)

---

# Definition Comparison: *"force"* — Qwen Families + WordNet

## Quality converges at 1.5B — then the style freezes

| Model | Definition | Issue |
|-------|-----------|-------|
| Qwen2.5-0.5B | *"Force refers to the ability to exert influence... through physical **force** or other means."* | self-ref, verbose |
| Qwen2.5-1.5B | *"To compel or press upon unwillingness."* | ✓ concise |
| Qwen2.5-7B | *"To make something happen by using strength or power."* | misses "against will" |
| Qwen2.5-72B | *"To make someone do something against their will."* | ✓ concise |
| Qwen3-0.6B | *"The act of **pushing or pushing** someone to do something."* | repetition error |
| Qwen3-8B | *"To **force** is to push someone or something to act against their will."* | self-ref |
| Qwen3-14B | *"To push or pull something strongly until it moves or changes."* | wrong sense |

<div class="bubble">
Qwen reaches acceptable quality at 1.5B — no further improvement with scale; Qwen3 is less consistent than Qwen2.5
</div>

---

# Two Distinct Failure Modes

## Same surface symptom — different root causes

<div class="two-columns">
<div class="column">

## Generation collapse

**Gemma3-270M — "desire"**

Output: *"Desire"*

The model outputs only the target word. It lacks the language generation capacity to produce a complete sentence reliably.

**Root cause:** insufficient capacity

Reflects tpw = 3.4 — the global average of 3.4 words per definition means many definitions are single words or fragments.

</div>
<div class="column">

## Instruction-following failure

**Qwen2.5-0.5B — "desire"**

Output: *"The desire to achieve something often drives our actions and aspirations."*

Fluent and grammatically correct — but uses the word in a sentence rather than defining it. The model understands "desire" yet fails the task.

**Root cause:** instruction comprehension

Reflects tpw = 12.4 — the model generates long output, but the output is usage, not definition.

</div>
</div>

<div class="bubble">
Both appear as "low quality" — but one is a language problem, the other is a task-comprehension problem
</div>

---

# Style Fingerprints Model Scale

## The regression result

Linear regression of $\log_2(\text{parameters})$ on style features, evaluated with leave-one-out cross-validation across 17 models:

| Features used | $R^2$ (training) | $Q^2_{loo}$ (held-out) |
|--------------|-----------------|----------------------|
| kernel ratio only | — | $-0.17$ |
| out-degree only | — | $-0.125$ |
| OOV rate only | — | $-0.137$ |
| tokens/word only | — | $-0.436$ |
| **out-degree + OOV rate + tokens/word** | **0.86** | **+0.71** |

Every individual feature performs **worse than predicting the mean**.
Together, $Q^2_{loo} = +0.71$ — the combination reliably predicts held-out model sizes.

<div class="bubble">
Definitional style fingerprints training recipe — Q²ₗₒₒ = +0.71 on unseen models
</div>

> $Q^2_{loo}$ = fraction of variance explained on held-out data; negative = worse than mean prediction

---

# Why Three Features — Not One

## Each feature eliminates an ambiguity the others cannot resolve

## Step 1: tokens/word separates length groups

A model with tpw ≈ 12–13 could be any of:
→ Gemma3-27B (12.3) · Qwen2.5-0.5B (12.4) · Qwen3-1.7B (13.0)

## Step 2: out-degree narrows within that group

| Model | tpw | out-degree |
|-------|-----|------------|
| Gemma3-27B | 12.3 | **2.88** |
| Qwen2.5-0.5B | 12.4 | 2.55 |
| Qwen3-1.7B | 13.0 | 2.58 |

## Step 3: OOV rate completes the disambiguation

OOV rates: Gemma3-27B **73.3%** · Qwen2.5-0.5B 63.6% · Qwen3-1.7B 55.9%

No single number can do this. <span class="marker">The fingerprint requires all three axes.</span> Kernel ratio — a single summary of the whole graph — compresses too much to discriminate.

---

# Graph Structure Is Downstream of Style

## The causal chain runs in one direction

$$\text{Training recipe} \;\longrightarrow\; \text{Definitional style} \;\longrightarrow\; \text{Graph structure} \;\longrightarrow\; \text{Kernel ratio}$$

## What each step means

| Stage | Measured by | Observable from |
|-------|-------------|----------------|
| Training recipe | — | not directly observable |
| **Definitional style** | tpw, out-degree, OOV rate | any single definition |
| Graph structure | edge density, SCC structure | requires all 3,000 definitions |
| **Kernel ratio** | largest SCC / vocabulary | requires full graph analysis |

At each step, information is transformed and partially lost.
Kernel ratio is a compressed summary of thousands of style decisions —
compression removes the variation that makes individual models distinguishable.

<div class="bubble">
Style features predict scale because they measure the cause; kernel fails because it measures the effect
</div>

---

# Family Divergence: Gemma3

## Elaboration grows monotonically with every size step

| Model | tpw | out-degree | kernel ratio | vs. WordNet |
|-------|-----|------------|-------------|-------------|
| 270M | 3.4 | 0.54 | 0.0% | ← catastrophic |
| 1B | 6.7 | 1.62 | 5.9% | — |
| 4B | 9.2 | 2.12 | 8.7% | od exceeds WN here |
| 12B | 11.0 | 2.56 | 11.9% | — |
| 27B | **12.3** | **2.88** | **12.5%** | closest to WN |
| **WordNet** | — | **1.67** | **15.45%** | reference |

## The structural paradox

Gemma3-27B has **73% higher out-degree than WordNet** (2.88 vs 1.67) yet achieves **only 81% of its kernel** (12.5% vs 15.45%).

More in-vocabulary references per definition does not automatically produce more kernel structure — *which* words reference *which* matters more than how many references exist.

<div class="bubble">
Gemma3 is the only family converging toward human lexicographic structure — but it overshoots in connectivity while undershooting in structure
</div>

---

# Family Divergence: Qwen — The Concision Plateau

## Style stabilizes at 1.5B and holds through 72B

| Model | tpw | out-degree | kernel ratio |
|-------|-----|------------|-------------|
| Qwen2.5-0.5B | **12.4** | 2.55 | 13.9% |
| Qwen2.5-1.5B | 7.8 | 1.85 | 8.4% |
| Qwen2.5-7B | 7.6 | 1.84 | 13.6% |
| Qwen2.5-14B | 8.0 | 1.94 | 7.8% |
| Qwen2.5-72B | **7.0** | **1.85** | 9.7% |

From 1.5B onward: **tpw 7.0–8.0, out-degree 1.84–1.94** — essentially unchanged across five model sizes.

## The "action" evidence

> Qwen2.5-14B: **"To do something."**
> Qwen2.5-72B: **"To do something."**

58 billion additional parameters. Zero change in definition output.

<div class="bubble">
Qwen's training recipe converges on concision by 1.5B — style encodes recipe, not parameter count
</div>

---

# The Qwen2.5-72B Paradox

## The regression's largest prediction error

The regression predicts $\log_2(\text{parameters})$ from style. For Qwen2.5-72B:

| Feature | Value | What it suggests |
|---------|-------|-----------------|
| tokens/word | 7.0 | short definitions — small/mid model |
| out-degree | 1.85 | near-WordNet connectivity — mid model |
| OOV rate | 67.8% | — |
| **Regression prediction** | | **≈ 16 B** |
| **Actual parameter count** | | **72 B** |

**Error: 2.14 $\log_2$ units** — the largest prediction error in the Qwen2.5 family.

## Why this happens

The concise, stable, vocabulary-efficient definition style was established at 14B. Scaling to 72B refined that recipe — it did not change it detectably. The regression "sees" a 14–16B model because the definition personality is identical.

<div class="bubble">
Style captures the training recipe — not the raw parameter count. A larger recipe can look identical to a smaller one.
</div>

---

# What the Pipeline Contributes

## Two measurement layers with different purposes

## Layer 1 — Style Fingerprinting *(fast, practical, cross-lingual)*

Out-degree + OOV rate + tokens/word

- Computed directly from definitions — no graph construction needed
- No benchmarks, no gold standard, no labeled data
- Works in any language by design
- **Predicts training recipe:** $Q^2_{loo} = +0.71$
- Distinguishes Gemma3's elaboration trajectory from Qwen's concision plateau

## Layer 2 — Emergent Topology *(deeper, structural)*

Kernel ratio, universal kernel, minset, NSM overlap

- Requires full graph construction across 3,000 definitions
- Cannot reliably predict scale ($Q^2_{loo} = -0.17$)
- Answers a different question: *does this model's vocabulary organize into a self-sufficient semantic core resembling WordNet?*

<div class="bubble">
The key finding is the relationship between the layers: style drives topology — measuring both reveals cause and effect in the same framework
</div>

---

# Conclusion

## What this study shows

- **Definitional style fingerprints training recipe** with $Q^2_{loo} = +0.71$ across 17 models — three features, no labels, no benchmarks
- **Graph topology is downstream of style** — kernel ratio is an emergent effect, not an independent signal
- **Family behavior diverges sharply:** Gemma3 elaborates monotonically toward WordNet; Qwen converges on concision by 1.5B and holds
- **Scale and style are not the same thing:** Qwen2.5-72B writes identically to Qwen2.5-14B — the recipe stabilizes before maximum scale
- **The pipeline provides two complementary probes:** style (the cause) and topology (the effect)

## Open questions

- Does this generalize across languages?
- Can style fingerprints detect fine-tuning vs. base model differences?
- What specific training decisions produce the Gemma3/Qwen divergence?

---

<!-- _class: lead -->

# Thank You

### Questions?

s253400@stn.nagaokaut.ac.jp
