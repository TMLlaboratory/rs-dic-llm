# rs-dic-llm

Code and data for a paper on whether LLM-generated dictionaries "close" like human ones
(definition graphs, kernel, reciprocity excess R) and whether instruction tuning creates that
structure. Main researcher: Pepe. Advisor: Kumoi, who reviews and approves the paper.

## Read first

1. `research/README.md`: dated status, source hierarchy, rules.
2. `research/PROJECT_CONTEXT.md`: pipeline, claims and what would falsify them, terminology.
3. As needed: `research/RESEARCH_AUDIT.md` (what the repo shows actually happened),
   `research/EXPERIMENT_REGISTRY.md` (E1-E8, commands, outputs), `research/DECISION_LOG.md`.
4. For the paper text: `manuscript/draft_v2.md` (v1 and v0 are kept unchanged) and `research/EVIDENCE_MAP.md` (every number of the draft is traced there). v2 reports R against a double-edge swap null (D032) and puts the first null's values beside it; making that null
   primary is proposed (D035) and not decided. The advisor gave a green light on the framing of v1 (D026; reported by the researcher, 2026-10-02); v2 and the text written after D029 are still to be shown to the advisor. The citations were checked by the assistant (`research/REFERENCE_CHECK_2026-10-02.md`)
   and verified by the researcher (2026-10-02); do not describe a source beyond what that file records.

`docs/`, `plan.md` and `docs/paper_*` are historical progress material, not evidence.
Check the status table in `research/README.md` before proposing work: experiment status
changes often.

## Rules

- Never edit or delete definitions, metrics or result files. New output goes in a new dated
  folder `results_<YYYY-MM-DD>_<where>/`.
- Every number in a document or draft must come from a file in the repo, cited by path.
  No recalled or estimated values. If a value is not in the repo, say so.
- R means the rewiring-null ratio defined in `research/PROJECT_CONTEXT.md` section 4. Always name the null: "three-edge" is networkx `directed_edge_swap` (E1-E5, draft v1), "double-edge" is the directed double-edge swap of D032 (draft v2).
  `R_analytic` (key `reciprocity_excess` in E3/E4/E5 metrics JSONs made up to 2026-09-09) is
  a different quantity: never report it or compare it with 8.9 / 23.5. Quote R only from runs at
  the converged setting (E1d and later, 32 x edges swaps): the 5 x results of E1 are a median
  19 % lower.
- Audits and reviews produce findings, not silent fixes. Scientific choices go through
  `research/DECISION_LOG.md`; an agent may propose an entry but never mark it approved.
- Cite only references in the project `.bib` or verified by Pepe.
- Keep limitations honest, including the correction of earlier claims.
- Do not commit, push or publish unless asked. The working tree is dirty on purpose (the
  E3/E4/E5 result folders were moved).
- Structural proposals (new folders, protocols, context files) go to chat first; create files
  after a go-ahead. Explain statistics and graph concepts in plain terms.
- The non-definition filter (`src/rs_dic_llm/quality_filter.py`) is built, validated and frozen
  (D023, 2026-10-01). `research/audit_scripts/outputs/14_test_scored.lock` holds the hash it had
  when the 50 test words were scored, once. Do not edit its rules without a decision entry and a
  fresh hand-labeled sample: the 100 labeled words can no longer serve as held-out data.
  `quality_filter_strict.py` (the D024 bracket) has its own lock, `14_test_scored_strict.lock`.
- The E3 hand check (D027) was labeled and read once on 2026-10-02 (100 of 100 definitions, rule met;
  `research/audit_scripts/outputs/22_e3_check_summary.txt`). Do not re-score it or change its labels to alter the outcome.
- Manuscript: tables and figures are generated (draft v2: `research/audit_scripts/33_manuscript_tables_v2.py`, `34_manuscript_figures_v2.py`; draft v1: `24_manuscript_tables.py`, `25_manuscript_figures.py`); regenerate them,
  do not edit them by hand. A number added to the draft needs its source in `research/EVIDENCE_MAP.md`. Do not cite a reference the
  researcher has not verified.
