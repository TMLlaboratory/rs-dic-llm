# Project Context

Stable, conceptual description of the research. What changes often (status, open decisions)
lives in `README.md`, `EXPERIMENT_REGISTRY.md` and `DECISION_LOG.md`, not here.
Written 2026-10-01 from the repository as it stands (see `RESEARCH_AUDIT.md` for the evidence
and for everything that is not yet settled).

## 1. Research topic and question

Dictionaries define words using other words, so a dictionary is a directed graph with cycles.
Vincent-Lamarre et al. (2016) showed that human dictionaries have a small "kernel" of words
from which everything else can be defined, and Levary et al. (2012) showed that the loops in
human dictionaries are much shorter than in random graphs.

**Question.** When a language model is asked to define the same 3,000 (word, part-of-speech)
entries, does the resulting "dictionary" close on itself like a human one, and what produces
that structure: model scale, or post-training (instruction tuning)?

One-line pitch: earlier work asked whether LLM definitions *match* dictionaries; we ask whether
they *close* like one.

## 2. Where the project stands scientifically

The original plan (2026-05, `plan.md`) was to propose kernel ratio as a measure of how well an
LLM "understands" concepts. A degree-preserving null model run by the advisor on 2026-09-01
showed that kernel ratio is explained by the degrees of the graph, chiefly its density, WordNet included. The project was
re-planned around what survived that check. All of the following are claims to be tested,
not established facts:

