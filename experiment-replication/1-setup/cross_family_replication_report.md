# Cross-Family Replication of Dictionary-Graph Topology Metrics: Analysis Report

**Date**: 2026-07-17
**Data**: 11 models served via Together AI (serverless), 3,000-word protocol, seed 42; WordNet baseline through the identical pipeline. Raw data: `replication/defs/*.jsonl`, `replication/metrics.json`.
**Reference**: "Dictionary Graph Topology as a Probe of LLM Conceptual Structure" (Kumoi, 2026) — hereafter "the prior study" — which analyzed 5 Qwen3.5 sizes (0.8B–27B) and 2 Gemma-4 sizes on a local MLX stack.

---

## 1. Executive summary

The replication was designed to test whether the prior study's findings are facts about LLMs in general or artifacts of the two families studied. The answer is split. The **instruction-regime finding replicates emphatically and gains new structure**: self-referential definition rate is a family- and generation-level property, essentially invariant to scale and to inference stack. The **scaling findings do not generalize across families**: pooled over 7 new families, kernel ratio shows no relationship with parameter count (r = −0.171, p = 0.67), and the one new within-family size pair (gpt-oss 20B→120B) moves in the *opposite* direction to the prior Qwen3.5 result on both headline metrics. The **universal-kernel finding survives only in weakened form**: heterogeneous families share far fewer kernel words (38 across all 11 models) than sizes within one family did (92), and NSM overlap drops from 15.4% to ~8%. Finally, the replication surfaced a **methodological alarm**: the WordNet baseline itself moved from kern 15.5% to 8.0% under a regenerated word sample, meaning absolute metric values are highly sensitive to the word list and cannot be compared across runs that do not share one.

A fair one-sentence synthesis: *dictionary-graph topology is a real and measurable signature of a model, but what it measures is predominantly family/training-recipe identity — mediated by graph density — rather than parameter scale.*

---

## 2. Setup and deviations from the prior study

Protocol was held identical where possible: same prompt template, temperature 0.7, top_p 0.8, top_k 20, max_tokens 80, thinking disabled, status labels ok / self_referential / failed, same graph construction and metric definitions. Deviations that must be kept in mind when reading the results:

1. **Word list**: regenerated deterministically (WordNet + Brown ≥5, seed 42) but not byte-identical to the prior study's list. The WordNet baseline shift (Section 4.6) shows this matters a great deal.
2. **Inference stack**: Together AI serverless (FP8/FP4/MXFP4 serving quantization, per model) versus local MLX bf16/quantized. The prior study's own quantization-robustness result (±1pp kern) partially mitigates this.
3. **Thinking switches**: gpt-oss models used `reasoning_effort:"low"`, which retains a short internal reasoning trace; all other models had thinking fully disabled via verified template switches.
4. **MoE**: gpt-oss and cogito are mixture-of-experts; the scaling axis uses total parameters (20B/120B/671B), with active parameters (3.6B/5.1B/37B) noted as a caveat — active-parameter spans are much narrower than total-parameter spans.
5. **MFVS solver**: this implementation iterates lazy cycle constraints to a verified-acyclic optimum (a convergence guarantee the prior code lacked), so mset/k values here are exact.

Data quality was excellent: 10 of 11 models completed 3,000/3,000 definitions with zero or near-zero failures; gpt-oss-120b completed 2,999/3,000 after endpoint instability (503s) was handled by retry.

---

## 3. Results table

