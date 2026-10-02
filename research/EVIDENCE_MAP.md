# Evidence Map

Manuscript statement to evidence, with readiness. Created 2026-10-02 with the first draft (`manuscript/draft_v0.md`), brought up to date the same day for `manuscript/draft_v1.md` and rebuilt for `manuscript/draft_v2.md`
(v1 and v0 stay unchanged), which reports R against a double-edge swap null (D032; making it primary is D035, not decided). **The next section is the map of draft v2 (current); the sections "Tables and figures" and "Statements in the text" after it
keep the numbering and the first-null R values of v1 and are superseded wherever v2 differs.** Update it whenever the draft or a source changes. Paths are relative to the repository root. "Outputs" are in `research/audit_scripts/outputs/`.

**Readiness codes.** *Ready*: the number comes from a recorded output or a file in the repository and was checked against the draft.
*Caveat*: ready, with a limit that the draft states. *Advisor*: depends on the framing of D026 (the advisor's green light was reported on 2026-10-02) or on text written after it.
*Pepe*: needs the researcher (reading, verification or a choice).

## Draft v2: numbering, tables, figures and statements (current)

Draft v2 (2026-10-02) follows an outside review of v1 and decisions D029 to D034. Its tables come from `audit_scripts/33_manuscript_tables_v2.py` (output `outputs/33_manuscript_tables_v2.md`; the text takes the table blocks from that file by program, so a table in the draft equals the generated one) and its figures from
`34_manuscript_figures_v2.py` (`manuscript/figures_v2/`); scripts 24 and 25 stay tied to v1. The text of v2 was assembled from unchanged slices of the first v2 build and new text; a screen of every number of the text against the recorded outputs, the tables and v1 found no number outside them (2026-10-02, by program; presence only).

| v1 | v2 |
|---|---|
| Abstract, 1 | Abstract, 1 (rewritten: kernel, R against the corrected null, the null, length, scale, tuning) |
| 3.5 | 3.5 (both nulls; the first null named) |
| 3.8 | 3.8 (predictions; readings in Appendix D) |
| 4.1, 4.2 | 4.1, 4.2 (both nulls) |
| (new) | 4.3 (which null; D030, D032) |
| 4.4 (controls) | 4.4 (controls against both nulls, D034; R and definition length, post hoc) |
| 4.3.4 | 4.5 (scale tested, D031, D032) |
| 4.3.1 / 4.3.5 / 4.3.2 / 4.3.3 | 4.6.1 / 4.6.2 and 4.6.3 / 4.6.4 / 4.6.5 |
| 5, 6, 7 | 5, 6, 7 (rewritten) |
| Tables 1, 2, 3 | Tables 1, 3, 4 (new: Table 2, R by group) |
| Table 4 / 5 / 6 / 7 / 8 | Tables 9 and A2 / 12 / 10 / 11 / A3 |
| (new) | Tables 5 (the two nulls), 6 (coverage), 7 (controls), 8 (scale), 13 (status of the questions, in the text), A4 (closed sub-dictionaries) |
| Table A1 | Table A1 (both nulls) |
| Fig. 1, 2, 3 | Fig. 1, 2, 3 (2 and 3 drawn for both nulls) |
| Fig. 4 / 5 | Fig. 5 (scale) / 6 (coverage); new Fig. 4 (R against the two nulls) |

| Section (v2) | Statement | Source | Readiness |
|---|---|---|---|
| 4.1, Table 1, Fig. 2 | Kernel z of the 17 instruct models: median +0.19 (double-edge), +0.31 / +0.16 / +0.10 (three-edge, default / unfiltered / strict); WordNet -0.26 / -0.08; three instruct models beyond +-2 (Qwen2.5-0.5B -3.9, Qwen2.5-1.5B -2.1, Qwen3-1.7B -2.3); circulation z -1.31 (12 of 17 below 0), WordNet -1.51 | `outputs/37_double_swap_claim1.txt` sections 1, 3 (D033); three-edge columns from the stored results, `outputs/17_...` section 14 | Ready |
| 4.2, Table 2, A1 | R against the double-edge null: instruct 18.1-52.1 (median 29.2), WordNet 18.1 [11.9, 26.4], zero-shot pretrained 6.0-28.0, few-shot 14.3-49.2; first null 8.8-42.5, 15.7, 2.1-8.4, 4.6-30.9; R(double) / R(three-edge) median 1.09, 2.64, 1.54 | `outputs/36_double_swap_readings.txt` section 1; `outputs/33_manuscript_tables_v2.md` Tables 2, A1 (from `results_2026-10-02_Local/d032_double_swap_null/results/` and the stored results) | Ready (R against the double-edge null awaits D035) |
| 4.2 | 16 of 17 instruct point estimates above WordNet's R; 13 ranges above, 0 below, 4 containing; the range of instruct R / WordNet R excludes 1 upward for 8 of 17, downward for none; 4 ranges above the upper end of WordNet's range (26.4); first null 12, 7, 2, 8, 6 | `outputs/36_...` section 7; `outputs/33_...` "Numbers quoted in the text" | Ready (the ratio test is descriptive, added in v2) |
| 4.2, Table 3, Fig. 3 | 2-cycles 29.6 x the double-edge null (18.8 x the three-edge null) for the instruct models; lengths 5 to 7 at 0.59 / 0.52 / 0.47; WordNet 16.9 x; pretrained 18.6 x | `outputs/37_...` section 2 (D033, 20 replicates) | Ready |
| 4.2 | Rank correlation of pairs with R over the 17 instruct models: -0.01 (three-edge), +0.30 (double-edge); of R under the two nulls: +0.07 | `outputs/33_...` "Numbers quoted in the text"; `outputs/36_...` section 1 | Ready |
| 4.3, Table 5 | Observed pairs in a replicate of the three-edge null: 0.00 to 10.40 on eight graphs (10.40 of 12.40 pairs on the closed 4B half); double-edge 0.00-0.01; independent-edge estimate agrees (1.87 / 2.01 etc.); all 160 rerun replicates equal the stored ones | `outputs/35_double_swap_validation.txt` sections 1, 2; `results_2026-10-02_Local/d032_networkx_persistence/`, `d032_double_swap_null/`; D032 validation note | Ready |
| 4.3 | In the fsS graphs 10.0 of 14.4 null pairs per replicate (69 %) are observed pairs; itS 6.1 of 10.2; random halves 55-82 %; whole few-shot 2.9 of 12.2; whole instruct 0.1 of 7.9; rule (a) met at 3 of 4 sizes (0.58, 0.76, 0.38, 0.60); pairs in all 40 replicates named; rho -0.21 | `outputs/29_null_pairs.txt` sections 1, 2, 3, 4 (section 4 added after 1-3 had been read); the pair names from a check of the stored replicates (battle-fight etc., all observed pairs) | Ready (post hoc part marked) |
| 4.3 | The NetworkX move is not made if c -> b exists; the middle edge cannot belong to a pair | networkx 3.6.1 `directed_edge_swap` (`second not in G.succ[third]`) | Ready (source code of the library) |
| 4.3 | Nine instruct models within 11 % of R, eight 1.7-4.2 times as high; Qwen2.5-72B null mean 6.65 against 1.59 | `outputs/36_...` section 1 | Ready |
| 4.3, Table 6 | rho of random halves: three-edge medians 0.14-0.30, double-edge 0.82-1.40; the reading of D032 (r1): R does not depend on coverage | `outputs/36_...` section 2; `outputs/30_...` section 2; Table 6 | Ready |
| 4.3, Table A4 | Closed dictionaries against the double-edge null: instruct / zero-shot R' 2.64 [0.71, 14.56], 1.22 [0.49, 3.04], 2.06 [0.83, 5.81], 0.40 [0.19, 0.86]; the rule of D030 (b2) applied to it: not shown at three of four sizes | `outputs/33_manuscript_tables_v2.md` Table A4 (from the d030c graphs of `d032_double_swap_null`); `outputs/30_closed_subdictionaries.txt` for the first null | Ready (post hoc application of an existing rule) |
| 4.4, Table 7 | Length cap: median ratio 1.62 (0.74-2.44), size 1.62, 13 of 17 within 2, R higher for 16 of 17, pairs higher for 13 of 17 (median 1.35); no template: 0.84 (0.06-1.39), size 1.21, 13 of 15; first null 1.11 / 1.28 and 0.76 / 1.94 | `outputs/38_controls_double_swap.txt`; D034 result | Ready |
| 4.4 | R against mean definition length: -0.75 (59 graphs), -0.73 (34 instruct graphs), -0.49 and -0.48 within a model; first null -0.35, +0.10, -0.14, -0.61; WordNet glosses 8.8 words; instruct 10.4 (7.9-14.6); 6.3 under the cap; 17.4 without template; zero-shot 18.3-23.7 | `outputs/38_...` last section (post hoc); `outputs/13_controls_vs_main.txt` for the per-model words | Ready (post hoc, descriptive) |
| 4.4 | No think tags or reasoning openings in the Qwen3 main run and length control (0 of 18,000 each); 1-107 of 3,000 per model in the template control | `outputs/32_qwen3_thinking_check.txt` | Ready (heuristic search) |
| 4.5, Table 8, Fig. 5 | No consistent approach: distance toward / none / away (double-edge), toward / none / none (three-edge), overlap none / away / none; including Qwen3-4B-Instruct-2507 changes no label; Gemma 3 R 38.6 to 24.7, null mean 0.88 to 2.87, pairs 34 to 71; Gemma 3 kernel z +1.40 to -1.40 | `outputs/31_scale_convergence.txt`; `outputs/36_...` section 6 and its sensitivity; `outputs/33_...` numbers quoted | Ready (weak evidence: n = 4, 7, 5) |
| 4.6.1, Table 9 | Instruct / pretrained R 6.4 [2.0, 32.8], 1.3 [0.7, 2.8], 2.0 [0.9, 5.1], 0.9 [0.5, 1.7]; two of four reach 2: gap absent; zero-shot null means 0.44 / 0.38 / 0.44 / 0.42, R' 6.8 / 28.9 / 15.9 / 33.3; filter drops 47.3-57.6 % (0.0-0.7 % of the instruct models) | `outputs/36_...` section 3; `outputs/33_...` Table 9 and numbers quoted; `outputs/15_filter_drop_rates.txt` | Ready |
| 4.6.2, Table 10, Fig. 6 | At equal coverage instruct / zero-shot 3.00 [0.75, 17.2], 1.09, 2.43, 1.01: not shown at 4 of 4; pairs 35 / 66 / 53; null means below the floor in 11 of 12 graphs | `outputs/36_...` section 4; `outputs/27_survivor_restriction.txt` (pairs, edges); Table 10 | Ready |
| 4.6.3, Table 11, A3 | 5 of 62 against 20 of 62, McNemar p = 0.0003; defining words 0.11-0.17 against 0.17-0.25 | `outputs/28_defining_words.txt`; `outputs/28b_c3_recheck.txt` | Ready (does not depend on the null; pooled test descriptive) |
| 4.6.4, Table 12 | Few-shot R 14.3 / 18.2 / 49.2 / 47.7 / 30.7; instruct / few-shot 2.12 [1.25, 3.60], 0.59 [0.41, 0.85], 0.59 [0.44, 0.79], 0.81 [0.58, 1.13]; within a factor 2 at 3 of 4; few-shot words 10.4-11.3 against instruct 7.9-14.4 | `outputs/36_...` section 5; Table 12; `outputs/13_...` section 1 | Ready |
| 4.6.5 | Hand check 100 of 100; pair overlap; example words | unchanged from v1 (`outputs/22_...`, `16_...`, `20_...`, `23_...`, `26_...`) | Ready |
| Appendix D | Readings of D024 to D034 and outcomes against both nulls | `DECISION_LOG.md`; `outputs/17_...`, `22_...`, `27_...` to `31_...`, `36_...`, `37_...`, `38_...` | Ready |
| 1 | The earlier analysis (Qwen3.5, 0.8B-27B, kernel ratio falling with size) stayed within the lab and did not replicate outside one family | Researcher's account (chat, 2026-10-02) and `docs/paper_en.md` (historical); family confirmed by the researcher | Ready |
| 5, 6, 7 | Conclusions and limits | rest on the rows above; Table 13 | Advisor / Pepe (D035; wording of D026) |

## Tables and figures (draft v1 numbering; superseded where v2 differs)

| Draft | What | Source | Readiness |
|---|---|---|---|
| Table 1 | z of kernel ratio and circulation rate by group | `24_manuscript_tables.py` -> `outputs/24_manuscript_tables.md` (Table 1); same numbers as `outputs/17_filtered_vs_unfiltered.txt` section 14 | Ready |
| Table 2 | Cycle-length profile (observed / null) | `outputs/24_manuscript_tables.md` (Table 2); `outputs/17_...` section 7 | Ready |
| Table 3 | Pair types by WordNet relation | `outputs/20_pair_types.txt` section 1, parsed by script 24 | Ready (WordNet typing is generous, stated) |
| Table 4 | Matched Gemma3 pairs, five variants, exact ranges | `outputs/24_...` (Table 4); `outputs/19_count_intervals.txt` sections 2-4; `outputs/17_...` section 3 | Ready |
| Table 5 | Three-example prompt, both interval methods | `outputs/24_...` (Table 5); `outputs/19_...` section 6 | Ready |
| Table 6 | Equal coverage (D029): R of the zero-shot, few-shot and instruct graphs on the same entries, five random halves, whole-list R | `outputs/24_...` (Table 6) from `results_2026-10-02_Local/d029_survivor_restriction/results/`; `outputs/27_survivor_restriction.txt` | Ready |
| Table 7 | Instruct pairs contained by the zero-shot and the few-shot graph at equal coverage | `outputs/24_...` (Table 7), parsed from `outputs/28_defining_words.txt` section 3 and 5; `outputs/28b_c3_recheck.txt` | Ready (pooled test descriptive) |
| Table 8 | Defining words: Jaccard with the instruct definition, frame words, top-5 share | `outputs/24_...` (Table 8), parsed from `outputs/28_defining_words.txt` sections 1, 2, 4 | Ready |
| Table A1 | Per-graph results | `outputs/24_...` (Table A1) from `results_2026-10-01_Local/e2_filtered_default_main_32x/results/` and `e1d_null_unfiltered_32x/results/` | Ready |
| Appendix A validation table | Filter precision and recall | `outputs/14_dev_final.txt`, `14_test_scored.txt`, `14_filter_validation.txt`; strict: `14_strict_test_scored.txt`; locks `14_test_scored.lock`, `14_test_scored_strict.lock` | Ready (checked line by line on 2026-10-02) |
| Fig. 1 | Pipeline drawing | `25_manuscript_figures.py` (no data) | Ready; style to be set by Pepe |
| Fig. 2 | Observed vs null kernel ratio | `25_manuscript_figures.py` from the per-graph results (unfiltered and default) | Ready |
| Fig. 3 | Cycle-length profile | `25_manuscript_figures.py` | Ready |
| Fig. 4 | R against size (a: Gemma3; b: families) | `25_manuscript_figures.py`; error bars are the Poisson ranges of script 19 | Ready |
| Fig. 5 | R as built and on the same entries (zero-shot survivors), with five random halves | `25_manuscript_figures.py` from the primary results and `results_2026-10-02_Local/d029_survivor_restriction/results/`; same numbers as Table 6 | Ready |

Both scripts are deterministic (checked with two hash seeds); the draft's table rows and captions were compared with the generated file by
program on 2026-10-02 and match exactly.

## Statements in the text (draft v1 numbering and first-null R values; superseded where v2 differs)

| Section | Statement | Source | Readiness |
|---|---|---|---|
| Abstract, 4.2 | R of instruct 8.8-42.5 (median 19.3), pretrained 2.1-8.4, WordNet 15.7; unfiltered and strict ranges | `outputs/17_...` section 2; `outputs/24_...` "numbers quoted" | Ready |
| Abstract, 4.2 | Each instruct model shares 1-4 of WordNet's 27 pairs (Jaccard 0.010-0.055); two instruct models median 0.14 (0.03-0.33) | `outputs/20_pair_types.txt` sections 2-3; `outputs/18_mutual_pairs.txt` | Ready |
| 4.2 | Ten of WordNet's 27 pairs occur in some instruct graph; 363 different pairs; 77 % of occurrences shared | `outputs/18_mutual_pairs.txt`; registry E2 "What the mutual pairs are" | Ready |
| 4.2 | Seven ranges above WordNet's R, two below, eight contain it; 12 of 17 above by point estimate | `outputs/24_...` "numbers quoted" | Ready |
| 4.1 | Kernel at chance, circulation below the null for instruct models and WordNet; base graphs unstable | `outputs/24_...` Table 1; `outputs/17_...` sections 6, 11, 14 | Ready |
| 3.5 | Convergence study (6 graphs, 4-24 x E, 5 x too low by 12-90 %); R a median 19 % higher at 32 x | registry E1c and E1d results; `outputs/12_e1d_vs_e1.txt` | Ready |
| 3.5 | Floor applies to one graph (Gemma3-1B-pt, null mean 0.45) | `outputs/24_...` Table A1; registry E2 primary run | Ready |
| 3.6 | Hand labels, 42 % definitions for pretrained models; self-agreement 88.2 % (kappa 0.79) and 95.5 % (kappa 0.90); second pass of 58 rows | registry E2 status; `outputs/9_selfconsistency_agreement.txt`, `11_secondpass_summary.txt` | Ready; the interval between labelings is the researcher's statement (D022) |
| 3.6 | Filter drops 47-58 % of pretrained records, 0.0-0.7 % of the 17 instruct models | `outputs/15_filter_drop_rates.txt` | Ready |
| 4.3.1 | Ratio >= 2 for four of four pairs under both filters; stored text; frame words; ranges exclude 1 in 20 of 20, 2 in 15 | `outputs/24_...` Table 4; `outputs/17_...` sections 3, 10; D024, D025 | Ready |
| 4.3.1 | Frame words: "mean" in 217-292 definitions; pretrained median 4.9 to 3.3, instruct 19.3 to 19.5 | `outputs/17_...` sections 2, 12 | Ready |
| 4.3.1, 5, 6 | Filter leaves about 18.5 % of pretrained non-definitions (29 of 157 on test words) | `outputs/14_test_scored.txt` (base models: 157 non-definitions, 132 dropped, recall 81.5 %); RESEARCH_AUDIT F22 | Ready |
| 4.3.2 | Few-shot R 4.6 / 22.3 / 23.5 / 30.9 / 28.5; instruct / few-shot 1.91 / 1.19 / 0.83 / 0.89; exact and conservative ranges | `outputs/24_...` Table 5; `outputs/19_...` section 6 | Ready; the 1B result depends on the interval method (stated) |
| 4.3.2 | Within a factor 2 at four of four sizes by point estimates (default 1.91, 1.19, 1.20, 1.12; strict 1.57, 1.14, 1.15, 1.46), three of four by ranges | `DECISION_LOG.md` D024 (result and count-based reading); `outputs/17_...` section 4 | Ready |
| 4.3.3 | Hand check 100 of 100 definitions, 25 of 25 per model, filter keeps all 100 | `outputs/22_e3_check_summary.txt`; D027 | Ready (one labeler; form, not accuracy) |
| 4.3.3 | Examples of circular and wrong outputs (spring, 1B; quarterly, 1B) | `data/exp2_e3_check_KEY_do_not_open_until_done.csv` ids 66 and 89 (key opened after labeling) | Ready |
| 4.3.3 | Copy check: exact copies 11/12/2/1/2; at most 2.2 % in repeats | `outputs/16_e3_copy_check.txt` | Ready |
| 4.3.3 | Pair overlap: 55/68/69/76 % in some instruct model; Jaccard with matched instruct 0.15/0.17/0.22/0.20; Gemma3 pairs 0.12-0.28 (median 0.21); non-Gemma medians | `outputs/20_pair_types.txt` sections 2 and 4 | Ready |
| 4.3.3 | Example words: 12 words in the vocabulary; 5.1-5.5 % of E3 edges at 4B-27B; one pair with a headword | `outputs/23_e3_example_words.txt`; RESEARCH_AUDIT F25 | Ready |
| 4.3.4 | R against size: pooled rho +0.18; Gemma3 falls, Qwen2.5 flat, Qwen3 rises (rho +0.84, n = 6) | `outputs/17_...` section 15; RESEARCH_AUDIT F27 | Ready (descriptive) |
| 4.4 | E4: ratio median 1.11 (0.46-2.98), change x1.28; Spearman -0.09 (p 0.72), rho -0.01 (n 34, unfiltered) | `outputs/17_...` section 5; `outputs/13_controls_vs_main.txt` | Ready |
| 4.4 | E5: Gemma3 ratios 0.53-1.19, five of seven Qwen2.5 within about 2 (0.48-1.94), Qwen3 too sparse; unfiltered medians 1.3 and 1.9 | `outputs/17_...` section 5; registry E2 "Controls under the default filter" | Ready |
| 3.1 | Word list, 2,750 lemmas, Brown frequency >= 5; rare words in the list | `PROJECT_CONTEXT.md` 3; `data/sample_words/word_list_3k_v1.json` | Ready |
| 3.2 | Prompt, decoding, one run per model; E3 header and examples | `PROJECT_CONTEXT.md` 3; `experiments/e3_fewshot_base.py` lines 43-60; registry "Common settings" | Ready |
| 3.8 | Readings fixed in advance (D024, D025, D027) and their timing | `DECISION_LOG.md` | Ready |
| 1, 2 | How the cited sources are described (Kernel 7-12 % and Core as the union of sources in [VL16]; the degree-preserving randomization and short loops in [Lev12]; NP-completeness in [BM08]; 77.7 / 82.4 / 82.2 % in [Lin24]; and so on) | `REFERENCE_CHECK_2026-10-02.md` (each claim found in the source text) | Ready (checked by the assistant; verified by the researcher, 2026-10-02) |
| 3.1 | Gemma 3 270M is not in the Gemma 3 report (1B to 27B) and was announced on 14 August 2025; Qwen3-4B-Instruct-2507 is an update whose card cites the Qwen3 report | `REFERENCE_CHECK_2026-10-02.md` section 3 (arXiv abstract, Google Developers Blog, Hugging Face card) | Ready |
| 4.2 | Pairs typed hypernym or "no direct link" include close pairs (flavor-taste, location-place) and associations (eat-mouth, greet-hello) | `outputs/20_pair_types.txt` section 1 (examples of each type) | Ready (examples, not a count) |
| 4.3.3, 5 | Removing every mutual pair that involves an example word lowers the few-shot count by at most 13.8 % (1B) and 5.3-6.5 % (4B-27B) | `26_derived_numbers.py` -> `outputs/26_derived_numbers.txt` section 2 (from `outputs/23_e3_example_words.txt`) | Ready (derived) |
| 5, 6 | Of the 98 records the filter keeps from the 1B-27B pretrained models on the test words, 82 are definitions and 16 (16.3 %, about one in six) are not | `outputs/26_derived_numbers.txt` section 1 (from the per-model lines of `outputs/14_test_scored.txt`) | Ready (derived) |
| 4.3.5, 5, 6 | The filter drops 47.3 / 55.9 / 49.9 / 56.7 % of the valid zero-shot records at 1B-27B; 1,580 / 1,322 / 1,503 / 1,296 of 3,000 entries survive | `results_2026-10-02_Local/d029_survivor_restriction/restriction_sets.json` (`zero_shot_dropped_share`, `survivors`), `run.log`; D029 | Ready |
| 4.3.5 | Table 6: R of the zero-shot, fsS and itS graphs and of five random halves; the reading is mixed (1 of 4 "explains", 0 of 4 "does not"); R falls to 0.07-0.51 of the whole-list value (survivors 0.11-0.26; single random halves 0.07-0.51; corrected 2026-10-02); survivors inside the random range at 3 of 4 sizes | `outputs/24_manuscript_tables.md` Table 6; `outputs/27_survivor_restriction.txt` sections 1-3; D029 result block | Ready (the descriptive part is not pre-registered, stated in the text) |
| 4.3.5, 5 | At equal coverage instruct / zero-shot = 0.49 / 0.54 / 3.02 / 1.80, exact ranges include 1 at 3 of 4 sizes; fsS / zero-shot and itS / fsS include 1 at 4 of 4; whole-graph ratios 7.1 / 3.3 / 12.2 / 5.2 | `outputs/27_survivor_restriction.txt` section 5 (added after sections 1-4 had been read); Table 6; Table 4 | Ready (post hoc, labelled) |
| 4.3.5 | Observed pairs x0.21 / 0.20 / 0.18 / 0.27 against squared shares 0.28 / 0.19 / 0.25 / 0.19; null mean x0.85 / 0.74 / 1.70 / 1.35 | `outputs/27_survivor_restriction.txt` section 5 (last block) | Ready; the cause for the null is not established (stated) |
| 4.3.5 | The null mean had settled by 8 x edges swaps on three restricted 1B graphs and stayed to 256 x | `results_2026-10-02_Local/d029_convergence_probe_1B/summary.txt` | Ready (side test, 3 graphs x 8 chains, not in D029) |
| 4.3.5, 5 | Instruct pairs at equal coverage: 5 of 62 in the zero-shot graphs against 20 of 62 in the few-shot graphs on the same entries; 16 against 1, p = 0.0003; 52 different pairs 14 against 1, p = 0.001; example pairs | `outputs/28_defining_words.txt` sections 3 and 5; `outputs/28b_c3_recheck.txt` (same counts, second derivation); Table 7 | Ready (the pooled test is descriptive; section 5 was added after the first reading) |
| 4.3.5, 5 | Mean Jaccard of defining words with the instruct definition 0.11-0.17 (zero-shot) against 0.17-0.25 (few-shot), ratio 1.43-1.65, reading mixed; frame word in 30-43 % against 7-10 % of records; top-5 words carry 21-30 % against 12-15 % | `outputs/28_defining_words.txt` sections 1, 2, 4; Table 8 | Ready |

## Interpretations: decided by the researcher on 2026-10-02

The seven sentences that v0 flagged as interpretations were reworded in v1 as the researcher decided (chat, 2026-10-02), following the
proposals of `DRAFT_REVIEW_2026-10-02.md`. What each rests on:

| # | v0 sentence (section) | v1 wording | Rests on |
|---|---|---|---|
| 1 | "a statement about the density of the graph and not about its structure; we withdraw ..." (4.1) | "...about the degrees of the graph, chiefly how many links longer definitions create, and not about how the links are arranged; this corrects our earlier analysis" (Intro, 4.1) | The null fixes every word's in- and out-links, so what it shows is that the kernel ratio follows the degrees, density being the main part (r(kernel, edges) +0.799, +0.640 without Gemma3-270M, on the 08-09 graphs: RESEARCH_AUDIT section 1 and F15; not quoted in the draft). The earlier claim (docs/paper_en.md) was not presented outside the lab (researcher, chat 2026-10-02), so "corrects" is the right verb; the same account says it came from the first models run and did not replicate outside one model family (no file: the researcher's statement) |
| 2 | "near-synonyms in ordinary use, which WordNet's typing undercounts" (4.2) | "WordNet's relations type the pairs coarsely: some ... are close in ordinary use (flavor-taste, location-place), others are associations (eat-mouth, greet-hello)"; also in PROJECT_CONTEXT claim 2 | Examples in `outputs/20_pair_types.txt` section 1; no count |
| 3 | "...it requires a prompt, or a tuning, that makes the model write one-sentence definitions" (5) | "What the zero-shot pretrained models lack, and three examples supply, is not identified: most of the zero-shot outputs the filter keeps are definitions (82 of 98 ...), yet they form few mutual pairs" | `26_derived_numbers.txt` section 1; R of those graphs 2.1-8.4 (Table A1) |
| 4 | "the models converge on one another's pairs more than on WordNet's" (5) | "share more of their pairs with one another than with WordNet: median Jaccard 0.14 between two instruct models, above every instruct model with WordNet (0.010-0.055)"; "resemble", not "converge on"; pointer to the Prompt limitation | `outputs/20_pair_types.txt` sections 2-4 |
| 5 | The three open explanations of the zero-shot gap (5) | Four, each testable: (a) leaked junk, 16 of 98 kept records; (b) which words keep a definition (CPU test: limit each few-shot graph to the words whose zero-shot record survived); (c) what the surviving definitions say (CPU test: defining words of zero-shot and few-shot outputs); (d) sampling, split into noise (seeds) and a temperature effect (greedy run), both GPU | `26_derived_numbers.txt` for (a); (b) and (c) were run (D029, 2026-10-02; Section 4.3.5 and Section 5 of the draft report them) |
| 6 | "...of the kind the superficial-alignment picture would lead one to expect; the zero-shot gap is the part it leaves unexplained" (2) | "Our few-shot result fits this hypothesis [Zho23; Lin24]: three examples ... bring pretrained R to the instruct level at 4B and above. The hypothesis also predicts the zero-shot failures of format, which the filter removes; it does not say why the zero-shot outputs that are definitions form fewer mutual pairs" | LIMA's definition of the hypothesis (text checked); [Lin24] 77.7 / 82.4 / 82.2 %; REFERENCE_CHECK. The last clause was adapted on 2026-10-02 to the D029 result ("on the same entries, ... contain fewer of the instruct models' mutual pairs than the three-example outputs do"); the researcher to confirm |
| 7 | "The examples do not drive R" (4.3.3) | "R does not come from copying the examples or reusing their words: removing every mutual pair that involves an example word would lower the few-shot count by at most 14 % (1B) and 5-7 % (4B-27B)" | `26_derived_numbers.txt` section 2; copy check `outputs/16_e3_copy_check.txt` |