| # | Claim | Evidence so far | What would falsify it |
|---|---|---|---|
| 1 | The kernel ratio of the LLM graphs and of the WordNet graph is indistinguishable from a degree-preserving null; "bigger models converge on human dictionary structure" is a definition-length artifact. The circulation rate is reported separately: for the instruct models and WordNet it is below the null (D016). Core and MinSet were not null-tested, so the claim does not cover them (D012). This includes correcting our own earlier claims. | E1d (unfiltered) and the filtered runs of 2026-10-01 (default and strict filter, first sentence), kernel ratio z against the converged null, over all 23 graphs: median -0.08 unfiltered (range -4.3 to +2.1; 4 graphs below -2, 1 above), +0.52 default (-4.4 to +3.3; 2 below, 3 above), +0.43 strict (-4.7 to +3.4; 3 below, 3 above); over the 17 instruct models: median +0.16 / +0.31 / +0.10 (2 / 2 / 3 below -2 and 1 above in each); WordNet -0.08 in every variant. Above +2 under the filters: Qwen2.5-32B (+2.1) and the base models Gemma3-4B-pt (+3.2) and 1B-pt (+2.5). Circulation rate is *below* the null for the 17 instruct models (median z -1.34 unfiltered, -1.51 default, -1.37 strict; 15 of 17 below 0 and 6 below -2 in each variant) and for WordNet (-1.89), which is why it is reported separately (D016). The five base graphs are too sparse for either measure to be stable: circulation z median -1.81 unfiltered and +1.90 default / +2.20 strict (none below 0 once filtered), kernel z median -1.67 unfiltered and +1.68 / +1.37 filtered (audit script 17, sections 6 and 14; an earlier wording quoted the pooled medians of all 23 graphs as instruct-only, F24). | A systematic positive z for LLM graphs. |
| 2 | After density correction one structure remains: reciprocity excess R, the number of mutual definitions (A defined with B and B with A) relative to the null. Reported: 8.9-23.5 for 17 instruction-tuned models, 1.5-7.3 for 5 base models, 10.0 for WordNet. | E1d (unfiltered) and the filtered runs: instruct 9.4-42.5 over 17 models (median 18.3) unfiltered, 8.8-42.5 (19.3) under the default filter, 8.9-34.9 (19.3) under the strict one; base zero-shot 2.1-9.0 (5.2), 2.1-8.4 (4.9), 1.8-6.0 (5.6); WordNet 15.7 throughout. Unfiltered, 12 of the 17 instruct models are above WordNet and all 5 base models below. Short cycles are in excess (default filter: 2-cycles 18.8x instruct, 4.2x base, 15.7x WordNet), cycles of length 5-7 are below chance for the instruct models (0.46-0.59x) and WordNet, and the base graphs have no cycle longer than 3. Across families the instruct and base ranges overlap unfiltered and under the default filter (Qwen3-0.6B 8.8 against Gemma3-4B-pt 8.4) and with the whole stored text (highest base Gemma3-4B-pt 12.5), and not under the strict filter or with the frame words removed (8.9 and 8.2 against 6.0, a floor value). Matched Gemma3 pairs, instruct R / base R at 1B / 4B / 12B / 27B: unfiltered 13.9 / 4.3 / 4.9 / 2.5, default 7.1 / 3.3 / 12.2 / 5.2, strict 5.8 / 4.8 / 11.7 / 3.8, whole stored text 7.1 / 2.2 / 10.0 / 3.4, six frame words removed 7.1 / 9.7 / 12.9 / 6.7. After filtering a base graph holds only 3-14 mutual pairs, so its R is uncertain by more than its null-sampling interval (count-based 95 % ranges, default filter: Gemma3-1B-pt 1.2-17.5, 12B-pt 0.8-4.3, 27B-pt 2.7-8.2). What the mutual pairs are (WordNet typing over all senses, audit script 20): of the 881 pair occurrences in the 17 instruct models 38 % are synonyms, 22 % hypernym pairs, 9 % sister terms (a shared hypernym), 2 % antonyms, 1 % derived forms and 29 % associates WordNet does not link (eat-mouth, greet-hello); WordNet's own 27 pairs are 2 synonyms, 3 derived forms, 9 hypernym pairs, 1 sister pair and 12 others, and 10 of them occur in some instruct model (1-4 in any one), so they agree in the size of the excess, not in which words form it: each instruct model shares 1-4 of WordNet's 27 pairs (Jaccard index 0.010-0.055), against a median of 0.14 between two instruct models (script 20, section 3). WordNet's relations type the pairs coarsely: some pairs typed as hypernym pairs or as unlinked are close in ordinary use (flavor-taste, location-place), others are associations (eat-mouth, greet-hello). R at 5 x (E1, and so the report's values) was a median 19 % lower. | R with a CI that includes 1, or an ordering that does not hold after filtering non-definitions (E2). |
| 3 | The structure is produced by instruction tuning, not by scale. Gemma3 pt/it pairs at matched sizes separate completely on R. | Not supported as stated (the readings of D024, fixed in advance; one generation run per condition, converged null). With the zero-shot prompt the Gemma3 pt/it pairs still separate after filtering: instruct R / base R is 7.1 / 3.3 / 12.2 / 5.2 under the default filter and 5.8 / 4.8 / 11.7 / 3.8 under the strict one (1B / 4B / 12B / 27B), all above 2 (reading (i)); with the whole stored text instead of the first sentence they are 7.1 / 2.2 / 10.0 / 3.4 (default filter). With the observed counts' own uncertainty (exact ranges, audit script 19) the ratio's 95 % range excludes 1 in all 20 pair-by-variant comparisons and excludes 2 in 15 of them (weakest: the 4B pair, 3.3 with range 1.7-7.1 under the default filter); written the same way, instruct R / few-shot base R is 1.91 [1.13, 3.24] at 1B (exact conditional range; the conservative range [0.92, 3.98] includes 1), 1.19 [0.82, 1.71] at 4B, 0.83 [0.61, 1.12] at 12B and 0.89 [0.64, 1.25] at 27B (script 19, section 6). At 4B, 12B and 27B no difference can be shown (the ranges include 1 and still allow differences of up to about 1.6-1.7x); at 1B the base model reaches about half of the instruct R by the exact method only. Gemma3-270M has no instruct comparison (D011); its few-shot base R is 4.6 [2.3, 8.3], below every instruct model. The few-shot base models' mutual pairs overlap the instruct models' pairs (audit script 20): 55 / 68 / 69 / 76 % of them (1B / 4B / 12B / 27B) occur in at least one instruct model, against 77 % for an instruct model's pairs in the other instruct models; their Jaccard index with the matched Gemma3 instruct model (0.15 / 0.17 / 0.22 / 0.20) lies inside the range between two Gemma3 instruct models (0.12-0.28, median 0.21). Scale (descriptive, not a test; script 17, section 15): among the 17 instruct models R shows no overall relation with size (Spearman +0.18, p = 0.50); it falls within Gemma3 (42.5 at 1B to 25.4 at 27B), has no trend within Qwen2.5 and rises within Qwen3 (8.8 at 0.6B to 29.3 at 8B); few-shot base R rises from 4.6 (270M) to 22-31 (1B-27B). But with a three-example prompt (E3) the base models reach the instruct range: few-shot base R 22.3 / 23.5 / 30.9 / 28.5 against instruct 42.5 / 28.0 / 25.7 / 25.4 under the default filter (factors 1.91, 1.19, 1.20, 1.12) and 22.3 / 23.5 / 29.5 / 31.3 against 34.9 / 26.9 / 25.7 / 21.4 under the strict one (1.57, 1.14, 1.15, 1.46): within a factor 2 at all four sizes, unfiltered as well. So instruction tuning is not needed for the structure at 4B and above; what it adds under a zero-shot prompt is not identified (removing six frame words from every graph, D025, leaves the gap: instruct R / base R 7.1 / 9.7 / 12.9 / 6.7; so neither junk nor frame words explain the zero-shot gap, and its cause is not identified). D029 (2026-10-02) then found that R falls to 0.07-0.51 of its whole-list value when a graph is limited to about half of the entries (survivors 0.11-0.26, single random halves 0.07-0.51), and that at equal coverage (the entries whose zero-shot record survives the filter) the zero-shot, few-shot and instruct graphs have R of 2.1-8.8, the instruct / zero-shot ratio being 0.49 / 0.54 / 3.02 / 1.80 against 7.1 / 3.3 / 12.2 / 5.2 on the whole graphs; so the zero-shot gap in R goes largely with how many entries the model defines (the filter keeps about half of the zero-shot records and nearly all of the instruct and few-shot ones). The zero-shot graphs still contain fewer of the instruct models' pairs (5 of 62 against 20 of 62 for the few-shot graphs on the same entries; `audit_scripts/outputs/27_survivor_restriction.txt`, `28_defining_words.txt`). Without the chat template (E5) R stays within about a factor 2 for the four Gemma3 and five of the seven Qwen2.5 instruct models; the Qwen3 E5 graphs are too sparse after filtering to read. Caveats: a filtered base graph holds only 3-14 mutual pairs; the strict filter closes only about 5 points of the junk leak; E4 and E5 are filtered but not hand-validated; the E3 outputs were hand-checked on 100 rows (100 of 100 definitions, 95 % interval 96-100 %, D027), a check of form and not of accuracy; R changes by a median factor of 1.3 (E4) to 1.9 (E5) when only the prompt changes, so differences under about 2x are not safe to interpret. | After E2 filtering and uniform extraction, base R overlaps instruct R: observed for the few-shot base models (E3) on the unfiltered, default and strict graphs, not for the zero-shot base models. That is a publishable result: the structure is latent in pretraining and instruction tuning is what makes it appear under a zero-shot prompt. (Qualified by D029, 2026-10-02: under a zero-shot prompt the pretrained models define only about half of the entries and at equal coverage the gap in R shrinks, so "appear" needs rewording; for the researcher and the advisor to settle.) |

