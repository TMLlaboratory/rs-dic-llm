# Research Documentation

Control records for turning the rs-dic-llm investigation into a paper: what the project is,
what was actually done, what each experiment is, what was decided. First written 2026-10-01
from an audit of the repository. Start here.

## Status (2026-10-01)

| ID | Experiment | Status |
|---|---|---|
| E1 | Null model, 100 replicates, 65 graphs | **finished 2026-10-01** (unfiltered, 5 x swaps; `results_2026-10-01_Local/e1_null_unfiltered/`); **superseded by E1d (main graphs) and E1d controls (E3, E4, E5)**: its R is a median 19 % lower on the main graphs |
| E1b | Same, main 24 graphs at 15 x swaps (D007) | **finished 2026-10-01** (`results_2026-10-01_Local/e1b_null_unfiltered_15x/`); R about 13 % higher where it finishes; 10 of 24 graphs hit the swap budget (D020) |
| E1c | Null-model convergence check (D020 b), 6 graphs x 30 swap chains | **finished 2026-10-01** (`results_2026-10-01_Local/e1c_null_convergence/`): the null settles within 4-24 x edges; R at 5 x was too low on the six graphs tested (+12 % to +90 %, four picked because R moved most); setting 32 x edges confirmed (D020) |
| E1d | E1 at the converged setting (32 x edges swaps), 23 main graphs (D020) | **finished 2026-10-01** (`results_2026-10-01_Local/e1d_null_unfiltered_32x/`, 78 min): instruct R 9.4-42.5, base 2.1-9.0, WordNet 15.7; R a median 19 % above the 5 x values; the unfiltered baseline for the main graphs |
| E1d controls | E3, E4 and E5 graphs at the converged setting, 40 graphs (D021) | **finished 2026-10-01 13:03** (`results_2026-10-01_Local/e1d_null_unfiltered_32x_controls/`): few-shot base R reaches the instruct range (E3); Gemma3 keeps R without the template (E5); the 8-word cap moves R both ways (E4) |
| E2 | Non-definition filter + hand labels | **all labeling passes finished 2026-10-01**; extraction rule approved (D019); **filter built and validated (D023)**: on the 50 test words (scored once, rules frozen) precision of a drop 97.5 %, recall of non-definitions 77.7 % (base models 81.5 %), 0.4 % of definitions wrongly dropped; off-topic text is the weak class (F22); **re-run on the filtered graphs finished 2026-10-02 (next row)** |
| E2 re-run | Null model on the filtered graphs: default filter (primary), strict filter (D024), frame words removed (D025), stored text, imperatives; seven runs (a first-sentence-only run was dropped) | **finished 2026-10-02 00:27**: reading (i) of D024 (the four main Gemma3 pairs stay at 2x or more under both filters), E3 few-shot base R within a factor 2 of the instruct R at four of four sizes, reading (B) of D025 (the gap stays when six frame words are removed), and the gap stays with the whole stored text (7.1 / 2.2 / 10.0 / 3.4; the 4B pair is close to the line); `results_2026-10-01_Local/e2_*`; read with `audit_scripts/17_filtered_vs_unfiltered.py` |
| E3 | Few-shot prompt, base models | generated; converged R under the unfiltered, default and strict filters: 22-31 at 1B-27B, within a factor 2 of the same-size instruct R at four of four sizes (the reading of D024); hand check of 100 outputs **finished 2026-10-02 (D027): 100 of 100 are definitions, rule met** (F2) |
| E4 | Length control | generated; converged R, default filter: ratio to the main run 0.46-2.98 (median 1.11), no link to length; no hand validation (F14) |
| E5 | No chat template | generated; default filter: R stays within about a factor 2 without the template for the four Gemma3 and five of the seven Qwen2.5 models, the Qwen3 graphs are too sparse after filtering to read; no hand validation (F4) |
| D029 | Two CPU tests of the zero-shot gap: (b) null model on the E3 and instruct graphs limited to the zero-shot survivors and on five random restrictions of the same size, (c) defining words of zero-shot, few-shot and instruct definitions | **finished 2026-10-02** (`experiments/d029_survivor_restriction.py`, 28 graphs x 100 replicates, 03:24-04:23 JST, `results_2026-10-02_Local/d029_survivor_restriction/`; read with `audit_scripts/27_survivor_restriction.py` and `28_defining_words.py`). Readings fixed in D029 before the run: (b) mixed, (c1) mixed, (c3) content differs. Beyond the readings: limiting a graph to about half of the entries lowers R to 0.07-0.51 of its whole-list value (survivors 0.11-0.26, single random halves 0.07-0.51), and at equal coverage the zero-shot gap shrinks (instruct / zero-shot 0.49 / 0.54 / 3.02 / 1.80 against 7.1 / 3.3 / 12.2 / 5.2). **Superseded by D030-D034 (next row): these R values are against the E1 null, which keeps pairs it cannot move; against a double-edge swap null R does not depend on coverage.** |
| D030-D034 | The null model, the scale test and the prompt controls (CPU): D030 where the null's pairs come from and closed sub-dictionaries; D031 convergence of R on WordNet's with size; D032 a double-edge swap null that can break every pair, with the readings that rest on R repeated; D033 kernel, circulation and cycles against it; D034 the prompt controls | **finished 2026-10-02** (`experiments/d030_*.py`, `d032_*.py`, `d033_*.py`, `d034_*.py`; results `results_2026-10-02_Local/d030_*` to `d034_*`; read with `audit_scripts/29` to `38`). The E1-E5 null (networkx `directed_edge_swap`) keeps mutual pairs it cannot move and biases R toward 1 in sparse graphs (up to 10.40 of 12.40 null pairs are observed pairs). Against the double-edge null: R does not depend on coverage; the zero-shot gap is absent by the rule of D024 (6.4 / 1.3 / 2.0 / 0.9); instruct R 18.1-52.1 against WordNet 18.1; the order of the 17 instruct models by R changes (rank correlation +0.07 with the first null); kernel, circulation and cycle results are unchanged; no consistent approach of R to WordNet's with size (D031); the factor 2 of the prompt controls stands (D034), and R falls with definition length (post hoc, rank correlation -0.75 over 59 graphs). **Which null is primary: D035, proposed, not decided.** Draft Sections 4.2-4.6 |
| E8 | WordNet-gloss similarity | not started; exploratory, non-blocking |

