# Reference check, 2026-10-02 (JST)

Written by the assistant for the researcher. It finishes the check that `DRAFT_REVIEW_2026-10-02.md` (section 4) left partial: only LIMA and
[Bou26] had been checked when the earlier agents were stopped. Nothing here is a decision. **The assistant checked these sources, and the researcher then verified them (chat, 2026-10-02: "i verified them everything correct").** By the rule
in `CLAUDE.md` the references can now be cited. The limits listed in section 5 (for example the unconfirmed venue of [Gud26]) are unchanged: the
researcher's check did not add the missing facts.

## 1. Method and limits

- **Metadata:** Crossref (DOIs), the arXiv API, the ACL Anthology (bib files), the ICLR and NeurIPS proceedings pages, Europe PMC (the Frontiers
  article). **Claims:** each claim the draft makes about a source was checked by finding the passage in the source's text (PDFs downloaded and
  converted with `pdftotext`, then searched), not by a summary. Codes below: **C** Crossref, **A** arXiv API, **T** full text searched,
  **P** proceedings or conference page, **S** a web-search summary only (weakest).
- The papers were **not read in full**. A statement such as "no null model in [Bou26]" means that a search of the text found none.
- The downloaded PDFs are not kept in the repository. The helper scripts are in `reference_checks_2026-10-02/` (`ref_meta.py`, `fetch_ref.py`,
  `grep_ref.py`); `fetch_ref.py` writes to a `refs/` subfolder next to itself.
- The quotes below are short, only to identify wording; everything else is paraphrase.

## 2. The twelve references cited in `draft_v0.md`

