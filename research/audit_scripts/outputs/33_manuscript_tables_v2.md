**Table 1.** z-scores of the kernel ratio and the circulation rate against the degree-preserving null, by group (median, with the number of graphs below 0 / beyond -2 / beyond +2). Three-edge null: the null of our first analysis, 100 replicates, three filter variants; double-edge null: 20 replicates, default filter (D033).

| Measure | Group | n | Three-edge null: unfiltered | Three-edge null: default filter | Three-edge null: strict filter | Double-edge null: default filter |
|---|---|---:|---|---|---|---|
| Kernel ratio | 17 instruct models | 17 | +0.16 (7 / 2 / 1) | +0.31 (7 / 2 / 1) | +0.10 (7 / 3 / 1) | +0.19 (8 / 3 / 0) |
| Kernel ratio | 5 pretrained models | 5 | -1.67 (5 / 2 / 0) | +1.68 (0 / 0 / 2) | +1.37 (0 / 0 / 2) | +1.70 (0 / 0 / 2) |
| Kernel ratio | WordNet | 1 | -0.08 (1 / 0 / 0) | -0.08 (1 / 0 / 0) | -0.08 (1 / 0 / 0) | -0.26 (1 / 0 / 0) |
| Circulation rate | 17 instruct models | 17 | -1.34 (15 / 6 / 0) | -1.51 (15 / 6 / 0) | -1.37 (15 / 6 / 0) | -1.31 (12 / 6 / 0) |
| Circulation rate | 5 pretrained models | 5 | -1.81 (5 / 2 / 0) | +1.90 (0 / 0 / 2) | +2.20 (0 / 0 / 3) | +4.00 (0 / 0 / 3) |
| Circulation rate | WordNet | 1 | -1.89 (1 / 0 / 0) | -1.89 (1 / 0 / 0) | -1.89 (1 / 0 / 0) | -1.51 (1 / 0 / 0) |

**Table 3.** Cycle lengths in the default-filter graphs: observed number of cycles / mean number in the null, summed over the graphs of a group, against the three-edge null (100 replicates) and the double-edge null (20 replicates, D033).

| Group | Null | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---:|---:|---:|---:|---:|---:|
| 17 instruct models | three-edge | 881 / 47 = 18.83x | 93 / 41 = 2.24x | 56 / 58 = 0.97x | 58 / 98 = 0.59x | 86 / 167 = 0.52x | 138 / 302 = 0.46x |
| 17 instruct models | double-edge | 881 / 30 = 29.56x | 93 / 39 = 2.37x | 56 / 59 = 0.94x | 58 / 99 = 0.59x | 86 / 165 = 0.52x | 138 / 295 = 0.47x |
| 5 pretrained models | three-edge | 39 / 9 = 4.21x | 2 / 3 = 0.76x | 0 / 1 = 0.00x | 0 / 1 = 0.00x | 0 / 0 = 0.00x | 0 / 0 = 0.00x |
| 5 pretrained models | double-edge | 39 / 2 = 18.57x | 2 / 1 = 1.74x | 0 / 1 = 0.00x | 0 / 1 = 0.00x | 0 / 0 = 0.00x | 0 / 0 = 0.00x |
| WordNet | three-edge | 27 / 2 = 15.70x | 2 / 2 = 1.00x | 4 / 3 = 1.57x | 3 / 3 = 0.88x | 3 / 4 = 0.69x | 2 / 6 = 0.34x |
| WordNet | double-edge | 27 / 2 = 16.88x | 2 / 2 = 1.14x | 4 / 2 = 2.29x | 3 / 3 = 1.00x | 3 / 4 = 0.68x | 2 / 5 = 0.38x |

**Table 2.** Mutual pairs and R by group (default filter, first sentence, 2,750-lemma node set): the range over the graphs of a group, with the median in brackets. R = observed pairs / null mean (floor 0.5). Three-edge null: 100 replicates of 32 x |E| swaps; double-edge null: 100 replicates of 64 x |E| swaps (D032). The last column is the ratio of the double-edge R to the three-edge R of the same graph.