All values from `metrics.json` (this run's word list). B = total parameters (billions); "?" = undisclosed.

| Model | Family | B | kern% | core/k% | mset/k% | circ% | out_deg | sr% |
|---|---|---|---|---|---|---|---|---|
| Llama-3.3-70B | llama | 70 | **10.9** | 9.9 | 21.5 | **8.4** | **2.45** | 0.5 |
| Qwen2.5-7B | qwen2.5 | 7 | 10.1 | 21.1 | 19.6 | 4.4 | 1.51 | 19.7 |
| gpt-oss-120b | gpt-oss | 120 | 9.7 | 14.1 | 18.5 | 5.5 | 1.87 | 2.9 |
| DeepSeek-V4-Pro | deepseek | ? | 9.2 | 16.5 | 15.0 | 5.8 | 1.83 | 0.4 |
| Kimi-K2.6 | kimi | ? | 9.2 | 12.9 | 17.6 | 5.1 | 2.00 | 4.2 |
| gpt-oss-20b | gpt-oss | 20 | 8.7 | 18.7 | 20.3 | 5.1 | 1.75 | 8.2 |
| Qwen3.5-9B | qwen3.5 | 9 | 8.6 | 11.2 | 16.7 | 3.7 | 2.04 | **80.4** |
| gemma-3n-E4B | gemma3n | 4 | 8.4 | 20.9 | 20.5 | 4.3 | 1.91 | 2.0 |
| cogito-671b | cogito | 671 | 7.0 | 13.5 | 21.2 | 3.8 | 1.67 | 0.1 |
| gemma-4-31B | gemma4 | 31 | 5.3 | 21.2 | 20.5 | 2.5 | 1.42 | 0.0 |
| Qwen3.6-Plus | qwen3.6 | ? | **4.8** | 27.8 | **23.3** | 2.4 | 1.32 | 35.0 |
| **WordNet baseline** | — | — | 8.0 | 26.5 | 10.3 | 4.6 | 1.49 | 9.6 |

---

## 4. Claim-by-claim verdicts

### 4.1 "Kernel ratio decreases monotonically with model size" — **NOT CONFIRMED cross-family**

The prior study's within-Qwen3.5 result (r = −0.862, p ≈ 0.003) was the headline finding. In the new data it finds no cross-family support. Across the 8 API models with known parameter counts (spanning 4B–671B, seven families), kernel ratio versus log2(params) gives r = −0.171 (p = 0.67); the rank (Spearman) correlation is −0.048 — indistinguishable from zero. The largest model in the entire study (cogito, 671B) has a *lower* kernel ratio than models 100× smaller, while the biggest kernel belongs to a mid-sized 70B. Controlling for sr_rate does not rescue the relationship (r_partial = −0.138).

The single new within-family comparison available, gpt-oss 20B→120B, moves the wrong way: kernel ratio *rises* from 8.7% to 9.7%. Two caveats soften but do not reverse this: it is a 2-point comparison, and in active-parameter terms the pair spans only 3.6B→5.1B. Note also that the prior study's own Gemma-4 pair already rose with size (7.3%→8.1%); at the time this was attributable to the instruction-regime confound, but the new data — where nearly all families share Gemma's low-sr regime and still show no scale trend — makes that explanation insufficient.

The pooled n=15 correlation (API + prior MLX models) of r = −0.550 (p = 0.018) should be treated with suspicion: it mixes two different word lists (Section 4.6), and its significance is carried almost entirely by the five prior Qwen3.5 points. Within this run's internally consistent data, the scale effect is absent.

**Verdict**: kernel contraction with scale is real *within Qwen3.5* but is not a general law of LLMs. Family identity dominates scale.

### 4.2 "MinSet/Kernel ratio increases monotonically with size" — **NOT CONFIRMED cross-family**

The prior r = +0.982 within Qwen3.5 was the study's strongest statistic. Cross-family: r = +0.345 (p = 0.37), Spearman +0.381, and the partial correlation controlling for sr_rate collapses to +0.005. The gpt-oss pair again moves oppositely (20.3% → 18.5%). As with kernel ratio, the prior Gemma-4 pair had also contradicted the trend (23.3% → 16.2%).

One prior observation *does* extend across families: mset/k anti-correlates with kernel size (r = −0.454 across 11 models) — models with smaller kernels tend to have more irreducibly cyclic ones, echoing the prior Gemma-vs-Qwen contrast. The relationship is a topology-internal trade-off, apparently not a scale phenomenon.

**Verdict**: not a general scaling law; plausibly a within-Qwen3.5 regularity or a correlate of something that co-varies with size inside that family (e.g., training recipe maturity across the release ladder).

### 4.3 "Instruction-following (sr_rate) is a family-level property, not a scale property" — **CONFIRMED and refined**

This replication is unambiguous. Ordered by sr_rate: Qwen3.5-9B 80.4%, Qwen3.6-Plus 35.0%, Qwen2.5-7B 19.7%, gpt-oss-20b 8.2%, Kimi 4.2%, gpt-oss-120b 2.9%, gemma-3n 2.0%, Llama-70B 0.5%, DeepSeek 0.4%, cogito 0.1%, gemma-4-31B 0.0%. Three structural facts stand out.

First, the Qwen anomaly is real and enormous — 80.4% versus ≤8.2% for every non-Qwen family — and it replicated across a completely different inference stack (80.4% API vs 75.9% MLX for the same model and size), ruling out a serving artifact.

Second — a genuinely new finding — the property is **generation-level, not lineage-level**: within the Qwen line it moves 19.7% (2.5) → 80.4% (3.5) → 35.0% (3.6). Whatever causes it was introduced in the Qwen3.5 post-training recipe and partially corrected in 3.6. This sharpens the prior study's "family-level" claim into something more specific and more publishable: the negative-instruction failure is a *training-recipe fingerprint* that can be tracked across a vendor's release history.

Third, sr_rate is confirmed as decoupled from the topology metrics at the cross-family level (kern~sr r = −0.115, p = 0.73), supporting the prior study's treatment of it as a covariate rather than a driver.

**Verdict**: confirmed, and upgraded from family-level to generation-level resolution.

### 4.4 "A universal lexical anchor exists (92 words, 15.4% NSM overlap)" — **PARTIALLY CONFIRMED, substantially weakened**

Across all 11 heterogeneous models, only **38 words** appear in every kernel (union of all kernels: 672), versus 92 across the five same-family Qwen3.5 sizes. The surviving 38 skew concrete and functional (hand, eye, object, shape, hold, put, take, show, flat, top...) rather than cognitive-primitive. NSM overlap falls to 3/38 (one, people, someone) — about 8% versus the prior 15.4%, and only 4.6% of the 65 NSM primitives. A more lenient majority criterion (word in ≥6 of 11 kernels) yields 183 words with 7 NSM hits, still proportionally below the prior result. Leave-one-out analysis shows the shrinkage is not driven by one outlier model (removing any single model recovers at most 45 words), and overlap with the known sample of the prior 92-word list is minimal (3–5 of 23 checkable words).

The honest reading: the prior "universal kernel" was substantially a *family* kernel — words the Qwen3.5 recipe reuses across scales — sitting atop a smaller genuinely cross-family core. The word-list change contributes some noise here, so the 38-word figure should be re-derived on a shared list before being quoted, but the qualitative conclusion (family >> universality) is robust to that.

**Verdict**: a cross-family shared kernel exists but is much smaller and less NSM-like than the within-family result suggested.

### 4.5 "Larger LLMs converge toward the human-dictionary kernel range" — **NOT INTERPRETABLE AS STATED**

On this run's word list, the WordNet baseline (kern 8.0%) sits *inside* the LLM range (4.8–10.9%), so half the models — of all sizes — are already "below human." The prior framing assumed a stable human reference point; Section 4.6 shows the reference point itself is sample-dependent. One robust cross-family observation does emerge: **every LLM's mset/k (15.0–23.3%) far exceeds WordNet's (10.3%)** — LLM kernels are systematically more irreducibly cyclic than the human baseline, in both the prior run and this one. That, rather than kernel-ratio convergence, may be the durable human-vs-LLM contrast.

### 4.6 The WordNet baseline shift — **new methodological finding, important**

Identical pipeline, same nominal source (WordNet first-sense definitions), different 3,000-word sample: kern 15.5% (prior) → 8.0% (this run); out_deg 1.67 → 1.49; circ 7.4% → 4.6%. Since WordNet definitions are deterministic, this gap is attributable to the word sample (possibly plus minor library-version differences in lemmatization/stopwords). The implication cuts both ways: it invalidates naive comparison of absolute values between the prior tables and these, and it reveals that the pipeline's outputs carry a large sample-dependent component that the original single-sample design cannot quantify. Every within-run comparison in this report is unaffected (all 12 graphs share one word list); every cross-run comparison must be treated as ordinal at best.

This also reframes the cross-stack validation: Qwen3.5-9B (MLX kern 10.1 → API 8.6) and gemma-4-31B (8.1 → 5.3) both shifted down, directionally consistent with the WordNet baseline shift, so stack effects cannot be separated from word-list effects in this design. The regime variable (sr_rate) — which is word-list-insensitive — did replicate cleanly across stacks.

---

## 5. New observation: graph density mediates topology

The strongest correlations in the new data involve neither scale nor sr_rate but **mean out-degree**: kern~out_deg r = +0.746 (p = 0.001) and circ~out_deg r = +0.828 (p < 0.001) across 11 models. Models whose definitions recycle more in-vocabulary words build denser graphs, which mechanically retain larger kernels and more circulation. Out-degree, in turn, is a family-level stylistic property (Llama's verbose, common-word definitions at 2.45 versus Qwen3.6-Plus's terse 1.32) — visibly a function of definitional *style*, not size.

This suggests a revised causal picture worth testing in the paper: **training recipe → definitional style (verbosity, lexical choice, instruction compliance) → graph density → topology metrics**, with parameter scale acting only insofar as it correlates with style within a given family's release ladder. The prior Qwen3.5 scaling result fits this picture: out_deg fell monotonically with size within Qwen3.5 (3.73 → 2.52), so scale may have been a proxy for a style gradient inside that family.

---

## 6. Discussion

The replication does what replications should: it separates the durable findings from the local ones. The instruction-regime result now stands on eleven families and two inference stacks, with a new generation-level resolution that makes it a stronger paper contribution than before — it is, in effect, a cheap behavioral fingerprint of post-training recipes, and the Qwen 2.5→3.5→3.6 trajectory demonstrates it can track recipe changes a vendor never documents publicly.

The scaling results, by contrast, look like within-family regularities that were over-generalized by the available data. This is not a refutation of the prior study's measurements — the Qwen3.5 monotonicity is real and was honestly computed — but it is a refutation of the natural reading that kernel contraction is *what scale does to conceptual organization*. Seven families at fixed sizes show no such gradient, and the one new size pair inverts it. The paper's framing should shift from "graph topology tracks scale" to "graph topology is a family fingerprint; within at least one family it also tracks scale, for reasons plausibly mediated by definitional style."

The density-mediation observation offers a concrete mechanism and a testable prediction: any intervention that changes definitional verbosity (few-shot prompting, length constraints, style instructions) should move kernel metrics without touching model weights. If confirmed, topology metrics measure *how a model writes definitions* more than *how it organizes concepts* — a less romantic but more precise interpretation, and one that directly engages the prompt-sensitivity limitation the prior study already acknowledged.

The word-list sensitivity finding is uncomfortable but valuable, and it is fixable: the pipeline needs either the original frozen word list (for strict comparability) or, better, bootstrap resampling of word lists to put confidence intervals on every metric. An 8-point kern% swing in a deterministic baseline is larger than most of the effects under study; no cross-run claim should be published without quantifying it.

## 7. Limitations

Single seed (42) and single generation per word, as in the prior study; generation stochasticity at T=0.7 is unquantified here. The word list differs from the prior study's, contaminating all cross-run comparisons including the cross-stack validation. Parameter counts are undisclosed for three models (analyzed regime-only) and ambiguous for MoE (total vs active). Serving quantization varies per model. Only one new family contributed two sizes, so "no within-family scaling elsewhere" rests heavily on cross-sectional evidence. gpt-oss models retained a short reasoning trace. And this replication inherits the prior study's construct-validity question: definitional graphs measure elicited definitional behavior, not internal representations.

## 8. Conclusions

Confirmed: sr_rate as a family-level (now generation-level) instruction-regime property, robust across stacks; the small-kernel/denser-core trade-off; LLMs' systematically higher cyclic irreducibility versus WordNet. Not confirmed: kernel contraction and mset/k growth as general scale effects — both are family-dominated, and the sole new within-family test inverted them. Weakened: the universal kernel, which shrinks from 92 to 38 words and loses most of its NSM character once families are heterogeneous. New: graph density (out-degree) as the proximate driver of topology metrics, and severe word-list sensitivity of all absolute values.

Recommended next steps, in order of scientific payoff per effort: (1) rerun this exact battery on the prior study's frozen word list, restoring cross-run comparability and cleanly isolating the stack effect; (2) multi-seed runs (42/123/456) to put error bars on every metric; (3) a style-intervention experiment (few-shot / length-controlled prompts) to test the density-mediation hypothesis directly; (4) a third-family size ladder (dedicated endpoint or local Llama-3.2 1B/3B/8B + Phi-4) to determine whether *any* family besides Qwen3.5 shows within-family scaling; (5) bootstrap word-sampling to quantify sample sensitivity for the paper's methods section.

---

*Analysis artifacts: `replication/metrics.json` (per-model metrics + kernel/minset word lists), `replication/analysis.json` (correlation output), this report. All statistics recomputable via `replication/analyse.py`.*
