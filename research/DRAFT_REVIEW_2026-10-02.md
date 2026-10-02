# Draft review, 2026-10-02 (JST): references, interpretations, venue

Written by the assistant for the researcher. The work was stopped early on the researcher's request, and these are the results
saved at that point. `manuscript/draft_v0.md` was **not** edited. Nothing here is a decision. Derived numbers marked (derived) need an
`EVIDENCE_MAP.md` entry before they go into the draft.

Status:
- Reference check: **partial**. Five background checks (dictionary graphs, alignment, competitors, models and tools, venues) were
  stopped before they reported. Their transcripts were saved by Claude Code and can be resumed; otherwise, re-run the checklist in section 4.
- Interpretation review: **complete** (section 2).
- Venue facts: **almost all unchecked** (section 3).

## 1. References: what was checked

| Ref | Result | Source used |
|---|---|---|
| LIMA (not yet cited) | Zhou, Liu, Xu, Iyer, Sun, Mao, Ma, Efrat, Yu, Yu, Zhang, Ghosh, Lewis, Zettlemoyer, Levy, "LIMA: Less Is More for Alignment", NeurIPS 2023 (Advances in Neural Information Processing Systems 36), arXiv:2305.11206. The paper defines the term **Superficial Alignment Hypothesis** in Section 2 ("Alignment Data"): knowledge and capabilities are learnt almost entirely in pretraining, and alignment teaches which "subdistribution of formats" to use. **Cite it beside [Lin24] in Section 2.** | arxiv.org/abs/2305.11206; ar5iv.labs.arxiv.org/html/2305.11206; proceedings.neurips.cc/paper_files/paper/2023/hash/ac662d74829e4407ce1d126477f4a03a-Abstract-Conference.html |
| [Bou26] | The paper exists. Moses Boudourides, "Structural Hallucination in Large Language Models: A Network-Based Evaluation of Knowledge Organization and Citation Integrity", arXiv:2603.01341, cs.SI; v1 2026-03-02, v2 2026-08-21. Abstract: it tests three domains (Roget's Thesaurus, Wikidata philosopher records, citation databases), with lexical F1 below 0.05. It was not read in full, so whether it uses a null model or cycles is not checked. | arxiv.org/abs/2603.01341 |
| All others | **Not checked** ([VL16], [Lev12], [BM08], [Har25], [Lin24], [Res24], [Lak25], [Gud26], [Baa25], [Sch23], [New18], and the candidates in section 4). | — |

Problems in the draft's citing sentences, found from the repository alone:
- **"the usual 5×|E| swaps"** (Section 1 and 3.5). The 5× setting comes from the project's own code (`experiments/null_model.py` line 67,
  `nswap=5 * H.number_of_edges()`), not from any cited practice. Either cite a source (Fosdick et al. 2018 is a candidate) or write "the
  5×|E| swaps of our first run".
- **"Earlier work asked whether the definitions they write match human ones"** (Section 1) has no citation. Candidates, all unverified:
  Noraset et al. 2017 (AAAI), Giulianelli et al. 2023 (ACL), Periti et al. 2024 (EMNLP), Pham et al. 2023 (arXiv:2311.06362).
- **Harnad sentence** (Section 1): check against the paper whether "a reason why language models can work at all" is his claim or a
  stronger paraphrase.

## 2. The seven interpretations (EVIDENCE_MAP "Interpretations to check")

**1. Section 4.1, "a statement about the density of the graph". Keep the logic and change three words.**
- The null fixes every word's in- and out-degree, so what it shows is that the kernel ratio is explained by the *degrees*. Density is the
  main part of that (r(kernel, edges) +0.80, or +0.64 without Gemma3-270M; RESEARCH_AUDIT section 1 and F15, on the 08-09 graphs, so the
  figure is not citable as is).
- "Not about its structure": the degrees are themselves structure.
- "Withdraw": the earlier claim is in an unpublished internal draft (`docs/paper_en.md` 5.3). If it was never presented outside the lab,
  "correct" fits better.
- Proposed: "...is thus a statement about the degrees of the graph, chiefly how many links longer definitions create, and not about how
  the links are arranged; this corrects our earlier analysis (Section 1)."

**2. Section 4.2, "near-synonyms ..., which WordNet's typing undercounts". Change.**
- No count stands behind it, and it is one-sided: the unlinked class also holds associates (eat–mouth, greet–hello, big–size;
  `20_pair_types.txt` section 1).
