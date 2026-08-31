# Phase 0 Final Model Matrix — Together AI Serverless Replication

**Date**: 2026-07-16
**Basis**: live probes `phase0_probe_results.json` + `phase0b_results.json` (both in this folder).
**Goal**: test whether kernel-contraction / mset-k findings hold beyond Gemma-4 and Qwen3.5.

---

## Tier 1 — Core replication set (known params → usable in scaling regression)

All run under the **exact paper protocol** (T=0.7, top_p=0.8, top_k=20, max_tokens=80, thinking off).

| Model string | Family | Params | Arch | Required API switch |
|---|---|---|---|---|
| `openai/gpt-oss-20b` | gpt-oss | 20B (3.6B act) | MoE | `reasoning_effort: "low"` |
| `openai/gpt-oss-120b` | gpt-oss | 120B (5.1B act) | MoE | `reasoning_effort: "low"` (80tok variant untested — 503s; retry) |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` | Llama | 70B | dense | none |
| `Qwen/Qwen2.5-7B-Instruct-Turbo` | Qwen2.5 | 7B | dense | none |
| `deepcogito/cogito-v2-1-671b` | Cogito | 671B (37B act) | MoE (DeepSeek-V3 base) | none |
| `google/gemma-3n-E4B-it` | Gemma-3n | ~4B eff (8B raw) | dense/matformer | none |

**Cross-stack validation pair** (same models as local MLX runs, different inference stack):

| Model string | Local counterpart | Switch |
|---|---|---|
| `Qwen/Qwen3.5-9B` | Qwen3.5-9B-bf16 (MLX) | `chat_template_kwargs: {enable_thinking: false}` |
| `google/gemma-4-31B-it` | gemma-4-31b-8bit (MLX) | `chat_template_kwargs: {enable_thinking: false}` |

→ Pooled cross-family n grows from 7 to **15**.

## Tier 2 — Instruction-regime (sr_rate) analysis only (params undisclosed)

Protocol-preserved, but cannot be placed on the log2(params) axis.

| Model string | Family | Switch |
|---|---|---|
| `moonshotai/Kimi-K2.6` | Kimi | `chat_template_kwargs: {thinking: false}` |
| `deepseek-ai/DeepSeek-V4-Pro` | DeepSeek | `chat_template_kwargs: {thinking: false}` |
| `Qwen/Qwen3.6-Plus` | Qwen3.6 | `enable_thinking: false` + **requires `stream: true`** |

## Tier 3 — Protocol deviation (optional, document if used)

| Model string | Issue |
|---|---|
| `MiniMaxAI/MiniMax-M2.7` | Thinking **cannot** be disabled (`enable_thinking:false` ignored; ~350–500 reasoning tokens before content). Needs max_tokens≈1024 and post-reasoning extraction → different generation conditions from all other models. |

## Excluded (confirmed dedicated-endpoint-only, despite docs claiming serverless)

`Qwen3.5-397B-A17B`, `GLM-5`, `GLM-5.1`, `DeepSeek-V3.1`, `DeepSeek-R1`, `Kimi-K2.5`,
`Meta-Llama-3-8B-Instruct-Lite`, `Qwen3-235B-A22B-*`, `LFM2-24B-A2B`, `rnj-1-instruct`.

---

## What this set can and cannot replicate

**Can**: (1) pooled cross-family scaling correlation with n=15; (2) direction check
within gpt-oss (20B→120B: does kern% fall, mset/k rise?); (3) family-level sr_rate
regime test across 8+ families — the core "not exclusive to Gemma/Qwen" question;
(4) MLX-vs-API stack robustness on two anchor models.

**Cannot**: a clean within-family correlation like Qwen3.5's r=−0.862 in a *new*
family — no new family has ≥3 serverless sizes. gpt-oss gives only a 2-point line.
If a within-family slope in a third family is required, options: (a) dedicated
endpoint for Llama 8B (+70B = 2 points, hourly billing), (b) local runs of small
open families (Llama-3.2 1B/3B, Phi-4 etc.) on the lab machine.

**Caveats to record in the paper**: gpt-oss retains a short reasoning trace even at
`reasoning_effort: low` (~120 chars; content still fits in 80 tokens); MoE
total-vs-active params (use total, note active); Turbo/FP8/FP4 serving quantization
differs per model (paper's own quantization-robustness result mitigates this);
API sampling stacks may differ from MLX even at identical parameters.

## Cost estimate (full 3,000-word run, 1 seed)

~0.2M input + ~0.1M output tokens per model. Most models: $0.02–0.15.
Priciest: DeepSeek-V4-Pro ≈ $0.90, cogito-671b ≈ $0.40, MiniMax (with reasoning) ≈ $2.
**All 12 models ≈ $4–5 per seed; 3 seeds ≈ $15.**
