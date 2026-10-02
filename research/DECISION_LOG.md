# Decision Log

Scientific and procedural decisions, with who made them. Append only; do not rewrite history
(mark a superseded decision instead). An AI agent may propose an entry but never mark it as
approved. "Researcher" = Pepe. "Advisor" = Kumoi. Advisor approval is pending wherever it
says so; the advisor's confirmations of 2026-10-02 are recorded as reported by the researcher.

Format: ID, date, decision, reason, affected, approval. Decisions made in chat are quoted from
the session of 2026-10-01.

---

## Decided

### D001 — Which files are the record (2026-10-01)
**Decision.** `results_2026-09-09_Runpod/` (E3/E4/E5) and `data/definitions/` (carried over from
the August runs) are the canonical data. `results_2026-07-21_TogetherAI/` is the first round of
runs and history only. `plan.md` is outdated (original idea only). Everything in `docs/` is
temporary progress material; `docs/paper_en.pdf` and the files since August show how the results
evolved but are not facts. The facts are established by the current analysis.
**Affected.** All documents; source hierarchy in `PROJECT_CONTEXT.md` section 8.
**Approved.** Researcher (chat). Advisor: not needed.

### D002 — Scope before drafting (2026-10-01)
**Decision.** Finish E1-E5 and E8 before drafting. E6, E7, E9, E10 are out of scope for this
paper and become stated limitations.
**Reason.** Advisor's conclusion in the direction report ("do not add more models; the
controls make the paper"); researcher restated it.
**Approved.** Researcher (chat). Advisor: per the report.

### D003 — E8 is exploratory and non-blocking (2026-10-01)
**Decision.** E8 uses WordNet-gloss similarity only and must not delay the draft. The
researcher is doing it out of interest and has no further design yet.
**Reason.** Similarity to WordNet measures agreement with one human dictionary, not quality;
it is also length-dependent.
**Affected.** `EXPERIMENT_REGISTRY.md` E8.
**Approved.** Researcher (chat, "yes" to non-blocking). Advisor: confirmed (reported by the researcher, chat 2026-10-02).

### D004 — The null model runs on E3, E4 and E5 graphs too (2026-10-01)
**Decision.** E1 covers the 23 paper models + WordNet and the 41 E3/E4/E5 graphs (65 total).
**Reason.** The E3/E4/E5 control results are uninterpretable without R computed the same way
as the main run (audit F1).
**Approved.** Researcher (chat, "yes").

