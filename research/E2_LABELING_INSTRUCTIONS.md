# E2 Labeling Instructions (solo labeler)

Purpose: build the hand-labelled answer key that the automated non-definition filter
(`src/quality_filter.py`) will be validated against. The labels are evidence for the
paper, so they must be consistent and must not be influenced by the filter.

Workbook to use: `data/exp2_labeling_workbook_labeled.xlsx` (already created for you).
23 model tabs, 100 rows each; row 2 of each tab is an EXAMPLE row, do not label it.
Every tab uses the same 100 words (a random sample of the 3,000-word list), so models can
be compared row by row. Do not label in the original `exp2_labeling_workbook.xlsx`.

What the labeled copy changes (columns A-D are identical to the original, checked cell by cell):
- the Label dropdown lists all seven labels below
- a new column E, `POS (added)`, shows the part of speech the model was asked about.
  About 12 of the 100 words per tab exist as both noun and verb (or adjective), so the same
  word can appear under two parts of speech. The column is informational only: no label
  depends on it and no analysis uses it.
- the Read me tab lists the seven labels

---

## 0. Ground rules

1. **Judge only: is this output an attempt to explain what the word means?** Not whether it
   is correct, good, or well written. A wrong or awkward attempt is still `definition`.
2. **Judge by meaning, not keywords.** Do not scan for words like *use, word, one, short,
   common, sentence*. Those will also appear in the filter; if you label by keyword, the
   validation becomes circular.
3. **Do not look at, write, or run the filter before you finish labeling.** Label first.
4. **Ignore formatting noise:** `<b>`, `<tex>`, markdown, leading `A.` / `A)` / `1.`, line
   breaks. Judge the content underneath.