- The three-edge null biases R toward 1 where mutual pairs involve words with few other links: its replicates keep such pairs (`research/audit_scripts/outputs/29_null_pairs.txt`, `35_double_swap_validation.txt`; D030, D032). The dependence of R on coverage found in D029
  (0.07-0.51 of the whole-list value), the zero-shot gap of draft v1 and the reading "instruct R equals WordNet's" came from it. Against the double-edge null R does not depend on coverage, the zero-shot gap is absent by the rule of D024, and instruct R (18.1-52.1) lies above WordNet's (18.1). Never quote
  a three-edge R alone to compare graphs of different density or coverage, and do not write that the zero-shot gap "survives" filtering or that R "falls with coverage" without this qualification. R also falls with mean definition length against the double-edge null (rank correlation -0.75 over 59 graphs; D034, post hoc), so conditions that differ in length are not compared by R alone.
  Equal-coverage comparisons (Table 10 of the draft, `outputs/36_double_swap_readings.txt`) and counts beside R remain the rule.
- Part of speech is out of scope for this investigation (D017): do not analyse it, add
  decisions about it, or build anything on the POS column of the labeling workbook.

## Commands

- Tests: `PYTHONPATH=src python -m pytest -q` (182 pass).
- Null model, CPU, resumable, deterministic seeds:
  `python -m experiments.e1_full_null --out results_<date>_Local/<name> --reps 100 --workers 10`
  (`--sets main e3 e4 e5` selects graphs). Since D020 use `--nswap-mult 32 --tries-mult 9600`:
  the old default of 5 x edges swaps left R 12-90 % too low on the graphs tested.
  Swap-count convergence study: `python -m experiments.e1c_null_convergence --out <folder>`.
- Filtered null runs (E2): add `--filter default|strict|extract --unit first_sentence|stored`
  (`--drop-imperatives` for the sensitivity); every filtered graph has the fixed 2,750-lemma node set.
  Results are read with `research/audit_scripts/17_filtered_vs_unfiltered.py`.
- Double-edge swap null (D032-D034, CPU, resumable): `python -m experiments.d032_double_swap_null --out results_<date>_Local/<name> --workers 12 --swap-mult 64` (graph lists are in the script), `d033_double_swap_full_stats`, `d034_controls_double_swap`; validation `d032_convergence`, `d032_networkx_persistence`.
  Readings: `research/audit_scripts/35` to `38`. Draft tables and figures: `33_manuscript_tables_v2.py`, `34_manuscript_figures_v2.py`.
- Generation (E3/E4/E5) needs a GPU, `transformers` and `HUGGINGFACE_HUB_TOKEN`; it is not
  available locally. Everything else (graphs, null model, filter, figures) is CPU.
- Environment used: Python 3.11, networkx 3.6.1, nltk 3.9.1. Record versions in run manifests.

## Layout

- `src/rs_dic_llm/`: the package the experiments import. `src/*.py` are older duplicates
  (audit F8); `experiments/null_model.py` still imports them.
- `experiments/`: runs (`run_experiment.py`, `e3_*`, `e4_*`, `e5_*`, `e1_full_null.py`).
- `data/sample_words/word_list_3k_v1.json`: 3,000 entries, 2,750 unique lemmas.
  `data/definitions/`: 23 paper models plus 10 older files that are not part of the paper;
  select models from `MODEL_REGISTRY`, never by glob.
- Results: `results_2026-08-09_Runpod/`, `results_2026-08-31_Runpod/`,
  `results_2026-09-09_Runpod/` (E3/E4/E5), `results_2026-10-01_Local/` (null model),
  `results_2026-10-02_Local/` (D029: survivor restriction; D030-D034: closed sub-dictionaries, null pairs, double-edge null, validation, controls).
- E2 labels: `data/exp2_labeling_workbook_labeled.xlsx` (work here; the original
  `exp2_labeling_workbook.xlsx` is a stale partial copy).