Other sentences that interpret rather than report, to read critically: the Discussion's reading that few examples make the pretrained model reach the
instruct level "given three examples" (the comparison is few-shot pretrained against zero-shot instruct); and "WordNet and the models differ in which
words form the excess" (descriptive, from Jaccard indices).

## Open items

- **Pepe and the advisor: D035.** Which null is primary (proposed: the double-edge swap null; not decided). Until then draft v2 gives both. The wording of D026 and the one-page claims sheet for the advisor (version 2, written before D029) are outdated: the zero-shot gap is absent by the rule of D024 against the double-edge null, and the instruct models' R is above WordNet's.
- **Pepe:** the references are verified (assistant's check of 2026-10-02, `REFERENCE_CHECK_2026-10-02.md`; the researcher's check the same day); no `.bib` exists yet. Answered by the researcher on 2026-10-02: no source is missing from Section 2 (rewritten as continuous text); no venue is decided and there is no length limit; the earlier
  "larger models converge" claim (Qwen3.5) was not presented outside the lab, so "corrects" is the right verb. The title is still open (five candidates were offered; D028 option A is in the draft).
- **Not rerun against the double-edge null:** the unfiltered, strict-filter, stored-text and frame-word variants (Table A2 is first-null only) and the v1 length analyses on unfiltered graphs (the length relation was repeated on the default-filter graphs, post hoc, in script 38). About 30 minutes of CPU.
- **Recommended by the review, not done (CPU):** R without each graph's most frequent words; a per-definition synonym rate. **GPU:** an instruction-tuned model with the few-shot prompt; several generation seeds and a greedy run.
- **Not done:** `DATA_LINEAGE.md` (raw data to figure); a second labeler.
