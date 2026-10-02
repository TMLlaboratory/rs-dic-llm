
**Table 1.** Claim 1: z-scores of the kernel ratio and the circulation rate against the degree-preserving null, by group (median, with the number of graphs below 0 / beyond -2 / beyond +2).

| Measure | Group | n | Unfiltered | Default filter | Strict filter |
|---|---|---:|---|---|---|
| Kernel ratio | 17 instruct models | 17 | +0.16 (7 / 2 / 1) | +0.31 (7 / 2 / 1) | +0.10 (7 / 3 / 1) |
| Kernel ratio | 5 pretrained models | 5 | -1.67 (5 / 2 / 0) | +1.68 (0 / 0 / 2) | +1.37 (0 / 0 / 2) |
| Kernel ratio | WordNet | 1 | -0.08 (1 / 0 / 0) | -0.08 (1 / 0 / 0) | -0.08 (1 / 0 / 0) |
| Circulation rate | 17 instruct models | 17 | -1.34 (15 / 6 / 0) | -1.51 (15 / 6 / 0) | -1.37 (15 / 6 / 0) |
| Circulation rate | 5 pretrained models | 5 | -1.81 (5 / 2 / 0) | +1.90 (0 / 0 / 2) | +2.20 (0 / 0 / 3) |
| Circulation rate | WordNet | 1 | -1.89 (1 / 0 / 0) | -1.89 (1 / 0 / 0) | -1.89 (1 / 0 / 0) |

**Table 2.** Cycle lengths in the default-filter graphs: observed number of cycles / mean number in the null, summed over the graphs of a group.

| Group | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|
| 17 instruct models | 881 / 47 = 18.83x | 93 / 41 = 2.24x | 56 / 58 = 0.97x | 58 / 98 = 0.59x | 86 / 167 = 0.52x | 138 / 302 = 0.46x |
| 5 pretrained models | 39 / 9 = 4.21x | 2 / 3 = 0.76x | 0 / 1 = 0.00x | 0 / 1 = 0.00x | 0 / 0 = 0.00x | 0 / 0 = 0.00x |
| WordNet | 27 / 2 = 15.70x | 2 / 2 = 1.00x | 4 / 3 = 1.57x | 3 / 3 = 0.88x | 3 / 4 = 0.69x | 2 / 6 = 0.34x |

**Table 3.** Mutual pairs by WordNet relation (all senses, no part of speech; the first match in the order of the columns decides). Counts, with shares of the pair occurrences in brackets.

| Source | Pair occurrences | Synonym | Hypernym | Sister term | Antonym | Derived form | No direct link |
|---|---:|---:|---:|---:|---:|---:|---:|
| WordNet | 27 | 2 (7 %) | 9 (33 %) | 1 (4 %) | 0 (0 %) | 3 (11 %) | 12 (44 %) |
| 17 instruct models | 881 | 339 (38 %) | 192 (22 %) | 77 (9 %) | 14 (2 %) | 7 (1 %) | 252 (29 %) |
| Few-shot pretrained (E3) | 324 | 106 (33 %) | 69 (21 %) | 35 (11 %) | 3 (1 %) | 5 (2 %) | 106 (33 %) |
| Zero-shot pretrained | 39 | 9 (23 %) | 11 (28 %) | 0 (0 %) | 0 (0 %) | 1 (3 %) | 18 (46 %) |

**Table 4.** Matched Gemma3 pairs under a zero-shot prompt: R of the instruct model / R of the pretrained model, with the exact conditional 95 % range of the ratio, under five variants of the analysis.

