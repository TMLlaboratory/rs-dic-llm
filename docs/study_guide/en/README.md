# rs-dic-llm Study Guide (English)

**For**: Lopez Chapa Jose (undergraduate researcher)

---

## Research in One Sentence

> **"We make LLMs write word definitions, then analyse the network structure of those definitions to quantify how conceptual organisation changes with model scale."**

---

## Key Findings at a Glance

| Finding | Number |
|---|---|
| Kernel ratio decreases with model size | Qwen3.5: r = −0.862 |
| mset/k (irreducible cycle fraction) increases | Qwen3.5: r = +0.982 |
| Universal kernel words across all models | 92 words (10 overlap with NSM) |
| Instruction-following: Gemma-4 vs Qwen3.5 | 99.9% vs 76–92% |
| Quantization variation (4–8 bit) | within ±1 pp |

---

## Learning Roadmap

```
[Start here]
      ↓
01_background/01_graph_theory.md          (directed graphs, SCC)      60 min
      ↓
01_background/02_dictionary_structure.md  (dictionary graph intuition) 45 min
      ↓
01_background/03_llm_basics.md            (LLMs, scaling laws)         60 min
      ↓
02_key_papers/01_vincent_lamarre_2016.md  (original paper)             90 min
      ↓
02_key_papers/02_scaling_laws.md          (scaling law papers)          45 min
      ↓
03_this_research/01_motivation.md         (research motivation)         30 min
      ↓
03_this_research/02_pipeline.md           (experiment pipeline)         60 min
      ↓
03_this_research/03_metrics.md            (metrics in detail)           60 min
      ↓
03_this_research/04_results.md            (how to read results)         60 min
      ↓
03_this_research/05_confound_analysis.md  (confound analysis)           45 min
      ↓
04_future_plan/01_research_issues.md      (open problems)               30 min
      ↓
04_future_plan/02_experiment_plan.md      (next experiments)            30 min
```

Total: **~10 hours**

---

## Quick Reference Glossary

| Term | One-line definition | Details |
|---|---|---|
| Dictionary graph | Directed graph encoding definitional relationships | `01_background/02` |
| Kernel | Minimal self-sufficient vocabulary (after removing out-degree-0 nodes) | `03_this_research/03` |
| Core | Union of Source SCCs within the Kernel | `03_this_research/03` |
| MinSet / MFVS | Minimum set of words whose removal breaks all cycles | `03_this_research/03` |
| SCC | Strongly Connected Component — nodes mutually reachable | `01_background/01` |
| sr\_rate | Self-referential rate — fraction of definitions containing the defined word | `03_this_research/05` |
| mset/k | MinSet/Kernel ratio — cyclic density of the kernel | `03_this_research/03` |
| Instruction regime | Gemma-4 (low sr) vs Qwen3.5 (high sr) family-level difference | `03_this_research/05` |
| Partial correlation | Correlation between X and Y after removing Z's effect | `03_this_research/05` |

---

## Models Used

| Model | Family | Parameters |
|---|---|---|
| Qwen3.5-0.8B-MLX-bf16 | Qwen3.5 | 0.8B |
| Qwen3.5-2B-bf16 | Qwen3.5 | 2B |
| Qwen3.5-4B-MLX-bf16 | Qwen3.5 | 4B |
| Qwen3.5-9B-bf16 | Qwen3.5 | 9B |
| Qwen3.5-27B-bf16 | Qwen3.5 | 27B |
| gemma-4-e4b-bf16 | Gemma-4 | 4B |
| gemma-4-31b-8bit | Gemma-4 | 31B |

---

Next: `01_background/01_graph_theory.md`
