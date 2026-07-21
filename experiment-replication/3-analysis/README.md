# Cross-Family Replication — Together AI Serverless

Replicates the dictionary-graph methodology (see `../current state of the
investigation.pdf`) on new model families to test whether kernel contraction and
cycle irreducibility are general, not Gemma/Qwen-specific.

## Setup (once)

```powershell
pip install requests networkx nltk pulp highspy numpy
$env:TOGETHER_API_KEY = "tgp_v1_..."
```

## Run

```powershell
cd replication

# Stage 0: word sampling (seed=42, WordNet + Brown freq>=5)
python sample_words.py

# Stage 1: definitions. Start with tier1 (8 models, ~$1, a few hours at 4 workers)
python generate_definitions.py --models tier1
python generate_definitions.py --models tier12      # add regime-analysis models
# Interrupted? Just rerun the same command - it resumes from the JSONL checkpoint.

# Stages 2-4 + WordNet baseline
python graph_metrics.py --wordnet

# Stage 6: tables, correlations, partial correlations, universal kernel
python analyse.py
```

Multi-seed (variance reporting, matches 04_future_plan):
```powershell
python generate_definitions.py --models tier1 --gen-seed 123
python generate_definitions.py --models tier1 --gen-seed 456
```

## Files

| File | Role |
|---|---|
| `models_config.py` | model matrix + thinking switches (from Phase 0b probes) + prior MLX results |
| `sample_words.py` | Stage 0 |
| `generate_definitions.py` | Stage 1 (checkpointed, concurrent) |
| `graph_metrics.py` | Stages 2–4 (kernel / core / exact MFVS via HiGHS ILP) + WordNet baseline |
| `analyse.py` | Stage 6 (pooled + within-family correlations, partial corr vs sr_rate, 2-point direction checks, universal kernel) |

## Protocol notes / deviations from the local MLX runs

1. **Word list**: regenerated deterministically (seed=42, sorted candidates) but not
   guaranteed byte-identical to the original list (nltk-version dependent). The
   original runs' word list should be diffed against `words.json` if available.
2. **Thinking switches**: gpt-oss uses `reasoning_effort:"low"` (a short reasoning
   trace remains; final content verified to fit in 80 tokens). Qwen3.5/3.6, gemma-4,
   Kimi, DeepSeek-V4 use verified `chat_template_kwargs` switches (zero reasoning).
3. **MiniMax-M2.7 (tier 3)**: thinking cannot be disabled; runs with max_tokens=1024
   and post-reasoning extraction. Exclude from protocol-strict comparisons.
4. **Serving quantization** differs per model (FP8/FP4/MXFP4 per Together docs).
   The paper's quantization-robustness result (kern% within ±1pp, 4–8 bit) supports
   comparability, but note it in any write-up.
5. **MFVS**: this implementation iterates lazy cycle constraints until the removal
   set is verified acyclic — a convergence guarantee the original lacked
   (addresses the "MinSet completeness uncertainty" open issue).
6. **kernel_ratio denominator**: |V| = full 3,000-word vocab (all nodes added to
   the graph). The original reports 2,750 nodes after cross-model failures; when
   comparing against prior numbers, optionally recompute on the shared-success
   vocab intersection.
