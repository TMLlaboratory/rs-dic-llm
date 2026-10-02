# Research Audit

Reconstruction of what the repository shows was actually done, compared with what the
roadmap, the direction report and the code say was intended. Date: 2026-10-01.
This document reports findings. It does not resolve them: every item marked *decision needed*
goes to the researcher and advisor (see `DECISION_LOG.md`).

## 0. How this audit was done

- Read: all code in `src/`, `src/rs_dic_llm/`, `experiments/`, `tests/`; the roadmap; the
  direction report (Artifact); `docs/correction_en.md`; the labeling workbook.
- Ran (CPU only, no GPU, no network): rebuilt all 65 graphs from the stored definitions; ran
  pytest; compared the two R definitions; tested rewiring sensitivity; checked report numbers
  against stored metrics. Scripts and recorded outputs: `research/audit_scripts/`.
- Not done: no model generation, no web lookups (references are not checked), no review of
  `docs/study_guide/`, `logs/`, `AA_semi-resources/`, `results_2026-07-21_TogetherAI/`.
- Interpretation of any result is left to the researcher. Numbers below from 10-20 null
  replicates are diagnostics, not results; the 100-replicate run is E1.

## 1. Verified facts

| Item | Result |
|---|---|
| Definitions per model | 23 models x 3,000 records, same word list (sha256 `bd4de5c6...359363`), 2,750 unique lemmas. |
| Report Table 1, observed columns | All 11 rows (edges, observed kernel %) equal the stored metrics JSONs exactly. The null and z columns come from the advisor's run and are not in the repo. |
| r(kernel, mean out-degree) = +0.798, r(kernel, edges) = +0.799 | Reproduced exactly for the 17 instruct models of the 08-09 run, **including Gemma3-270M**. Without it: +0.640 (n=16). Base models only: +0.992 (n=5). |
| Report Table 2 | Mean words reproduced (19.1, 23.7, 18.8, 18.3, 14.4). The "questions" column equals the share of records containing a `?` anywhere (36.6, 32.9, 11.6, 16.3 %), a crude rule. The "prompt echo" column could not be reproduced exactly (a phrase search gives 16.1, 17.8, 16.5, 15.3 % vs the report's 15.3, 16.5, 15.4, 12.2 %); no script for it is in the repo. |
| Headline R values | With 20 replicates: Gemma3-27B 21.2 (report 21.5), Gemma3-27B-pt 6.9 (6.9), Gemma3-4B 21.4 (23.5), Gemma3-4B-pt 6.7 (7.3), Qwen2.5-72B 11.2 (11.4), WordNet 10.8 (10.0). Consistent within replicate noise. |
| E1 (100 replicates) versus the report | Instruct 7.8-32.6 (report 8.9-23.5), base 2.1-7.5 (1.5-7.3), WordNet 9.1 (10.0). Per model the difference is -19 % to +41 % (Gemma3-4B 32.6 vs 23.5, Gemma3-1B 25.2 vs 17.9, Gemma3-4B-pt 5.9 vs 7.3), as expected from 10 replicates. Kernel z from -3.7 to +2.2 (report -4.2 to +3.0). The report's two quoted long-cycle figures reproduce: Gemma3-12B 16 observed vs 75 null (report 67), Gemma3-27B-pt 78 vs 57 (report 45). |
| Kernel z | Qwen2.5-0.5B z = -4.9 (3 replicates; report -4.2). |
| 2-cycle counting | `nx.simple_cycles` counts each mutual pair once; `cycles_2` equals the number of mutual pairs on all 9 graphs tested. (The docstring of `reciprocity_excess` says two, which is wrong; the code is consistent.) |
| Tests | 12 of 12 passed with `src/` on `PYTHONPATH` at the time of the audit; 55 pass now, after `tests/test_extraction.py` was added. |
| Kernel and Core code | Kernel removes out-degree-0 nodes; Core = union of source SCCs of the condensation. Both agree with `docs/correction_en.md`. Not checked against the original paper. |
| Workbook for E2 | Same 100 words in all 23 tabs (random sample, positions 36-2,911 of the list); every output equals a stored record; 12 of 100 rows per tab are lemmas listed under two parts of speech; 3 blank outputs (Gemma3-270M). |

## 2. Findings

Severity: High = can change a paper claim; Medium = must be handled before writing;
Low/Info = record and move on.

### F1 (High, decision needed) Two different definitions of R; E3/E4/E5 use the wrong one for comparison

- `experiments/null_model.py`: R = observed mutual pairs / mean over degree-preserving
  rewirings. This is the R of the report and the one in `PROJECT_CONTEXT.md`.
- `src/rs_dic_llm/metrics/scc.py::reciprocity_excess`, called by `compute_all_metrics`:
  an analytic configuration-model approximation. A factor 2 is missing: the denominator counts
  ordered pairs, the numerator unordered pairs. With the factor, the analytic expected number of
  mutual pairs matches the rewiring null on some graphs (Gemma3-27B 3.16 vs 3.35, Gemma3-4B-pt
  2.87 vs 2.85) but is 2-5 times too low on others (Qwen2.5-72B 1.52 vs 7.30, E3 Gemma3-27B-pt
  2.14 vs 5.40, WordNet 1.44 vs 2.50). It is stored as `reciprocity_excess` in every E3/E4/E5
  metrics JSON.
- So the stored value is not a rescaling of R. Same graphs, 20 replicates:

| graph | R (rewiring null) | R_analytic (stored) | analytic / rewiring |
|---|---|---|---|
| main Gemma3-27B | 21.2 | 11.3 | 0.53 |
| main Gemma3-27B-pt | 6.9 | 5.2 | 0.76 |
| main Gemma3-4B | 21.4 | 14.5 | 0.68 |
| main Gemma3-4B-pt | 6.7 | 3.3 | 0.50 |
| main Qwen2.5-72B | 11.2 | 27.0 | 2.41 |
| WordNet | 10.8 | 9.4 | 0.87 |
| E3 Gemma3-27B-pt | 14.4 | 18.2 | 1.26 |
| E4 Gemma3-27B | 33.6 | 22.4 | 0.67 |
| E5 Qwen3-0.6B | 1.3 | 0.7 | 0.55 |

- Impact: the stored E3 (9.0-23.1), E4 (12.4-38.7) and E5 (0.7-26.1) `reciprocity_excess`
  values cannot be compared with the 8.9 / 23.5 thresholds or with the main-run R. The
  "IN INSTRUCT RANGE" / ">= 8.9" tags printed by the three scripts used these values and are
  not valid. The August metrics files have no R at all.
- Decided (D004, D008): R is recomputed with the rewiring null on all E3/E4/E5 graphs (E1),
  and only the rewiring R is reported. New runs store the analytic value as `R_analytic`
  (code changed 2026-10-01); existing JSONs are not edited, and their `reciprocity_excess`
  must be read as `R_analytic`. `docs/runpod-*.md` still tell the reader to print
  `reciprocity_excess` from the summaries: stale for this purpose.

### F2 (High, decision needed) E3 differs from the main base run in extraction, not only in prompt

- Main zero-shot runs store the output cut by `_first_sentence`; E3 uses
  `_extract_fewshot_definition` (cuts at the next `Q:` and at the first sentence).
- Stored definitions: Gemma3-27B-pt main: 68.0 % single-sentence, 19.1 words, 15.3 % contain a
  newline; E3: 100 %, 11.2 words, 0 %. Gemma3-4B-pt: 53.7 % / 23.7 words / 16.8 % versus
  100 % / 10.9 words / 0 %. `sr_rate` falls from 0.68-0.80 to 0.04-0.27.
- So the change in R between main and E3 mixes the effect of few-shot prompting with the
  effect of shorter, single-sentence text. R is known to depend on definition length
  (claim 1).
- Converged reading, not a result (unfiltered, one run per condition): R of the base models is
  2.1-9.0 zero-shot and 4.7 / 22.3 / 23.5 / 30.9 / 28.0 with the few-shot prompt (270M to 27B),
  against 42.5 / 28.0 / 25.7 / 22.3 for the instruct models of 1B-27B (270M-it is degenerate).
  At 5 x swaps the few-shot values were 4.5 / 17.6 / 20.4 / 22.8 / 17.1. If this
  survives E2 and uniform extraction, claim 3 changes from "instruction tuning creates the
  structure" to "the structure is latent in pretraining and exposed by format".
- Outcome of the filtered runs (D024, 2026-10-01): the E3 few-shot base R is within a factor 2 of the instruct R at
  four of four sizes under the unfiltered, the default-filter and the strict-filter graphs (factors 1.12-1.91), while the
  zero-shot Gemma3 pairs still separate by 3.3-12.2x. The reading "latent in pretraining and exposed by format" is
  supported; why the zero-shot gap exists is the question of D025.
- Hand check of the E3 outputs: D027 (2026-10-02). 100 E3 outputs of four base models, labeled by the researcher blind to the
  model and to the filter, read once by a rule fixed beforehand. Result 2026-10-02: 100 of 100 labeled definition (95 % interval 96-100 %), rule met; the E3 outputs are definitions in form (accuracy was not judged).
- Action: apply one extraction rule to every model before filtering (decision D009) and
  recompute. Raw model output was not saved (only the extracted `definition`), but the stored
  text starts at the beginning of the output, so a uniform first-line / first-sentence cut is
  possible after the fact.
- Decided (D009): the uniform cut is the primary analysis and the stored text a sensitivity
  row. The cut rule was built on 2026-10-01 (`src/rs_dic_llm/extraction.py`, see F3).

### F3 (High, decision needed) `_first_sentence` returns multi-line text for many base outputs

- `generation.py::_first_sentence` tries the separators `".\n"`, `"\n"`, `". "` in that order
  and cuts at the first separator *of the first kind that occurs anywhere*. An output that
  contains a newline early and `".\n"` later is cut at the later point, keeping the newline.
- Effect in the stored data (non-empty definitions, 5 base models): 32-47 % are
  multi-sentence and 12-17 % contain newlines (examples: multiple-choice questions, essay
  prompts); the instruct models checked (Gemma3-27B, Qwen2.5-72B, Gemma3-270M) have 0-0.1 %.
  `normalize` tokenizes all of it, so off-topic vocabulary becomes edges (Gemma3-4B-pt has
  the most edges of all 23 models, 8,624).
- The roadmap attributes the base-model problem to prompt echoes and questions. Multi-sentence
  capture is a separate, additional cause.
- Decided (D009): part of the E2 preprocessing. The obvious fix (cut at the earliest
  separator) would break list-formatted outputs: `1. Habit is ...` would be cut to `1.`. The
  new rule must skip list markers (`A.`, `1.`, `I.`). `_first_sentence` in `generation.py` is
  fixed only when a GPU run is planned.
- Built 2026-10-01: `src/rs_dic_llm/extraction.py` (tests in `tests/test_extraction.py`, effect
  in `audit_scripts/7_extraction_effect.py`). Words are removed from 36.6 % of base-model
  records and 15.5 % of E5 records, from almost none of the instruct, E3 and E4 records; base
  graphs lose 29-39 % of their edges and E5 graphs 0-54 %. Approved in D019.

### F4 (High) E5 outputs are raw continuations, not definitions

- Without the chat template, small instruct models continue the prompt: Qwen2.5-1.5B
  "Residential means ... Now, write an essay of at least 500 words...", Qwen3-0.6B
  "Also, use the word ... as a noun, not a verb.", Gemma3-270M "A.".
- Mean words per record: Qwen2.5-1.5B 35.8, Qwen2.5-0.5B 28.8, Qwen3-0.6B 24.8,
  Gemma3-270M 23.4. Edges: Qwen2.5-1.5B 16,211 (its main-run graph has 5,075).
- `ok_rate` counts only statuses, so 1.0 does not mean clean definitions.
- Impact: E5 conclusions about the template cannot be read before E2 filtering; the answer may
  differ by model size and family (R_analytic ranged from 0.7 to 26.1).
- Converged R (unfiltered, one run, 2026-10-01; `audit_scripts/outputs/13_controls_vs_main.txt`):
  Gemma3 4B / 12B / 27B keep their R without the template (ratio to the main run 1.28 / 1.03 /
  0.92; 1B 0.53); Qwen3 0.6B / 1.7B / 4B / 14B fall to 0.12 / 0.12 / 0.44 / 0.33 of it (R 1.1,
  2.2, 5.5, 6.1) with 21-27 words per output against 9-15 in the main run, and the first six
  outputs of each are mostly the prompt's own instructions continued ("Use only one sentence.").
  Median ratio 0.63, range 0.12-2.61, median size of the change a factor 1.9. A count of
  non-definitions in E5 would need its own labeling; none exists.

### F5 (Medium, decision needed) Null model settings

- Null replicate counts: the report used 10. The null mean of mutual pairs is small
  (2.2-7.3) with SD 1.3-2.2 across replicates, so at 10 replicates the standard error of the
  null mean is 6-21 % of the mean, and R carries the same relative noise (for example 23.5
  in the report versus 21.4 here for Gemma3-4B). E1 uses 100 replicates and adds bootstrap
  CIs (which cover null sampling only, not variation of the generated definitions).
- Partial randomisation is silent: `null_model.rewire` catches `NetworkXAlgorithmError`
  (swap budget not met) and keeps the partly shuffled graph. On E5 Qwen3-0.6B all 20 of 20
  replicates hit it (22 s per replicate); main graphs had 0 failures in 20. E1 records every
  failure.
- Number of swaps: the null mean keeps falling with more swaps (Gemma3-27B: 4.83 at 2E,
  3.42 at 5E, 3.00 at 15E; Qwen2.5-72B: 11.92, 7.33, 6.67; 12 replicates each). If the 15E
  values are right, R at 5E is about 10-14 % too low (conservative). Not confirmed at this
  replicate count.
- `R = obs / max(null mean, 0.5)`: the 0.5 floor is arbitrary; E1 reports when it applies.
- Decided (D007): E1 at 5E is the run of record; E1b repeats the 24 main graphs at 15E. Result:
  on the 14 graphs valid at both, R is a median 13 % higher at 15E (range -20 % to +70 %,
  WordNet 9.1 to 15.4), and 10 of 24 graphs do not reach 15E swaps within the try budget
  (registry, E1b; D020). E1c then showed that the null mean settles within 4-24 x E and that 5E
  left R too low by 12-90 % on the six graphs tested (median 24 %, WordNet 9.1 to 17.3; four picked
  because R moved most, so the typical effect is smaller); acceptance is 3-12 %
  on those graphs and as low as 1 % (E5 Qwen3-0.6B) or 0.05 % (degenerate graphs) on others, so
  the try limit has to scale with the requested swaps. E1d (converged setting, 23 main graphs,
  no swap failures) then measured the typical effect: R a median 19 % higher than at 5E (range
  -14 % to +73 %, WordNet 9.1 to 15.7), instruct 9.4-42.5, base 2.1-9.0.

### F6 (Medium, mitigated) `experiments/null_model.py` as written would not produce the E1 output

- Default glob `data/definitions/*_42.jsonl` matches 33 files (23 paper models + 8 Qwen3.5 +
  2 Gemma-4); the roadmap asks for 23 + WordNet.
- It writes `results/null_model.json`, but `results/` does not exist and the script does not
  create it: the run would crash after hours of computation (per-model JSON lines are printed
  to stdout first).
- `cycles_long` counts lengths 5-7 only (`CYCLE_BOUND = 7`), although the roadmap and report
  say ">= 5".
- Replicate seeds come from one `random.Random(0)` shared across models, so results depend on
  the order of files.
- It imports the flat `src/` copy of the graph code, not `rs_dic_llm`.
- Mitigation: `experiments/e1_full_null.py` (new; `null_model.py` is unchanged) imports the
  audited functions, uses explicit model lists, per-replicate deterministic seeds, resumable
  output, failure flags and saves every graph. Decided (D015): it is the E1 of record;
  confirmed by the advisor (reported by the researcher, 2026-10-02).

### F7 (Medium, decision needed) Claim 1 is wider than the null tests

- The roadmap states claim 1 for "kernel / core / MinSet". The null model tests kernel ratio,
  circulation rate and cycle counts. Core and MinSet are not compared to any null.
- Decided (D012): claim 1 is narrowed to kernel ratio and circulation rate; Core on the null
  replicates only if time allows (MinSet by ILP is expensive).

### F8 (Medium) Two divergent copies of the source

- `src/*.py` (July) and `src/rs_dic_llm/*.py` (September, commit `6546af4`) differ in
  `analysis.py` (adds R_analytic), `config.py` (adds INSTRUCT/BASE lists), `generation.py`
  (template/prompt/extractor options), `hf_client.py` (`use_template`), `metrics/scc.py`
  (adds `reciprocity_excess`). `graph_build.py`, `normalize.py`, `sampling.py`,
  `wordnet_baseline.py`, `kernel_core.py`, `minset.py`, `nsm.py` are identical.
- All experiments and tests import `rs_dic_llm`; `null_model.py` imports `src`. The roadmap
  item "package is broken" is resolved by `6546af4` (the package now exists); the duplicate
  remains.
- Action: after the advisor confirms, delete the flat copies or make them thin re-exports.

### F9 (Medium) Generation reproducibility

- Three generation modes were used: the 08-09 run (17 instruct models) predates batching and
  its manifests say `generation_seed + word_index` (true per-word seeding); the 08-31 run
  (5 base models + Qwen3-4B-Instruct-2507) used batched generation and six manifests say
  `generation_seed + batch_start`, a label that was never committed in any `.py` file (the
  committed `_write_manifest` always writes `word_index`), so that run used a code revision
  that is not in git; E3-E5 (09-09) are batched, but their manifests still say `word_index`.
- In batched mode the per-record `generation_seed` field is not the seed used (the seed is set
  per batch), and outputs depend on batch composition and left-padding. The docstring claim
  that "any individual word's output is reproducible independently of list order" does not
  hold in batched mode.
- Sampling is stochastic (temperature 0.7) with one run per model; `_42` in file names is the
  word-sampling seed, generation seed is 0.
- Impact: pt versus it, and E4/E5 versus main, differ in generation path as well as in the
  intended factor. Probably small, but it must be stated in the methods.
- Decided (D014): stated as a limitation; E6 (multi-seed) is out of scope and no GPU is
  available.

### F10 (Medium, decision needed) Vocabulary and node count vary

- Records with status `failed` or `empty` drop the lemma from the vocabulary, so node counts
  range from 2,681 (Gemma3-270M) to 2,750, and 2,551 for E5 Qwen2.5-3B. Also, 3,000 entries
  map to 2,750 nodes because same-lemma entries merge (a noun and a verb entry share one
  node and all edges from both definitions).
- Decided (D010): a filtered record keeps its node and only its edges are dropped (fixed
  vocabulary of 2,750 lemmas for every model, so graphs and nulls are comparable).
- The paper should say "3,000 entries, 2,750 lemmas".

### F11 (Low) Graph rebuilds depend slightly on the NLTK version

- Rebuilding locally (Python 3.11.4, networkx 3.6.1, nltk 3.9.1) reproduces the stored edge
  count exactly for 59 of 65 graphs; 6 differ: WordNet +17 (4,599 vs 4,582), Gemma3-27B -3,
  E4 Gemma3-27B -3, E5 Qwen2.5-1.5B -3, E5 Qwen3-4B-Instruct-2507 -3, E5 Qwen3-8B -1.
- Action: record NLTK and WordNet versions in every run manifest. E1 uses the locally rebuilt
  graphs (snapshots saved), so its numbers differ from stored metrics by these amounts.

### F12 (Low) Extra files and absent manifests

- `data/definitions/` holds 10 files that are not paper models (Qwen3.5 x8, Gemma-4 x2, no
  manifests; Qwen3.5 is documented as incompatible with the pipeline). `docs/for-pepe/README.md`
  calls the folder "23 models". Pipeline code should select models from `MODEL_REGISTRY`,
  never by glob.

### F13 (Low, decision needed) Model exclusion rule is not written down

- Gemma3-270M (instruct) has no cycles and is excluded from the 17-model R range; Gemma3-270M
  is also degenerate in E4 (465 edges, 84 % self-referential). The report says "18" in one
  place and "(17)" in another. Decided (D011): exclude a model from R comparisons if its
  unfiltered graph has no cycle, and show results with and without it.

### F14 (Low) E4 equalises length only partly

- Prompt "in 8 words or fewer". Mean words: Gemma3-1B 7.9 to 5.5, 4B 11.1 to 6.6, 12B 13.0 to
  7.3, 27B 14.4 to 7.3, Qwen2.5-7B 8.8 to 5.5, Qwen2.5-72B 8.2 to 5.3. Lengths fall but differ
  between models (E4 range 2.2-8.5 words across all 18). The roadmap's alternative, post-hoc
  matching of out-degree distributions, has not been done.
- Converged R (unfiltered, 2026-10-01): the cap changes R by a factor 0.44-2.92 per model
  (median ratio 1.17, higher in 11 of 17; median size of the change 1.3, 14 of 17 within a
  factor 2) and the change does not follow the change in mean length (Spearman -0.09, p = 0.72,
  n = 17). Within the 34 instruct graphs (main and E4) R is unrelated to mean length (rho -0.01);
  across all 62 converged graphs it is negative (rho -0.47), which comes from the contrast
  between long, low-R base outputs and short, high-R instruct outputs (within the 10 base graphs
  rho -0.26, p = 0.47).
- Scripts and docs say "17 instruct models"; 18 ran.

### F15 (Low) The +0.798 kernel/density correlation depends on one degenerate model

- See section 1: +0.640 without Gemma3-270M. The qualitative conclusion (density explains the
  kernel) is unchanged, but the headline number should come with the exclusion stated.

### F16 (Low) Secondary analyses outside the three claims

- `experiments/regress_model_size.py` ranks all 3-feature subsets by leave-one-out Q2 and
  prints the top six (selection on the validation metric; the reported Q2 = 0.71 is
  optimistic). The roadmap's n=5 correlations come from the Qwen3.5 draft.
  `quantization_study.py`: the conclusion text is chosen by a 1 pp threshold, not a
  statistical test, and the stored results have bit-identical `kernel_ratio` across
  bf16/int8/int4 for both 32B (0.01417...) and 72B (0.01012...): do not cite. These belong to
  the student thesis, not to the paper.

### F17 (Info) Core definition

- `plan.md` and the Japanese study guide say "largest SCC"; the code and
  `docs/correction_en.md` say "union of source SCCs". Not checked against the original paper.
  Core only matters for secondary metrics.

### F18 (Info) Unverified assumptions

- Whether the Gemma3 `-pt` tokenizers carry a chat template. `hf_client._format_prompt` applies
  one if present and falls back to raw text otherwise; the roadmap says base models get none,
  and the zero-shot outputs (prompt echoes) suggest raw text, but it was not checked.
- The direction report's null numbers (10 replicates, 24 graphs) are not stored in the repo.
- All references in the roadmap and report.
- Runtime environment of the RunPod runs (library versions) is not recorded.

### F19 (Info) Repository state

- Git shows 126 tracked files deleted: `results_e3 (fewshot)/`, `results_e4 (lenght)/`,
  `results_e5 (no template)/` were moved into the untracked `results_2026-09-09_Runpod/`.
  Also untracked: the labeling workbook, `research/`, `experiments/e1_full_null.py`,
  `results_2026-10-01_Local/`. Nothing was committed by this audit.
- The E3/E4/E5 scripts write to `results/e3_fewshot`, `data/definitions/e3_fewshot`, etc.;
  the folders were renamed by hand. Root `README.md` is empty. The E4 folder name is
  misspelled (`lenght`).

### F20 (Info, out of scope) Part of speech

- The prompt names the part of speech listed for each entry, and the stored outputs show the
  models following it when they name one (2,087 outputs begin "The noun/verb/adjective
  <word>", 99.9 % naming the listed one). While labeling, the researcher noted 72 of 2,300
  rows `wrong-pos` (the model defined another part of speech); all are labeled `definition`.
- Decision (2026-10-01, D017 withdrawn): part of speech is outside the scope of this
  investigation. No analysis uses the POS column of the labeling workbook or the `wrong-pos`
  tag, and no sensitivity run or word-list change is planned. This entry exists only so the
  tag is not mistaken for something that was analysed.

### F21 (Medium, resolved by D022) The self-consistency sheet was saved less than a day after the first pass, by the file times

- `data/exp2_selfconsistency_sheet.xlsx` was generated at 08:23 JST on 2026-10-01 and saved with
  all 118 labels at 08:55 JST (file properties: last modified by the researcher). The first-pass
  workbook was created 2026-09-29 11:04 UTC and last saved 2026-09-30 22:51 UTC (07:51 JST on
  2026-10-01). The gap between a row's first label and its re-label is therefore somewhere
  between about half an hour and a day and a half; the workbook does not record when each row
  was first labeled.
- Why: the sheet's "Read me" says "Start no earlier than 2026-10-01 (at least one day after the
  first pass ended on 2026-09-30)". Those are the UTC dates of the file timestamps; in the
  researcher's calendar (JST) the first pass ended on 2026-10-01. The script and the docs were
  corrected to 2026-10-02 afterwards, but the generated sheet could not be regenerated (the script
  refuses to overwrite a sheet that may hold labels), so the sheet and the docs disagreed and the
  researcher followed the sheet.
- Effect: D005 asks for at least one day. The agreement (88.2 %, kappa 0.79 on seven labels;
  95.5 %, kappa 0.90 for definition versus not; `audit_scripts/outputs/9_selfconsistency_agreement.txt`)
  is probably an upper bound on the one-day figure. It is still informative about where the
  labels are unstable: offtopic versus question on quiz-style outputs (6 of 18 first-pass offtopic
  rows came back as question), weak or circular definitions (4 came back as offtopic), and
  imperative-form outputs of Qwen3-0.6B (2 of 6 targeted rows changed).
- Resolved: D022 (a). The researcher keeps the re-label as the self-consistency measurement and
  states that about a day passed between the first labeling of the sampled rows and the re-label;
  the file times cannot confirm or contradict that for individual rows. The paper gives the
  interval as the researcher states it and calls the agreement a possible upper bound.

### F22 (Medium) The filter misses off-topic text, and what that does to the pt/it comparison

- The frozen filter (D023; hash in `outputs/14_test_scored.lock`), test words scored once: precision
  of a drop 97.5 %, recall of non-definitions 77.7 % (base models 81.5 %), 0.4 % of definitions
  wrongly dropped. The misses are mostly fluent off-topic sentences from the smallest models ("The dog
  is a small, furry creature.") and the bare imperatives of Qwen3-0.6B. A rule on the subject of a
  sentence caught them on the development words but dropped valid definitions on the other 2,900
  words ("A courageous person is willing to face danger." defines "brave"), so it was removed.
- Direction of the error (expected, not measured). Junk that stays in a graph adds edges that rarely
  point back at each other, so it keeps reciprocity excess low. On the test words 29 of the 157
  base-model non-definitions remain (18.5 %). The filtered R of the base models is then a lower
  bound of what a perfect filter would give: if the pt/it gap disappears after filtering, leakage
  works against that result; if the gap persists, leakage is one explanation that has to be bounded
  before claim 3 is stated, for example by a run with a more aggressive filter beside the default one.
- Not validated: E3, E4 and E5 have no hand labels. The E5 rules for task language were added after
  reading unlabeled E5 outputs. The imperatives and usage fragments of Qwen3-0.6B (D018) are not
  detected by the default filter.
- Label noise seen: "Frame is a verb." (Gemma3-270M-pt) is labeled `definition` while "Performer is a
  noun." is `restatement` (pos-only); the filter drops both, so the first counts as a false drop.
- The strict bracket of D024 catches about 5 more points of the junk (test words: recall 82.7 %, base
  models 85.4 %) at 0.8 points more wrongly dropped definitions, so even the pair of filters leaves
  about 15 % of the base-model junk in the graphs.

### F23 (Info) Untested confound: the prompt asks for common English words

- Every prompt (main, E3 header, E4, E5) tells the model to use only common English words (E3: simple English
  words). That pushes definitions toward other high-frequency words, which makes mutual pairs of closely related
  words likely (audit script 18: begin-start, complete-finish, big-size; typed in script 20, 38 % of the instruct pair
  occurrences are synonyms, 22 % hypernym pairs, 9 % sister terms, 29 % other associates). R may therefore partly measure how well a
  model follows that constraint, and not an intrinsic property of its definitions.
- Not tested. A CPU-only check was proposed on 2026-10-01 (does R across the 22 graphs follow the frequency of the
  words used in the definitions?); the researcher chose not to run it for now. It belongs in the limitations of the
  paper. Prompt variation (E10) is out of scope.
- The E3 header keeps both constraints ("uses only simple English words, and does not repeat the word being defined",
  `experiments/e3_fewshot_base.py` line 48), as does the zero-shot prompt, so this confound cannot explain why three examples
  close the zero-shot gap. It does bear on the comparison with WordNet.

### F24 (Medium, corrected 2026-10-02) The claim-1 z medians were quoted for the wrong group

- Section 6 of `audit_scripts/17_filtered_vs_unfiltered.py` pools all 23 main graphs (17 instruct, 5 base, WordNet). The claims
  table and a draft claims sheet quoted its circulation medians (-1.5 / -1.1 / -1.2) as medians "for the instruct models".
  Section 14 (added 2026-10-02) gives the groups: for the 17 instruct models the circulation z median is -1.34 / -1.51 / -1.37
  (unfiltered / default / strict), 15 of 17 below 0 and 6 below -2 in each variant; WordNet -1.89. Their kernel z median is
  +0.16 / +0.31 / +0.10 (WordNet -0.08).
- The five base graphs change sign with the filter: circulation z median -1.81 unfiltered, +1.90 default, +2.20 strict (none of
  the five below 0 once filtered); kernel z median -1.67, +1.68, +1.37. Filtered, they hold 3-14 mutual pairs, so neither
  measure is stable for them. Claim 1 now states the circulation result for the instruct models and WordNet only.

### F25 (Info, found 2026-10-02) The words of the E3 examples are not absent from the sample

- The comment in `experiments/e3_fewshot_base.py` (lines 45-46) says the examples were chosen so that their words are
  unlikely to be in the 3,000-word sample. "book" and "large" are in the vocabulary ("walk" is not), and so are ten words of
  the example definitions (bound, cover, set; forward, front, place, steady; average, great, size).
- Effect on the E3 graphs (`audit_scripts/outputs/23_e3_example_words.txt`): edges that start at these 12 words are 5.1-5.5 % of
  the edges at 4B-27B, as in the matched instruct graphs (5.1-5.6 %); 8.7 % at 1B (instruct 6.5 %) and 12.8 % at 270M (no
  instruct graph). Mutual pairs that involve one: 4 of 29, 6 of 92, 6 of 114, 5 of 78 (1B-27B), against 4 of 34, 3 of 47, 10 of
  78, 6 of 71 for the instruct models; the two headwords are in one pair only (great-large, 270M). No sign that the examples
  drive R. To disclose in the methods.

### F26 (Info, found 2026-10-02) Two interval methods in script 19 disagree at E3 1B

- `19_count_intervals.txt` gives the E3 ratio with a conservative method (sections 2-3, combining the two ends) and an exact
  conditional one (sections 4-5), in the direction base / instruct, while the zero-shot pairs are instruct / base. At 1B the exact
  range excludes 1 (instruct / base 1.91 [1.13, 3.24]) and the conservative range does not ([0.92, 3.98]). Section 6 (added
  2026-10-02) gives both in one direction. Name the method with every interval. "Indistinguishable from 1" at 4B, 12B and 27B
  means that no difference can be shown; the exact ranges still allow differences of up to about 1.6-1.7x.

### F27 (Info, found 2026-10-02) "R does not rise with size" holds family by family, not for all instruct models

- A draft amendment of D026 said that R does not rise with size among the instruct models.
  `audit_scripts/outputs/17_filtered_vs_unfiltered.txt`, section 15 (default filter, Spearman rank correlation of R with size):
  Gemma3 falls (42.5 at 1B, 25.4 at 27B, rho -1.00, n = 4), Qwen2.5 has no trend (rho -0.18, n = 7), Qwen3 rises (8.8 at 0.6B,
  29.3 at 8B, rho +0.84, n = 6, p = 0.04), and the 17 pooled give rho +0.18 (p = 0.50). A statement about scale has to name the
  family or say "no overall relation"; D026's amendment, claim 3 and the claims sheet now do. Few-shot base R rises from 270M
  (4.6) to 1B (22.3) and is flat from 1B to 27B (22-31).

### F28 (Medium, found 2026-10-02) Several descriptions of cited sources did not match the sources

- Checked against the original texts (`REFERENCE_CHECK_2026-10-02.md`): the roadmap's one-line summaries, which draft v0 repeated, were wrong or too
  strong in several places. [Gud26] does not compare matched base and instruct pairs (it compares older base models with newer instruction-tuned ones,
  on news text); [Har25] offers the circularity of verbal definition as one of several hunches, not as the reason language models work; [Lev12] compares
  with a degree-preserving randomization and finds an excess of short loops; [Lak25] does not state an objection about length, it finds that apparent
  diversity loss is largely quality control and aggregation and that aligned behaviour is recoverable in context; [Res24] has a new title and a third
  author; [Baa25]'s title is not "DeepNSM"; the chapters of Newman's *Networks* (2nd ed.) for the configuration model are 12, not 12-13.
- The Core of [VL16] is the union of the source components of the Kernel (equal to the largest component in two of the four dictionaries), which is what
  our code uses: the open point of the roadmap is settled, and the audit's note that the original says "largest SCC" was half right.
- Draft v0 called 5×|E| swaps "the usual" setting; no source gives it (the setting comes from `experiments/null_model.py`).
- Consequence: draft v1 describes each source as the check records, and the researcher then verified the references (2026-10-02).

### F29 (High, found 2026-10-02) The null of every R so far cannot move some mutual pairs and biases R toward 1

- The null model of E1 to E5, of draft v1 and of D020 to D029 is NetworkX `directed_edge_swap` (networkx 3.6.1). Its move replaces a path a -> b -> c -> d by a -> c, c -> b and b -> d and is not made if c -> b exists (`second not in G.succ[third]` in the source), so the middle
  edge of the path never belongs to a mutual pair, and a pair can be broken only if one of its words starts or ends such a path through other words. Evidence: `audit_scripts/outputs/29_null_pairs.txt` (D030 (a), 40 graphs x 40 stored replicates): in the few-shot graphs limited to the zero-shot survivors 10.0 of the
  14.4 pairs per null replicate (69 %) are observed pairs, and pairs such as battle-fight, initiate-start, asleep-awake, mention-refer are present in all 40 replicates; in the whole instruct graphs 0.1 of 7.9. `outputs/35_double_swap_validation.txt` section 2 (eight graphs, 20 stored
  replicates rerun with the stored seeds, all 160 equal the stored ones): 0.00 to 10.40 observed pairs kept per replicate (10.40 of 12.40 pairs on a closed half of the 4B few-shot graph with 14 observed pairs). A pair that is always present adds the same number to the observed count and to the null mean,
  so R is pulled toward 1, the more so the sparser the graph. A directed double-edge swap null (D032) keeps 0.00-0.03 of the observed pairs and agrees with the independent-edge estimate on eight graphs.
- Consequences (D032, `outputs/36_double_swap_readings.txt`): R of a graph changes by a factor of 0.89 to 6.7 (instruct median 1.09, range 0.89-4.18; zero-shot pretrained median 2.64); the order of the 17 instruct models by R changes (rank correlation +0.07); the dependence of R on coverage found in D029 and D030 (b) is
  absent (median rho 0.82-1.40 against 0.14-0.30); the zero-shot gap of D024 is absent (6.4, 1.3, 2.0, 0.9 against 7.1, 3.3, 12.2, 5.2); instruct R (18.1-52.1) is above WordNet's (18.1), not equal to it (15.7). Not changed: the kernel ratio, the circulation rate and the cycle profile (D033), the pairs themselves, and the verdict of the scale test (D031).
- Status: draft v2 reports R against the double-edge null with the first null's values beside it. Which null is primary is D035 (proposed, not decided). The unfiltered, strict-filter, stored-text and frame-word variants were not rerun against it. The earlier statement "the cause of the dependence of R on coverage is not established" (D029) is settled by this finding.

### F30 (Medium, found 2026-10-02) Against the double-edge null R falls with the length of the definitions; v1 said it did not

- Draft v1 said that R is not related to definition length (Spearman -0.09, p = 0.72 for the change under the 8-word cap; rho -0.01, n = 34), computed on the unfiltered graphs against the three-edge null (`outputs/13_controls_vs_main.txt`). `outputs/38_controls_double_swap.txt` (D034; the last section is post hoc): against the
  double-edge null the length cap raises R for 16 of 17 instruct models (median ratio 1.62), and the rank correlation of R with mean words is -0.75 over 59 graphs, -0.73 over the 34 instruct graphs of the main run and the cap, -0.49 and -0.48 for the changes within a model; the same analyses against the three-edge null give -0.35, +0.10, -0.14 and -0.61.
  WordNet's glosses have 8.8 words, the instruct models 10.4 (7.9-14.6), the zero-shot pretrained models 18.3-23.7. Consequence: conditions that differ in length (zero-shot against instruct, Gemma 3 sizes, prompts) are confounded with length when compared by R; the draft says so (Sections 4.4, 4.5, 4.6.1, 4.6.4, 5, 6).

## 3. What the experiments contain today

| Experiment | Files | What is usable now |
|---|---|---|
| Main run (08-09, 08-31) | definitions in `data/definitions/`, metrics in `results_2026-08-09_Runpod/metrics`, `results_2026-08-31_Runpod/metrics` | Observed graph metrics (no R). |
| E3 (09-09) | 5 Gemma3-pt, few-shot, `results_e3 (fewshot)/` | Definitions and graph metrics; converged R in the E1d controls run (unfiltered). Stored R is `R_analytic` (F1): do not use. Extraction differs from main (F2). |
| E4 (09-09) | 18 instruct models, 8-word cap | Same (F1, F14); converged R available. |
| E5 (09-09) | 18 instruct models, no template | Same (F1, F4); converged R available. |
| E1 | `results_2026-10-01_Local/e1_null_unfiltered/` (65 graphs x 100 replicates) | Finished 2026-10-01 in 76 minutes at 5 x swaps; superseded by E1d and E1d controls (R a median 19 % lower on the main graphs). |
| E1b | `results_2026-10-01_Local/e1b_null_unfiltered_15x/` (24 main graphs, 15 x edges swaps) | Finished 2026-10-01 (D007): 10 of 24 graphs hit the swap budget; R about 13 % above E1. |
| E1c | `results_2026-10-01_Local/e1c_null_convergence/` (6 graphs x 30 chains) | Finished 2026-10-01: the null settles within 4-24 x edges; 32 x confirmed (D020). |
| E1d | `results_2026-10-01_Local/e1d_null_unfiltered_32x/` (23 main graphs) | Finished 2026-10-01 in 78 minutes: the unfiltered baseline for the main graphs. |
| E1d controls | `results_2026-10-01_Local/e1d_null_unfiltered_32x_controls/` (40 graphs) | Finished 2026-10-01 in 2.4 hours: the unfiltered baseline for E3, E4, E5 (D021). |
| E2 | `data/exp2_labeling_workbook_labeled.xlsx`, `research/E2_LABELING_INSTRUCTIONS.md` | First labeling pass complete: 2,300 of 2,300 rows, reviewed in 3b. All labeling passes finished 2026-10-01 (self-consistency kept as is, F21, D022). Extraction rule built; filter built and validated (D023, F22); graphs rebuilt and re-run on the filtered graphs 2026-10-02. |
| E8 | none | Not started. |

### 3b. E2 first-pass label review (2026-10-01)

Script `audit_scripts/5_e2_label_review.py`, recorded output `outputs/5_e2_label_review.txt`,
flags in `outputs/5_e2_label_flags.csv`.

- **Complete and valid.** 2,300 of 2,300 rows labeled, no invalid label, every output equals a
  stored record of that word, the same 100 words in every tab. The 68 groups of identical
  outputs from different models all received the same label.
- **Labels per model.** Instruct models are `definition` on about 100 % of rows, except
  Gemma3-270M (27 definition, 61 restatement, 8 offtopic, 4 unclear) and Qwen3-0.6B (87
  definition, 5 offtopic, 5 unclear, 2 restatement, 1 echo); Gemma3-1B and
  Qwen3-4B-Instruct-2507 have 99. The five base models: 42.0 % definition (21, 54, 39, 53, 43
  for 270M to 27B), 16.2 % echo, 26.4 % offtopic, 9.6 % question, 1.8 % restatement, 0.8 %
  refusal, 3.2 % unclear. On this sample more than half of base outputs are not definitions.
- **Against the report's Table 2** (100 words per model, so about +/-5 points): echo 13-21 %
  by hand against 12-17 % in the report; "question" 6-20 % by hand against 12-37 % in the
  report, which counted any `?` in the output (Gemma3-4B-pt: 6 % by hand, 33 % in the report).
- **Notes.** 218 rows: `wrong-pos` 72 (all `definition`; informational, F20), `format` 63, `trailing-junk`
  12, `q+def` 11, `wrong-word` 11, `task-meta` 11, `empty` 9 (3 blank outputs, 6 list-marker
  only or empty list), `imperative` 8, `pos-only` 5, `usage-fragment` 5, `truncated` 5,
  `hedged` 3.
- **Crude consistency flags** (60, all inspected, none an error): definitions containing `?`
  (2) start with a real definition; questions without `?` (2) are clearly questions; echo
  without a prompt phrase (9) paraphrase the task; short definitions (11) are real glosses
  (`happy`, `Not awake.`); `pos-only` outputs are consistently `restatement`.
- **Conventions that split.** (a) Bare imperatives built on the target verb: 3 labeled
  `definition` (`Pinpoint the specific location.`, `Bury something in the ground.`, `Group
  people together.`) and 5 `offtopic` (`Devise a plan.`, `Wait for something.`, `Wear a shirt.`,
  `Acknowledge someone's actions or thoughts.`, and `A) Pinpoint the location of a point.`);
  all are Qwen3-0.6B rows except the last, and `Wait for something.` and `Bury something in
  the ground.` look alike. (b) Usage fragments (`A pack of animals.`, `Interchange between two
  things.`) are `unclear` + `usage-fragment`, while the imperative ones are `offtopic` +
  `imperative`. (c) `task-meta` is 7 `offtopic` and 4 `echo`. (d) `empty` covers blank outputs
  and list-marker-only outputs.
- **Reading.** These rows are few (about 20 of 2,300, mostly Qwen3-0.6B and Gemma3-270M) and
  matter for validating the non-definition class of instruct models, not for the base-model
  result. Suggested handling (D018): no relabeling; define analysis classes from label plus
  tag (`usage` = `usage-fragment` or `imperative`; `task text` = `task-meta`; `blank or
  fragment` = `empty` or `truncated`); re-look at the six Qwen3-0.6B imperative rows in the
  self-consistency pass.

## 4. Decisions (all taken 2026-10-01; details in `DECISION_LOG.md`)

D007 swaps: E1 at 5E plus E1b at 15E; D008 only the rewiring R is reported; D009 uniform
first-sentence cut is primary, stored text a sensitivity row; D010 filtered records keep their
node; D011 exclude models whose unfiltered graph has no cycle; D012 claim 1 narrowed to kernel
ratio and circulation rate; D013 Gemma-specific matched-pair framing; D014 sampling variance
stated as a limitation; D015 `e1_full_null.py` is the E1 of record.
Advisor confirmation of D003, D005, D007, D012, D013, D015, D016 and D020: given (reported by the researcher, 2026-10-02).
Raised after E1 and the label review: D016 (claim 1 and circulation rate), D018 (label
conventions). D017 (part of speech) was withdrawn as out of scope.