**Update 2026-10-02 (D030-D034, draft v2): the null.** The R values in claims 2 and 3 above are against the three-edge null (networkx `directed_edge_swap`), which keeps mutual pairs it cannot move and biases R toward 1 in sparse graphs (D030, D032; up to 10.40 of 12.40 null pairs
per replicate are observed pairs). Against the directed double-edge swap null (D032: 64 x edges, 100 replicates; draft v2 puts the three-edge values beside it): instruct R 18.1-52.1 (median 29.2; first null 8.8-42.5) against WordNet 18.1 [11.9, 26.4] (first null 15.7), zero-shot pretrained 6.0-28.0 on 3-14 pairs (first null
2.1-8.4), few-shot pretrained 14.3-49.2. The instruct / pretrained ratio at 1B / 4B / 12B / 27B is 6.4 / 1.3 / 2.0 / 0.9 (first null 7.1 / 3.3 / 12.2 / 5.2): the zero-shot gap of claim 3 is absent by the rule of D024 and, on the same entries, not shown (the ranges include 1 at four of four sizes). The few-shot R is higher than the instruct R at 4B and 12B (instruct / few-shot
0.59 and 0.59), not different at 27B (0.81) and about half at 1B (2.12). R does not depend on coverage (median rho 0.82-1.40; first null 0.14-0.30). Claim 1 holds against both nulls (instruct models: kernel z +0.19, circulation z -1.31, 12 of 17 below 0), and so does the cycle profile (2-cycles 29.6 times the null). The scale test of D031 gives no consistent approach of R to WordNet's with
size against both nulls. Post hoc (D034): R falls with the mean length of the definitions against the double-edge null (rank correlation -0.75 over 59 graphs; the length cap raises R for 16 of 17 models). Which null is primary is D035 (proposed, not decided); claims 2 and 3 above are to be rewritten once it is. Sources: `audit_scripts/outputs/29` to `38`.