5. **Target word appearing in its own definition is fine** ("A plank is a long piece of
   wood" = `definition`). Self-reference is measured separately later.
6. **Go fast.** A few seconds per row. First impression, then move on. If it is not obvious,
   use `unclear`.
7. One model tab at a time, top to bottom. Do not reorder or delete rows.

---

## 1. The labels (exactly one per row, lowercase)

| Label | Use when | Example (word → output) |
|---|---|---|
| `definition` | Output tries to say what the word means, however badly | crack → "A narrow break or split in something." |
| `echo` | Output repeats the task/instructions instead of defining | plank → "Define the noun "plank" in one short sentence. Use only common English words." |
| `question` | Output asks something instead of answering, and no standalone definition is present | crack → "What do you mean by crack?" |
| `offtopic` | Coherent text, but unrelated to the target word | crack → "A sentence is a group of words that expresses a complete thought." |
| `restatement` | Output only repeats the word (or a trivial variant), no content | plank → "Plank" |
| `refusal` | Output says it cannot or does not know the word | pinpoint → "I can't find the word "pinpoint" in the dictionary." |
| `unclear` | Garbled, truncated, or you cannot decide in a few seconds | (explain in Notes) |

Mapping to the roadmap classes for the classifier: `echo`=prompt_echo, `offtopic`=off_topic,
`restatement`+`unclear`-fragments=fragment. `refusal` is new; report it separately.

---

## 2. Decision order (use the first rule that fits)

1. Is it only the word itself, or the word plus nothing? → `restatement`
2. Does it say it can't find / doesn't know the word? → `refusal`
3. Does it contain a standalone sentence that explains the word's meaning? → `definition`
   (even if a question or junk comes before or after; add a note, see tags below)
4. Does it mostly restate the instructions given to the model? → `echo`
5. Is it a question with no explanation in it? → `question`
6. Is it coherent but about something else? → `offtopic`
7. Otherwise → `unclear`

---

## 3. Edge cases seen in the actual data

| Output | Label | Notes tag |
|---|---|---|
| "What is the definition of the word "pinpoint"? The word "pinpoint" is used to describe a very precise location." | `definition` (a real explanation stands on its own) | `q+def` |
| "A) Pinpoint the location of a point." | `definition` if it reads as a gloss of the word; otherwise `unclear` | `format` |
| "A. A <b>plank</b> is a piece of wood used for a bed." | `definition` | `format` |
| "Pinpoint the specific location." (bare imperative gloss of a verb) | `definition` | `imperative` |
| "If you could travel back in time to the 1980s, what would you tell yourself?" | `offtopic` | |
| "What is the value of f(x)=2(x-3)^2-1 when x=-1?" | `offtopic` | |
| A definition followed by unrelated junk | `definition` | `trailing-junk` |
| A definition of a *different* word than the target | `offtopic` | `wrong-word` |
| Blank output cell (3 rows in Gemma3-270M: infantry, y, rehabilitation) | `unclear` | `empty` |
| A definition of the same word but the *other* part of speech than column E | `definition` | `wrong-pos` (informational only) |

Use the Notes tags above whenever they apply. They let us later report how many ambiguous
cases there were. For `unclear`, write one short sentence on why.

---

## 4. Order of work

Label in this order. Do Tier 1 first; it is the minimum the roadmap requires.

**Tier 1 (required):** Gemma3-27B-pt, Gemma3-4B-pt, Gemma3-27B, Qwen2.5-0.5B

**Tier 2 (needed for claim 3, the matched pt/it pairs):**
Gemma3-12B-pt, Gemma3-12B, Gemma3-1B-pt, Gemma3-1B, Gemma3-270M-pt, Gemma3-270M, Gemma3-4B

**Tier 3 (mostly definitions, lowest value; do last, or do 50 rows each if time is short):**
all remaining Qwen2.5 and Qwen3 tabs.

Rough effort: ~10-20 seconds per row, about 2,300 rows in total. Do it in sessions of one
to two models. Stop when you catch yourself labeling on autopilot.

---

## 5. Quality checks

1. **Self-consistency (required).** After at least one day, re-label 10 random rows from each
   Tier 1 and Tier 2 model *without looking at your first label*. Compute agreement (percent
   and Cohen's kappa between your two passes). Any class where you disagree with yourself
   often needs a clearer rule. Write the result in `DECISION_LOG.md`.
2. **Second labeler (recommended, small).** Ask one other person to label 20 rows from each
   of the 4 Tier 1 models (80 rows), using this document, and report kappa against you.
   A reviewer will ask for an agreement number; one other person on a small subset is enough.
3. **Blinding (optional).** If you want, have the rows shuffled across models with names
   hidden and a separate key file, so you do not know which output is from a base model.
   Ask and I will generate the shuffled sheet and the key.
4. **Record how the 100 rows per model were sampled** (random? seed?) in `DECISION_LOG.md`.
   If you do not know, check the script that created the workbook before you start.

---

## 6. When you finish

- Every row in Tier 1 and Tier 2 has exactly one label from the list above, in lowercase.
- Save in place in `data/exp2_labeling_workbook_labeled.xlsx`. Do not rename tabs or reorder rows.
  Keep a dated backup copy after each finished model (copy the file, do not edit the copy).
- Note the date you finished each model, and the date of the self-consistency pass.
- Only then build or run the filter. Report precision and recall **per class**; for
  instruct models most classes will have very few or zero examples, so report counts too.

---

## 7. Conventions seen in the first 222 labels (2026-10-01)

Keep these consistent; change one only with a note in this file.

- Formatting is not content: list markers (`A.`, `1.`, `I.`), HTML tags and answer keys are
  ignored when judging the output; the note is `format`.
- A marked-up sentence that is about something else (for example `1. The sun is shining
  brightly.` for *glare*) is `offtopic` + `format`.
- An exercise-style imperative built around the word (`A) Pinpoint the location of a point.`)
  is `offtopic` + `imperative`.
- Output that only repeats the task text (`The noun "midnight" in one short sentence. ...`) is
  `echo`.
- Blank output is `unclear`; add the note `empty` (Gemma3-270M rows 37, 44, 69 have none yet).

Borderline rows to re-check in the self-consistency pass, because similar rows were labeled
differently: Gemma3-270M-pt row 31 (`1. To devise a plan for a project.`, labeled `offtopic`
although it reads like a gloss of the verb) and row 22 (`1. branch of a tree` for the verb
*branch*, labeled `offtopic`).

## 8. Second pass for the uniform first-sentence unit (decision D009)

The filter will classify the first line / first sentence of each output, while this first pass
labels the whole stored output. Do not change how you label now. After the first pass, a
shorter second pass will cover only the rows where the first sentence differs from the stored
text, ignoring differences that are only markup or list markers. With the extraction rule as
built (`src/rs_dic_llm/extraction.py`) that is 180 rows, all in the five base-model tabs
(Gemma3-270M-pt 36, 1B-pt 33, 4B-pt 41, 12B-pt 34, 27B-pt 36); the instruct tabs have none.
Only 58 of them (first-pass label `definition` or `unclear`) can change between definition and
not-definition; the other 122 are taken to stay non-definitions (class not re-labeled). The
rule and the 58-row pass were approved in D019. The sheet is
`data/exp2_secondpass_sheet.xlsx` (ID, Word, First sentence, Label, Notes; shuffled, model
names hidden). Label the first sentence as if it were the model's entire answer; do not open
the key (`data/exp2_secondpass_KEY_do_not_open_until_done.csv`); it can be done any time, not
only after a day. Then `research/audit_scripts/11_secondpass_summary.py` reports how many
first-pass definitions survive on the first sentence alone and writes the validation set for
the first-sentence unit (2,300 rows: first-pass labels where the rule cuts nothing, second-pass
labels for the 58, "non-definition" for the 122).

---

## 9. After the first pass (status 2026-10-01)

The first pass is complete: 2,300 of 2,300 rows, reviewed in `RESEARCH_AUDIT.md` section 3b.
Tags beyond the ones defined above that came into use, and how they will be read in the
analysis (no relabeling needed, D018): `usage-fragment` and `imperative` = *usage* (the phrase
uses the word without explaining it); `task-meta` = *task text*; `empty` and `truncated` =
*blank or fragment*; `pos-only` with `restatement`; `wrong-pos` with `definition` (informational
only, never analysed: part of speech is out of scope, D017).

Still to do for the labels:
1. **Self-consistency re-label** (required, D005). The sheet is ready:
   `data/exp2_selfconsistency_sheet.xlsx`, 118 rows = 110 random (10 from each of the 11 Tier
   1/2 models) + 8 targeted (the six borderline Qwen3-0.6B imperatives and Gemma3-270M-pt rows
   22 and 31). Rows are shuffled, model names are hidden and there is no POS column. Label it
   from 2026-10-02 (at least one day after the first pass; the researcher labeled it earlier, on
   2026-10-01 at 08:55 JST: audit F21, D022), with the same seven labels and
   rules, without opening the first-pass workbook or the key file
   (`data/exp2_selfconsistency_KEY_do_not_open_until_done.csv`). Then tell the assistant: agreement
   (percent and Cohen's kappa, pooled and by group) is computed by
   `research/audit_scripts/9_selfconsistency_agreement.py`. Kappa is uninformative for the
   instruct models alone (nearly every label is `definition`); the pooled value and the base
   models carry the result.
2. **Second labeler** (optional, about 80 rows from the four Tier 1 models, person to be
   decided).
3. **Second pass on the first-sentence unit** (section 8): the 58-row sheet is ready,
   `data/exp2_secondpass_sheet.xlsx`.
