# rs-dic-llm — Roadmap to the Paper (Plan B)

**For:** José López Chapa (Pepe)
**From:** Kumoi
**Date:** 2026-09-01
**Japanese version:** [`roadmap_ja.md`](roadmap_ja.md)
**Where to start reading:** [`README.md`](README.md)

---

## 1. What changed, and why the plan changed

Your controlled 17-model study and the new base-vs-instruct run gave us enough
material for a real paper. But when I re-checked the results against a
**degree-preserving null model** — something the pipeline never had — the headline
metric did not survive:

> Randomly rewire the definition graph while keeping every word's in-degree and
> out-degree exactly the same. If the kernel is real structure, the observed
> kernel ratio should be clearly higher than this null. **It is not.** Across 23
> models the z-scores scatter between −4.2 and +3.0 with no systematic excess,
> and **WordNet itself sits at z ≈ 0.**

So `kernel_ratio` measures how densely definitions reference in-vocabulary words —
that is, definition length and word choice — not conceptual organization. This is
consistent with what you already found: r(kernel, out-degree) = +0.798, and
kernel_ratio alone gives Q²_loo = −0.17.

**But one thing does survive the correction.** Mutual definitions — A defined using
B while B is defined using A — occur **9 to 24 times more often than chance**, and
that excess separates instruction-tuned models from base models completely:

| Group | Reciprocity Excess *R* |
|---|---|
| Instruction-tuned (17 models) | **8.9 – 23.5** |
| WordNet (human dictionary) | **10.0** |
| Base / pretrained (5 models) | **1.5 – 7.3** |

No overlap. And long cycles (length ≥ 5) go the other way: instruction-tuned models
have *fewer* than chance, base models have chance-level or more. This is exactly the
pattern Levary et al. (2012) found in human dictionaries — meaningful loops are
short; long loops signal semantic drift.

**That is the paper.** Not "LLM dictionaries approach human dictionaries as they
scale" (false), but "LLM dictionaries contain an above-chance short-circularity
structure, they have *more* of it than WordNet does, and instruction tuning — not
pretraining scale — is what creates it."

Full analysis: [`../research-direction-2026-09_en.md`](../research-direction-2026-09_en.md)

---

## 2. The claim we are going to defend

**Title (working)**
> *Do LLM Dictionaries Close? Density-Corrected Definitional Circularity Shows What
> Instruction Tuning Adds*

**Three steps. Each step is one results section.**

1. **Classical dictionary-graph metrics do not survive a null model.**
   Applying Vincent-Lamarre's kernel / core / MinSet directly to LLM-generated
   definitions produces values indistinguishable from a degree-preserving null —
   and the same is true for a 3,000-word subgraph of WordNet. Any claim of the form
   "bigger models converge on human dictionary structure" is an artifact of
   definition length.
   *This includes correcting our own earlier claims. We say so openly — reviewers
   respect a paper that audits itself, and it inoculates us against the objection.*

2. **After density correction, one structure remains: reciprocity excess.**
   *R* = (observed 2-cycles) / (expected 2-cycles under the degree-preserving null).
   LLMs score 8.9–23.5; WordNet scores 10.0. LLM dictionaries are *more* mutually
   recursive than the human one, even after correcting for density.

3. **That structure is produced by instruction tuning, not by scale.**
   Gemma3 pt/it pairs at matched parameter counts separate completely on *R*.
   Instruction tuning does not add knowledge; it converts model scale into
   lexical elaboration (it: 4.0 → 14.4 words per definition as size grows;
   pt: flat at 18–24 words regardless of size).

**One important honesty constraint on step 3.** Right now the base-model outputs are
not really definitions: 12–18% are verbatim prompt echoes and 12–37% are questions.
Until E2 below is done, the pt/it contrast measures *format compliance*, not
structure. We must fix this before we can make claim 3. If after filtering the
separation disappears, that is also a publishable finding — we report what we find.

---

## 3. Experiments — do them in this order

Each task lists what to build, what to output, and **what "done" means**. Do not
skip ahead: E1 and E2 need no GPU and gate everything else.

### E1 — Null model at full scale · no GPU · ~half a day

`experiments/null_model.py` already exists (I wrote it while auditing; read it
first — it is short).

- Run with `R=100` replicates over all 23 models **plus** WordNet.
- Output `results/null_model.json` with, per model: observed and null mean/SD for
  `kernel_ratio`, `circulation_rate`, 2-cycle count, long-cycle (≥5) count; plus
  the z-score and *R*.