| Group | n | Mutual pairs | Three-edge null: null mean | Three-edge null: R | Double-edge null: null mean | Double-edge null: R | R double / R three-edge: median (range) |
|---|---:|---|---|---|---|---|---|
| 17 instruct models | 17 | 17 to 82 | 0.80 to 6.65 (2.70) | 8.8 to 42.5 (19.3) | 0.88 to 2.92 (1.59) | 18.1 to 52.1 (29.2) | 1.09 (0.89 to 4.18) |
| 5 pretrained models, zero-shot | 5 | 3 to 14 | 0.45 to 3.33 (1.32) | 2.1 to 8.4 (4.9) | 0.38 to 0.44 (0.42) | 6.0 to 28.0 (14.0) | 2.64 (1.00 to 6.66) |
| 5 pretrained models, few-shot | 5 | 11 to 114 | 1.30 to 3.92 (2.74) | 4.6 to 30.9 (23.5) | 0.77 to 2.54 (1.87) | 14.3 to 49.2 (30.7) | 1.54 (0.82 to 3.08) |
| WordNet | 1 | 27 | 1.72 | 15.7 | 1.49 | 18.1 | 1.15 |

**Table 4.** Mutual pairs by WordNet relation (all senses, no part of speech; the first match in the order of the columns decides). Counts, with shares of the pair occurrences in brackets.

| Source | Pair occurrences | Synonym | Hypernym | Sister term | Antonym | Derived form | No direct link |
|---|---:|---:|---:|---:|---:|---:|---:|
| WordNet | 27 | 2 (7 %) | 9 (33 %) | 1 (4 %) | 0 (0 %) | 3 (11 %) | 12 (44 %) |
| 17 instruct models | 881 | 339 (38 %) | 192 (22 %) | 77 (9 %) | 14 (2 %) | 7 (1 %) | 252 (29 %) |
| Few-shot pretrained | 324 | 106 (33 %) | 69 (21 %) | 35 (11 %) | 3 (1 %) | 5 (2 %) | 106 (33 %) |
| Zero-shot pretrained | 39 | 9 (23 %) | 11 (28 %) | 0 (0 %) | 0 (0 %) | 1 (3 %) | 18 (46 %) |

**Table 5.** The two nulls on eight graphs (default filter): mutual pairs in a replicate and how many of them are pairs of the observed graph. Three-edge null: the first 20 stored replicates (32 x |E| swaps, stored seeds); double-edge null: 100 replicates (64 x |E| swaps, D032). Independent-edge estimate: the expected number of mutual pairs if every edge u -> v were present with probability min(1, d_out(u) d_in(v) / |E|) independently.

| Graph | Observed pairs | Independent-edge estimate | Three-edge null: pairs | of them observed pairs | Double-edge null: pairs | of them observed pairs |
|---|---:|---:|---:|---:|---:|---:|
| Gemma 3 4B pretrained, few-shot | 92 | 2.01 | 4.05 | 1.60 | 1.87 | 0.00 |
| Gemma 3 1B instruct | 34 | 0.98 | 0.70 | 0.00 | 0.88 | 0.00 |
| Gemma 3 12B instruct | 78 | 2.54 | 3.10 | 0.15 | 2.78 | 0.01 |
| WordNet | 27 | 1.44 | 2.00 | 0.10 | 1.49 | 0.00 |
| Gemma 3 12B pretrained, zero-shot | 7 | 0.36 | 3.10 | 1.00 | 0.44 | 0.00 |
| 4B few-shot, entries of the zero-shot survivors | 18 | 0.31 | 2.95 | 2.20 | 0.27 | 0.00 |
| 4B few-shot, closed on a random half of the words | 14 | 0.33 | 12.40 | 10.40 | 0.33 | 0.00 |
| 1B instruct, closed on the survivors' words | 12 | 0.40 | 2.85 | 1.05 | 0.44 | 0.00 |

