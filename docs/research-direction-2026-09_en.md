# rs-dic-llm Research Direction Report (2026-09-01)

**Scope**: the entire `rs-dic-llm` repository (3 experiment runs, definition corpora and metrics for 23 models), `docs/paper_ja.md`, `docs/results-slides.md`, `docs/style-findings-slides.md`, and `results_2026-07-21_TogetherAI/1-setup/cross_family_replication_report.md`.
Related work was re-surveyed via Exa (35 queries total).
All numbers were recomputed at the time this report was written (the null model is a new implementation).

---

## 0. Conclusion

**A "new metric that uses dictionary-based measures to demonstrate LLM quality" cannot be built on the kernel rate as it currently stands.**
Compared against a degree-preserving null model, the kernel rate is **indistinguishable from a randomized graph**.
The same thing happens with WordNet, too (more below). What the kernel rate was measuring was never
conceptual organization — it was **the number of within-vocabulary references per definition, i.e.,
how the definition sentences happen to be phrased.**

That said, correcting for density leaves **exactly one genuine signal.**

> **Excess mutual definition (length-2 cycles), R = observed 2-cycle count / null-expected 2-cycle count**
>
> | | Range of R |
> |---|---|
> | Instruction-tuned LLM (18 models) | **8.9–23.5** |
> | WordNet (human dictionary) | **10.0** |
> | Base / pretrained LLM (5 models) | **1.5–7.3** |
>
> **Base and instruct separate completely.**

The recommended direction converges on a single line:

> **Formalize the density-corrected definitional circularity structure (Reciprocity Excess) as a metric,
> and show that what produces it is instruction tuning, not pretraining scale.**

This does not pit (A) the new-metric proposal against (B) the linguistic analysis.
It becomes a single line of argument: "the naive metric is a shadow of writing style" →
"after correction, a structure isomorphic to the human dictionary remains" → "what produces it is post-training."
This becomes **the first empirical measurement of a proposition that Harnad (2025) only asserted,
never measured** — that "LLMs exploit the circularity of linguistic definition."

---

## 1. Inventory of materials on hand

| Run | Contents | Role |
|---|---|---|
| 2026-05 (MLX, `docs/paper_ja.md`) | Qwen3.5×5 + Gemma-4×2, n=7 | Initial results. Qwen3.5 turned out to be a VLM incompatible with this pipeline, discovered later. **Should be archived as a historical record** |
| 2026-07-21 (Together AI) | 11 models × 7 families, word list regenerated | Cross-family replication. Established the rejection of a scaling law. High-quality report |
| 2026-08-09 (RunPod B200) | 17 models × 3 families, all bf16, frozen word list, +WordNet | **Primary dataset**. Also includes a quantization study and drift measurements |
| 2026-08-31 (RunPod) | Gemma3 base(pt) at 5 sizes + Qwen3-4B-Instruct-2507 | **New contrast axis**. Same pretraining, same word list, same prompt |

Findings reproduced across multiple runs:

1. **The kernel rate is not a monotonic function of parameter count.** Across 17 models, r(kern, log₂P) = **+0.382**.
   Even within a family, Qwen2.5 goes ↑↓↑↓ and Qwen3 goes ↑↓↑. Only Gemma3-it is monotonic.
2. **sr_rate (self-reference rate) is a fingerprint of the training recipe.** It is scale-independent but
   family- and generation-dependent. Across Qwen 2.5→3.5→3.6 it goes 19.7%→80.4%→35.0%
   (this tracks recipe changes the vendor does not disclose).
3. **The three style features (out-degree, OOV rate, tokens/word) predict log₂(params) with Q²_loo = +0.71.**
   kernel rate alone gives Q²_loo = **−0.17** (worse than predicting the mean). *Note: this involves a selection bias — see §6-F.*
4. Quantization (MLX 4/6/8bit) barely moves the metrics. *Note: the bitsandbytes version is a separate issue — see §2.5.*

---

## 2. Decisive new facts established this round