- Add bootstrap 95% CIs on *R* (resample the null replicates).

**Done when:** every model has *R* with a CI, and you can state whether the base
and instruct CIs overlap. Expect this to take hours, not minutes — `simple_cycles`
on the denser graphs is slow. Run it in the background.

### E2 — Non-definition filter · no GPU · ~2 days

This is the one that decides whether claim 3 stands.

- Write `src/quality_filter.py` classifying each JSONL record as one of:
  `definition` / `prompt_echo` / `question` / `off_topic` / `fragment`.
  Start with rules (does the output contain a span of the prompt? does it start
  with an interrogative? is it under 3 tokens?), then check them.
- **Validate the classifier by hand.** Sample 100 records from each of
  Gemma3-27B-pt, Gemma3-4B-pt, Gemma3-27B (it), Qwen2.5-0.5B; label them yourself;
  report precision and recall per class. A filter you have not validated is not
  evidence.
- Note the trap in the current code: `generation.py` marks prompt echoes as
  `self_referential`, and `graph_build.py` **still feeds them into the graph**, so
  template words (`use`, `word`, `one`, `short`, `common`, `sentence`) become
  artificial hubs. Fix that path.
- Rebuild every graph from filtered definitions and re-run E1.

**Done when:** you can show the *R* table before and after filtering, with the
hand-labelled precision/recall of the filter, and state plainly whether the
base/instruct separation survives.

### E3 — Few-shot / URIAL prompt on base models · 1 GPU session

**This is the single most valuable experiment left.** A reviewer will say: base
models fail because they have no response distribution, not because they lack
structure (Response Tuning, arXiv:2410.02465).

- Take the 5 Gemma3 `-pt` models. Give them a 3-shot definitional prompt
  (the skeleton in `docs/study_guide/en/04_future_plan/02_experiment_plan.md` is a
  fine starting point) instead of the zero-shot instruction.
- Everything else identical: same 3,000-word list, same seed, same decoding.
- Recompute *R* after the E2 filter.

**Done when:** you can answer one question with a number — does base-model *R* move
into the instruct range (8.9+) or stay below it?

- If it **stays low**: instruction tuning creates the structure. Strong claim 3.
- If it **rises**: the structure was latent in pretraining and instruction tuning
  only exposes it. Weaker claim 3, but a *more interesting* paper — write it that way.

Either outcome is a result. Do not root for one.

### E4 — Length control · 1 GPU session

Reviewers will ask whether *R* just tracks verbosity (Lake et al., NAACL 2025).

- Two approaches, do the cheaper one first:
  (a) **Post-hoc matching** — subsample definitions so that the out-degree
      distribution matches across the models being compared. No GPU needed.
  (b) **Prompt control** — regenerate with an explicit length constraint
      ("in about 12 words") so tokens/word is roughly equal across sizes.
- Recompute *R*.

**Done when:** you can show *R* for a length-matched comparison and state whether
the base/instruct gap survives.

### E5 — Instruct models without the chat template · 1 GPU session

The chat template alone can drive structural effects ("The Price of Format",
Findings of EMNLP 2025). Our it-models get a template and our pt-models do not, so
this is a real confound.

- Re-run 3 instruct models (e.g. Gemma3-4B, Gemma3-27B, Qwen2.5-7B) with the raw
  prompt string, no chat template applied.
- Recompute *R*.

**Done when:** you can say whether *R* stays high without the template.

### Reserve — only after E1–E5 are done

| # | Experiment | Why |
|---|---|---|
| E6 | Multi-seed (42 / 123 / 456) | Error bars on every metric |
| E7 | Word-list bootstrap (×20) | Quantifies the 15.5% → 8.0% WordNet baseline swing you found |
| E8 | Definition quality axis (WordNet gloss similarity or LLM-as-judge) | The only way to claim *R* measures "goodness" |
| E9 | Re-run the bitsandbytes quantization study, saving definitions | The current file reports identical values to 15 significant figures across bf16/int8/int4 — it cannot be reported as-is |
| E10 | Prompt-variation ablation (3 prompt templates) | Answers Suresh et al. (2023) |

**What NOT to do:** do not add more model families or more scale points. We have 23
models and the scale axis is not where the signal is. More models will not make the
paper stronger; the five controls above will.

---

## 4. Statistical corrections to make

These are bugs in the analysis, not in the pipeline. Fix them while E1–E2 run.