- "Near-synonyms" is the label the project agreed not to use for the pairs (D026 amendment).
- It also sits uneasily with Section 3.7's "the typing is generous".
- Proposed: "WordNet's relations type the pairs coarsely: some pairs typed as hypernym pairs or as unlinked are close in ordinary use
  (flavor–taste, location–place), while others are associations (eat–mouth, greet–hello)."
- The same sentence is in `PROJECT_CONTEXT.md` claim 2. Change both together.

**3. Section 5, "...it requires a prompt, or a tuning, that makes the model write one-sentence definitions". Keep the first half and
replace the second.**
- The second half assumes the answer to the open question about the zero-shot gap.
- The filtered zero-shot graphs are mostly definitions already. On the 50 test words, the filter keeps 98 records from the four matched
  pretrained models (1B–27B), and 82 of them are labeled definitions; 16 are not (derived from `14_test_scored.txt`, per-model lines:
  kept 31/21/29/17, missed 5/3/6/2).
- Those graphs still have R of 2.1–8.4, so writing definitions is not enough by itself.
- Proposed: "So, given three examples, the structure R measures does not require instruction tuning at 4B and above. What the zero-shot
  pretrained models lack, and three examples supply, is not identified: most zero-shot outputs that the filter keeps are definitions, yet
  they form few mutual pairs."

**4. Section 5, "the models converge on one another's pairs more than on WordNet's". Change the verb.**
- "Converge" implies a trend over size or training. It is also the verb of the corrected earlier claim. The title (D028) uses "resemble".
- "Each ... overlaps another instruct model more than it overlaps WordNet" is not printed per model anywhere. State what is printed.
- Proposed: "the median overlap between two instruct models (Jaccard 0.14) is above the overlap of every instruct model with WordNet
  (0.010–0.055)", and "the models share more of their pairs with one another than with WordNet".
- Also change "converge *on* human dictionaries" to "resemble human ones".
- Point to the Limitations "Prompt" bullet: a shared prompt (common words) can make the models share pairs.

**5. Section 5, the three open explanations of the zero-shot gap. Keep them as hypotheses and make them concrete.**
- (1) Leaked junk. Give the share of *kept* records: about 1 in 6 at 1B–27B (16 of 98, derived). That share is what dilutes the graph,
  and it says more than "18.5 % of non-definitions".
- (2) "A mismatch between what the prompt elicits and what the filter and graph can read" is too vague to test. Split it in two:
  - (2a) Which words keep a definition. The filter drops 47–58 % of the pretrained records. The null corrects for this only if the
    dropped words are random, not if they are the words that would form pairs. This can be tested on the CPU: restrict each few-shot graph
    to the words whose zero-shot record survived, then recompute R.
  - (2b) What the definitions say. Compare the defining words of zero-shot and few-shot outputs for the same headwords.
- (3) Sampling covers two separate things: run-to-run noise (needs seeds) and a systematic effect of temperature 0.7 on an untuned model
  (needs a greedy run). Both need a GPU.
- Observation (not followed up): at each size the null means of the instruct and pretrained graphs are similar (Table A1:
  0.80/0.45, 1.68/1.31, 3.04/3.33, 2.79/2.85), although the pretrained graphs have about half the edges. The observed pair counts differ
  sharply (34/3, 47/11, 78/7, 71/14).
- Update the "Next steps" sentence to match.

**6. Section 2, "the few-shot result is of the kind the superficial-alignment picture would lead one to expect; the zero-shot gap is the
part it leaves unexplained". Keep the first half and reword the second.**
- On LIMA's definition (verified above), the few-shot result is what the hypothesis predicts.
- The hypothesis also predicts the zero-shot failure of format (echoes, questions), and the filter removes that failure. What the
  hypothesis does not explain is the part that survives filtering.
- Proposed: "Our few-shot result fits this hypothesis [LIMA; Lin24]: three examples, which change only the prompt, bring pretrained R to
  the instruct level at 4B and above. The hypothesis also predicts a zero-shot failure of format, which the filter removes; it does not
  say why the zero-shot outputs that are definitions form fewer mutual pairs."
- [Lin24] and [Lak25] are still to be checked.

**7. Section 4.3.3, "The examples do not drive R". Change.**
- As written, the sentence contradicts the main E3 result: the examples are what raise pretrained R from 2.1–8.4 to 22–31. The evidence
  shows something narrower.
- A bound exists without a rerun. The mutual pairs that involve one of the 12 example words are 4 of 29 (1B), 6 of 92, 6 of 114 and
  5 of 78 (`23_e3_example_words.txt` section 2). Removing all of them lowers the count by at most 14 % (1B) and 5–7 % (4B–27B) (derived).