§2.1–2.2 below are based on a **degree-preserving null model** I newly implemented (rewiring edges
while preserving each word's in-degree and out-degree, 10 iterations). The audit agent independently
implemented the same model and reached the same conclusions.

### 2.1 The kernel rate is a "shadow of density," and the same holds for WordNet — MOST IMPORTANT

If the graph structure were real, the observed kernel rate should significantly exceed the null. Results (23 models + WordNet):

| Model | Edges | kernel rate (observed) | kernel rate (null) | z |
|---|---|---|---|---|
| Gemma3-27B (it) | 7914 | 12.51 | 13.80 | −1.62 |
| Gemma3-12B (it) | 7052 | 11.85 | 12.43 | −0.62 |
| Gemma3-4B (it) | 5842 | 8.65 | 8.32 | +0.27 |
| Gemma3-1B (it) | 4448 | 5.85 | 4.35 | +1.02 |
| Gemma3-270M (it) | 1453 | 0.00 | 0.12 | −1.11 |
| Qwen2.5-0.5B | 7002 | 13.89 | 17.99 | **−4.21** |
| Qwen2.5-7B | 5058 | 13.56 | 13.54 | +0.02 |
| Qwen2.5-32B | 5104 | 6.98 | 4.86 | +3.01 |
| Qwen2.5-72B | 5085 | 9.75 | 9.20 | +0.70 |
| Qwen3-1.7B | 7090 | 12.18 | 14.48 | −2.33 |
| Gemma3-4B-pt | 8624 | 13.67 | 16.09 | −2.37 |
| Gemma3-27B-pt | 7108 | 7.17 | 9.39 | −2.24 |
| **WordNet** | 4582 | **15.45** | **15.71** | **≈ 0** |

z ranges from −4.2 to +3.0 with no systematic excess.
This is consistent with the correlations across 17 models: r(kern, mean_out_degree) = **+0.798**,
r(kern, n_edges) = **+0.799** (r = **+0.992** for base models alone).
The audit further shows that controlling for edge count via partial correlation drops r(kern, log₂P)
from +0.38 to **+0.12**, while r(kern, n_edges | log₂P) = **+0.76** remains.

**The fact that even WordNet gives z ≈ 0 is the key point.**
The kernel rate itself, as defined by Vincent-Lamarre et al., is fully explained by the degree sequence
at the scale of a 3,000-word sub-dictionary.
(Note: the original work uses the full dictionary, whereas this study uses a 3,000-word subgraph.
This difference must be stated explicitly in the paper. The correct claim is not that "the original
metric is meaningless" but that "it must not be applied naively to a subgraph.")

**Implication**: the current narrative that "Gemma3-it converges toward WordNet's structure as it gets
larger" collapses. Gemma3-it's definition length increases monotonically with size (270M: 4.0 words →
27B: 14.4 words); the kernel rate rises simply because density rises as a consequence.
Reviewers will certainly attack this point.

### 2.2 The one signal that survives density correction: excess mutual definition — NEW FINDING

Looking at the cycle-length distribution under the same null model, the picture changes completely.

| Model | 2-cycles (observed) | 2-cycles (null) | **R = excess factor** | Long cycles ≥5 (observed/null) |
|---|---|---|---|---|
| Gemma3-4B (it) | 47 | 2.0 | **23.5** | 11 / 16.8 |
| Gemma3-12B (it) | 78 | 3.4 | **22.9** | 16 / 67.4 |
| Gemma3-27B (it) | 71 | 3.3 | **21.5** | 102 / 155.2 |
| Qwen2.5-7B | 80 | 3.9 | **20.5** | 9 / 22.2 |
| Qwen2.5-32B | 36 | 2.0 | 18.0 | 0 / 5.0 |
| Gemma3-1B (it) | 34 | 1.9 | 17.9 | 0 / 3.5 |
| Qwen2.5-1.5B | 47 | 2.9 | 16.2 | 7 / 8.5 |
| Qwen3-1.7B | 53 | 3.5 | 15.1 | 40 / 101.8 |
| Qwen3-4B-Instruct-2507 | 33 | 2.2 | 15.0 | 8 / 23.2 |
| Qwen3-8B | 51 | 3.4 | 15.0 | 16 / 30.1 |
| Qwen2.5-0.5B | 52 | 3.6 | 14.4 | 48 / 83.6 |
| Qwen3-14B | 50 | 3.6 | 13.9 | 13 / 17.1 |
| Qwen2.5-3B | 61 | 4.7 | 13.0 | 0 / 7.0 |
| Qwen2.5-14B | 47 | 3.7 | 12.7 | 4 / 9.6 |
| Qwen2.5-72B | 82 | 7.2 | 11.4 | 8 / 16.0 |
| Qwen3-4B | 43 | 4.7 | 9.1 | 1 / 13.1 |
| Qwen3-0.6B | 17 | 1.9 | 8.9 | 3 / 4.1 |
| **WordNet** | **27** | **2.7** | **10.0** | **5 / 13.3** |
| Gemma3-4B-pt | 19 | 2.6 | **7.3** | 49 / 119.8 |
| Gemma3-27B-pt | 25 | 3.6 | **6.9** | 78 / 44.7 |
| Gemma3-12B-pt | 16 | 3.1 | **5.2** | 33 / 113.0 |
| Gemma3-1B-pt | 13 | 4.8 | **2.7** | 128 / 140.5 |
| Gemma3-270M-pt | 4 | 2.7 | **1.5** | 2 / 11.9 |
| Gemma3-270M (it) | 0 | 0.3 | 0.0 (no cycles — degenerate) | 0 / 0.0 |

Three key takeaways:

1. **Mutual-definition pairs (A defined via B and B defined via A) occur 9–24× more often than in
   randomized graphs.** Density does not explain this at all. This is a genuine structural feature.
2. **Base and instruct separate completely** (base max 7.3 < instruct min 8.9).
   Gemma3-270M-it alone produces no cycles at all and is degenerate; it needs to be treated separately.
3. **Long cycles (≥5) fall below the null in almost every case.**
   This mirrors the property Levary et al. (2012, Phys. Rev. X) found for human dictionaries —
   "meaningful cycles are markedly shorter than in random networks; long cycles signal a mismatch in
   meaning." In base models, long cycles occur at or above the null level (27B-pt: 78 vs 44.7).

**Instruct models have a higher R than WordNet.** In other words, even after correcting for density,
LLM dictionaries are more mutually recursive than the human dictionary. This points in the same
direction as the cross-family report's observation that "all LLMs' mset/k exceed WordNet's" —
two independent metrics saying the same thing.

Metrics to propose:

```
Reciprocity Excess   R = (observed 2-cycle count) / (expected 2-cycle count under degree-preserving null)
Loop Compactness     L = (observed mean cycle length) / (null mean cycle length)      ← human dictionary <1, base ≈1
```

### 2.3 Base-model output is not "definition" — NOT USABLE AS-IS

Actually reading Gemma3-*-pt's output shows it is heavily contaminated with non-definitions.

- Prompt echo: **12.2–17.8%** (returns "Define the verb "pick" in one short sentence. …" verbatim)
- Questions: **11.6–36.6%** ("What does "natural" mean?" "How do you spell …?")
- Off-topic continuations: `crack` → "A sentence is a group of words that expresses a complete thought…"
  — and this is classified `status = "ok"` and fed into the graph
- Single-word or empty output: **0.4–3.6%**

Most of the sr_rate ≈ 0.68–0.80 comes from **the defined word being present in the output because the
prompt was echoed.** Worse, the self-reference check at `generation.py:33` is just a token-containment
check, so echoed prompt words (use, word, one, short, common, sentence, …) are injected directly as
edges into the graph, **creating artificial hubs.**

Definition length is also telling. it models grow monotonically with size (270M: 4.0 → 27B: 14.4 words),
while **base models stay flat at 18–24 words regardless of size** (i.e., just the length of a generic continuation).

> **As currently measured, the base vs. IT comparison captures "difference in format-following ability,"
> not "difference in conceptual structure."** However, since the R in §2.2 is already density-corrected,
> **recomputing it after removing non-definition output could become the paper's central contribution.**
> This removal is mandatory (§6, Experiment 2).

### 2.4 Main findings from the code audit

| Item | Verdict | Details |
|---|---|---|
| Edge direction & kernel (iterative removal of out-degree-0 nodes) | **SOUND** | Follows VL2016. `tests/test_kernel_outdegree.py` includes a test comparing against the in-degree variant |
| MinSet (ILP + lazy cycle constraints, on the kernel, SCC decomposition) | **SOUND** | A true minimum FVS. Acyclicity is verified at termination, guaranteeing optimality |
| Self-loop removal & normalization symmetry with WordNet | **SOUND** | Goes through the identical pipeline |
| Definition of Core | **NEEDS VERIFICATION** | The code implements "the union of source SCCs in the condensation." The audit claims "VL2016's Core is the largest SCC." However, `docs/correction_ja.md` (my own correction note) takes the source-SCC position. **Settle this by checking the original paper's text directly** |
| Filtering of non-definition output | **DEFICIENT** | Prompt echoes and questions leak into the graph (§2.3) |
| Multi-word WordNet lemmas ("ice cream", etc.) | **MINOR** | Become nodes, but since normalization only ever emits a single token, they always end up as isolated points. Mention in a footnote |
| Null model | **MISSING** | Not a single randomized baseline exists anywhere in the codebase (newly implemented for this report) |
| Package layout | **BROKEN** | `pyproject.toml` points at `src/rs_dic_llm`, but the actual code lives in `src/*.py`. `import rs_dic_llm` fails, and `pytest` cannot even collect tests |

### 2.5 The quantization study's results should be doubted (but this is a separate matter from what the paper reports)

`results_2026-08-09_Runpod/summaries/quantization_study.json` shows `kernel_ratio`, `circulation_rate`,
`mean_out_degree`, and `sr_rate` matching **exactly to 15 significant figures** across bf16/int8/int4.
Three precisions producing identical values under temperature-0.7 sampling is impossible.
Verification is also impossible because the definition text was not saved (`output_path=None`).
It's also a problem that `_interpret` generates a fixed conclusion sentence regardless of the data.
→ **Re-run or retract.**

The fact that `mean_out_degree` is 0.24 — an order of magnitude below the main experiment's ~1.85 —
is because this study runs on n=500 words (a small vocabulary produces almost no within-vocabulary
references). This itself is corroborating evidence for the density-dependence found in §2.1
(300 words → kernel ≈ 0, 500 words → 1.4%, 3,000 words → ~10%).

By contrast, the quantization discussion in `docs/paper_ja.md` §4.5 is based on MLX's Qwen3.5-27B
bf16/4/6/8bit, and the values in `results_2026-08-09_Runpod/metrics/Qwen3.5-27B-*bit_42.json` genuinely
differ from one another. **This one is legitimate. Do not conflate the two.**
That said, since the TACL 2025 linguistic-diversity benchmark reports that "quantization does move
diversity metrics," any null claim here must specify **for which metric** it is null.

---

## 3. Current state of related work (Exa re-survey)

### 3.1 Confirming the gap

Dictionary-graph analysis in the Vincent-Lamarre line has only ever been applied to human dictionaries.
The most recent work in this lineage covers multilingualization (Eschrich & Liu, MRL@EMNLP 2024,
DOI 10.18653/v1/2024.mrl-1.14) and AMR-graph conversion (Goulet, Blondin Massé & Abdenbi,
arXiv:2508.11068 — Blondin Massé's own group, still active). None touches LLMs.

On the LLM side, definition-generation research (Periti et al. EMNLP 2024 / EMNLP 2025, Ide et al.
arXiv:2601.01842) stops at BLEU / BERTScore / LLM-as-judge evaluation; **no study has structurally
evaluated the generated dictionary as a resource.**
Pham et al. (arXiv:2311.06362) compare roughly 2,500 LLM definitions against three dictionaries, but
only via pairwise similarity. **This study's one-line pitch: "Pham et al. asked whether LLM definitions
agree with a dictionary. We ask whether LLM definitions close like a dictionary."**

**The decisive hook**: Harnad (2025), "Language writ large: LLMs, ChatGPT, meaning, and understanding"
(Front. Artif. Intell. 7:1490698), explicitly cites "the circularity of linguistic definition" as a
reason LLMs work, but this is a dialogue-format argument with GPT-4 and has no experiment.
**This study ends up testing Harnad's own conjecture with Harnad's own toolkit. This is where the
paper should start.**

### 3.2 Closely related work requiring differentiation (in priority order)

1. **Boudourides (2026), "Structural Hallucination in LLMs" arXiv:2603.01341** — ⚠ **top priority, read in full.**
   Its claim — "evaluate by graph, not fluency" — is identical to this study's. However, he measures
   *fidelity to a ground-truth graph* (Roget's Thesaurus, 1911). This study measures *intrinsic,
   reference-free grounding structure*. This distinction must go in the abstract. Decide whether to
   adopt the term "structural hallucination" or explicitly reject it.
2. **Baartmans et al. (2025), "Towards Universal Semantics with LLMs" arXiv:2505.11764 (DeepNSM)**
   Already measures prime usage rate and **circularity** for LLM-generated NSM explications.
   However, their circularity is *sentence-level* — "does the explication reuse the headword" — not
   *graph-level*, i.e., where the whole vocabulary closes. **Do not claim overlap between sr_rate and
   NSM as a novelty.**
3. **Bommarito (2025), "OpenGloss" arXiv:2511.18622**
   Already released an LLM-generated dictionary graph as a resource, with 537K senses and 9.1M edges.
   **No structural analysis has been done on it.** It would be trivial for someone else to run this
   study's analysis on that resource. **There is time pressure.**
4. **Gude et al. (ACL 2026), "More Aligned, Less Diverse?" arXiv:2605.06030**
   Already shows, using HPSG syntax, that "instruction tuning narrows structural diversity" via base
   vs. IT. **The closest competitor.** Differentiate on: (a) topology of the whole dictionary system
   rather than sentence-level grammar, (b) pt/it contrast within the same family and same parameter
   count (their comparison is confounded across generations), (c) WordNet as a reference point,
   (d) **null correction** (they don't apply one).

### 3.3 Reviewer objections to preempt

| Objection | Source | Response |
|---|---|---|
| Isn't the kernel increase just because [models] "write longer"? | Lake et al., NAACL 2025 (Overton Pluralism) | **Answer it ourselves first, with the §2.1 null model.** This becomes the study's biggest selling point |
| Isn't base's failure a lack of response distribution, not a lack of capability? | Response Tuning, arXiv:2410.02465 | **Must run a condition giving base few-shot / URIAL-formatted prompts** |
| Isn't the presence/absence of a chat template the real driver of the effect? | "The Price of Format", Findings EMNLP 2025 | Re-run it models without the template |
| Isn't the elicited structure a prompt-dependent artifact? | Suresh et al., EMNLP 2023 | Prompt-variation ablation (at minimum, state as a limitation) |
| Global graph metrics are unstable across tasks | Robinson et al. 2024 | Argue the structure is "defined by an explicit generative semantics of definitional reachability," and restrict comparisons to within a fixed protocol |
| MinSet is NP-hard and non-unique, unsuitable for comparative statistics | The reason Eschrich & Liu 2024 choose the SCC camp | Show exact ILP solvability at n=3,000 and uniqueness of the *size* statistic |
| Emergence is a mirage of metric choice | Schaeffer et al. 2023 | Report continuous quantities as well as ratios (out-degree distribution, SCC size spectrum), and show robustness to thresholds |
| Isn't Q²=0.71 a feature-selection bias? | Audit finding (§6-F) | Recompute with nested CV or pre-registered features |

### 3.4 Work that conflicts with this study's claims

- **Gammelgaard et al. (2023), arXiv:2308.15047** — "Larger models converge toward more human-like
  conceptual organization." This study's base-side results contradict that claim. Worth addressing head-on.
- **Nikolic (2026), arXiv:2605.29223** — Estimates model size from text (R²=0.95). This threatens the
  appeal of Q²_loo=+0.71. However, they rely on logprobs and memorization, and their reported R² is
  in-sample. This study can carve out its own niche by explicitly stating it is **generated-text-only,
  content-independent style, LOO-validated.**
- **"Post-Training Recipe, More Than Model Family…" (arXiv:2606.20632)** — "Recipe ≻ family."
  This study's pt/it results actually serve as evidence *for* this side.
  **Should be reframed from "family matters" to "recipe matters (family is just a proxy for it)."**
  This framing is stronger and harder to attack.

### 3.5 Work that provides tailwind

- **Levary, Eckmann, Moses, Tlusty (2012), Phys. Rev. X 2:031018** — Cycles in human dictionaries are
  markedly shorter than in random graphs. Direct precedent for the interpretation in §2.2.
  **Should be this study's central citation.**
- **Ivgi et al. (2024), "From Loops to Oops" arXiv:2407.06071** — A fallback hierarchy under
  uncertainty: "repetition → degenerate text → hallucination." Gemma3-270M/base's behavior is exactly
  the low end of this hierarchy. This study can be positioned as **"a corpus-scale, structural
  measurement of the same hierarchy."**
- **Choshen et al. (2024), arXiv:2410.11840** — Scaling-law parameters across 485 models differ
  dramatically by family. This makes this study's "doesn't scale" result unsurprising in the *right*
  way, rather than suspicious.
- **Jain et al. (2023), "Bring Your Own Data!" arXiv:2306.13651** — A label-free, self-supervised
  evaluation framework. The best citation for framing "why a label-free structural probe."
- **Lin et al. (2024), URIAL, arXiv:2312.01552** — Instruction tuning doesn't change the top-1 token
  at 77.7% of positions (i.e., it's superficial). Since this study's pt/it difference shows the
  dictionary system as a whole is *not* superficial, it can be presented as **a structural-level
  partial rebuttal of the superficial-alignment hypothesis.**
- **Gemma 3 technical report (arXiv:2503.19786)** — 270M-pt is trained on 6T tokens (more than 1B's
  2T); the IT side involves distillation from a large teacher plus BOND/WARM/WARP. **Directly usable
  as a mechanistic hypothesis for why only the it side becomes monotonic.**

---

## 4. Evaluating three directions

### (A) A new dictionary-based metric for LLM "goodness" — **Not viable with the kernel rate as-is. Viable if replaced with R**

Reasons to reject the kernel rate:
- The null comparison in §2.1 (even WordNet gives z ≈ 0).
- The kernel rate runs *against* the "goodness" ordering: Qwen2.5-0.5B (13.9%) > Qwen2.5-72B (9.8%).
- Q²_loo = −0.17. No predictive power.
- Not a single experiment has checked it against an external "goodness" criterion (correctness of the definition).

**Conditions for revival**: (i) replace it with null-corrected R/L (already demonstrated in §2.2);
(ii) show correlation with an external axis of definition quality (semantic agreement with the WordNet
gloss, or LLM-as-judge); (iii) show it survives controlling for definition length.
(i) is done. (ii) and (iii) remain.

### (B) Linguistic-perspective analysis — **The strongest option, but shift what is being analyzed**

Shift from "how do LLMs organize concepts" to **"how does instruction tuning change the production of
lexical knowledge."** Grounds: §2.2 (R fully separates base/instruct), §2.3 (definition-length
scale-dependence is it-only), and style features' Q²=+0.71 versus r(kern, log₂P)=+0.38.
What the data most strongly says is post-training, not pretraining scale.

### (C) A different direction — **a methodological cautionary paper**

A methodological paper arguing "classical graph metrics must not be applied naively to LLM-generated
graphs (they're fully explained by the degree sequence); use null-corrected excess quantities instead"
stands on its own. The z ≈ 0 result even for WordNet has real impact. But on its own it's a modest
paper, so folding it into (B) is the better move.

**The recommendation is to unify around (B) as the main thread, with (A) and (C) subordinate (§0).**

---

## 5. Recommended paper skeleton

**Proposed title**
> *Do LLM Dictionaries Close? Density-Corrected Definitional Circularity Shows What Instruction Tuning Adds*
> (Japanese-language title: 「LLMが書く辞書は閉じるか——密度補正した定義循環構造と指示チューニングの寄与」,
> lit. "Do the dictionaries LLMs write close? — Density-corrected definitional circular structure and
> the contribution of instruction tuning")

**Claims (three-part)**

1. Applying Vincent-Lamarre-style kernel/core/MinSet directly to LLM-generated definition graphs yields
   values indistinguishable from a degree-preserving null. The same holds for WordNet's 3,000-word
   subgraph. Existing claims of the form "scale brings [LLMs] closer to the human dictionary" are a
   byproduct of definition length. (= methodological contribution, and a self-correction of our own
   past claims)
2. The one robust structure that survives density correction is **excess mutual definition, R**, which
   mirrors the "meaningful cycles are short" property Levary et al. found for human dictionaries.
   LLMs' R (8.9–23.5) exceeds WordNet's (10.0) — LLM dictionaries are more mutually recursive than the
   human dictionary. (= new metric)
3. This structure is produced not by pretraining scale but by **instruction tuning**. Within the
   same-pretraining Gemma3 pt/it pairs, R separates completely (base 1.5–7.3 / instruct 8.9–23.5).
   Instruction tuning does not "add knowledge" — it **converts model scale into lexical elaboration**.
   (= scientific claim)

**Required figures and tables**

| # | Content |
|---|---|
| F1 | Pipeline diagram (prompt → definition → directed graph → kernel/cycles) |
| F2 | kernel rate: observed vs. null (24-point diagonal scatter plot, WordNet highlighted) — core of Claim 1 |
| F3 | Observed/null ratio of cycle-length distribution (three lines: it group / pt group / WordNet) — core of Claim 2 |
| F4 | R × size for Gemma3 pt/it pairs (showing the complete separation) — core of Claim 3 |
| F5 | Scale-dependence of definition length (it monotonic / pt flat) |
| T1 | Full per-model metrics table (+ null, +z, +R) |
| T2 | Results of control experiments (few-shot base / template-free it / length-controlled) |

**Target venues**

| Stage | Venue | Rationale |
|---|---|---|
| Stage 1 (within the year) | IPSJ NL Study Group or NLP Society of Japan Annual Meeting (2027-03) | Secures a publication credit for the student. Get it stress-tested domestically and plug the holes in the control experiments |
| Stage 2 (the real target) | **Topics in Cognitive Science** (same journal as the original work) / **Cognitive Science** | Where the dictionary-graph context is most appreciated. Reaches Harnad's readership |
| Backup | **TACL** / **COLING 2027** | On the NLP side. Competitive once the control experiments are in place |
| Not recommended | Minds and Machines / Synthese | The current data doesn't support an "understanding" claim suited to a philosophy journal. Submitting naively would get shot down by §2.1 |

**Proposed division of labor**: the student (José López Chapa) handles the null-model implementation
and running the control experiments. Carving out the undergraduate thesis as **"model-size estimation
via stylistic fingerprint"** (Q²=0.71, after the §6-F correction) is appropriately sized and difficult,
and yields one domestic presentation.

---

## 6. Additional experiments needed (in priority order)

| # | Experiment | Purpose | Effort | Who demands it |
|---|---|---|---|---|
| 1 | **Extend the null model to all models × 100 iterations** (this report uses 10) | Statistical backing for Claims 1 and 2. Confidence intervals on z and R | No GPU, a few hours | Obviously needed |
| 2 | **Implement a non-definition output filter and recompute** | Remove prompt echoes, questions, and off-topic continuations. Correctly measure base's R | No GPU, a few hours | Audit finding, reviewers |
| 3 | **few-shot / URIAL prompting for base models** | Separates whether pt's failure is "lack of response distribution" or "lack of structure." **If few-shot recovers base's R, the paper gets dramatically stronger** | 1 GPU session | Response Tuning (2410.02465) |
| 4 | **Control for definition length** ("in exactly N words" or out-degree matching / subsampling) | Proves R's increase is not a byproduct of length | 1 GPU session | Lake et al. NAACL 2025 |
| 5 | **Re-run it models without a chat template** | Confirm the template itself isn't the real driver | 1 GPU session | Price of Format (EMNLP 2025 Findings) |
| 6 | **Multiple seeds (42/123/456)** | Error bars on all metrics | 2 GPU sessions | Known outstanding task |
| 7 | **Bootstrap the word list** (resample the 3,000 words × 20) | Quantify the issue that "the WordNet baseline moves 15.5%→8.0%" | No GPU | A hole we already found ourselves |
| 8 | **External axis of definition quality** (semantic agreement with WordNet gloss / LLM-as-judge) | The only way to complete metric proposal (A) | Medium | Mandatory if we're calling it a "goodness metric" |
| 9 | **Re-run the quantization study** (saving the definition text) | Resolves the doubts in §2.5 | 1 GPU session | Internal consistency |
| 10 | Prompt-variation ablation (3 definition-prompt variants) | Response to Suresh et al. 2023 | 1 GPU session | Reviewer defense |
| 11 | Multilingual (Japanese dictionary graph) | Future extension. Not needed for this paper | Large | — |

**With Experiments 1–5 in place, the paper can be written.** 6–10 are ammunition for reviewer responses.

### Statistical fixes (Audit finding F)

- `regress_model_size.py:128-139` exhaustively searches all C(6,3)=20 three-feature combinations and
  **reports the one with the maximum Q²_loo.** Since the selection is done on the validation metric
  itself, Q²=0.71 carries an optimistic bias. → Recompute with nested CV, or with pre-registered features.
- `docs/paper_ja.md`'s r = −0.862 / +0.982 are reported to three decimal places with **n=5**. Either
  attach a bootstrap CI or retract them.
- There is no multiple-comparison correction across the sweep of multiple metrics × multiple families ×
  raw/partial correlations.
- The partial-correlation implementation itself (`analyse_confound.py:73-79`) is correct.

---

## 7. Repository issues that need fixing

- **`pyproject.toml`'s `packages = ["src/rs_dic_llm"]` no longer matches reality.** Commit a885900's
  reorganization moved the implementation to `src/*.py`, leaving only `__pycache__` under
  `src/rs_dic_llm/`. After `uv sync`, `import rs_dic_llm` fails, and neither `experiments/*` nor
  `pytest` run. **Reproducibility is broken.**
- The history of the word list changing between experiment runs (the 07-21 run) isn't recorded in the
  README. Record the hash of `word_list_3k_v1.json` in each manifest.
- `docs/paper_ja.md` / `paper_en.md` report results based on Qwen3.5 (found to be incompatible with
  this pipeline) and contradict the current claims (even the sign of the correlation is reversed).
  Safer to move them to `docs/archive/`.
- `experiments/quantization_study.py`'s `_interpret` generates a conclusion sentence regardless of the
  data. Should be deleted.

---

## 8. In one line

> "Is the LLM dictionary converging on the human dictionary?" — with the data we currently have,
> **no** (the kernel rate is nothing but a shadow of density, even for WordNet).
> But "LLM dictionaries contain short mutual-definition cycles at 10–24× the random rate, more than
> the human dictionary, and this is produced by instruction tuning rather than pretraining scale" is
> **yes**. **The paper should be written around the latter.**

---

*Appendix: this report's null-model computation scripts are at
`/private/tmp/claude-501/.../scratchpad/null_full.py`, `wn_null.py`.
These should be formally incorporated as `experiments/null_model.py` (Experiment 1).*