1. **`experiments/regress_model_size.py` selects on the validation metric.**
   It enumerates all C(6,3) = 20 three-feature combinations and reports the one
   with the highest Q²_loo. That makes Q² = 0.71 optimistically biased. Fix by
   either (a) pre-registering the three features and reporting only those, or
   (b) nested cross-validation (inner loop selects, outer loop scores).
2. **n = 5 correlations reported to three decimals.** The r = −0.862 / +0.982 in
   `docs/paper_ja.md` come from five Qwen3.5 points. Attach bootstrap CIs or drop them.
3. **No multiple-comparison control.** We scan many metrics × families × raw/partial
   and highlight the monotone ones. Apply BH-FDR when reporting a family of tests.
4. Partial correlation in `analyse_confound.py` is implemented correctly — leave it.

---

## 5. What to learn (and in what order)

You do not need all of this before starting. Learn each item just before the task
that uses it.

### Before E1 — null models and random graphs

- **Degree-preserving randomization / the configuration model.** Why comparing a
  measurement to a random graph *with the same degree sequence* is the standard way
  to show structure is real. Newman, *Networks* (2nd ed.), ch. 12–13.
- **z-scores and bootstrap confidence intervals.** How to say "this is more than
  chance" with a number rather than an adjective.
- Re-read `experiments/null_model.py` line by line and make sure you can explain
  what `nx.directed_edge_swap` preserves and what it destroys.

### Before E2 — the pipeline's own internals

- Read `src/graph_build.py`, `src/normalize.py`, `src/generation.py` end to end.
  Specifically: trace what happens to a record whose `status` is
  `self_referential`, and confirm for yourself that prompt-echo text becomes edges.
- **Precision and recall** for your own classifier. You will be asked "how do you
  know the filter is right?" — the answer must be a hand-labelled sample.

### Before E3 — instruction tuning

- **What instruction tuning actually changes.** Lin et al. (2024), URIAL,
  arXiv:2312.01552 — 77.7% of token positions keep the same top-1 token after
  alignment; the shifts are stylistic. Our result complicates this at the level of
  a whole dictionary, which is why it is interesting.
- **Chat templates.** What `tokenizer.apply_chat_template` does, why base models
  have none, and why our commit `ef1c130` had to add a fallback.
- **Why base models echo prompts.** Response Tuning, arXiv:2410.02465 — base models
  lack an established response distribution, not the underlying capability.

### Before writing — the argument you are joining

Read these in this order. For each, extract the one thing named.

| # | Paper | Extract |
|---|---|---|
| 1 | Vincent-Lamarre et al. (2016), *Topics in Cognitive Science* 8(3), DOI 10.1111/tops.12211 | Re-read the Core definition. Our code uses "union of source SCCs of the condensation"; the audit claimed the original says "largest SCC". **Settle this from the original text and tell me the answer.** |
| 2 | **Levary, Eckmann, Moses, Tlusty (2012), Phys. Rev. X 2:031018** | The central citation now. Meaningful loops in human dictionaries are much shorter than random. This is the precedent for *R* |
| 3 | Blondin Massé et al. (2008), TextGraphs-3, arXiv:0806.3710 | Grounding set = minimum feedback vertex set; the NP-hardness result |
| 4 | **Harnad (2025), "Language writ large", Front. Artif. Intell. 7:1490698** | He names "the circularity of verbal definition" as a reason LLMs work — and never measures it. This is our opening paragraph |
| 5 | Lin et al. (2024), URIAL, arXiv:2312.01552 | The superficial-alignment picture we are complicating |
| 6 | Ivgi et al. (2024), "From Loops to Oops", arXiv:2407.06071 | The fallback ladder (repetition → degenerate text → hallucination). Gemma3-270M and the base models sit on its lower rungs |
| 7 | Lake, Choi, Durrett (2025), NAACL 2025 | The "it's just length/aggregation" objection, in its strongest form. E4 answers it |
| 8 | Boudourides (2026), arXiv:2603.01341 | "Structural hallucination" — closest competing framing. Read in full; we must state our difference in the abstract |
| 9 | Baartmans et al. (2025), DeepNSM, arXiv:2505.11764 | They already measure per-sentence circularity and NSM prime usage. We must not claim `sr_rate` or NSM overlap as novel |
| 10 | Gude et al. (2026), ACL 2026, arXiv:2605.06030 | "Instruction tuning narrows structure", done with HPSG grammar. Our nearest competitor — know exactly how we differ |
| 11 | Schaeffer et al. (2023), arXiv:2304.15004 | The "emergence is a metric artifact" critique. Report continuous quantities alongside ratios |