Working title (D028, 2026-10-02): *Do LLM-Written Dictionaries Resemble Human Ones? Mutual Definitions with and without
Instruction Tuning*. The title and claim 3 must follow the data; if E2/E3 change the
story, the paper changes.

## 3. The measurement pipeline

1. **Word list.** `data/sample_words/word_list_3k_v1.json` (sha256 `bd4de5c6...359363`):
   3,000 entries = 1,500 nouns, 900 verbs, 600 adjectives, sampled from WordNet with seed 42,
   Brown-corpus frequency >= 5. They contain **2,750 unique lemmas** (234 lemmas are listed
   twice and 8 three times, under different parts of speech), so graphs have at most 2,750
   nodes.
2. **Generation.** Each model gets, per entry:
   `Define the {noun|verb|adjective} "{word}" in one short sentence. Use only common English words. Do not use the word itself in the definition.`
   bf16, temperature 0.7, top-p 0.8, top-k 20, max 200 new tokens, sampling (not greedy), one
   run per model. Instruct models use the chat template. File suffix `_42` is the word-sampling
   seed, not the generation seed (generation seed 0).
3. **Status per record:** `ok`, `self_referential` (the definition contains the target word;
   these records stay in the graph), `failed`, `empty`, `thinking_leak`.
4. **Normalisation** (`normalize.py`): lowercase, strip punctuation, stopword removal, POS tag,
   WordNet lemmatisation, keep only tokens in the vocabulary (lemmas with a valid record).
   Uniform extraction (`extraction.py`, D009) keeps only the first line and first sentence of a stored definition, without
   markup or list markers; it is applied in the filtered analyses, which are the primary ones (the unfiltered E1d numbers use the stored text).
5. **Graph** (`graph_build.py`): edge `u -> v` iff lemma `u` occurs in the definition of `v`
   ("u defines v"); no self-loops, no multi-edges.
6. **Metrics:**
   - *Kernel*: repeatedly remove nodes with out-degree 0; `kernel_ratio = |kernel| / |nodes|`.
     The test `tests/test_kernel_outdegree.py` pins the direction (out-degree, not in-degree).
   - *Core*: union of the source SCCs of the condensation of the kernel (`docs/correction_en.md`
     attributes this to the original paper).
   - *MinSet*: minimum feedback vertex set by ILP (computed in the main run, not in E3-E5).
   - *circulation_rate*: share of nodes in a strongly connected component of size >= 2.
   - *Cycle counts*: simple cycles up to length 7 (`CYCLE_BOUND = 7`).