Paper drafting was agreed on 2026-10-02 (framing D026). **Current draft: `../manuscript/draft_v2.md` (2026-10-02; v1 and v0 kept unchanged):** v2 follows an outside review of v1 and decisions D029-D034; it reports R against the double-edge swap null with the first null's values beside it, which changes several conclusions of v1 (D032, D035). v1 was drafted on the researcher's approval of D026 and D028 while the advisor was
unavailable; the advisor then gave a green light on the framing of v1 (reported by the researcher, 2026-10-02); v2 and the text written after the D029 result are still to be shown to the advisor; the
references were checked by the assistant and verified by the researcher (`REFERENCE_CHECK_2026-10-02.md`). Section 2 was rewritten as continuous text and Figure 5 added the same day. The E3 hand check
(D027) passed on 2026-10-02 (100 of 100 outputs are definitions), so the E3 result stands within its stated limits. Decisions D001-D025 were taken on 2026-10-01, D026 to D029 on 2026-10-02 (D017
was withdrawn as out of scope); D030-D034 were proposed by the assistant and approved in general terms by the researcher on 2026-10-02 ("fix the following"), D035 is proposed and not decided. The advisor confirmed D003, D005, D007, D012, D013,
D015, D016 and D020 (reported by the researcher, 2026-10-02) and is still to be informed of D018, D019, D021, D022, D023, D024, D025, D027, D028 and D029 to D035 (`DECISION_LOG.md`); the advisor's green light on the framing of D026 was reported on 2026-10-02.
Update this table whenever a status changes and write the date.

## Documents