| Key | Verified citation | Checked | What v0 said | What the source says | Action in v1 |
|---|---|---|---|---|---|
| [VL16] | Vincent-Lamarre, Blondin Massé, Lopes, Lord, Marcotte, Harnad (2016), *The Latent Structure of Dictionaries*, Topics in Cognitive Science 8(3): 625-659, DOI 10.1111/tops.12211 | C, A, T (text of arXiv 1411.0129v2, 22 Jan 2016; Wiley returns 403) | A kernel of words that defines all the others; Core definition left open | Four dictionaries (Longman, Cambridge, Merriam-Webster, WordNet). Links run from defining to defined words, as in our graphs. Kernel: what remains after recursively removing words that define nothing further, 7-12 % of the words, a grounding set. **Core: "the union of Sources" of the Kernel**, equal to its largest strongly connected component in two dictionaries and the largest plus a few small components in the other two (attributed to preprocessing). Satellites: the other components of the Kernel. MinSets: about 15 % of the Kernel. The C-hierarchy paragraph speaks of "the biggest" component, which is where the audit's "largest SCC" came from | **Open point settled:** our code's Core is the paper's. Description corrected; WordNet has precedent as a baseline |
| [Lev12] | Levary, Eckmann, Moses, Tlusty (2012), *Loops and Self-Reference in the Construction of Dictionaries*, Physical Review X 2: 031018 | C, T (PRX PDF) | Loops in human dictionaries "much shorter than in random graphs" | The abstract: unlike a random lexical network, meaningful loops in dictionary graphs are quite short. In the paper, long loops (more than 5 links) are predicted by the in- and out-degree distributions (links redrawn at random with the distributions kept), while short loops are not. Graphs: eXtended WordNet (synsets, primary), English Wiktionary, WordNet 3.0 | Reworded. **It is the direct precedent for R** (excess of short loops against a degree-preserving randomization) |
| [BM08] | Blondin Massé, Chicoisne, Gargouri, Harnad, Picard, Marcotte (2008), *How Is Meaning Grounded in Dictionary Definitions?*, TextGraphs-3 at Coling 2008, arXiv:0806.3710 | A, T | Grounding sets as minimum feedback vertex sets (NP-hardness) | Theorem 7: a set is a grounding set if and only if it is a feedback vertex set. Corollary 8: deciding whether a graph has a grounding set of size k is NP-complete | Confirmed; wording made exact |
| [Har25] | Harnad (2025), *Language writ large: LLMs, ChatGPT, meaning, and understanding*, Frontiers in Artificial Intelligence 7: 1490698 (online 12 Feb 2025), DOI 10.3389/frai.2024.1490698 | C, T (Europe PMC full text) | Named the circularity of verbal definition "as a reason why language models can work at all" | Offers "hunches" about benign "biases", convergent constraints at LLM scale that may help ChatGPT do better than expected, related to six items including the circularity of verbal definition. The paper is a dialogue with ChatGPT-4; no measurement | **Stronger than the source; reworded** to the abstract's level |
| [Lin24] | Lin, Ravichander, Lu, Dziri, Sclar, Chandu, Bhagavatula, Choi (2024), *The Unlocking Spell on Base LLMs: Rethinking Alignment via In-Context Learning*, ICLR 2024, arXiv:2312.01552 | A, T, P | Most token positions keep the same top-1 token; shifts are stylistic | On average 77.7 % of tokens of Llama-2-7b-chat's responses are also the base model's top-1 token (1,000 examples) and 92.2 % are within its top 3; 82.4 % for Vicuna and 82.2 % for Mistral-7b-instruct. Shifted tokens are mostly stylistic (discourse markers, safety phrases). URIAL aligns base models in context with as few as three constant stylistic examples and a system prompt | Confirmed; numbers added; the three-example parallel with E3 noted |
| [Res24] | An, Kim, Kim (2025), *Revealing the Inherent Instructability of Pre-Trained Language Models*, Findings of EMNLP 2025, arXiv:2410.02465 (v1, 3 Oct 2024, was titled *Response Tuning: Aligning Large Language Models without Instruction*, by An and Kim) | A, T | "Response Tuning", authors and title to complete; base models lack a response distribution, not the capability | Hypothesis: pretraining already gives the ability to comprehend and address instructions. Models tuned only on responses, without instructions, respond to a wide range of instructions like instruction-tuned ones | **Title and authors corrected**; description reworded |
| [Lak25] | Lake, Choi, Durrett (2025), *From Distributional to Overton Pluralism: Investigating Large Language Model Alignment*, NAACL 2025 (Long Papers), pp. 6794-6814, DOI 10.18653/v1/2025.naacl-long.346 | T (ACL Anthology PDF), bib | "The objection that effects of this kind reduce to length or aggregation" | The apparent drop in response diversity after alignment is largely explained by quality control and information aggregation (longer responses that cover several base-model responses). Aligned behaviour is recoverable from base models without fine-tuning, with in-context examples and semantic hints; supports the Superficial Alignment Hypothesis | **Identified; the "objection" attribution dropped**; relevant to E3 |
| [Bou26] | Boudourides (2026), *Structural Hallucination in Large Language Models: A Network-Based Evaluation of Knowledge Organization and Citation Integrity*, arXiv:2603.01341 (v1 2 Mar 2026, v2 21 Aug 2026) | A, T | The "closest competing framing", to be read so the difference can be stated | Introduces structural hallucination; stress test on Roget's Thesaurus, Wikidata philosophers and citation records (lexical F1 below 0.05; node-set Jaccard 0.028 on Roget). A search of the text found no null model, no cycle statistic and no dictionary graph | **Difference stated**: it compares LLM-built networks with reference networks |
| [Baa25] | Baartmans, Raffel, Vikram, Deringer, Chen (2025), *Towards Universal Semantics With Large Language Models*, arXiv:2505.11764 (v3, 3 Jul 2025) | A, T | "DeepNSM", per-sentence circularity and prime use | DeepNSM is the name of the code and models. The paper generates Natural Semantic Metalanguage explications with LLMs. Circularity is detected by checking whether any form of the original word is in the explication; a "legality" score counts semantic primes | Title corrected; wording made exact |
| [Gud26] | Gude, Santos-Ríos, Bond, Flickinger, Gómez-Rodríguez, Zamaraeva (2026), *More Aligned, Less Diverse? Analyzing the Grammar and Lexicon of Two Generations of LLMs*, arXiv:2605.06030 (7 May 2026) | A, T | "Instruction tuning narrows structure", HPSG, "the nearest competitor" | Compares older base models (LLaMA, Mistral, Falcon, before 2023) with newer instruction-tuned ones (Qwen2.5, Mistral 7B v0.3, GPT-4o, LLaMA 3.3) and with New York Times lead paragraphs of 2023 and 2025, using HPSG and Shannon and Simpson indices. Newer models show lower syntactic and especially lexical diversity. The groups differ in generation as well as in tuning; news text, not definitions | **Title corrected; described as it is**; "nearest competitor" dropped. **Venue unconfirmed:** the roadmap says ACL 2026, the arXiv record shows no venue |
| [Sch23] | Schaeffer, Miranda, Koyejo (2023), *Are Emergent Abilities of Large Language Models a Mirage?*, NeurIPS 2023 (Advances in Neural Information Processing Systems 36), arXiv:2304.15004 | A, T, P | Apparent emergence can be a metric artifact | Confirmed: nonlinear or discontinuous metrics produce apparent emergent abilities, linear or continuous ones give smooth, predictable change | Unchanged in substance |
| [New18] | Newman (2018), *Networks*, 2nd ed., Oxford University Press | C (chapter titles), S | "Chapters 12-13" | In the 2nd edition chapter 11 is *Random graphs*, **12 *The configuration model***, 13 *Models of network formation*. The numbers are inferred from the chapter DOIs (10.1093/oso/9780198805090.003.0011-0013); OUP's own page could not be opened | Pointer changed to chapter 12 |