| Size | Instruct R | Pretrained R | Default filter | Unfiltered | Strict filter | Whole stored text | Six frame words removed |
|---|---:|---:|---|---|---|---|---|
| 1B | 42.5 | 6.0 | 7.1 [2.2, 36.0] | 13.9 [7.1, 28.6] | 5.8 [1.8, 29.9] | 7.1 [2.9, 20.6] | 7.1 [2.2, 35.9] |
| 4B | 28.0 | 8.4 | 3.3 [1.7, 7.1] | 4.3 [2.5, 7.8] | 4.8 [2.4, 10.7] | 2.2 [1.2, 4.5] | 9.7 [4.9, 20.7] |
| 12B | 25.7 | 2.1 | 12.2 [5.7, 31.4] | 4.9 [2.9, 9.1] | 11.7 [5.4, 29.9] | 10.0 [4.8, 23.9] | 12.9 [6.0, 33.1] |
| 27B | 25.4 | 4.9 | 5.2 [2.9, 10.0] | 2.5 [1.6, 4.1] | 3.8 [2.1, 7.3] | 3.4 [1.9, 6.4] | 6.7 [3.7, 12.9] |

Over the 20 pair-by-variant comparisons the range excludes 1 in 20 and excludes 2 in 15.

**Table 5.** The three-example prompt (E3): R of the pretrained Gemma3 models given three example definitions, against the zero-shot pretrained model and the instruct model of the same size (default filter). The ratio is instruct R / few-shot R; the exact range is the conditional range, the conservative range combines the two ends of the Poisson ranges.

| Size | Zero-shot pretrained R | Few-shot pretrained R (95 % range) | Instruct R | Instruct / few-shot | Exact range | Conservative range |
|---|---:|---:|---:|---:|---|---|
| 270M | 3.0 | 4.6 [2.3, 8.3] | no cycles (D011) | -- | -- | -- |
| 1B | 6.0 | 22.3 [14.9, 32.0] | 42.5 | 1.91 | [1.13, 3.24] | [0.92, 3.98] |
| 4B | 8.4 | 23.5 [18.9, 28.8] | 28.0 | 1.19 | [0.82, 1.71] | [0.71, 1.97] |
| 12B | 2.1 | 30.9 [25.5, 37.1] | 25.7 | 0.83 | [0.61, 1.12] | [0.55, 1.26] |
| 27B | 4.9 | 28.5 [22.5, 35.5] | 25.4 | 0.89 | [0.64, 1.25] | [0.56, 1.43] |

**Table 6.** Equal coverage (D029). R of the zero-shot pretrained graph and of the few-shot and instruct graphs limited to the entries whose zero-shot record survived the filter (the same entries), with the exact Poisson 95 % range, and the exact conditional range of instruct / zero-shot. The last three columns are the few-shot graph limited to five random sets of entries of the same size (smallest to largest R) and the graphs of the whole word list.

| Size | Entries kept (of 3,000) | Zero-shot pretrained | Few-shot, same entries | Instruct, same entries | Instruct / zero-shot (exact range) | Few-shot, five random halves | Few-shot, whole list | Instruct, whole list |
|---|---:|---|---|---|---|---|---:|---:|
| 1B | 1,580 | 6.0 [1.2, 17.5] (3 pairs) | 5.4 [2.0, 11.8] (6) | 3.0 [1.3, 5.6] (9) | 0.49 [0.12, 2.82] | 4.6 to 11.3 | 22.3 | 42.5 |
| 4B | 1,322 | 8.4 [4.2, 15.0] (11 pairs) | 6.2 [3.7, 9.8] (18) | 4.5 [2.3, 7.9] (12) | 0.54 [0.22, 1.34] | 2.5 to 8.7 | 23.5 | 28.0 |
| 12B | 1,503 | 2.1 [0.8, 4.3] (7 pairs) | 3.3 [2.1, 5.1] (21) | 6.3 [3.7, 10.2] (17) | 3.02 [1.19, 8.61] | 3.7 to 6.3 | 30.9 | 25.7 |
| 27B | 1,296 | 4.9 [2.7, 8.2] (14 pairs) | 5.7 [3.5, 8.7] (21) | 8.8 [4.9, 14.6] (15) | 1.80 [0.81, 4.02] | 1.9 to 10.0 | 28.5 | 25.4 |

The exact range of instruct / zero-shot includes 1 at 3 of 4 sizes.