### Skills worth building along the way

- Running long jobs in the background and checking on them, rather than watching a
  terminal. E1 and E3 both take hours.
- Writing a figure that makes one point. Each of F2, F3, F4 below has exactly one job.
- Reporting a negative result cleanly. Half of this paper is "our earlier claim was
  wrong, here is why, here is what is true instead." That is good science, and
  learning to write it without either hiding it or over-apologizing is a real skill.

---

## 6. Figures the paper needs

| # | Figure | The one thing it shows |
|---|---|---|
| F1 | Pipeline diagram: prompt → definitions → directed graph → kernel / cycles | How the measurement works |
| F2 | Observed vs null kernel ratio, 24 points, diagonal line, WordNet highlighted | Claim 1: the classical metric is at chance |
| F3 | Cycle-length distribution, observed/null ratio: it group / pt group / WordNet | Claim 2: short cycles in excess, long cycles suppressed |
| F4 | *R* × model size for the Gemma3 pt/it pairs | Claim 3: complete separation |
| F5 | Definition length vs model size (it monotone, pt flat) | The mechanism behind claim 3 |
| T1 | Full metric table: observed, null, z, *R*, CI | Everything, for the appendix |
| T2 | Control experiments E3/E4/E5 | The confounds are handled |

---

## 7. Schedule

| Period | Work | Output |
|---|---|---|
| 2026-09 | E1, E2, statistical fixes (§4) | `results/null_model.json`, `src/quality_filter.py`, filter validation report |
| 2026-10 | E3, E4, E5 (GPU sessions) | Control results; a decision on claim 3 |
| 2026-11 | Figures F1–F5, table T1–T2 | Full results set |
| 2026-12 | Draft (English) | Complete manuscript draft |
| 2027-01 (early) | **NLP2027 / IPSJ-NL submission** | Domestic paper submitted |
| 2027-03 | Presentation, feedback | Reviewer comments |
| 2027-04 onward | Extend to *Topics in Cognitive Science* | Journal submission |

**Target venues.** First the domestic conference (NLP2027 annual meeting or IPSJ
NL-SIG) — that secures your record and gets the controls stress-tested. Then
*Topics in Cognitive Science*, the journal that published Vincent-Lamarre et al.,
where this framing lands with the right readers. TACL or COLING 2027 are the
alternatives if the controls come out clean. **Not** Minds and Machines or Synthese
— the current data does not support a philosophical claim about "understanding",
and §1 of the report would sink it.

**Your thesis.** I suggest carving out "predicting model scale from definitional
style" (the Q² = 0.71 result, after the §4-1 fix) as your undergraduate thesis and
a separate domestic talk. It is self-contained and the right size.

**Time pressure, for real.** OpenGloss (arXiv:2511.18622) is a public 537k-sense
LLM-generated dictionary graph with no structural analysis attached. Someone can run
our analysis on it in a weekend. We should not sit on this for a year.

---

## 8. Repository fixes to make first

Small, but they block everything else.

1. **The package is broken.** `pyproject.toml` declares `packages = ["src/rs_dic_llm"]`,
   but after the reorganization the sources live at `src/*.py` and
   `src/rs_dic_llm/` contains only stale `__pycache__`. `import rs_dic_llm` fails,
   so `experiments/*` and `pytest` do not run from a clean checkout. Fix the
   packaging or move the sources back — either is fine, but pick one today.
2. Record the hash of `word_list_3k_v1.json` in every run manifest, so a word-list
   change can never silently invalidate a comparison again.
3. Move `docs/paper_ja.md` and `docs/paper_en.md` to `docs/archive/`. They are based
   on Qwen3.5, which turned out to be incompatible with this pipeline, and their
   central correlation has the opposite sign to our current results. Keep them as a
   record; do not let anyone cite them.
4. Delete `_interpret` in `experiments/quantization_study.py` — it generates a
   conclusion sentence regardless of the data.

---

## 9. How to report progress

For each experiment, when you bring it to me, have these four things:

1. **The number**, with its uncertainty.
2. **The null or control it is compared against** — a number without a comparison is
   not evidence. This is the whole lesson of this round.
3. **What would have falsified it.** If you cannot say what result would have made
   you abandon the claim, the experiment was not a test.
4. **The command that reproduces it**, and where the output file is.

If a result contradicts the plan above, that is the most valuable thing you can
bring me. Bring it early.