## 3. References added in v1 (metadata checked)

| Key | Citation | Checked | Use |
|---|---|---|---|
| [Zho23] | Zhou et al. (2023), *LIMA: Less Is More for Alignment*, NeurIPS 2023, arXiv:2305.11206 | A, T (definition read in Section 2 of the paper); venue from the earlier check | Defines the Superficial Alignment Hypothesis (knowledge and capabilities learnt in pretraining; alignment teaches the subdistribution of formats) |
| [Gam23] | Gammelgaard, Christiansen, Søgaard (2023), *Large language models converge toward human-like concept organization*, arXiv:2308.15047 | A, T | Bigger and better models organise concepts more like knowledge-graph embeddings (four families). Same verb as our corrected earlier claim; a different structure |
| [Sur23] | Suresh et al. (2023), *Conceptual structure coheres in human cognition but not in large language models*, EMNLP 2023, pp. 722-738 | S (ACL Anthology link) | The opposing result: LLM-derived structure varies more across tasks than human structure |
| [Nor17] | Noraset, Liang, Birnbaum, Downey (2017), *Definition Modeling*, AAAI 2017, arXiv:1612.00394 | A, T | Definition generation as a task |
| [Pha25] | Pham, Wong, Kim, Yin, Skiena (2025), *Word Definitions from Large Language Models*, IEEE ICSC 2025, DOI 10.1109/ICSC64641.2025.00028, arXiv:2311.06362 | A, T | The earlier work that compared LLM definitions with dictionaries (over 2,500 words; WordNet, Merriam-Webster, Random House) |
| [Bom25] | Bommarito (2025), *OpenGloss*, arXiv:2511.18622 | A, T | An LLM-generated dictionary and semantic graph, 537 thousand senses |
| [GL04] | Garlaschelli, Loffredo (2004), *Patterns of Link Reciprocity in Directed Networks*, Phys. Rev. Lett. 93: 268701 | C, A, T | Reciprocity must be compared with what a random graph of the same size gives; a density-corrected measure |
| [Fos18] | Fosdick, Larremore, Nishimura, Ugander (2018), *Configuring Random Graph Models with Fixed Degree Sequences*, SIAM Review 60(2): 315-355 | C, A, T | Null models with fixed degrees; mixing time of edge-swap samplers. No rule of thumb for the number of swaps was found |
| [Gar36], [CP34] | Garwood (1936), Biometrika 28: 437-442; Clopper, Pearson (1934), Biometrika 26: 404-413 | C | The exact Poisson and exact binomial intervals |
| [Gem25], [Gem270] | Gemma Team (2025), *Gemma 3 Technical Report*, arXiv:2503.19786 (covers 1B to 27B); Google Developers Blog, *Introducing Gemma 3 270M*, 14 Aug 2025 | A; blog fetched | **The 270M models are not in the Gemma 3 report** |
| [Qw25], [Qw3] | Qwen2.5 Technical Report, arXiv:2412.15115; Qwen3 Technical Report (Yang et al.), arXiv:2505.09388 (0.6 to 235B) | A; Hugging Face model card | The card of Qwen3-4B-Instruct-2507 calls it an update of the 4B non-thinking model and gives the Qwen3 report as its citation |
| [Mil95], [Fel98] | Miller (1995), *WordNet*, CACM 38(11): 39-41, DOI 10.1145/219717.219748; Fellbaum (ed., 1998), *WordNet: An Electronic Lexical Database*, MIT Press, DOI 10.7551/mitpress/7287.001.0001 | C | WordNet |
| [FK79] | Francis, Kučera (1979), *Brown Corpus Manual* (revised and amplified), Brown University | S | The Brown corpus |
| [BKL09] | Bird, Klein, Loper (2009), *Natural Language Processing with Python*, O'Reilly | nltk.org page text | The citation NLTK asks for |
| [HSS08] | Hagberg, Schult, Swart (2008), *Exploring network structure, dynamics, and function using NetworkX*, SciPy 2008, pp. 11-15 | S | NetworkX |