**Table 7.** Mutual pairs of the instruct graph that the other graphs contain, at equal coverage (D029). At risk: mutual pairs of the instruct graph (whole word list) whose two words both have a surviving zero-shot entry. Zero-shot: the zero-shot graph; few-shot: the few-shot graph limited to the same entries. Exact McNemar test on the pairs found in one graph and not in the other.

| Size | Instruct pairs | At risk | Zero-shot | Few-shot, same entries | Only few-shot | Only zero-shot | Exact McNemar p |
|---|---:|---:|---|---|---:|---:|---:|
| 1B | 34 | 12 | 0 (0 %) | 0 (0 %) | 0 | 0 | 1.000 |
| 4B | 47 | 12 | 1 (8 %) | 6 (50 %) | 5 | 0 | 0.062 |
| 12B | 78 | 19 | 2 (10 %) | 8 (42 %) | 7 | 1 | 0.070 |
| 27B | 71 | 19 | 2 (10 %) | 6 (32 %) | 4 | 0 | 0.125 |
| Pooled (descriptive: pairs recur across sizes) | -- | 62 | 5 (8 %; 95 % range 3-18 %) | 20 (32 %; 21-45 %) | 16 | 1 | 0.0003 |
| Each different pair once (52 pairs) | -- | 52 | 4 | 17 | 14 | 1 | 0.001 |

**Table 8.** Defining words of the same entries in the three conditions (D029 (c); entries kept in all three conditions; the defining words of an entry are the in-vocabulary lemmas of its first sentence, the headword excluded). Jaccard index of the defining-word sets with the instruct definition of the same entry (mean); share of records that contain one of six frame words (define, mean, refer, describe, phrase, use); share of all defining-word occurrences carried by the five most used words.

| Size | Mean Jaccard with instruct: zero-shot | few-shot | few-shot / zero-shot | Frame word: zero-shot | few-shot | instruct | Top-5 words: zero-shot | few-shot | instruct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1B | 0.114 | 0.167 | 1.46 | 43 % | 7 % | 6 % | 30 % | 15 % | 14 % |
| 4B | 0.134 | 0.199 | 1.48 | 35 % | 9 % | 13 % | 22 % | 12 % | 14 % |
| 12B | 0.152 | 0.250 | 1.65 | 32 % | 10 % | 27 % | 22 % | 12 % | 17 % |
| 27B | 0.173 | 0.247 | 1.43 | 30 % | 9 % | 20 % | 21 % | 12 % | 13 % |

**Table A1.** Definition graphs of the 23 analysed sources (default filter, first sentence; 2,750-lemma node set). R = observed mutual pairs / null mean (floor 0.5); the 95 % range is the exact Poisson range of the observed number of mutual pairs divided by the null mean; the last column is R of the unfiltered graphs (stored text). The zero-shot pretrained graphs cover about half of the entries (Section 4.3.5), which lowers their R.