**Table 6.** Does R depend on coverage? rho = R' of the few-shot graph limited to a random half of the entries (D029) or induced on a random half of the words (closed, D030) divided by R' of the whole few-shot graph (R' = observed pairs / null mean, no floor); median of five halves, with the smallest and the largest in brackets. A value near 1 means that the half has the same R' as the whole graph.

| Size | Whole few-shot graph: R' three-edge | R' double-edge | Entry-level halves: rho three-edge | rho double-edge | Closed halves: rho three-edge | rho double-edge |
|---|---:|---:|---|---|---|---|
| 1B | 22.3 | 18.2 | 0.30 (0.21 to 0.51) | 1.22 (0.73 to 1.41) | 0.20 (0.12 to 0.59) | 1.04 (0.95 to 1.61) |
| 4B | 23.5 | 49.2 | 0.16 (0.11 to 0.37) | 0.82 (0.65 to 1.52) | 0.14 (0.05 to 0.20) | 0.88 (0.65 to 1.09) |
| 12B | 30.9 | 47.7 | 0.15 (0.12 to 0.20) | 0.89 (0.87 to 1.20) | 0.28 (0.13 to 0.59) | 0.84 (0.73 to 1.37) |
| 27B | 28.5 | 30.7 | 0.24 (0.07 to 0.35) | 1.21 (0.74 to 1.41) | 0.18 (0.10 to 0.77) | 1.40 (0.64 to 1.73) |

**Table 7.** The prompt controls: R of the control divided by R of the same instruct model in the main run (default filter), for the models where both graphs hold a mutual pair. Size of the change = the larger of the ratio and its inverse. Length cap: answers of 8 words or fewer; no chat template: the original prompt without the chat template.

| Control | Null | Models | Median ratio (range) | Median size of the change (largest) | Within a factor 2 | Control R higher |
|---|---|---:|---|---|---:|---:|
| Length cap | three-edge | 17 | 1.11 (0.46 to 2.98) | 1.28 (2.98) | 14 of 17 | 9 of 17 |
| Length cap | double-edge | 17 | 1.62 (0.74 to 2.44) | 1.62 (2.44) | 13 of 17 | 16 of 17 |
| No chat template | three-edge | 15 | 0.76 (0.10 to 2.52) | 1.94 (9.69) | 8 of 15 | 6 of 15 |
| No chat template | double-edge | 15 | 0.84 (0.06 to 1.39) | 1.21 (16.78) | 13 of 15 | 4 of 15 |

**Table 8.** Does R approach WordNet's with model size? Spearman rank correlation with the parameter count within each family, 17 instruct models (default filter; Qwen3-4B-Instruct-2507 left out of the trends). Labels fixed in advance (D031): the distance |ln R - ln R_WordNet| is *toward* if the correlation is -0.6 or lower, *away* if it is +0.6 or higher; the Jaccard index of the model's mutual pairs with WordNet's 27 pairs is *toward* if it is +0.6 or higher, *away* if -0.6 or lower. The overlap does not depend on the null. The last two columns are descriptive.

| Family | n | Distance in R, three-edge null | Label | Distance in R, double-edge null | Label | Overlap with WordNet's pairs | Label | Observed pairs | Null mean, double-edge |
|---|---:|---:|---|---:|---|---:|---|---:|---:|
| Gemma3 | 4 | -1.00 | toward | -1.00 | toward | -0.40 | none | +0.80 | +1.00 |
| Qwen2.5 | 7 | +0.36 | none | +0.43 | none | -0.75 | away | +0.18 | -0.29 |
| Qwen3 | 5 | +0.00 | none | +0.80 | away | +0.30 | none | +0.30 | +0.10 |

Reading fixed in advance: no consistent approach under both nulls.

**Table 9.** Matched Gemma3 pairs under a zero-shot prompt, as built (the pretrained graphs cover about half of the entries; Section 4.6.2): R against the double-edge null with the observed mutual pairs and the null mean in brackets, and instruct R / pretrained R with the exact conditional 95 % range of the ratio. The last column is the ratio against the three-edge null (our first analysis). The strict filter and the other variants were not re-run with the double-edge null (Table A2).

| Size | Instruct R (pairs / null mean) | Pretrained R (pairs / null mean) | Instruct / pretrained | Same ratio, three-edge null |
|---|---:|---:|---|---|
| 1B | 38.6 (34 / 0.88) | 6.0 (3 / 0.44) | 6.4 [2.0, 32.8] | 7.1 [2.2, 36.0] |
| 4B | 29.2 (47 / 1.61) | 22.0 (11 / 0.38) | 1.3 [0.7, 2.8] | 3.3 [1.7, 7.1] |
| 12B | 28.1 (78 / 2.78) | 14.0 (7 / 0.44) | 2.0 [0.9, 5.1] | 12.2 [5.7, 31.4] |
| 27B | 24.7 (71 / 2.87) | 28.0 (14 / 0.42) | 0.9 [0.5, 1.7] | 5.2 [2.9, 10.0] |

**Table 10.** The same entries (D029 graphs, double-edge null): R of the zero-shot pretrained graph and of the few-shot and instruct graphs limited to the entries whose zero-shot record survived the filter, with the exact Poisson 95 % range, the observed mutual pairs and the null mean in brackets, and the exact conditional range of instruct / zero-shot. The last two columns give the range over five random sets of entries of the same size for the few-shot graph.

| Size | Entries kept (of 3,000) | Zero-shot pretrained | Few-shot, same entries | Instruct, same entries | Instruct / zero-shot (exact range) | Five random halves: R | Five random halves: null mean |
|---|---:|---|---|---|---|---|---|
| 1B | 1,580 | 6.0 [1.2, 17.5] (3 / 0.44) | 12.0 [4.4, 26.1] (6 / 0.34) | 18.0 [8.2, 34.2] (9 / 0.27) | 3.00 [0.75, 17.23] | 8.0 to 18.0 | 0.30 to 0.70 |
| 4B | 1,322 | 22.0 [11.0, 39.4] (11 / 0.38) | 36.0 [21.3, 56.9] (18 / 0.27) | 24.0 [12.4, 41.9] (12 / 0.42) | 1.09 [0.44, 2.73] | 24.0 to 44.2 | 0.24 to 0.52 |
| 12B | 1,503 | 14.0 [5.6, 28.8] (7 / 0.44) | 42.0 [26.0, 64.2] (21 / 0.46) | 34.0 [19.8, 54.4] (17 / 0.47) | 2.43 [0.96, 6.93] | 41.5 to 57.1 | 0.50 to 0.70 |
| 27B | 1,296 | 28.0 [15.3, 47.0] (14 / 0.42) | 42.0 [26.0, 64.2] (21 / 0.43) | 28.3 [15.8, 46.7] (15 / 0.53) | 1.01 [0.45, 2.26] | 22.6 to 32.0 | 0.28 to 0.53 |

The exact range of instruct / zero-shot includes 1 at 4 of 4 sizes.

**Table 11.** Mutual pairs of the instruct graph that the other graphs contain, at equal coverage (D029; the pairs do not depend on the null). At risk: mutual pairs of the instruct graph (whole word list) whose two words both have a surviving zero-shot entry. Zero-shot: the zero-shot graph; few-shot: the few-shot graph limited to the same entries. Exact McNemar test on the pairs found in one graph and not in the other.

| Size | Instruct pairs | At risk | Zero-shot | Few-shot, same entries | Only few-shot | Only zero-shot | Exact McNemar p |
|---|---:|---:|---|---|---:|---:|---:|
| 1B | 34 | 12 | 0 (0 %) | 0 (0 %) | 0 | 0 | 1.000 |
| 4B | 47 | 12 | 1 (8 %) | 6 (50 %) | 5 | 0 | 0.062 |
| 12B | 78 | 19 | 2 (10 %) | 8 (42 %) | 7 | 1 | 0.070 |
| 27B | 71 | 19 | 2 (10 %) | 6 (32 %) | 4 | 0 | 0.125 |
| Pooled (descriptive: pairs recur across sizes) | -- | 62 | 5 (8 %; 95 % range 3-18 %) | 20 (32 %; 21-45 %) | 16 | 1 | 0.0003 |
| Each different pair once (52 pairs) | -- | 52 | 4 | 17 | 14 | 1 | 0.001 |

**Table 12.** The few-shot prompt (three worked examples): R of the pretrained Gemma3 models given three example definitions, against the zero-shot pretrained model and the instruct model of the same size (default filter, double-edge null), with the observed mutual pairs and the null mean in brackets. The ratio is instruct R / few-shot R; the exact range is the conditional range, the conservative range combines the two ends of the Poisson ranges. The last column is the few-shot R against the three-edge null.

| Size | Zero-shot pretrained R | Few-shot pretrained R (95 % range) | Instruct R | Instruct / few-shot | Exact range | Conservative range | Few-shot R, three-edge null |
|---|---:|---|---:|---:|---|---|---:|
| 270M | 8.0 (4 / 0.40) | 14.3 [7.1, 25.6] (11 / 0.77) | no cycles (D011) | -- | -- | -- | 4.6 |
| 1B | 6.0 (3 / 0.44) | 18.2 [12.2, 26.2] (29 / 1.59) | 38.6 (34 / 0.88) | 2.12 | [1.25, 3.60] | [1.02, 4.42] | 22.3 |
| 4B | 22.0 (11 / 0.38) | 49.2 [39.7, 60.3] (92 / 1.87) | 29.2 (47 / 1.61) | 0.59 | [0.41, 0.85] | [0.36, 0.98] | 23.5 |
| 12B | 14.0 (7 / 0.44) | 47.7 [39.3, 57.3] (114 / 2.39) | 28.1 (78 / 2.78) | 0.59 | [0.44, 0.79] | [0.39, 0.89] | 30.9 |
| 27B | 28.0 (14 / 0.42) | 30.7 [24.3, 38.3] (78 / 2.54) | 24.7 (71 / 2.87) | 0.81 | [0.58, 1.13] | [0.50, 1.29] | 28.5 |

- Few-shot ranges of instruct / few-shot include 1: 1B: exact no, conservative no; 4B: exact no, conservative no; 12B: exact no, conservative no; 27B: exact yes, conservative yes

**Table A1.** Definition graphs of the 23 analysed sources (default filter, first sentence; 2,750-lemma node set). Null mean and R against the three-edge null (100 replicates, 32 x |E| swaps) and against the double-edge null (100 replicates, 64 x |E| swaps); R = observed mutual pairs / null mean (floor 0.5); the 95 % range is the exact Poisson range of the observed number of mutual pairs divided by the null mean of the double-edge null; the last column is R of the unfiltered graphs (stored text; three-edge null only). The zero-shot pretrained graphs cover about half of the entries (Section 4.6.2).

| Source | Edges | Mutual pairs | Three-edge null: mean | R | Double-edge null: mean | R | 95 % range of R | R unfiltered (three-edge) |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| *Gemma3 instruct* | | | | | | | | |
| Gemma3-1B | 4448 | 34 | 0.80 | 42.5 | 0.88 | 38.6 | [26.8, 54.0] | 42.5 |
| Gemma3-4B | 5842 | 47 | 1.68 | 28.0 | 1.61 | 29.2 | [21.4, 38.8] | 28.0 |
| Gemma3-12B | 7052 | 78 | 3.04 | 25.7 | 2.78 | 28.1 | [22.2, 35.0] | 25.7 |
| Gemma3-27B | 7896 | 71 | 2.79 | 25.4 | 2.87 | 24.7 | [19.3, 31.2] | 22.3 |
| *Qwen2.5 instruct* | | | | | | | | |
| Qwen2.5-0.5B | 6999 | 52 | 2.70 | 19.3 | 2.67 | 19.5 | [14.5, 25.5] | 17.5 |
| Qwen2.5-1.5B | 5074 | 46 | 2.68 | 17.2 | 1.49 | 30.9 | [22.6, 41.2] | 17.9 |
| Qwen2.5-3B | 4880 | 61 | 3.93 | 15.5 | 1.17 | 52.1 | [39.9, 67.0] | 15.4 |
| Qwen2.5-7B | 5054 | 80 | 3.88 | 20.6 | 1.66 | 48.2 | [38.2, 60.0] | 20.4 |
| Qwen2.5-14B | 5343 | 47 | 3.02 | 15.6 | 1.54 | 30.5 | [22.4, 40.6] | 14.4 |
| Qwen2.5-32B | 5104 | 36 | 1.10 | 32.7 | 1.08 | 33.3 | [23.3, 46.1] | 32.7 |
| Qwen2.5-72B | 5085 | 82 | 6.65 | 12.3 | 1.59 | 51.6 | [41.0, 64.0] | 12.3 |
| *Qwen3 instruct* | | | | | | | | |
| Qwen3-0.6B | 4939 | 17 | 1.94 | 8.8 | 0.94 | 18.1 | [10.5, 29.0] | 9.4 |
| Qwen3-1.7B | 7087 | 53 | 3.04 | 17.4 | 2.92 | 18.2 | [13.6, 23.7] | 18.3 |
| Qwen3-4B | 5113 | 43 | 3.42 | 12.6 | 1.53 | 28.1 | [20.3, 37.9] | 12.6 |
| Qwen3-4B-Instruct-2507 | 5904 | 33 | 1.80 | 18.3 | 1.75 | 18.9 | [13.0, 26.5] | 17.0 |
| Qwen3-8B | 6220 | 51 | 1.74 | 29.3 | 1.95 | 26.2 | [19.5, 34.4] | 23.7 |
| Qwen3-14B | 5869 | 50 | 2.58 | 19.4 | 1.49 | 33.6 | [24.9, 44.2] | 18.5 |
| *Gemma3 pretrained (zero-shot)* | | | | | | | | |
| Gemma3-270M-pt | 2358 | 4 | 1.32 | 3.0 | 0.40 | 8.0 | [2.2, 20.5] | 2.1 |
| Gemma3-1B-pt | 3249 | 3 | 0.45 | 6.0 | 0.44 | 6.0 | [1.2, 17.5] | 3.1 |
| Gemma3-4B-pt | 2904 | 11 | 1.31 | 8.4 | 0.38 | 22.0 | [11.0, 39.4] | 6.5 |
| Gemma3-12B-pt | 3268 | 7 | 3.33 | 2.1 | 0.44 | 14.0 | [5.6, 28.8] | 5.2 |
| Gemma3-27B-pt | 2812 | 14 | 2.85 | 4.9 | 0.42 | 28.0 | [15.3, 47.0] | 9.0 |
| *Gemma3 pretrained (few-shot)* | | | | | | | | |
| Gemma3-270M-pt | 4475 | 11 | 2.37 | 4.6 | 0.77 | 14.3 | [7.1, 25.6] | 4.7 |
| Gemma3-1B-pt | 5465 | 29 | 1.30 | 22.3 | 1.59 | 18.2 | [12.2, 26.2] | 22.3 |
| Gemma3-4B-pt | 5868 | 92 | 3.92 | 23.5 | 1.87 | 49.2 | [39.7, 60.3] | 23.5 |
| Gemma3-12B-pt | 6201 | 114 | 3.69 | 30.9 | 2.39 | 47.7 | [39.3, 57.3] | 30.9 |
| Gemma3-27B-pt | 6076 | 78 | 2.74 | 28.5 | 2.54 | 30.7 | [24.3, 38.3] | 28.0 |
| *Reference* | | | | | | | | |
| wordnet | 4599 | 27 | 1.72 | 15.7 | 1.49 | 18.1 | [11.9, 26.4] | 15.7 |

**Table A2.** Matched Gemma3 pairs under a zero-shot prompt, against the three-edge null (our first analysis; these variants were not re-run with the double-edge null): R of the instruct model / R of the pretrained model, with the exact conditional 95 % range of the ratio, under five variants of the analysis.

| Size | Instruct R | Pretrained R | Default filter | Unfiltered | Strict filter | Whole stored text | Six frame words removed |
|---|---:|---:|---|---|---|---|---|
| 1B | 42.5 | 6.0 | 7.1 [2.2, 36.0] | 13.9 [7.1, 28.6] | 5.8 [1.8, 29.9] | 7.1 [2.9, 20.6] | 7.1 [2.2, 35.9] |
| 4B | 28.0 | 8.4 | 3.3 [1.7, 7.1] | 4.3 [2.5, 7.8] | 4.8 [2.4, 10.7] | 2.2 [1.2, 4.5] | 9.7 [4.9, 20.7] |
| 12B | 25.7 | 2.1 | 12.2 [5.7, 31.4] | 4.9 [2.9, 9.1] | 11.7 [5.4, 29.9] | 10.0 [4.8, 23.9] | 12.9 [6.0, 33.1] |
| 27B | 25.4 | 4.9 | 5.2 [2.9, 10.0] | 2.5 [1.6, 4.1] | 3.8 [2.1, 7.3] | 3.4 [1.9, 6.4] | 6.7 [3.7, 12.9] |

Over the 20 pair-by-variant comparisons the range excludes 1 in 20 and excludes 2 in 15.

**Table A3.** Defining words of the same entries in the three conditions (D029 (c); entries kept in all three conditions; the defining words of an entry are the in-vocabulary lemmas of its first sentence, the headword excluded). Jaccard index of the defining-word sets with the instruct definition of the same entry (mean); share of records that contain one of six frame words (define, mean, refer, describe, phrase, use); share of all defining-word occurrences carried by the five most used words.

| Size | Mean Jaccard with instruct: zero-shot | few-shot | few-shot / zero-shot | Frame word: zero-shot | few-shot | instruct | Top-5 words: zero-shot | few-shot | instruct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1B | 0.114 | 0.167 | 1.46 | 43 % | 7 % | 6 % | 30 % | 15 % | 14 % |
| 4B | 0.134 | 0.199 | 1.48 | 35 % | 9 % | 13 % | 22 % | 12 % | 14 % |
| 12B | 0.152 | 0.250 | 1.65 | 32 % | 10 % | 27 % | 22 % | 12 % | 17 % |
| 27B | 0.173 | 0.247 | 1.43 | 30 % | 9 % | 20 % | 21 % | 12 % | 13 % |

**Table A4.** Closed sub-dictionaries (D030, double-edge null): the zero-shot graph, the whole few-shot graph and the whole instruct graph induced on the words that have a surviving zero-shot entry (the other words and their edges removed), and the whole few-shot graph induced on five random sets of words of the same size. R' = observed pairs / null mean without the floor; brackets: the exact Poisson 95 % range of R', then the observed pairs and the null mean. Instruct / zero-shot: exact conditional range without the floor. rho = R' of a random half / R' of the whole few-shot graph (median of five).

| Size | Words | Zero-shot | Few-shot | Instruct | Instruct / zero-shot | Few-shot / zero-shot | Whole few-shot R' | Random halves: R' | rho (median) |
|---|---:|---|---|---|---|---|---:|---|---:|
| 1B | 1,506 | 10.3 [2.1, 30.2] (3 / 0.29) | 15.7 [6.8, 30.9] (8 / 0.51) | 27.3 [14.1, 47.6] (12 / 0.44) | 2.64 [0.71, 14.56] | 1.52 [0.36, 8.87] | 18.2 | 17.3 to 29.4 | 1.04 |
| 4B | 1,265 | 28.2 [14.1, 50.5] (11 / 0.39) | 48.9 [30.6, 74.0] (22 / 0.45) | 34.3 [17.7, 59.9] (12 / 0.35) | 1.22 [0.49, 3.04] | 1.73 [0.81, 3.96] | 49.2 | 32.1 to 53.8 | 0.88 |
| 12B | 1,434 | 18.4 [7.4, 38.0] (7 / 0.38) | 50.0 [32.0, 74.4] (24 / 0.48) | 38.0 [22.9, 59.3] (19 / 0.50) | 2.06 [0.83, 5.81] | 2.71 [1.13, 7.46] | 47.7 | 34.7 to 65.3 | 0.84 |
| 27B | 1,251 | 42.4 [23.2, 71.2] (14 / 0.33) | 39.3 [24.6, 59.5] (22 / 0.56) | 17.0 [10.2, 26.5] (19 / 1.12) | 0.40 [0.19, 0.86] | 0.93 [0.45, 1.96] | 30.7 | 19.8 to 53.1 | 1.40 |

**Numbers quoted in the text**

- double-edge null: WordNet R 18.1 [11.9, 26.4], null mean 1.49; instruct models with the range entirely above 13, entirely below 0 (none), containing it 4; point estimates above WordNet's: 16 of 17
  lowest instruct Qwen3-0.6B 18.1 [10.5, 29.0]; highest zero-shot pretrained Gemma3-27B-pt 28.0 [15.3, 47.0]
  instruct: R 18.1-52.1 (median 29.2); zero-shot pretrained 6.0-28.0 (median 14.0); few-shot pretrained 14.3-49.2
- three-edge null: WordNet R 15.7 [10.3, 22.8], null mean 1.72; instruct models with the range entirely above 7, entirely below 2 (Qwen2.5-72B, Qwen3-0.6B), containing it 8; point estimates above WordNet's: 12 of 17
  lowest instruct Qwen3-0.6B 8.8 [5.1, 14.0]; highest zero-shot pretrained Gemma3-4B-pt 8.4 [4.2, 15.0]
  instruct: R 8.8-42.5 (median 19.3); zero-shot pretrained 2.1-8.4 (median 4.9); few-shot pretrained 4.6-30.9
- double-edge null: exact conditional range of instruct R / WordNet R excludes 1 above for 8 of 17 models, below for 0, includes 1 for 9; instruct ranges above the upper end of WordNet's range (26.4): 4
  rank correlation over the 17 instruct models: mutual pairs with R +0.30; null mean with R -0.49
- three-edge null: exact conditional range of instruct R / WordNet R excludes 1 above for 6 of 17 models, below for 0, includes 1 for 11; instruct ranges above the upper end of WordNet's range (22.8): 2
  rank correlation over the 17 instruct models: mutual pairs with R -0.01; null mean with R -0.62
- rank correlation of R (three-edge) and R (double-edge) over the 17 instruct models: +0.07; R double-edge / R three-edge below 1.11 for 9 models, at least 1.7 for 8
- zero-shot pretrained graphs, double-edge null: null means 0.40, 0.44, 0.38, 0.44, 0.42 (below the floor of 0.5 in 5 of 5); R' without the floor 10.0, 6.8, 28.9, 15.9, 33.3; observed pairs 4, 3, 11, 7, 14
- graphs under the double-edge null whose null mean is below the floor: main and few-shot graphs ['main__Gemma3-12B-pt', 'main__Gemma3-1B-pt', 'main__Gemma3-270M-pt', 'main__Gemma3-27B-pt', 'main__Gemma3-4B-pt']; restricted graphs of D029 and D030: 36 of 60
- Gemma 3 instruct kernel-ratio z, double-edge null: 1B +1.40, 4B -0.20, 12B -0.51, 27B -1.40; three-edge null: 1B +1.68, 4B +0.04, 12B -0.58, 27B -1.39
- observed mutual pairs: instruct 17-82, zero-shot pretrained [3, 4, 7, 11, 14], few-shot pretrained [11, 29, 78, 92, 114], WordNet 27
- observed pairs kept in a double-edge replicate (mean over replicates), largest over the 88 graphs: 0.03
- replicates short of the swap budget (double-edge null): 0