| File | Purpose |
|---|---|
| `PROJECT_CONTEXT.md` | What we study, pipeline, claims and what would falsify them, terminology. |
| `RESEARCH_AUDIT.md` | What the repository shows actually happened; discrepancies F1-F30 with evidence (F29: the null of every R so far biases R; F30: R falls with definition length); E2 label review. |
| `EXPERIMENT_REGISTRY.md` | E1-E8: purpose, inputs, commands, outputs, status, remaining work; data locations. |
| `DECISION_LOG.md` | Decisions D001-D035 with options, resolution and approvals (D035 proposed, not decided). |
| `EVIDENCE_MAP.md` | Manuscript statement to evidence, with readiness; the interpretations to check; open items (created 2026-10-02). |
| `../manuscript/draft_v2.md`, `draft_v1.md`, `draft_v0.md`, `figures_v2/`, `figures/` | Drafts of the paper and their figures (2026-10-02): v2 current (R against the double-edge swap null, D032; provisional until the researcher and the advisor decide D035 and the advisor confirms D026), v1 and v0 kept unchanged; citations checked by the assistant and verified by the researcher. |
| `REFERENCE_CHECK_2026-10-02.md` | What each cited source says, checked against the original text; what was corrected in the draft; what is still unchecked. |
| `DRAFT_REVIEW_2026-10-02.md` | Review of the draft's interpretations and a partial reference and venue check, written by another session; its interpretation proposals were applied in v1. |
| `CLAIMS_SHEET_2026-10-02.docx`, `.pdf` | One-page claims sheet for the advisor: a dated snapshot of claims 1-3 (`PROJECT_CONTEXT.md` stays the record). **Outdated:** written before D029-D034; do not send it as it stands. |
| `E2_LABELING_INSTRUCTIONS.md` | How to label the E2 workbook (solo labeler). |
| `audit_scripts/` | Scripts and recorded outputs behind the audit findings, the label review, the extraction rule's effect and the self-consistency sheet and its agreement script, the filter validation and its application (scripts 14-16), the filtered-versus-unfiltered readings and count-based ranges (17-19), pair typing (20), the E3 check sheet and its reading (21, 22), the E3 example words (23), the tables and figures of the manuscript (24, 25), the derived numbers it quotes (26), and the two CPU tests of the zero-shot gap (D029: 27 survivor restriction, 28 defining words, 28b second derivation of the pair counts), then D030-D034 (29 null pairs, 30 closed sub-dictionaries, 31 scale, 32 Qwen3 thinking check, 33 and 34 tables and figures of draft v2, 35 validation of the double-edge null, 36 its readings, 37 kernel/circulation/cycles, 38 prompt controls and definition length). `parked/` holds a script set aside as out of scope. |

Planned, to create when its inputs exist: `DATA_LINEAGE.md` (raw data to paper figure). `EVIDENCE_MAP.md` and `manuscript/` were created on
2026-10-02 with the first draft. Do not create files earlier than their inputs; empty control files go stale.

## Source hierarchy

1. Code, data and result files in the repository (what actually ran).
2. `research/` (audited reconstruction and decisions).
3. `docs/for-pepe/roadmap_en.md`, `docs/research-direction-2026-09_en.md` (advisor's plan,
   2026-09-01; a plan, not a record).
4. Historical, not evidence: `plan.md`, `docs/paper_*`, `docs/results-slides.md`,
   `docs/style-findings-slides.md`, `docs/study_guide/`, `results_2026-07-21_TogetherAI/`,
   `logs/`, `AA_semi-resources/`.

## Where things are

- Definitions: `data/definitions/` (main run, 23 paper models plus 10 files that are not paper
  models); `results_2026-09-09_Runpod/results_e{3,4,5}*/definitions/`.
- Metrics: `results_2026-08-09_Runpod/`, `results_2026-08-31_Runpod/`,
  `results_2026-09-09_Runpod/`; null model: `results_2026-10-01_Local/`.
- Code: `src/rs_dic_llm/` (the package the experiments use; `src/*.py` are older duplicates,
  F8), `experiments/`, `tests/`.
- Word list: `data/sample_words/word_list_3k_v1.json`.
- E2 labels: `data/exp2_labeling_workbook_labeled.xlsx` (work here; the original
  `exp2_labeling_workbook.xlsx` holds an older partial copy of the same labels).
- Null-model runs resume when interrupted: re-run the command recorded in
  `EXPERIMENT_REGISTRY.md` (E1d, E1d controls) with the same output folder.

## Rules for any agent working in this repository

1. Read this file, then `PROJECT_CONTEXT.md`, before doing anything else.
2. Never edit or delete definitions, metrics or result files. New output goes in a new dated
   folder. Never overwrite a file you did not create in this session without asking.
3. Every number in a document or draft must come from a file in the repository and cite its
   path. If it is not there, say so; do not recall or estimate values.
4. Do not report the `reciprocity_excess` field of metrics JSONs made up to 2026-09-09 (it is
   `R_analytic`, F1, D008). R means the rewiring-null R defined in `PROJECT_CONTEXT.md`; always name the null ("three-edge" = networkx `directed_edge_swap`, E1-E5 and draft v1; "double-edge" = D032, draft v2). A three-edge R is biased toward 1 in sparse graphs (D030, D032).
5. Audits produce findings, not fixes. When code or data contradicts a document, record it in
   `RESEARCH_AUDIT.md` and ask; scientific choices go through `DECISION_LOG.md`.
6. Cite only references in the project `.bib` or that the researcher has verified.
7. Keep limitations honest, including the correction of earlier claims.
8. Status lines need a date. A status without a date is treated as stale.
9. Do not commit, push or publish without being asked.
10. Part of speech is out of scope (D017): no analysis or decision builds on the POS column of
    the labeling workbook or on the `wrong-pos` tag.