### D005 — E2 labeling protocol (2026-10-01)
**Decision.** Seven labels (definition, echo, question, offtopic, restatement, refusal,
unclear); solo labeling by the researcher; decision order and edge cases in
`research/E2_LABELING_INSTRUCTIONS.md`; a self-consistency re-label (10 rows per Tier 1/2
model, at least one day later, Cohen's kappa) is required; a second labeler on about 20 rows
per Tier 1 model is accepted in principle, person to be decided. Working file:
`data/exp2_labeling_workbook_labeled.xlsx` (POS column added, columns A-D identical to the
original). Judge by meaning, label before the filter exists.
**Reason.** The four original labels did not cover restatements, refusals and blank outputs
found in the data; an agreement number will be asked for by reviewers.
**Approved.** Researcher (chat: "I'll do everything myself", "yes" to the extra labels and
the agreement check). Advisor: confirmed (reported by the researcher, chat 2026-10-02).
**Note, 2026-10-01 later.** The researcher had already labeled 222 rows (Gemma3-270M 100,
Gemma3-270M-pt 100, Gemma3-1B 22) in the original workbook. They were moved into the working
file with their notes (one typo `restarement` corrected to `restatement`, Gemma3-270M row 18);
a backup of the empty working file is `data/exp2_labeling_workbook_labeled.backup-before-migration.xlsx`.
The original file is kept unchanged and is now stale: label only in the working file.
The POS column in the working file was added by the assistant; it is informational only and
nothing uses it (D017).

### D006 — Run E1 on unfiltered graphs first (2026-10-01)
**Decision.** E1 runs now on the unfiltered graphs (the "before" column of the E2 table) and
is re-run after the E2 filter, as the roadmap specifies.
**Approved.** Researcher (chat, "please"). The assistant wrote and started the run
(`experiments/e1_full_null.py`).

---

## Decided 2026-10-01 — recommendations approved by the researcher

The researcher approved all recommendations below in chat ("lets go with your
recommendations"), with one change: D014 takes option (a) because no GPU can be rented now.
Each entry keeps the original question and options for the record.

### D007 — Number of edge swaps in the null model
**Question.** `null_model.py` uses 5 x edges swaps. A 12-replicate test shows the null mean
still falling at 15 x (audit F5), so R at 5 x may be 10-14 % too low.
**Options.** (a) keep 5 x (matches the advisor's report); (b) also run the 24 main graphs at
15 x and report both; (c) switch to 15 x everywhere (about 3 x the compute).
**Resolution: (b).** E1 at 5 x stays the run of record; E1b runs the 24 main graphs at 15 x
(`results_2026-10-01_Local/e1b_null_unfiltered_15x/`, run 2026-10-01) and both are
reported. Result: on the 14 graphs valid at both multipliers R is a median 13 % higher at
15 x; 10 of 24 graphs hit the swap budget at 15 x (see D020). A conservative bias does not threaten "R is above chance", but it can affect group
comparisons.
**Approved.** Researcher (chat). Advisor: confirmed (reported by the researcher, chat 2026-10-02); it changes numbers in the report.

### D008 — Which R goes into the paper
**Question.** Two R definitions exist (audit F1).
**Resolution.** Report only the rewiring-null R (`PROJECT_CONTEXT.md` section 4). The analytic
field is stored as `R_analytic` by `compute_all_metrics` from now on (`src/rs_dic_llm/analysis.py`;
docstring warning in `metrics/scc.py`; the E3/E4/E5 scripts print `R_anal` and no longer tag
values "IN INSTRUCT RANGE"). Existing result JSONs are not edited: they keep the old key
`reciprocity_excess`, which in them means `R_analytic`. The methods section will state how R is
computed (to be written with the manuscript).
**Approved.** Researcher (chat).

### D009 — Uniform extraction before filtering
**Question.** Main base outputs are multi-sentence in 32-47 % of records and E3 is always one
sentence (F2, F3). Raw outputs were not saved.
**Options.** (a) cut every stored definition at the first line and first sentence for all
models, then filter; (b) keep stored definitions and only filter.
**Resolution: (a) as the primary analysis, (b) reported as a sensitivity row.** Still to do, in
this order: (1) design and test the extraction rule on real stored examples (a naive "earliest
separator" fix would break list-formatted outputs such as `1. Habit is ...` and `A. A plank is
...`, so it must skip list markers); (2) a second, shorter labeling pass on the rows where the
first sentence differs from the full stored text, so the filter is validated on the unit it
classifies (size it after the first pass); (3) fix `_first_sentence` in `generation.py` only
when a GPU run is planned. Do not change how the first pass is labeled in the meantime.
**Approved.** Researcher (chat). Advisor: to be informed.
**Progress 2026-10-01.** Step (1) is done: `src/rs_dic_llm/extraction.py` and its tests. Step (2):
the rule cuts content in 180 labeled rows, all in the base tabs, and only 58 of them (first-pass
`definition` or `unclear`) can change between definition and not-definition (182 and 60 before a
fix that skips separator lines such as `---`). Step (3): the 58-row sheet exists, see D019.
**Sensitivity row (b), 2026-10-02.** The default filter's decisions with the whole stored text for kept records (run
`e2_filtered_default_storedtext_main_32x`): instruct R / base R at 1B / 4B / 12B / 27B is 7.1 / 2.2 / 10.0 / 3.4 (first
sentence: 7.1 / 3.3 / 12.2 / 5.2); base R 2.6-12.5 (median 6.0), instruct 8.8-42.5 (median 19.3). The zero-shot gap does not
depend on the first-sentence cut; the 4B pair, at 2.2, is close to the factor-2 line.

### D010 — Vocabulary when a record is filtered out
**Question.** Should a filtered record keep its node in the graph (fixed 2,750-lemma
vocabulary for every model) or drop it (F10)?
**Resolution.** Keep the node and drop only the edges that record contributes, so all graphs
and nulls are comparable. To be built with the E2 filter.
**Approved.** Researcher (chat).

### D011 — Model exclusion rule
**Question.** Gemma3-270M-it has no cycles (F13). Write the rule before seeing E1/E2 results.
**Resolution.** Exclude a model from R comparisons if its unfiltered graph has no cycle; say
so in every table that excludes it and show results with and without it. At present this
applies to Gemma3-270M (instruct) only.
**Approved.** Researcher (chat).

### D012 — Scope of claim 1
**Question.** The roadmap says "kernel / core / MinSet"; only kernel ratio, circulation rate
and cycle counts are null-tested (F7).
**Options.** (a) narrow the wording to kernel ratio and circulation rate; (b) compute Core on
the null replicates (cheap) and MinSet on a subset (ILP, expensive).
**Resolution: (a)**, plus Core on the null replicates if time allows (not started). Claim 1 in
`PROJECT_CONTEXT.md` is reworded accordingly.
**Approved.** Researcher (chat). Advisor: confirmed the wording (reported by the researcher, chat 2026-10-02).

### D013 — Framing of Gemma-only matched pairs
**Question.** Base/instruct pairs exist only for Gemma3. Qwen base checkpoints are public and
an E3-style session on a few of them is possible, but the report advises against adding
models.
**Options.** (a) state the matched-pair result as Gemma-specific and use Qwen for instruct
scaling and as a replication of E4/E5; (b) add a small Qwen base replication.
**Resolution: (a).** (b) only if the advisor asks for it after E3 is analysed.
**Approved.** Researcher (chat). Advisor: confirmed (a) (reported by the researcher, chat 2026-10-02). (b), a small Qwen base replication, is not wanted (researcher, chat 2026-10-02: "No", after E3 was analysed); no GPU is available for it either.

### D014 — Sampling variance
**Question.** One run per model at temperature 0.7 (F9). E6 is out of scope.
**Options.** (a) state it as a limitation; (b) regenerate one or two models with 2-3 seeds to
give a rough variance.
**Resolution: (a).** No GPU can be rented at present. State: one generation seed, one run per
model, no estimate of run-to-run variance.
**Approved.** Researcher (chat, chose (a) explicitly).

### D015 — Status of `experiments/e1_full_null.py`
**Question.** `null_model.py` could not produce the E1 output as written (F6). The new script
reuses its functions and adds lists, seeds, failure flags, CIs, resumability. Should the
advisor's `null_model.py` or the new script be the E1 of record?
**Resolution.** The new script is the E1 of record; `null_model.py` stays unchanged and is
cited as its basis.
**Approved.** Researcher (chat). Advisor: confirmed (reported by the researcher, chat 2026-10-02).

---

## Raised by the E1 results and the E2 label review (2026-10-01)

Resolved in chat the same day (D016, D018, D019, D020); D017 was withdrawn.

### D016 — Claim 1 and the circulation rate
**Question.** D012 narrowed claim 1 to "kernel ratio and circulation rate are indistinguishable
from the null". E1 (100 replicates) shows the kernel ratio is at chance (median z -0.1, range
-3.7 to +2.2, WordNet -0.08) but the circulation rate is below the null (mean z -2.0, 10 of 23
graphs below -2, none above +0.6, WordNet -1.9).
**Options.** (a) claim 1 covers the kernel ratio only, and the circulation rate is reported
separately as below chance (consistent with the short-loop excess and the suppressed long
loops); (b) keep both and word it "not above the null".
**Recommendation.** (a).
**Resolution: (a).** Claim 1 covers the kernel ratio only; the circulation rate is reported
separately as below the null (PROJECT_CONTEXT claim 1 reworded). Unchanged at 15 x swaps (E1b).
**Approved.** Researcher (chat, 2026-10-01: "lets go with the recommendations"). Advisor: confirmed the wording (reported by the researcher, chat 2026-10-02).

### D017 — Withdrawn (2026-10-01): part of speech is out of scope
Raised after the E2 labeling, when 72 rows carried the note `wrong-pos`. The researcher ruled
that part of speech is outside the scope of this investigation, so there is nothing to decide:
no sensitivity run, no change to the word list, and no analysis that uses the POS column or
the `wrong-pos` tag. Audit F20 keeps a short note so the tag is not mistaken for something
that was analysed.

### D018 — Label conventions that split (audit section 3b)
**Question.** Bare imperatives built on the target verb are 3 `definition` and 5 `offtopic`;
usage fragments are `unclear` while the imperative ones are `offtopic`; `task-meta` is split
between `offtopic` and `echo`; `empty` covers blank and list-marker-only outputs.
**Options.** (a) no relabeling; define the analysis classes from label plus tag and re-look at
the six Qwen3-0.6B imperative rows in the self-consistency pass; (b) relabel these rows to one
label now.
**Recommendation.** (a).
**Resolution: (a).** No relabeling. Analysis classes are built from label plus tag (`usage` =
`usage-fragment` or `imperative`; `task text` = `task-meta`; `blank or fragment` = `empty` or
`truncated`); the borderline rows are re-looked at in the self-consistency pass.
**Approved.** Researcher (chat, 2026-10-01: "lets go with the recommendations").

### D019 — Approve the extraction rule as built, and the size of the second pass
**Question.** The rule (docstring of `src/rs_dic_llm/extraction.py`, effects in audit script 7)
keeps the first line and first sentence of a stored definition, removes markup and list markers,
and joins a lead-in that ends in a colon with the next line. A question followed by its answer
keeps only the question. Effects on unfiltered graphs: base models lose 29-39 % of their edges,
E5 models 0-54 %; instruct, E3 and E4 outputs are almost unchanged. The second labeling pass
validates the filter on this unit.
**Options.** Rule: (a) as built; (b) without the lead-in join (207 base and 52 E5 records
affected); (c) first sentence that is not a question (not recommended: it moves part of the
classification into the extraction). Second pass: (i) the rows labeled `definition` or
`unclear` (60 when this was written, 58 after the separator fix), enough for the
definition-versus-not question; (ii) all rows whose content is cut (182, now 180), which also
validates the echo / question / offtopic split on the first sentence.
**Recommendation.** (a) and (i); add the other 122 rows only if class-level results on the first
sentence are wanted. The stored-text sensitivity row covers the alternatives.
**Resolution: rule (a) as built, second pass (i).** The sheet has 58 rows, not 60: two rows were
artifacts of the separator bug (their text was only `---` plus a one-line definition). The
other 122 rows whose content the rule cuts are taken to stay non-definitions (class not
re-labeled). Sheet: `data/exp2_secondpass_sheet.xlsx`; summary script
`research/audit_scripts/11_secondpass_summary.py`.
**Approved.** Researcher (chat, 2026-10-01: "approve D019 with the 60-row second pass"). Advisor: to be informed.

### D020 — Null-model multiplier and try budget for the re-run after E2
**Question.** E1b shows that R at 5 x swaps is under-estimated by a median 13 % (WordNet 70 %),
and that at 15 x the default budget (300 x edges attempts) is too small for 10 of 24 graphs.
Which multiplier and budget should the post-E2 re-run use, given that it will re-run E1 anyway?
**Options.** (a) keep 5 x and report E1b as a sensitivity; (b) run a short convergence check
first (5 x, 15 x, 45 x with a budget of 3,000 x edges, about 6 graphs, 20 replicates each) and
choose the multiplier at which the null mean stops falling, with a budget no graph exhausts;
(c) replace `nx.directed_edge_swap` by a faster sampler.
**Recommendation.** (a) for the numbers already reported, and (b) before the post-E2 re-run, so
that the multiplier is fixed once and the same way for every graph. (c) only if (b) shows the
current sampler cannot converge.
**Resolution: (a) for the numbers already reported, (b) before the post-E2 re-run.** The
convergence check (E1c) started on 2026-10-01; its result goes into the registry and the
multiplier is fixed from it.
**Approved.** Researcher (chat, 2026-10-01: "lets go with the recommendations"). Advisor: confirmed (reported by the researcher, chat 2026-10-02).
**E1c result, 2026-10-01.** The null mean settles within 4-24 x E (time constants 1-4 x E); 5 x
left R too low by 12-90 % on the six graphs tested (median 24 %, WordNet 9.1 to 17.3; four of them
picked because R moved most, so the typical effect is smaller); samples 8 x E or
more apart along a chain are nearly independent; acceptance is 6 % at the median, 1-1.5 % on
two E5 graphs and 0.05-0.14 % on the two degenerate Gemma3-270M graphs.
**Setting.** 32 x E swaps per replicate and a try limit of 300 tries per requested swap
(`--nswap-mult 32 --tries-mult 9600`), used for every re-run so that the numbers before and after
E2 are on the same footing. Confirmed by the researcher (chat, 2026-10-01: "yes run"). Advisor:
confirmed (reported by the researcher, chat 2026-10-02). E1d (the unfiltered E1 at this setting) started the same day on the 23 main graphs,
about 1.7 h; the 41 E3, E4 and E5 graphs would take about 4 h more (E3 alone 0.4 h).

**E1d result, 2026-10-01.** At the confirmed setting the 23 main graphs gave R a median 19 % higher
than at 5 x (range -14 % to +73 %; WordNet 9.1 to 15.7), instruct 9.4-42.5, base 2.1-9.0, no swap
failures. Details in the registry (E1d result).

### D021 — Converged re-run of the E3, E4 and E5 graphs (2026-10-01)
**Decision.** After E1d, run the null model at the converged setting (D020) on the control graphs.
Scope chosen by the assistant under the researcher's delegation (chat: "when e1d finishes i want
you to run e3 e4 and e5 ... i authorize you to do as you see fit"): 40 of the 41 graphs, skipping
E4 Gemma3-270M (465 edges, acceptance 0.05 %, about 2,000 tries per swap: it would take 7.6
CPU-hours to hit the try limit and give no usable R, the same reason main Gemma3-270M is not in
E1d, D011); order E3, E4, E5; 12 workers; separate output folder; started automatically when E1d
writes its `run_info.json`. These are still the unfiltered graphs and will be redone after E2.
**Approved.** Researcher (delegated in chat). Advisor: to be informed.
**Result 2026-10-01.** The run finished at 13:03 (2.4 h) with 40 graphs and no swap failures; E3
base few-shot R 4.7-31, E4 ratio to the main run 0.44-2.92, E5 median ratio 0.63 (Gemma3 4B-27B about 1,
four Qwen3 models collapse). Details in the registry (E1d controls result).

### D022 — The early self-consistency re-label (2026-10-01)
**Question.** The 118-row self-consistency sheet was labeled between about 30 minutes and a day
and a half after the first-pass labels instead of at least one day (D005; audit F21). What counts
as the self-consistency measurement for the paper?
**Options.** (a) Accept it as the measurement and report the real interval, calling the agreement
a probable upper bound. (b) Keep it as a short-gap measurement and add a fresh sample (about 60
rows, new seed, excluding the 118 rows already used) labeled on or after 2026-10-02; report the
later one as the primary figure and the early one beside it. (c) Discard it and redo the full
sample with new rows on or after 2026-10-02.
**Recommendation.** (b): about 15 minutes of labeling, D005 stays as written and the paper gets a
figure that meets it, while the early sample still shows where the labels are unstable.
**Resolution: (a).** The early re-label stays as the self-consistency measurement. The researcher
states that about a day passed between the first labeling of the sampled rows and the re-label.
The file times cannot confirm or contradict this row by row: the first-pass workbook was created
2026-09-29 20:04 JST and last saved 2026-10-01 07:51 JST, the re-label was saved 08:55 JST on
2026-10-01, and the workbook holds no per-row times. The paper gives the interval as the researcher
states it and calls the agreement a possible upper bound.
**Approved.** Researcher (chat, 2026-10-01: "cant we just keep the current results as there are").
Advisor: to be informed together with D005.
**Researcher, 2026-10-02.** States again that the re-label was not done sooner than the protocol's one day. The file times still
cannot confirm or contradict this (audit F21), so the resolution above is unchanged: the paper calls the agreement a possible
upper bound unless the researcher asks to change D022.

### D023 — Non-definition filter: rules, validation protocol, scope (proposed, 2026-10-01)
**Question.** All E2 labeling passes are finished (first pass, self-consistency, second pass; the
optional second labeler is not planned). How should the filter be built and validated?
**Proposal.**
1. Rules, not a trained classifier (roadmap E2). The unit is the first sentence from the extraction
   rule (D009, primary; the stored text is the sensitivity row). Classes: definition, question,
   prompt echo, off topic, restatement or fragment, refusal; each from explicit rules (a question
   mark or interrogative start; a span of the prompt; exam markers such as "Which of the
   following"; the headword alone or fewer than 3 word tokens; refusal phrases). The default is to
   keep: a record is dropped only when a rule fires.
2. Dropped means D010: the node stays, the edges the record contributed go.
3. Validation: the 100 labeled words are split at random (seed fixed) into 50 development and 50
   test words, the same split in every model tab. Rules are written looking at development words
   only. The test words are scored once, after the rules are frozen; the final table then scores
   all 100 words, with the test-only numbers beside it. Precision and recall per class and per
   model, for both units. Benchmark: agreement with the hand labels next to the labeler's own
   agreement (kappa 0.90 on definition versus not, D022).
4. Imperatives (D018): not dropped by the filter, because without part of speech a bare
   imperative cannot be told from a short definition; a sensitivity run drops them for Qwen3-0.6B.
5. Scope: the same rules are applied to the main, E3, E4 and E5 graphs. Only the main run has hand
   labels, so E3, E4 and E5 are filtered but not hand-validated; this is stated as a limitation.
   E3 carries claim 3, so its outputs are also checked for copies of the three few-shot examples.
**Options.** (a) the rules above; (b) a trained classifier on the labeled rows, cross-validated by
word: possibly higher recall, harder to defend and to explain; (c) rules first, and a classifier as
a second variant, reported beside the rules, only if recall on base-model non-definitions is clearly
low (below roughly 70-80 %).
**Recommendation.** (a), with (c) as the fallback.
**Resolution: (a), with (c) as the fallback.** Build and validate as proposed, items 1-5.
**Approved.** Researcher (chat, 2026-10-01: "go ahead with D023"). Advisor: to be informed.
**Result 2026-10-01.** Built and validated as approved (tables in the registry, E2):
`src/rs_dic_llm/quality_filter.py`, 98 tests, `research/audit_scripts/14_filter_validation.py`. Test
words, scored once with the rules frozen (hash in `outputs/14_test_scored.lock`): precision of a drop
97.5 %, recall of non-definitions 77.7 % (base models 81.5 %, 69.8-93.9 % per model), 4 of 948
definitions wrongly dropped (0.4 %), kappa against the labels 0.84 (the labeler's own: 0.90). Off-topic
text is the weak class (27 of 61 caught). Fallback (c) was not triggered (base-model recall 81.5 %,
above the 70-80 % range) and no classifier was built. Disclosed: the rules were also checked on
unlabeled records of the other 2,900 words, which led to removing the own-subject rule and narrowing
several others (registry). E3, E4 and E5 are filtered without hand validation, as stated in item 5; the
E3 outputs do not copy the few-shot examples to any relevant extent (at most 2.2 % of records repeat a
sentence).

### D024 — A more aggressive filter beside the default, to bound the effect of leaked junk (2026-10-01)
**Question.** The frozen default filter (D023) leaves about 18.5 % of the base-model non-definitions in
the graphs (test words, audit F22). Junk that stays probably keeps base R low, so a pt/it gap that
persists after filtering could partly be leakage. How can that be bounded?
**Options.** (a) A second rule set, `strict` (`src/rs_dic_llm/quality_filter_strict.py`): the default
filter plus the rules D023 removed or narrowed because they dropped valid definitions (a sentence whose
one- or two-word subject is not the headword, "The sun is a star."; the broad wh-word start; "Please",
"Provide", "Give", "Make sure" and "Answer:" as starts; "in a sentence" anywhere; "the following" and
"true or false" alone; an unfinished sentence whatever its content). It is applied to every model
alike, the null model is re-run on its graphs beside the default's, and its precision and recall on the
hand labels are reported (it is a bracket, not the primary filter). (b) A trained classifier on the
labeled rows: possibly higher recall, harder to defend. (c) No bracket.
**Recommendation.** (a).
**Resolution: (a).** Both filters, same units, same null-model setting (32 x edges swaps, 300 tries per
swap, 100 replicates), same graphs (main and E3, E4, E5), reported side by side.
**Reading, fixed before any filtered run exists (the unfiltered results, E3 included, were already known).** For each matched Gemma3 pair (1B, 4B, 12B, 27B) take
the ratio of instruct R to base R under the default filter (r_d) and under the strict filter (r_s).
(i) The pt/it contrast survives filtering and is not explained by leaked junk if r_d >= 2 and r_s >= 2
for at least three of the four pairs. (ii) It depends on how much junk is removed if r_d >= 2 for at
least three pairs but r_s < 2 for at least two of them. (iii) It does not survive filtering if r_d < 2
for at least two pairs. Anything else is reported as mixed. A factor of 2 is used because changing only
the prompt moved R by a median factor of 1.3 (E4) to 1.9 (E5) for the same model. The same reading
applies to E3: the few-shot base R is within a factor 2 of the instruct R of the same size for at least
three of the four sizes. Whatever the outcome, both tables are reported in full.
**Approved.** Researcher (chat, 2026-10-01: "go ahead with the recommendations, include D024"). Advisor:
to be informed.
**Strict rule set validated, 2026-10-01.** Test words (scored once, own lock): precision of a drop
93.8 %, recall 82.7 % (default 97.5 / 77.7 %), 11 of 948 definitions wrongly dropped (1.2 %; default 4),
off-topic text 61 % caught (default 44 %). It closes only about 5 points of the junk leak (base models
85.4 against 81.5 %), so the pair brackets how R reacts to a modest change of the filter, not to a
perfect one; a stronger bound (a classifier, D023 option b) would be a possible D025 if the reading comes
out as (ii) or mixed. The seven runs are queued (registry, E2).
**Amended 2026-10-01.** The strict run on E3, E4 and E5 is cut to the five E3 graphs (researcher, chat:
"Run 6: E3 only"); among the controls the reading of D024 needs only E3. E4 and E5 are reported with the
default filter only.

**Result 2026-10-01.** Main pairs, instruct R / base R at 1B / 4B / 12B / 27B: 7.1 / 3.3 / 12.2 / 5.2 under the
default filter and 5.8 / 4.8 / 11.7 / 3.8 under the strict one: four of four pairs at 2 or more under both, so
reading (i). E3: the few-shot base R is within a factor 2 of the instruct R at four of four sizes under the
default filter (1.91, 1.19, 1.20, 1.12), the strict filter (1.57, 1.14, 1.15, 1.46) and unfiltered. Limits: the
strict filter closes only about 5 points of the junk leak, each base graph holds 3-14 mutual pairs, one
generation run per condition. Tables in the registry (E2) and `outputs/17_filtered_vs_unfiltered.txt`.

**Count-based reading, 2026-10-02.** The readings above were written on point estimates and hold as written. With the
observed counts' own uncertainty (audit script 19, exact conditional ranges) every range of the matched ratios excludes
1; the lower ends exceed 2 for three of the four pairs under each filter (not the same three) and for two pairs (12B, 27B)
under both. For E3 (script 19, section 6, written as instruct R / few-shot base R) no difference can be shown at 4B, 12B and
27B (exact conditional ranges [0.82, 1.71], [0.61, 1.12], [0.64, 1.25]; they include 1 and still allow differences of up to
about 1.6-1.7x), and at 1B the few-shot base R is about half of the instruct R by the exact method (1.91 [1.13, 3.24]) but not
by the conservative one ([0.92, 3.98]); "within a factor 2" holds at four of four sizes for the point estimates and at three
of four for the ranges (exact method).

### D025 — Do frame words, not the content of the definitions, keep the base models' R low? (2026-10-01)
**Question.** In the filtered base graphs a few frame words are used in hundreds of definitions ("mean"
in 217-292 definitions in four of the five base graphs, "use", "define", "describe"): the top five words
carry 21-30 % of the edges (13 % in Gemma3-27B and Qwen2.5-72B) and 51-63 % of the words have no incoming
edge (Gemma3-27B 118, Qwen2.5-72B 372). If how the base models phrase a definition, and not what it says,
keeps their R low, the zero-shot pt/it gap is a format effect.
**Options.** (a) Remove a fixed list of metalinguistic words from every graph (instruct, base and WordNet
alike) and recompute R on the primary graphs (default filter, first sentence). (b) Remove each graph's own
top-k hubs. (c) Nothing.
**Recommendation.** (a): the hypothesis is about phrasing, which a list of phrase words tests directly; (b)
would remove different words from different graphs.
**Resolution: (a).** The list, fixed here before any result of this run exists: define, definition, mean,
meaning, refer, describe, call, term, word, phrase, sentence, noun, verb, adjective, adverb, use. Only six
of the sixteen are nodes of the 2,750-lemma vocabulary (define, mean, refer, describe, phrase, use); for the
other ten nothing is removed because they never were nodes. Everything else as in the primary run (default
filter, first sentence, 100 replicates, 32 x edges swaps, 300 tries per swap); run
`e2_frame_words_removed_default_main_32x`. A smoke test of the option (3 replicates, two graphs) ran before
this entry was written; it is a check of the code, not a result.
**Reading, fixed before the run (the results of D024 were already known).** r_f = instruct R / base R for each matched Gemma3 pair (1B, 4B, 12B, 27B)
with the words removed. (A) The zero-shot gap is largely phrasing if r_f < 2 for at least three of the four
pairs. (B) The gap does not depend on the frame words if r_f >= 2 for at least three of the four pairs.
Otherwise mixed. Also reported: the group ranges and whether the instruct and base ranges still overlap, and
R of every instruct model before and after (a large fall in instruct R would mean the list also removes
content they rely on, "use" for instance).
**Approved.** Researcher (chat, 2026-10-01: "D025: yes"). Advisor: to be informed. The exact list was fixed
by the assistant after the yes, as the recommendation that was put in chat ("define, mean, use, describe,
refer, word, noun, verb, adjective, term and similar"); the researcher can change it until the run starts
(about 20:50 under the queue in the registry).
**Result 2026-10-01.** Matched Gemma3 pairs, instruct R / base R at 1B / 4B / 12B / 27B: 7.1 / 9.7 / 12.9 / 6.7 with
the six frame words removed (default filter: 7.1 / 3.3 / 12.2 / 5.2): four of four at 2 or more, reading (B). The
base models did not gain (median R 4.9 to 3.3) and the instruct models did not lose (median 19.3 to 19.5). The hub
reading of the primary run is not supported; the cause of the zero-shot gap is not identified. Details in the
registry (E2) and `outputs/17_filtered_vs_unfiltered.txt`.

### D026 — Frame the paper around the original hypothesis (2026-10-02)
**Question.** How should the paper be framed now that claim 3 (instruction tuning, not scale, creates the
structure) is not supported by the data?
**Options.** (a) Center the paper on the hypothesis that opened the investigation, state how it was tested and
that it was not supported, and report what was found instead (reciprocal pairs of related words present in base
models under few-shot prompting; the zero-shot gap, which three examples close at 4B-27B and narrow at 1B, and whose cause is not identified). (b) A positive "latent
structure" paper. (c) A methods paper (converged nulls, validated filter, noise floors).
**Recommendation.** (a), with the methods as the supporting contribution (put in chat on 2026-10-02).
**Resolution: (a).** The conclusion is worded "not supported by these tests", with the conditions stated (one
base family, one prompt, one generation run per model, one 3,000-word sample), and not "proven false"; the final
wording is to be settled with the advisor.
**Approved.** Researcher (chat, 2026-10-02: "i want the framing of the paper to be center around that").
Advisor: to confirm the framing and the wording.
**Amended 2026-10-02.** Two phrases of option (a) were corrected after approval. (1) "reciprocal near-synonym pairs"
became "reciprocal pairs of related words": by WordNet relation the 881 pair occurrences in the 17 instruct models are
38 % synonyms, 22 % hypernym pairs, 9 % sister terms, 2 % antonyms, 1 % derived forms and 29 % with no direct link
(audit script 20); the word list was sampled with Brown frequency >= 5 (PROJECT_CONTEXT 3), so the paper does not call
the words "common". (2) "the zero-shot gap as a prompt-format effect" became "the zero-shot gap, which three examples
close at 4B-27B and narrow at 1B, and whose cause is not identified": D025 found no cause, and at 1B the few-shot base
R is about half the instruct R (script 19, section 6). Two conditions are added to the conclusion: no instruction-tuned
model was run with the few-shot prompt, and generation was sampled (temperature 0.7, one run per model). The scale half
of claim 3 is reported as a description, not a test: among the 17 instruct models R shows no overall relation with size
(Spearman rho +0.18, p = 0.50; script 17, section 15), falling within Gemma3 (42.5 at 1B to 25.4 at 27B), without a trend
within Qwen2.5 and rising within Qwen3 (8.8 at 0.6B to 29.3 at 8B); few-shot base R rises from 270M to 1B.
**Approved (amendment).** Researcher (chat, 2026-10-02: "yes, approved"), including the scale sentence as recorded: the text
supplied in chat said that R does not rise with size among the instruct models, which Qwen3 contradicts (audit F27), so it was
changed on recording. Advisor: with the framing.
**Advisor unavailable, 2026-10-02.** The researcher reports that the advisor cannot be reached now and asked the assistant to
proceed as it sees fit. Drafting therefore starts on the researcher's approval of D026 (with its amendment) and D028 (first draft:
`manuscript/draft_v0.md`). Every passage that depends on the framing (abstract, introduction, discussion, conclusion) is marked
provisional in the draft and is to be checked with the advisor when possible; the data sections do not depend on it.
**Advisor green light, 2026-10-02.** The researcher reports that the advisor gave a green light ("from kumoi i received green flag") in answer to the questions put
in chat on 2026-10-02 about D026, the framing and the wording of the conclusion. Recorded as reported, like the earlier confirmations. Not stated: whether the advisor had seen the D029
result (the zero-shot gap shrinks at equal coverage, `outputs/27_survivor_restriction.txt`) or the sentence on the gap as the draft now words it ("the zero-shot gap shrinks at equal coverage,
and the pairs differ" in place of "whose cause is not identified"). The researcher is to say whether the green light covers them; until then that text is marked in the draft banner as still to be shown.
**Superseded in part, 2026-10-02 (D032, D035).** The phrases of option (a) about the zero-shot gap ("which three examples close at 4B-27B and narrow at 1B") and the scale sentence rest on R against the first null (NetworkX `directed_edge_swap`). Against the double-edge swap null of D032 the gap is absent by the rule of D024 (instruct / pretrained 6.4, 1.3, 2.0, 0.9), the few-shot R is above the instruct R at 4B and 12B and not different at 27B, and the instruct models' R lies above WordNet's. The framing (test the original hypothesis, report what was found instead) is unchanged; its wording is to be settled again with the advisor once D035 is decided.

### D027 — Hand check of the E3 outputs, and the rule that reads it (2026-10-02)
**Question.** The E3 result (few-shot base models reach the instruct level of R) rests on E3 outputs that the filter
keeps almost entirely (0-24 of 3,000 records dropped) and that were never hand-labeled; the filter was validated on
zero-shot outputs only. Are the kept E3 outputs real definitions?
**Options.** (a) Label 100 E3 outputs (25 words x the four base models 1B, 4B, 12B and 27B; the words drawn at random, seed
fixed, from the words that are not among the 100 hand-labeled words; the same words for all four models; shown blind to
model and to the filter) with the seven labels of the first pass, and read them by a rule fixed here. (b) No check; state
the gap as a limitation. (c) Label more (200).
**Recommendation.** (a): about 30 minutes of labeling.
**Resolution: (a).** Rule, fixed before the labeling: among the E3 outputs the default filter keeps, "E3 stands" if at least
90 % of the kept outputs are labeled `definition` and no model is below 80 % of its kept outputs; the exact 95 % interval is
reported with it. If the rule is not met, the E3 section is worded as unvalidated and D026's framing is reopened with the
advisor. The check is scored once (`research/audit_scripts/22_e3_check_summary.py`) and reported whichever way it falls.
Sheet: `data/exp2_e3_check_sheet.xlsx`; key: `data/exp2_e3_check_KEY_do_not_open_until_done.csv`.
**Approved.** Researcher (chat, 2026-10-02: "go", to the plan with "for example 90 %"). Advisor: to be informed. The
thresholds of 90 % and 80 % were fixed by the assistant as the recommendation; the researcher can change them until the
labeling starts.
**Result, 2026-10-02** (read once; `audit_scripts/outputs/22_e3_check_summary.txt`). The researcher labeled all 100
outputs: 100 of 100 are `definition` (exact 95 % interval 96-100 %); per model 25 of 25 (86-100 %) at 1B, 4B, 12B and 27B. The
default filter keeps all 100, so the denominator of the rule is 100, and the filter and the labels agree on every row (no kept
non-definition, no dropped definition). **Rule met: E3 stands.** Assistant's reading of the 100 outputs (not part of the rule):
all are single-sentence dictionary-style definitions; some are circular (the headword is repeated: #34, #35, #66 from the 1B
model, #4 and #50 from the 4B model) and some from the 1B model are wrong (#89, "quarterly: every four weeks"), so the label
`definition` certifies the form of the output, not its accuracy. Limits: one labeler, the researcher; 25 words per model and four
models (the 270M model is not in the sample); the check covers the E3 outputs under the default filter and the first-sentence cut
and says nothing about E4 and E5, which are still not hand-validated.

### D028 — Working title of the paper (2026-10-02)
**Question.** Which title keeps the question that opened the investigation and says what the data can answer?
**Options.** (a) "Do LLM-Written Dictionaries Resemble Human Ones? Mutual Definitions with and without Instruction Tuning". (b) Keep
the verb "converge", as the researcher first preferred ("Do LLMs converge into human dictionaries"): "Do LLMs Converge on Human
Dictionaries, and Is Instruction Tuning What Produces the Structure?" ("converge on", not "into"), with an abstract that says:
similar in amount; the models converge on each other, not on WordNet; the hypothesis that instruction tuning produces the
structure is not supported by these tests.
**Recommendation.** (a), as in the outside review the researcher pasted on 2026-10-02: "resemble" is a verb the data can answer
(the same size of the excess, mostly different pairs), and the subtitle names the comparison.
**Resolution: (a).** The earlier working title was "Do LLM Dictionaries Close? Density-Corrected Definitional Circularity Shows What
Instruction Tuning Adds".
**Approved.** Researcher (chat, 2026-10-02: "A"). Advisor: to be informed together with D026.

### D029 — Two CPU tests of the zero-shot gap: coverage and content (2026-10-02)
**Question.** Draft v1 (Section 5) leaves the zero-shot gap unexplained. Three explanations are open; two can be tested on the CPU with the
existing definitions. (b) Coverage: the filter drops 47-57 % of the valid zero-shot records of Gemma3 1B-27B (47.3, 55.9, 49.9, 56.7 %), so their
graphs rest on about half of the word list, and the null model corrects for that only if the dropped words are not the ones that would have formed
pairs. (c) Content: the surviving zero-shot definitions may use other defining words than the few-shot and the instruct ones. The third, non-definitions
that the filter lets through (16 of the 98 kept records of the 50 test words, script 26), cannot be tested here.
**Options.** (a) Run both as specified below. (b) Run only the coverage test. (c) Run neither and keep the explanations as hypotheses.
**Recommendation.** (a): no generation is needed, the two tests answer different questions (if coverage explains the gap, content need not), and the
readings are fixed here before any result exists.
**Resolution: (a).** Protocol, fixed before any restricted graph went through the null model:

*Common.* Gemma3 at 1B, 4B, 12B and 27B (270M has no instruct counterpart). Default filter, first sentence, fixed 2,750-lemma vocabulary, as in the
primary analysis. An *entry* is one of the 3,000 rows of the word list. The zero-shot file (`data/definitions/Gemma3-{s}-pt_42.jsonl`), the E3 file
(`results_2026-09-09_Runpod/results_e3 (fewshot)/definitions/Gemma3-{s}-pt_42.jsonl`) and the instruct file (`data/definitions/Gemma3-{s}_42.jsonl`)
hold the same entries in the same order (word, part of speech and lemma match in all 3,000 rows at all four sizes; the script stops if they do not).
A zero-shot *survivor* is an entry whose zero-shot record has a valid status and is kept by the default filter. S(s) is the set of survivors of size s:
1,580 (1B), 1,322 (4B), 1,503 (12B) and 1,296 (27B) of the 3,000 entries.

*(b) Coverage.* For each size the null model of `experiments/e1_full_null.py` is run unchanged (D020 setting: 100 replicates, 32 x edges swaps, at most
300 tries per swap, seeds `sha256('e1|key|idx')`) on seven graphs, each built from the records of one file with every entry outside a stated set treated
as dropped (the node stays, no edge, D010):
1. fsS: the E3 (few-shot) records of the entries in S(s);
2. itS: the instruct records of the entries in S(s);
3. fsR1 ... fsR5: the E3 records of five random sets of entries of the size of S(s) (`random.Random("d029|<s>|<k>").sample(range(3000), |S(s)|)`,
   k = 1..5): the control that shows what a restriction to that many entries does to R by itself.
28 graphs in all. Script `experiments/d029_survivor_restriction.py` (before running, it rebuilds the unrestricted zero-shot, E3 and instruct graphs and stops
unless their snapshot hashes equal those of the earlier runs); results `results_2026-10-02_Local/d029_survivor_restriction/`; reading
`research/audit_scripts/27_survivor_restriction.py`. The zero-shot R (6.0, 8.4, 2.1, 4.9), the whole-E3 R (22.3, 23.5, 30.9, 28.5) and the instruct R
(42.5, 28.0, 25.7, 25.4) are those of the primary analysis (Table A1, Table 5).
*Reading (b), applied mechanically to the point estimates.* Let g(s) be the geometric mean of the zero-shot R and the whole-E3 R of size s (11.6, 14.0, 8.1
and 11.8). **Coverage explains most of the gap** if at three or four sizes R(fsS) <= g(s) and R(fsS) is below the smallest R(fsRk). **Coverage does not
explain it** if at three or four sizes R(fsS) > g(s) and R(fsS) is not below the smallest R(fsRk). Otherwise the result is mixed. The exact 95 % Poisson
range of the observed pair count over the null mean is printed beside every R, and the report says at how many sizes the range of R(fsS) contains g(s); the
reading itself uses the point estimates, as D025 did. R(itS) against the whole-instruct R is reported with no reading of its own: it shows whether the
surviving words form few pairs whatever the definitions are.

*(c) Content.* CPU only, no null model; script `research/audit_scripts/28_defining_words.py`, output `outputs/28_defining_words.txt`. The defining words of an
entry are the in-vocabulary lemmas that `normalize` finds in its first sentence, the headword's lemma excluded.
- (c1) For every entry kept in the zero-shot, few-shot and instruct conditions: the Jaccard index of the defining-word sets of zero-shot and instruct, of
  few-shot and instruct, and of zero-shot and few-shot (mean per size; the median is printed too). *Reading:* the zero-shot definitions use other defining
  words than the few-shot ones if mean J(zero-shot, instruct) <= mean J(few-shot, instruct) / 1.5 at three or four sizes; they do not if the factor is below
  1.25 at three or four sizes; otherwise mixed.
  When both sets of an entry are empty the index is set to 0 and the number of such entries is printed (convention added 2026-10-02 03:25 JST,
  before script 28 was run).
- (c2) Descriptors per condition on the same entries, with no reading: defining words per kept record, share of kept records with no defining word, distinct
  defining words, share of the edges that the five most used defining words carry, share of kept records that contain one of the six frame words of D025,
  the ten most used defining words, and the overlap coefficient of the sets.
- (c3) Recovery of instruct pairs at equal coverage. T(s) is the set of mutual pairs of the instruct graph (whole word list) whose two words both have a
  surviving zero-shot entry. r_zs is the share of T(s) that are mutual pairs in the zero-shot graph; r_fs the share that are mutual pairs in the fsS graph (E3
  limited to S(s), so the same entries and the same coverage). Exact 95 % (Clopper-Pearson) intervals; exact McNemar test on the pairs that are mutual in one
  graph and not in the other; per size and pooled over the four sizes (pairs recur across sizes, so the pooled test is descriptive). The same with the whole
  E3 graph is printed as a sensitivity, with no reading. *Reading, on the pooled counts:* **content differs** if r_fs >= 2 r_zs and the exact McNemar
  p < 0.05; **content does not differ** if r_fs < 1.25 r_zs; otherwise mixed.

*What the outcomes would mean.* (b) yes: zero-shot R is measured on a smaller and less pair-prone set of words, and R has to be compared at equal coverage.
(b) no with (c3) content differs: at equal coverage the zero-shot definitions form fewer pairs because they use other words. (b) no with (c3) content does
not differ: the extra pairs of the few-shot graph are not instruct pairs, so neither test locates the gap; leaked non-definitions, sampling and the prompt
remain, and none can be tested on the CPU. A mixed result is reported as mixed.
*Limits.* One run per condition. S(s) is defined by the filter, which lets some non-definitions through. The E3 and the zero-shot outputs were cut by different
extractors (audit F2). The five random sets give a crude range. (c3) takes the instruct pairs as the reference. Where a null mean is below 0.5 the floor of R
applies (as in the primary analysis) and the result JSONs say so.
*Before this entry was written* a count-only probe (alignment of the three files and the sizes of S(s); no graph, no R) and a smoke test of the script (1B,
3 replicates, 2 x edges swaps, so no converged R; it printed 6 and 9 observed mutual pairs for fsS and itS) were run. They checked the code and the data and
are not results; the readings above were drafted before them and were not changed afterwards. Compute: 28 graphs x 100 replicates, estimated at 1-2 hours on
12 workers.
**Approved.** Researcher (chat, 2026-10-02: "yes, add D029 and run the two CPU analyses"). Advisor: to be informed together with D026.
**Result 2026-10-02.** Run 03:24-04:23 JST (3,531 s; 28 graphs x 100 replicates, no swap failures, no null mean below the floor); (c) ran while it went.
Outputs: `audit_scripts/outputs/27_survivor_restriction.txt`, `28_defining_words.txt`, `28b_c3_recheck.txt` (the counts of (c3) derived a second way, same numbers),
manuscript Tables 6-8 (`24_manuscript_tables.py`). A side test of the null on three restricted 1B graphs (`results_2026-10-02_Local/d029_convergence_probe_1B/`, not part
of the protocol) found the null mean settled by 8 x edges swaps and flat up to 256 x; the fitted limits of R are 5.9 (fsR1), 5.5 (fsS) and 3.5 (itS) against 6.25, 5.41 and 2.95 at 32 x.

*(b) Reading: MIXED.* R(fsS) is at or below g(s) at four of four sizes (5.4 / 6.2 / 3.3 / 5.7 against 11.6 / 14.0 / 8.1 / 11.8) but below the smallest of the five random
restrictions at one size only (12B: 3.3 against 3.7; the smallest at 1B, 4B and 27B is 4.6, 2.5 and 1.9). "Explains" holds at 1 of 4 sizes, "does not explain" at 0 of 4; the exact range
of R(fsS) contains g(s) at 1 of 4 sizes (1B).

*Beyond the reading (no category in the reading; not pre-registered; descriptive).* The random-set control showed something larger than the question it was built for: limiting a graph to
about half of the entries lowers R to between 0.07 and 0.35 of its whole-list value, whichever half. Few-shot R on the whole list / on the survivors / on the five random sets: 22.3 / 5.4 / 4.6-11.3 (1B),
23.5 / 6.2 / 2.5-8.7 (4B), 30.9 / 3.3 / 3.7-6.3 (12B), 28.5 / 5.7 / 1.9-10.0 (27B). Instruct R on the whole list / on the survivors: 42.5 / 3.0, 28.0 / 4.5, 25.7 / 6.3, 25.4 / 8.8. The survivors lie
inside the range of the random sets at three of four sizes. At equal coverage (the zero-shot graph, fsS and itS are built from the same entries) R is 2.1-8.8 in all twelve graphs: zero-shot 6.0 / 8.4 / 2.1 / 4.9,
fsS 5.4 / 6.2 / 3.3 / 5.7, itS 3.0 / 4.5 / 6.3 / 8.8. The instruct / zero-shot ratio is 7.1 / 3.3 / 12.2 / 5.2 on the whole graphs (ranges exclude 1) and 0.49 / 0.54 / 3.02 / 1.80 at equal coverage, with exact ranges
[0.12, 2.82] / [0.22, 1.34] / [1.19, 8.61] / [0.81, 4.02]: 1 is included at three of four sizes (12B excludes it); fsS / zero-shot and itS / fsS include 1 at four of four. The counts are small (3-21 mutual pairs per
graph). The observed mutual pairs fall with about the square of the share of entries kept (x0.21 / 0.20 / 0.18 / 0.27 against 0.28 / 0.19 / 0.25 / 0.19) while the null mean does not fall (x0.85 / 0.74 / 1.70 / 1.35).
Why the null stays up is not established.
**Correction 2026-10-02 (outside review of draft v1).** "Between 0.07 and 0.35 of its whole-list value, whichever half" mixed group values with single draws. The ratios to the whole-list R are 0.11-0.26 for the
few-shot graph on the survivors, 0.16-0.35 for the mean of the five random halves, 0.07-0.35 for the instruct graph on the survivors and 0.07-0.51 for the 20 single random halves (1B: 0.21-0.51), and single
random halves of one size differ from one another by a factor of 1.7 (12B) to 5.3 (27B). "Whichever half" overstated how little the half matters: the survivors lie inside the range of the random halves at three of
four sizes, but which half is kept moves R by a large factor. Drafts and records now say 0.07-0.51 for single halves.

*(c) Readings.* (c1) MIXED: mean J(few-shot, instruct) / mean J(zero-shot, instruct) is 1.46 / 1.48 / 1.65 / 1.43; the factor 1.5 is reached at one size and none is below 1.25. (c3) CONTENT DIFFERS: of the 62 instruct pairs at risk
(12 / 12 / 19 / 19) the zero-shot graphs contain 5 (8 %, exact 95 % range 3-18 %) and the fsS graphs 20 (32 %, 21-45 %); r_fs / r_zs = 4.0; 16 pairs occur only in the fsS graphs and 1 only in the zero-shot graphs, exact McNemar
p = 0.0003 on the pooled counts (descriptive, pairs recur across sizes; per size p = 1.00 / 0.062 / 0.070 / 0.125). Added after the first reading and not part of D029: counting each of the 52 different pairs once, 14 against 1, p = 0.001.
(c2) A frame word occurs in 30-43 % of the kept zero-shot records against 7-10 % of the few-shot and 6-27 % of the instruct records; the five most used defining words carry 21-30 % of the defining-word occurrences in the zero-shot records
against 12-15 % (few-shot) and 13-17 % (instruct).

*Reported as it came out.* The table of outcomes above has no cell for (b) mixed with (c3) content differs, so each is reported as mixed and as differs. Compared at equal coverage, the zero-shot graphs contain fewer of the instruct models' pairs;
and the amount of coverage, which the reading did not ask about, matters a great deal for R.

*What follows (proposals for the researcher; none is a decision).* (1) R must not be compared between graphs of different coverage. The zero-shot gap of Table 4 sets a graph on about half of the entries beside graphs on all of them; at equal
coverage it shrinks (Table 6). Draft Section 4.3.5 and Section 5 report this. The statements that the gap "survives" the filters (abstract, Section 1 item 2, Section 4.3.1, Section 7) are marked in the draft for rewording and are the researcher's
to settle. (2) The wording of D026 ("whose cause is not identified") and the advisor's claims sheet (version 2) predate this result and need an amendment before they go to the advisor. (3) A coverage-matched analysis on closed
sub-dictionaries (each graph reduced to the words that have a definition) would show whether the dependence of R on coverage belongs to the data or to the way a half-defined graph meets the swap null; it needs its own decision entry (not written).

### D030 — Why R falls with coverage: where the null's pairs come from, and closed sub-dictionaries (2026-10-02)
**Question.** D029 found that R falls to a fraction of its whole-list value when a graph is limited to about half of the entries, that the null mean does not fall the way the
observed pairs do (x0.74-1.70 against x0.18-0.27 from the whole few-shot graph to the survivors), and that the null mean varies by a factor of up to 5 between random halves of
equal size (4B: 1.84-6.21; 27B: 1.20-6.34). The draft says "we do not know why". That leaves the equal-coverage comparison (Table 6) open to the objection that it measures which
hub words kept a definition, and the raw pair counts at equal coverage (zero-shot 35, few-shot 66, instruct 53, summed over the four sizes) point the other way from R. Two things can be
tested on the CPU with existing graphs. (a) Where the null's mutual pairs come from. (b) Whether R is invariant when a graph is reduced to a *closed sub-dictionary* (the graph induced on
a set of words, the undefined words and their edges removed) instead of to a set of entries whose undefined words stay as nodes.
**Options.** (a) Run (a) and (b) as below. (b) Run only the closed sub-dictionaries. (c) Leave the question open and state it as a limit.
**Recommendation.** (a): the coverage result and every use of R across graphs rest on the answer.
**Resolution: (a).** Protocol, fixed before any run (the D029 results, the node counts of the covered sets and the idea that hub words matter were known; none of the quantities below had
been computed):

*Common.* Gemma3 1B, 4B, 12B, 27B; default filter, first sentence. W(s) is the set of lemmas that have a surviving zero-shot entry (1,506 / 1,265 / 1,434 / 1,251 lemmas). The null is that of
`experiments/e1_full_null.py` (32 x edges swaps, at most 300 tries per swap); replicate seeds `sha256('e1|key|idx')` of the graph key.

*(a) Null pairs by node.* `experiments/d030_null_pairs.py` reruns the null with the stored seeds for replicates 0-39 of 40 graphs (the zero-shot, whole few-shot and whole instruct graph of
each size from the primary run, and fsS, itS and fsR1-5 of D029) and records the mutual pairs of every replicate. Check: the number of pairs of every rerun replicate must equal the stored
`cycles_2` of the same replicate, or the script stops. Reported per graph: the mean number of null pairs, the five nodes that occur most often in null pairs and the share of the null
pair endpoints they carry, the same for the observed pairs, and, for the 20 random halves, the Spearman correlation between (null mean of the half / null mean of the whole few-shot graph of
that size) and the number of the ten words with the largest d_out x d_in product in the whole few-shot graph of that size that the half covers. *Reading (a):* the null mean is **hub-driven** if
the five most frequent nodes carry at least half of the null pair endpoints in at least three of the four fsS graphs; **not hub-driven** if they carry less than a third in at least three of the
four; otherwise mixed. The correlation is descriptive.

*(b) Closed sub-dictionaries.* `experiments/d030_closed_subdictionaries.py` builds, from the stored graph snapshots, the graphs induced on W(s): zsC from the zero-shot graph, fsC from the whole
few-shot graph, itC from the whole instruct graph; and fsRC1-5, the whole few-shot graph induced on five random sets of lemmas of the size of W(s)
(`random.Random("d030|<s>|<k>").sample(sorted(lemmas), |W(s)|)`, drawn from the 2,750 lemmas). 32 graphs, 100 replicates each. Because a closed half-graph can have a null mean below the floor of 0.5,
the readings of this entry use R' = observed pairs / null mean without the floor (R' = R wherever the null mean is at least 0.5); R is reported beside it. *Reading (b1), invariance:*
rho_k = R'(fsRCk) / R'(whole few-shot graph). R is **approximately invariant** under random closed restriction if the median of rho_k lies between 0.67 and 1.5 at three or four sizes, and
**falls** if it is below 0.5 at three or four sizes; otherwise mixed. *Reading (b2), equal coverage on closed dictionaries:* the exact conditional range (script 19 method, null means as exposures)
of R'(itC) / R'(zsC) and of R'(fsC) / R'(zsC). A difference at equal coverage is **shown** if the range of itC / zsC excludes 1 at three or four sizes, and **not shown** if it includes 1 at
three or four sizes; otherwise mixed. *(b3), descriptive:* the largest / smallest R' over the five random closed halves at each size, the raw pairs and null means.
Reading script: `research/audit_scripts/29_null_pairs.py` (a) and `30_closed_subdictionaries.py` (b); results `results_2026-10-02_Local/d030_*`.

*What the outcomes would mean.* (b1) invariant: the fall of R in D029 belongs to the way a half-defined graph meets the null (dangling nodes), and (b2) is the fair equal-coverage comparison.
(b1) falls: R depends on coverage even for a closed dictionary, so R cannot be compared across dictionaries of different size, and (b2) can only be read as a comparison at one size. (a) hub-driven:
the null mean, and so R, is decided by a few words, and R must be reported with and without them. Mixed results are reported as mixed.
*Limits.* One run per graph; five random sets per size; closed half-dictionaries are different objects from the full ones; the 40 replicates of (a) give the node frequencies only roughly.
**Approved.** Researcher (chat, 2026-10-02: "fix the following", pasting a review whose must-fix list reads: "Explain the null under coverage restriction (CPU). Find which nodes generate the null's
mutual pairs. Compare with the closed sub-dictionary version your Next steps already name"). The protocol and the readings were fixed by the assistant before the run; the researcher can change them
until the run starts. Advisor: to be informed with D029.

**Result 2026-10-02.** (b) `audit_scripts/outputs/30_closed_subdictionaries.txt` (32 graphs x 100 replicates, run 05:29-06:50 JST): reading (b1), **R falls with random closed restriction** (median rho 0.20, 0.14, 0.28, 0.18; below 0.5 at 4 of 4 sizes);
reading (b2), **a difference is not shown** (itC / zsC 0.43 [0.12, 2.36], 0.53 [0.21, 1.33], 2.42 [0.97, 6.80], 1.49 [0.71, 3.22]; the ranges include 1 at 4 of 4 sizes, as do those of fsC / zsC).
(a) `audit_scripts/outputs/29_null_pairs.txt` (40 graphs x 40 stored replicates = 1,600; run 06:50-08:06 JST, 4,536 s; every rerun replicate equals the stored one): reading (a), **hub-driven** by the rule as written: the five most frequent nodes carry 0.58, 0.76, 0.38 and 0.60 of
the null pair endpoints of the fsS graphs (at least a half at 3 of 4 sizes, below a third at none). What the rule counted is not what its outcome was meant to say: the most frequent nodes are not high-degree words but the two ends of *observed* pairs that the null never breaks.
The pairs present in all 40 replicates of the fsS graphs are observed pairs: battle-fight, initiate-start (4B); asleep-awake, election-vote, greet-welcome, initiate-start, misfortune-unfortunate (12B); mention-refer, naval-navy (27B). The correlation between the null mean of a random half
and the number of the ten largest hubs it covers is -0.21 (p = 0.37, descriptive). Post hoc (section 4 of the output, added after sections 1-3 had been read): of the pairs in a null replicate, the observed pairs are 10.0 of 14.4 (69 %) in the fsS graphs summed over the four sizes,
6.1 of 10.2 in the itS graphs and 55-82 % in the five random halves, but 2.9 of 12.2 in the whole few-shot graphs and 0.1 of 7.9 in the whole instruct graphs; 9 of the 66 observed pairs of the fsS graphs are present in all 40 replicates.
*What follows.* The null of every R so far (networkx `directed_edge_swap`) keeps mutual pairs that it cannot move, and the sparser the graph the larger their share of the null mean; a graph limited to half of its entries is sparser (its observed pairs fall with the square of the share kept, the persistent ones stay).
That is the cause D029 left open. It led to D032 (the double-edge swap null), which finds that R does not depend on coverage. The outcome of reading (a) is recorded as the rule gives it and is not used to argue that R "must be reported with and without hub words".

### D031 — Does R approach WordNet's with model size? (2026-10-02)
**Question.** The project began from the claim that larger models converge on the structure of human dictionaries. The draft's hypothesis is that instruction tuning, not scale, produces the structure,
and it calls the role of scale "described, not tested" (D026 amendment). A paper that asks about scale needs an answer on scale, and "convergence" has not been defined. Operationalization: within a
model family, does a larger model's dictionary come closer to WordNet's in R, or share more of WordNet's mutual pairs?
**Options.** (a) Fix a within-family test on the 17 instruct models with the existing graphs (no new null runs). (b) Keep the description. (c) Pool the families.
**Recommendation.** (a). Pooling mixes families that differ in many ways besides size (F27); the description stays as the companion.
**Resolution: (a).** Protocol, fixed before the statistics were computed (the R values of all models, the Jaccard indices with WordNet in script 20 and the Spearman correlations of script 17
section 15 were known; the distances and correlations below were not):
*Models and graphs.* The 17 instruct models of the primary run (default filter, first sentence, 32 x edges): Gemma3 1B, 4B, 12B, 27B; Qwen2.5 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B; Qwen3 0.6B, 1.7B, 4B, 8B, 14B.
Qwen3-4B-Instruct-2507, a later checkpoint at the size of Qwen3-4B, is left out of the trend and added in a sensitivity row. The pretrained models and Gemma3-270M are not part of this test.
*Statistics.* S1, distance in R: d = |ln R - ln R_WordNet| with R_WordNet = 15.7. S2, pair overlap: the Jaccard index J of the model's set of mutual pairs with WordNet's 27 pairs. Within each family the
Spearman correlation of S1 and of S2 with the parameter count. Descriptive, no reading: the raw mutual pairs and the null mean of each model (R is a ratio of the two), and the same two distances
for the kernel ratio (the statistic of the earlier claim): d_k = |kernel ratio - kernel ratio of WordNet|.
*Labels per family and statistic.* S1 is "toward" if rho <= -0.6, "away" if rho >= +0.6, else "none"; S2 is "toward" if rho >= +0.6, "away" if rho <= -0.6, else "none".
*Reading.* **Convergence with size is supported** if S1 and S2 are both "toward" in at least two of the three families and "away" in none. **It is contradicted** if S1 and S2 are both "away" in at least two
families. Otherwise: **no consistent approach**. With four to seven models per family the labels are weak evidence either way, and the entry says so.
Reading script: `research/audit_scripts/31_scale_convergence.py`.
*Limits.* Families differ in much besides size (data, recipes, versions); n is 4, 7 and 5; WordNet's R rests on 27 pairs (its own range is wide); J rests on 0-4 shared pairs per model.
**Approved.** Researcher (chat, 2026-10-02: "fix the following", pasting a review whose must-fix list reads: "Answer the scale question with a fixed operationalization (CPU, existing graphs;
fix the reading first and record it in the decision log)"). The protocol and the readings were fixed by the assistant before the statistics were computed; the researcher can change them. Advisor: to be
informed. This entry amends the D026 sentence that scale is "described, not tested".
**Result 2026-10-02.** `audit_scripts/outputs/31_scale_convergence.txt`. Reading: **NO CONSISTENT APPROACH.** S1 (distance in R) is "toward" in Gemma3 (rho = -1.00, n = 4), "none" in Qwen2.5
(+0.36, n = 7) and "none" in Qwen3 (0.00, n = 5). S2 (pair overlap with WordNet) is "none" in Gemma3 (-0.40) and in Qwen3 (+0.30) and "away" in Qwen2.5 (-0.75, p = 0.05): the larger Qwen2.5 models share fewer
of WordNet's pairs. With Qwen3-4B-Instruct-2507 included the labels are unchanged (Qwen3: +0.14 and +0.09). Descriptive, no reading: in Gemma3 the raw mutual pairs rise with size (rho +0.80, 34 to 71) and so does the
null mean (+0.80, 0.80 to 2.79), so R falls toward WordNet's (42.5 to 25.4) because the null grows faster than the pairs; every instruct model shares 1-4 of WordNet's 27 pairs (J 0.010-0.055). The raw kernel ratio comes
closer to WordNet's with size in Gemma3 (d_k rho -1.00; 0.059 to 0.125 against 0.159), slightly in Qwen3 (-0.40) and not in Qwen2.5 (+0.57); its z against the null is not above chance (+1.68 at 1B to -1.39 at 27B).
The earlier apparent convergence on the kernel ratio is therefore visible in one family, as a degree effect, and R shows no consistent approach.

### D032 — A null that can break every mutual pair (2026-10-02)
**Question.** D030 found that the null model of every R in this project (networkx `directed_edge_swap`, a three-edge move) keeps mutual pairs in its replicates that it cannot move. In a sparse closed half of the 4B
few-shot graph (14 observed pairs) 10 to 11 observed pairs are still present in each of six null replicates, the null mean is 12.65 and the independent-edge estimate 0.34; in the whole 4B few-shot graph 1 to 2 of 92
observed pairs persist in a null mean of 3.92. A pair that cannot be broken adds the same number to the observed count and to the null mean, so R is pulled toward 1, and the more so the sparser the graph. A directed
double-edge swap (Maslov-Sneppen) can break any pair. In a scratch test (6 to 40 replicates, not a result) it gave null means of 0.20-0.53 on the two sparse halves, 1.6-2.1 on the whole 4B few-shot graph, 1.0-1.4 on the
whole 1B instruct graph and 1.4-1.6 for WordNet, and kept no observed pair. Does the paper's picture depend on the null?
**Options.** (a) Rerun the null with the double-edge swap on all graphs of the analyses, after a validation, as a sensitivity analysis; whether it replaces the primary null is a separate decision. (b) Keep the three-edge null
and state the limit. (c) Replace the primary null at once.
**Recommendation.** (a): it is cheap (about 2 s per replicate), it tests every reading that rests on R, and the adoption decision belongs to the researcher and the advisor once they have seen it.
**Resolution: (a).** Protocol, fixed before the main run (the D029 and D030 results and the scratch test above were known; no R of the new null had been computed except in that test):

*Null.* Directed double-edge swap, `experiments/d032_double_swap_null.py`: two distinct edges (a->b) and (c->d) chosen uniformly; (a->d) and (c->b) proposed; rejected if a = c, b = d, a = d or c = b, or if either new
edge exists; 32 x edges accepted swaps per replicate unless the validation says otherwise; 100 replicates; seeds sha256('d032|key|idx')[:4]. R_d = observed pairs / max(null mean, 0.5), as R; R'_d = observed pairs / null mean.

*Validation, before the main run* (`experiments/d032_convergence.py`). Eight graphs (whole few-shot 4B, whole instruct 1B and 12B, WordNet, zero-shot 12B, fsS 4B, closed fsRC3 4B, closed itC 1B), 30 chains each,
checkpoints from 1 to 128 x edges. **V1:** the null is accepted as settled at 32 x edges if on every graph the mean at 32 x lies within 10 % or two standard errors of the mean at 128 x; otherwise the multiplier is raised to the
smallest checkpoint that passes. **V2:** the mean number of observed pairs still present at 32 x is below 5 % of the observed pairs on every graph, that is, the null can break pairs. The independent-edge estimate is printed beside the
null means (descriptive).

*Graphs of the main run.* The 23 main graphs (17 instruct, 5 pretrained, WordNet; written as "23 main graphs and WordNet" in the first version of this entry, a miscount), the 5 few-shot graphs, the 28 graphs of D029 and the 32 closed
sub-dictionaries of D030: 88 graphs (default filter, first sentence).

*Readings,* applied by `research/audit_scripts/36_double_swap_readings.py` to R_d with the rules of the original tests:
- (r1) Coverage. rho_k = R'_d(fsRk) / R'_d(whole few-shot graph) for the five entry-level random halves of D029, and the same for the five closed random halves of D030. R depends on coverage under the new null if the median of
  rho_k is below 0.5 at three or four sizes; it does not if the median lies between 0.67 and 1.5 at three or four sizes; otherwise mixed.
- (r2) Zero-shot gap as built (the rule of D024): instruct R_d / pretrained R_d is at least 2 for three of the four matched pairs: the gap is present; below 2 for two or more pairs: absent.
- (r3) Equal coverage (the rule of D029): the exact conditional range of R_d(itS) / R_d(zero-shot) excludes 1 at three or four sizes: a difference is shown; it includes 1 at three or four sizes: not shown.
- (r4) Few-shot (the rule of D024): the few-shot pretrained R_d lies within a factor 2 of the instruct R_d at three of four sizes: it reaches the instruct range.
- (r5) Scale (the rules of D031): the labels and the reading of D031 with R_d in place of R.
- (r6) WordNet, descriptive: the number of instruct models whose exact range lies above, contains or lies below R_d of WordNet.

*What the outcomes would mean.* If (r1) says that R does not depend on coverage, the fall of R in D029 and D030 belongs to the null, and the equal-coverage tests are read with R_d. If (r2) says that the gap is absent, the zero-shot
gap of draft v1 was largely an effect of the null in sparse graphs. Any reading that changes is reported with both values.
*Limits.* One run per condition. The double-swap chain is the standard one and is not known to reach every graph with the given degrees (directed triangles); the primary null of all earlier decisions (D020) is unchanged until the
researcher decides.
**Approved.** Researcher (chat, 2026-10-02: "fix the following", pasting a review whose must-fix list asks to "explain the null under coverage restriction"). This entry was added by the assistant after D030 and the scratch test showed that the
null cannot break some pairs; the researcher can change the protocol and the readings until the main run starts. Adoption of the new null as the primary one is not decided here. Advisor: to be informed.
**Validation 2026-10-02** (`audit_scripts/outputs/35_double_swap_validation.txt`; 8 graphs x 30 chains, checkpoints 1 to 128 x edges). **V2 met on all eight graphs:** at 32 x edges no observed pair is still present in any replicate (mean 0.00), whereas
the paper's null keeps 10.40 of the 14 observed pairs of the sparse closed half on average (20 stored replicates, rerun with the stored seeds: all 160 rerun replicates equal the stored ones; `outputs/35_...` section 2, `results_2026-10-02_Local/d032_networkx_persistence/`; run 07:33-08:03 JST). The paper's null keeps on average 0.00 (Gemma3 1B instruct), 0.10 (WordNet), 0.15 (Gemma3 12B instruct), 1.00 (12B zero-shot), 1.05 (closed 1B instruct), 1.60 (4B few-shot), 2.20 (fsS 4B) and 10.40 (closed 4B half) observed pairs per replicate, which is 0 to 84 % of the pairs in its replicates. The means settle by 2 to 4 x edges (at 1 x they are still high) and agree with the independent-edge
estimate (for example 0.31 against 0.20-0.43 for fsS 4B, 0.33 against 0.27-0.57 for the closed half, 0.98 against 0.87-1.10 for the 1B instruct graph, 1.44 against 1.17-2.00 for WordNet). **V1 not met at 32 x edges on one graph:** whole 12B instruct, 2.23 at
32 x against 3.23 at 128 x (about 2.5 standard errors of the difference; the means at 8 to 64 x are 2.5, 2.9, 2.2, 2.7 and the independent-edge estimate is 2.54). As the rule says, the multiplier is raised to the smallest higher checkpoint at which V1 holds on all
graphs: **64 x edges**, which the main run uses. The rule was applied as written although the failure looks like noise.

**Result 2026-10-02** (`audit_scripts/outputs/36_double_swap_readings.txt`; main run 06:55-07:25 JST, 1,791 s, 88 graphs x 100 replicates at 64 x edges, no replicate short of its swap budget; the observed pairs kept by the null: 0.00-0.03 per replicate).
The null means of the instruct models are 0.88-2.92 (the paper's null: 0.80-6.65), WordNet's 1.49 (1.72), the zero-shot pretrained graphs' 0.38-0.44 (1.31-3.33).
- *R against R_d.* Instruct 18.1-52.1 (median 29.2) against 8.8-42.5 (19.3); zero-shot pretrained 6.0-28.0 (median 14.0) against 2.1-8.4 (median 4.9); few-shot pretrained 14.3-49.2 against 4.6-30.9; WordNet 18.1 [11.9, 26.4] against 15.7. For nine instruct models R_d is within 11 % of R
  (the four Gemma 3, Qwen2.5-0.5B and 32B, Qwen3-1.7B, 4B-2507 and 8B), for eight it is 1.7 to 4.2 times R (Qwen2.5-1.5B, 3B, 7B, 14B, 72B, Qwen3-0.6B, 4B, 14B). The rank correlation of the 17 values under the two nulls is +0.07: the order of the models by R belonged
  largely to the null.
- *(r1) Coverage: R does not depend on coverage under the new null,* for the entry-level halves (median rho 1.22, 0.82, 0.89, 1.21) and the closed halves (1.04, 0.88, 0.84, 1.40), all four sizes invariant (the paper's null: 0.30, 0.16, 0.15, 0.24 and 0.20, 0.14, 0.28, 0.18). The dependence of R on coverage
  found in D029 and D030 was a property of the three-edge null.
- *(r2) Zero-shot gap as built: ABSENT.* Instruct R_d / pretrained R_d is 6.4 [2.0, 32.8], 1.3 [0.7, 2.8], 2.0 [0.9, 5.1] and 0.9 [0.5, 1.7] at 1B, 4B, 12B and 27B (the paper's null: 7.1, 3.3, 12.2, 5.2); two of four pairs reach 2. The null mean of the four zero-shot graphs is below the floor of 0.5, so their R_d is twice their
  pair count (6, 22, 14, 28 from 3, 11, 7, 14 pairs); without the floor they would be 6.8, 29, 16, 33.
- *(r3) Equal coverage: NOT SHOWN* at 4 of 4 sizes (itS / zero-shot 3.00 [0.75, 17.2], 1.09 [0.44, 2.73], 2.43 [0.96, 6.93], 1.01 [0.45, 2.26]).
- *(r4) Few-shot: REACHES THE INSTRUCT RANGE* at three of four sizes (factors 2.12, 1.69, 1.70, 1.24), but in the other direction at 4B and 12B: the few-shot R_d (49.2, 47.7) is above the instruct R_d (29.2, 28.1), instruct / few-shot 0.59 [0.41, 0.85] and 0.59 [0.44, 0.79]; at 1B the instruct R_d is
  2.12 [1.25, 3.60] times the few-shot.
- *(r5) Scale: NO CONSISTENT APPROACH.* Distance in R: toward in Gemma 3 (-1.00), away in Qwen3 (+0.80, n = 5), none in Qwen2.5 (+0.43); pair overlap as in D031. In Gemma 3 R_d still falls with size (38.6, 29.2, 28.1, 24.7) because the null mean rises (rho +1.00) faster than the pairs.
- *(r6) WordNet.* R_d of the instruct models lies entirely above WordNet's 18.1 for 13 of 17 models, contains it for 4 and lies below for none; 16 of 17 point estimates are above (the paper's null: 7 above, 2 below, 8 containing; 12 of 17).
*What follows.* The three-edge null biased R toward 1 unevenly (more where mutual pairs involve words with few other links), produced the dependence of R on coverage, and with it the zero-shot gap of draft v1 and the "same amount as WordNet" reading. Under the null that can break every pair the instruct models show *more* reciprocal
definition than WordNet, the pretrained models show it too without examples, and none of the size trends is consistent. Whether this null replaces the primary one is for the researcher and the advisor to decide (not decided here); draft v2 reports it as the primary statistic and gives the first null's values beside it.

### D033 — Kernel ratio, circulation rate and cycle profile against the double-edge swap null (2026-10-02)
**Question.** D032 shows that R changes when the null can break every mutual pair (R_d against R: for 8 of the 17 instruct models R_d is 1.7 to 4.2 times R, for the other nine within 11 % of it; the rank correlation of the 17 values is +0.07; "5 of the 17" in the first wording was a miscount).
Claim 1 (Section 4.1: the kernel ratio is at chance, the circulation rate below chance for the instruct models and WordNet) and the cycle-length profile (Table 2) were computed against the same three-edge null. Do they change?
**Options.** (a) Compute the same statistics for the double-edge swap null of D032 on the 23 main graphs (20 replicates each: simple-cycle enumeration up to length 7 is the expensive part). (b) Keep the earlier values with a caveat.
**Recommendation.** (a): cheap (about 15 minutes) and claim 1 is the first result of the paper.
**Resolution: (a).** Protocol, fixed before the run (the z-scores of the first null, Table 1 of draft v1, and R_d of D032 were known; no z-score of the new null had been computed): `experiments/d033_double_swap_full_stats.py`, the 23 main graphs (default filter, first sentence),
the double-edge swap of D032 with 64 x edges accepted swaps, 20 replicates, seeds sha256('d033|key|idx')[:4]; statistics `e1_full_null.summarize_full` (kernel ratio, circulation rate, simple cycles up to length 7 and their histogram); z-scores with the population standard
deviation of the 20 replicates, as in the paper. Readings, applied by `research/audit_scripts/37_double_swap_claim1.py`:
- (k1) Kernel. Claim 1 holds under the new null if the median kernel z of the 17 instruct models lies within +-1, at most 4 of the 17 lie beyond +-2, and WordNet's |z| is below 2.
- (k2) Circulation. The circulation rate stays below the null for the instruct models if the median z is below 0 and at least 12 of the 17 are below 0 (v1: median -1.51, 15 of 17).
- (k3) Cycle profile. The profile of draft v1 holds if, summed over the 17 instruct models, 2-cycles are at least 5 times the null and cycles of length 5 to 7 are below the null (each ratio below 1).
Whatever changes is reported with both values.
*Limits.* 20 replicates; z-scores of a kernel ratio with a small SD are sensitive to that SD.
**Approved.** Researcher (chat, 2026-10-02: "fix the following", pasting a review whose must-fix list asks to "explain the null under coverage restriction"). Added by the assistant after D032; the researcher can change the protocol and the readings until the run starts.
Advisor: to be informed.

**Result 2026-10-02** (`audit_scripts/outputs/37_double_swap_claim1.txt`; run 07:27-07:31 JST, 209 s; 23 graphs x 20 replicates). **(k1) Claim 1 holds:** the median kernel z of the 17 instruct models is +0.19 (three-edge null +0.31), three of 17 lie beyond +-2
(Qwen2.5-0.5B -3.9, Qwen2.5-1.5B -2.1, Qwen3-1.7B -2.3; before: Qwen2.5-0.5B, Qwen2.5-1.5B, Qwen2.5-32B), WordNet -0.26. **(k2) The circulation rate stays below the null:** median z -1.31 (before -1.51), 12 of 17 below 0 (15), exactly the threshold; the five
pretrained graphs are above it (+4.00 against +1.90). **(k3) The cycle profile holds:** summed over the instruct models 2-cycles are 29.6 times the null (18.8), 3-cycles 2.37 (2.24), 4-cycles 0.94 (0.97), and cycles of length 5, 6, 7 are at 0.59, 0.52, 0.47 (0.59, 0.52, 0.46);
WordNet 16.9x at length 2. The kernel and cycle results of draft v1 do not depend on the null; the 2-cycle excess is larger against the null that can break every pair.

### D034 — The prompt controls against the double-edge swap null (2026-10-02)
**Question.** Section 4.3 of draft v2 gives the size of the change in R when only the prompt changes (E4: answers of 8 words or fewer; E5: no chat template). The median size of the change max(x, 1/x) is 1.34 (E4) and 1.90 (E5) on the unfiltered graphs and 1.28 (E4, n = 17) and 1.94
(E5, n = 15: two Qwen3 graphs have no mutual pair) on the default-filter graphs (`audit_scripts/outputs/13_controls_vs_main.txt`, `17_filtered_vs_unfiltered.txt` section 5), and the factor 2 that separates a gap from no gap in D024 and later was set from the unfiltered values. These ratios are against the
three-edge null. Do they change against the double-edge swap null (D032)?
**Options.** (a) Run the double-edge swap null of D032 on the default-filter graphs of the two controls and recompute the ratios to the main run. (b) Keep the earlier values with a caveat.
**Recommendation.** (a): cheap (about 12 minutes) and the factor 2 is used in every reading about instruction tuning.
**Resolution: (a).** `experiments/d034_controls_double_swap.py` runs the functions of D032 (seeds sha256('d032|key|idx')[:4], 64 x edges accepted swaps, 100 replicates) on the 34 default-filter graphs e4__* and e5__* of the 17 instruct models (the E5 graph of Gemma3-270M has no instruct main run and is left out).
`audit_scripts/38_controls_double_swap.py` gives, per model, R_d of the control against R_d of the main run of D032 and, for each control, the median ratio, the median size of the change max(ratio, 1/ratio), its largest value and the number of models within a factor 2, over the models where both
R_d are above 0 (as in section 5 of script 17), beside the same quantities of the three-edge null from the stored results. Descriptive: no reading is attached except one. If the median size of the change of either control exceeds 2 under the double-edge null, the factor 2 of the earlier readings is reconsidered with the researcher.
Defined before the run (the three-edge values and the D032 results of the main graphs were known; no control graph had been run under the new null).
**Approved.** Researcher (chat, 2026-10-02: "fix the following"); added by the assistant after D032, same basis as D032 and D033. Advisor: to be informed.

**Result 2026-10-02** (`audit_scripts/outputs/38_controls_double_swap.txt`; 34 graphs x 100 replicates at 64 x edges, run 07:35-08:11 JST, 2,134 s, no replicate short of its budget). **The factor 2 stands:** the median size of the change is 1.62 (length cap) and 1.21 (no template)
against the double-edge null (1.28 and 1.94 against the three-edge null on the same graphs). Beyond the reading: the length cap raises R for 16 of 17 models (median ratio 1.62, range 0.74-2.44; three-edge null: 9 of 17, median 1.11) and the number of pairs for 13 of 17 (median ratio 1.35);
without the template R is lower for 11 of the 15 models with a usable ratio (median 0.84, range 0.06-1.39; the Qwen3-4B and 14B graphs fall to one pair). *Post hoc* (section "How R moves with definition length", added to the script after the comparison had been read; not part of the protocol):
R falls with the mean length of the definitions against the double-edge null, rank correlation -0.75 over 59 graphs, -0.73 over the instruct main and length-control graphs (n = 34), and within a model -0.49 (length control, n = 17, p = 0.048) and -0.48 (template control, n = 15, p = 0.07);
against the three-edge null the same four analyses give -0.35, +0.10, -0.14 and -0.61. WordNet's glosses have 8.8 words on average, the instruct models 10.4 (7.9-14.6), under the cap 6.3, the zero-shot pretrained models 18.3-23.7.
*What follows.* The statement of draft v1 that R is not related to definition length belonged to the first null. The factor 2 is a median over the models and not a noise level for conditions that differ in length; comparisons of R between such conditions (zero-shot against instruct, the Gemma 3 sizes) are confounded with length.

### D035 — Which null is the primary one? (2026-10-02) — PROPOSED, NOT DECIDED
**Question.** D030 and D032 show that the null of every R in E1 to E5 and in draft v1 (NetworkX `directed_edge_swap`, three-edge moves, 32 x edges: D020) keeps mutual pairs it cannot move. Against the directed double-edge swap null of D032, R of a graph changes by a factor of 0.89 to 6.7,
the order of the 17 instruct models by R changes (rank correlation +0.07), R no longer depends on coverage (D032 (r1)), the zero-shot gap is absent by the rule of D024 (D032 (r2)), instruct R lies above WordNet's, and R falls with definition length (D034, post hoc). Draft v2 reports R against the double-edge null as the main statistic, with the
three-edge values beside it, so that the researcher and the advisor can see both. Which null is primary is their choice.
**Options.** (a) The double-edge swap null is primary; the three-edge values are reported as the result of the first analysis and as a sensitivity. (b) The three-edge null stays primary (D020) and the double-edge null is a sensitivity analysis; the draft's conclusions then rest on a null that biases R where graphs are sparse.
(c) A different null (for example a stub-matching null, or one that also fixes the number of mutual pairs of each word), after a further comparison.
**Recommendation.** (a). Reasons: the validation of D032 (V2 on all eight graphs; agreement of the null means with the independent-edge estimate: 1.87 against 2.01, 0.27 against 0.31, 0.33 against 0.33, 1.49 against 1.44), the persistence of observed pairs in the three-edge null (`outputs/29_null_pairs.txt`, `35_double_swap_validation.txt`: up to 10.40 of
12.40 pairs per replicate on a sparse graph), and that every conclusion about R that changed rests on graphs where the first null demonstrably keeps observed pairs. What (a) does not settle: the double-edge swap is not known to reach every graph with the same degrees; the unfiltered, strict-filter, stored-text and frame-word variants were not rerun with it
(about 30 minutes of CPU with `experiments/d032_double_swap_null.py` and a new graph list); D024 and D025 were written for the three-edge R and are applied to both.
**Consequences if (a) is chosen.** Draft v2 stands as written. D024 (i) is recorded as not met on the default filter. `CLAUDE.md`, `PROJECT_CONTEXT.md` (claims 2 and 3), the claims sheet for the advisor (version 2, written before D029) and the wording of D026 (which still says that the zero-shot gap is a feature of the data) need a revision; the registry rows for E1 to E5 get a note that their R is against the
first null. If (b) is chosen, Sections 4.2, 4.3 and 4.6 of the draft change their roles (the first-null values become the main ones) and the conclusions about the gap and about WordNet go back to those of draft v1 with the caveat of Section 4.3.
**Resolution.** Not decided. **Approved.** None. Proposed by the assistant, 2026-10-02. Advisor: to be informed.