| Source | Edges | Mutual pairs | Null mean | R | 95 % range | R unfiltered |
|---|---:|---:|---:|---:|---|---:|
| *Gemma3 instruct* | | | | | | |
| Gemma3-1B | 4448 | 34 | 0.80 | 42.5 | [29.4, 59.4] | 42.5 |
| Gemma3-4B | 5842 | 47 | 1.68 | 28.0 | [20.6, 37.2] | 28.0 |
| Gemma3-12B | 7052 | 78 | 3.04 | 25.7 | [20.3, 32.0] | 25.7 |
| Gemma3-27B | 7896 | 71 | 2.79 | 25.4 | [19.9, 32.1] | 22.3 |
| *Qwen2.5 instruct* | | | | | | |
| Qwen2.5-0.5B | 6999 | 52 | 2.70 | 19.3 | [14.4, 25.3] | 17.5 |
| Qwen2.5-1.5B | 5074 | 46 | 2.68 | 17.2 | [12.6, 22.9] | 17.9 |
| Qwen2.5-3B | 4880 | 61 | 3.93 | 15.5 | [11.9, 19.9] | 15.4 |
| Qwen2.5-7B | 5054 | 80 | 3.88 | 20.6 | [16.3, 25.7] | 20.4 |
| Qwen2.5-14B | 5343 | 47 | 3.02 | 15.6 | [11.4, 20.7] | 14.4 |
| Qwen2.5-32B | 5104 | 36 | 1.10 | 32.7 | [22.9, 45.3] | 32.7 |
| Qwen2.5-72B | 5085 | 82 | 6.65 | 12.3 | [9.8, 15.3] | 12.3 |
| *Qwen3 instruct* | | | | | | |
| Qwen3-0.6B | 4939 | 17 | 1.94 | 8.8 | [5.1, 14.0] | 9.4 |
| Qwen3-1.7B | 7087 | 53 | 3.04 | 17.4 | [13.1, 22.8] | 18.3 |
| Qwen3-4B | 5113 | 43 | 3.42 | 12.6 | [9.1, 16.9] | 12.6 |
| Qwen3-4B-Instruct-2507 | 5904 | 33 | 1.80 | 18.3 | [12.6, 25.7] | 17.0 |
| Qwen3-8B | 6220 | 51 | 1.74 | 29.3 | [21.8, 38.5] | 23.7 |
| Qwen3-14B | 5869 | 50 | 2.58 | 19.4 | [14.4, 25.5] | 18.5 |
| *Gemma3 pretrained (zero-shot)* | | | | | | |
| Gemma3-270M-pt | 2358 | 4 | 1.32 | 3.0 | [0.8, 7.8] | 2.1 |
| Gemma3-1B-pt | 3249 | 3 | 0.45 | 6.0 | [1.2, 17.5] | 3.1 |
| Gemma3-4B-pt | 2904 | 11 | 1.31 | 8.4 | [4.2, 15.0] | 6.5 |
| Gemma3-12B-pt | 3268 | 7 | 3.33 | 2.1 | [0.8, 4.3] | 5.2 |
| Gemma3-27B-pt | 2812 | 14 | 2.85 | 4.9 | [2.7, 8.2] | 9.0 |
| *Human baseline* | | | | | | |
| wordnet | 4599 | 27 | 1.72 | 15.7 | [10.3, 22.8] | 15.7 |

**Numbers quoted in the text** (default filter unless stated)

- unfiltered: instruct R 9.4-42.5 (median 18.3); pretrained 2.1-9.0 (median 5.2); WordNet 15.7; instruct models above WordNet: 12 of 17
- default: instruct R 8.8-42.5 (median 19.3); pretrained 2.1-8.4 (median 4.9); WordNet 15.7; instruct models above WordNet: 12 of 17
- strict: instruct R 8.9-34.9 (median 19.3); pretrained 1.8-6.0 (median 5.6); WordNet 15.7; instruct models above WordNet: 12 of 17
- default: lowest instruct Qwen3-0.6B 8.8 [5.1, 14.0]; highest pretrained Gemma3-4B-pt 8.4 [4.2, 15.0]
- default: instruct models whose 95 % range lies entirely above WordNet's R (15.7): 7 (Gemma3-12B, Gemma3-1B, Gemma3-27B, Gemma3-4B, Qwen2.5-32B, Qwen2.5-7B, Qwen3-8B); entirely below: 2 (Qwen2.5-72B, Qwen3-0.6B); the other 8 ranges contain it
- mutual pairs of the filtered pretrained graphs: [3, 4, 7, 11, 14]; edges [2358, 2812, 2904, 3249, 3268]
- mutual pairs of the instruct graphs: 17-82; WordNet 27
- E3 few-shot R by size (270M, 1B, 4B, 12B, 27B): 4.6, 22.3, 23.5, 30.9, 28.5
- E3 conservative / exact ranges include 1 at 4B, 12B, 27B: 1B: exact no, conservative yes, 4B: exact yes, conservative yes, 12B: exact yes, conservative yes, 27B: exact yes, conservative yes