## 4. Checked, and not used

- Ivgi, Yoran, Berant, Geva (2024), *From Loops to Oops*, arXiv:2407.06071 (NeurIPS ATTRIB workshop 2024; A): fallback behaviours under uncertainty; the draft does not need it.
- Giulianelli et al. (2023), ACL 2023 long, pp. 3130-3148, and Periti, Alfter, Tahmasebi (2024), EMNLP 2024 main, pp. 14008-14026 (S): definition generation to model word meaning and semantic change; background only.
- Yun et al. (2025), *The Price of Format: Diversity Collapse in LLMs*, Findings of EMNLP 2025, pp. 15454-15468, arXiv:2505.18949 (S): format tokens and diversity; possibly relevant to the template control, not needed now.
- Milo et al. (2002), *Network Motifs*, Science 298: 824-827 (C only): the claim about its randomized networks was not checked, so it is not cited.

## 5. Not verified, or only partly

- [VL16]: the text is that of the arXiv version of January 2016; the journal version (July 2016) was not opened. [Lev12]: the abstract was read from a two-column PDF extraction.
- [Gud26]: venue. [Har25]: volume year 2024, online 2025; cited as 2025.
- [New18]: chapter numbers inferred from DOI suffixes. [Mil95]: Crossref gives the title as "WordNet". [FK79], [HSS08], [Sur23]: web-search summaries only.
- The **venue facts** of `DRAFT_REVIEW_2026-10-02.md` section 3 (NLP2027 and others) are **not** covered here.

## 6. What this changed in the draft (v1)

1. [VL16]'s description corrected, the open point on the Core settled, and WordNet's precedent as a baseline added.
2. [Lev12] reworded and identified as the precedent for R.
3. [Har25] reworded to what the abstract says.
4. [Res24] retitled; [Bou26], [Baa25] and [Gud26] described as they are, and "closest competitor" or "nearest competitor" dropped.
5. [Lak25] identified; the objection attributed to it removed.
6. [New18] pointed to chapter 12; "the usual 5×|E| swaps" replaced (no source gives it; [Fos18] gives none).
7. Models, tools and methods now have sources, and the 270M model's separate citation is stated.
8. A citation added for the sentence "earlier work asked whether the definitions they write match human ones" ([Pha25], with [Nor17]).
9. New related work added where it bears on the title and the scale question: [Gam23] and [Sur23].