- Proposed: "R does not come from the examples' own words: removing every mutual pair that involves one of them would lower the few-shot
  count by at most 14 % (1B) and 5–7 % (4B–27B). Exact copies of an example definition are rare (Section 4.3.3)."

## 3. Venue and length (partial)

- **Checked only in a web-search summary, not on anlp.jp:** NLP2027 (the 33rd annual meeting) runs 2027-03-15 to 03-19 at the Fukuoka
  International Congress Center, in hybrid form. The call for papers was not found.
- **Still to confirm:** the paper deadline, the page limit (and whether references and appendices count), whether English papers are
  accepted, the policy on later submission elsewhere, IPSJ SIG-NL dates, and whether Topics in Cognitive Science takes unsolicited papers.
- **Assistant's recommendation (not a decision; Pepe and Kumoi decide):** keep `draft_v0.md` as the full-length master, aimed at a
  journal, and make the domestic version a separate file once the limit is known.
  - For a version of about 4 pages, keep: the question and the kernel correction; the method (prompt, graph, converged null, R, the
    filter's validation in three lines, the readings fixed in advance); the R ranges; Table 4 (default and strict columns only); Table 5;
    Figure 4a; the WordNet overlap sentence; and a short discussion with the limits.
  - Cut Figures 1–3 and Tables 2–3 to one sentence each, E4/E5 to one sentence, and scale to one sentence. Move the filter details and
    Table A1 to an appendix, if appendices are allowed.

## 4. Checklist to finish the reference check

For each item, confirm the metadata from arXiv, the ACL Anthology, the DOI page or DBLP, and check the claim the draft makes:
- **[VL16]**: TopiCS 8(3), DOI 10.1111/tops.12211. Check the definitions of kernel, Core, Satellites and MinSet, and the edge direction.
  Settle whether the Core is the "source SCCs of the kernel's condensation" or the "largest SCC".
- **[Lev12]**: PRX 2:031018. Do loops come out "much shorter than random"? Which null and which resource (WordNet?) did they use?
- **[BM08]**: TextGraphs-3 pages. Are grounding sets feedback vertex sets, and is finding a minimum NP-hard?
- **[Har25]**: Front. Artif. Intell. 7:1490698. What is the exact framing of "the circularity of verbal definition" (a "bias" that "may
  help")? No experiment.
- **[Lin24]**: ICLR 2024. Check the 77.7 % figure, its unshifted / marginal / shifted categories, and the number of URIAL examples.
- **[Res24]**: arXiv:2410.02465. Authors and venue; the "adequate output space" wording.
- **[Lak25]**: NAACL 2025. Quality control and aggregation; base models with in-context examples resembling aligned ones; the
  Superficial Alignment Hypothesis.
- **[Gud26]**: arXiv:2605.06030, ACL 2026. HPSG; are the model pairs matched or from different generations? Is there a null?
- **[Baa25]**: arXiv:2505.11764. The definition of its circularity metric.
- **[Sch23]**: NeurIPS 2023.
- **[New18]**: chapter numbers. "Ch. 12–13" may be the 1st edition's numbering.
- **Candidates:**
  - Ivgi et al. 2024 (arXiv:2407.06071)
  - "The Price of Format" (Findings of EMNLP 2025)
  - Suresh et al. (EMNLP 2023)
  - Gammelgaard et al. (arXiv:2308.15047)
  - Pham et al. (arXiv:2311.06362)
  - Periti et al. (EMNLP 2024)
  - Noraset et al. (2017)
  - Giulianelli et al. (2023)
  - OpenGloss (arXiv:2511.18622)
  - Gemma 3 (arXiv:2503.19786), Qwen2.5 (arXiv:2412.15115) and Qwen3 (arXiv:2505.09388) reports
  - WordNet (Miller 1995; Fellbaum 1998), the Brown corpus, NLTK (Bird et al. 2009), NetworkX (Hagberg et al. 2008)
  - Garlaschelli & Loffredo 2004 (reciprocity against a null)
  - Milo et al. 2002/2003; Fosdick et al. 2018 (number of swaps)
  - Garwood 1936 (exact Poisson interval)

## 5. Questions for the researcher

1. Was the earlier "larger models converge" claim presented outside the lab? This decides "withdraw" versus "correct" in 4.1.
2. Should interpretation changes 1–7 be applied to the draft? The derived numbers would get evidence-map entries.
3. Should the CPU test in 5 (2a) be run? It would need a decision entry.