7. **Null model** (`experiments/null_model.py`, full run in `experiments/e1_full_null.py`):
   rewire the graph with `nx.directed_edge_swap` (keeps every node's in- and out-degree),
   recompute, repeat; compare observed to the null mean and SD. This three-edge move cannot break a mutual pair whose words have few other links (D030, D032). Draft v2 uses the directed double-edge swap instead
   (`experiments/d032_double_swap_null.py`: two edges (a->b), (c->d) become (a->d), (c->b); 64 x edges accepted swaps, 100 replicates), with the three-edge values beside it; which is primary is D035.

## 4. Terminology (use these exactly)

| Term | Meaning |
|---|---|
| mutual pair / 2-cycle | words A and B with edges A->B and B->A. `cycles_2` counts each pair once. |
| **R** (reciprocity excess) | `cycles_2(observed) / max(mean cycles_2 over null replicates, 0.5)`. The only R reported in the paper. Name the null: *three-edge* (networkx `directed_edge_swap`; E1-E5, draft v1) or *double-edge* (D032; draft v2). R' is the same without the floor of 0.5. |
| `R_analytic` (key `reciprocity_excess` in the E3/E4/E5 metrics JSONs made up to 2026-09-09) | A *different*, analytic quantity written by `rs_dic_llm.analysis`; new runs store it as `R_analytic` (D008). Not comparable to R. Do not report it. |
| z | `(observed - null mean) / null SD` (population SD, as in `null_model.py`). |
| `sr_rate` | Share of records with status `self_referential`. It is not a prompt-echo rate. |
| instruct / `it` | Post-trained model. 18 models, 17 after excluding Gemma3-270M-it (its graph has no cycles at all, so R = 0). Rule D011: exclude a model from R comparisons if its unfiltered graph has no cycle, and show results with and without it. |
| base / `pt` | Pretrained Gemma3 checkpoint. 5 models. |
| unfiltered | Graphs built from all records with status ok or self_referential, as in every run so far. |
| filtered | Graphs rebuilt after the E2 filter (D023): first sentence, fixed 2,750-lemma node set (D010); the primary analysis since 2026-10-02. |

## 5. Models (23 + WordNet)

| Group | Models |
|---|---|
| Gemma3 instruct (5) | 270M, 1B, 4B, 12B, 27B |
| Gemma3 base `-pt` (5) | 270M, 1B, 4B, 12B, 27B (matched pairs with the row above) |
| Qwen2.5 Instruct (7) | 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B |
| Qwen3 (5, thinking disabled) | 0.6B, 1.7B, 4B, 8B, 14B |
| Qwen3-4B-Instruct-2507 (1) | 4B |
| Human baseline | WordNet glosses for the same 3,000 entries |

Only Gemma3 has base/instruct pairs across sizes, so the scale-versus-tuning contrast rests on
one model family. Qwen is instruct-only and is used for the instruct scaling trend and as a
replication of E4/E5. Registry: `src/rs_dic_llm/config.py`. Not part of the paper: the Qwen3.5
and Gemma-4 files in `data/definitions/` (earlier, incompatible runs).

## 6. Experiments in scope before drafting

| ID | What | Purpose |
|---|---|---|
| E1 | Null model at full scale (100 replicates, bootstrap CI) | Claims 1 and 2 |
| E2 | Non-definition filter, validated by hand labels | Decides whether claim 3 stands |
| E3 | Few-shot prompt on the 5 base models | Is the base/instruct gap a format effect? |
| E4 | Length-constrained instruct models | Is R a byproduct of verbosity? |
| E5 | Instruct models without the chat template | Is R caused by the template? |
| E8 | WordNet-gloss similarity as a quality axis | Exploratory, non-blocking |

Out of scope for this paper: E6 multi-seed, E7 word-list bootstrap, E9 quantization re-run,
E10 prompt-variation ablation. Their absence is a stated limitation (single seed, single
prompt, single word list). Details per experiment: `EXPERIMENT_REGISTRY.md`.

## 7. People, venue, timeline

- Main researcher: Pepe. Advisor Kumoi wrote the roadmap and the direction report and approves
  the paper. Approvals are recorded in `DECISION_LOG.md`.
- First draft in English. No deadlines set as of 2026-10-01. The roadmap suggests NLP2027 or
  IPSJ NL-SIG first, then *Topics in Cognitive Science* (the journal that published
  Vincent-Lamarre et al.); Minds and Machines / Synthese are not recommended. This is the
  advisor's suggestion, not yet a decision. Researcher, 2026-10-02: no venue is decided and there is no length limit.

## 8. Sources and how far to trust them

1. Code, data and result files in the repository: what actually ran.
2. `research/` documents: the audited reconstruction and the decisions.
3. `docs/for-pepe/roadmap_en.md` and `docs/research-direction-2026-09_en.md` (also published as
   an Artifact): the advisor's plan and analysis of 2026-09-01. A plan, not a record; several
   numbers in it are reproduced in the audit, some are not.
4. Historical only, not evidence: `plan.md`, `docs/paper_*.md/pdf` (first draft, largely
   disproven), `docs/results-slides.md`, `docs/style-findings-slides.md`, `docs/study_guide/`,
   `docs/correction_*` (still useful for the kernel direction), `results_2026-07-21_TogetherAI/`
   (first runs), `logs/`, `AA_semi-resources/`.
5. Reading list for the argument the paper joins: `docs/for-pepe/roadmap_en.md` section 5.
   Cite only references that are in the project `.bib` or were verified; several in the roadmap
   have not been read in full (for example Boudourides 2026).

## 9. Known limits to state in the paper

Single generation seed and single prompt, run-to-run variance not estimated (D014);
sampling at temperature 0.7; one word list;
3,000 entries but 2,750 lemmas; Gemma-only matched pairs; the main instruct set (08-09) was
generated with per-word seeding while the base set (08-31) and E3-E5 (09-09) used batched
generation (inferred from git history and manifests, audit F9); preprocessing uses
lemmatisation where the original used stemming (`docs/correction_en.md` section 4); graph
edge counts depend slightly on the NLTK version (see audit F11).
