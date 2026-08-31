# Together AI — Serverless Model Availability (verified)

**Verified**: 2026-07-16 to 2026-07-20, via live API calls with the provided key.
**Method**: Phase 0 probe (one test prompt per model) → Phase 0b (retries resolving
transient 503s + streaming/thinking switches) → 11 models then completed full
3,000-word runs. Evidence files: `phase0_probe_results.json`, `phase0b_results.json`,
`replication/defs/*.jsonl`.

> Note: model IDs newer than the assistant's knowledge cutoff (GLM-5.x, Qwen3.5–3.7,
> Kimi K2.x, MiniMax M2.7, DeepSeek-V4-Pro, cogito v2.1, etc.) returned distinct live
> API responses but cannot be independently confirmed as the real production catalog.

---

## ✅ Serverless-usable — Chat models (12)

| Model string | Params | Required switch to disable "thinking" | Status |
|---|---|---|---|
| `openai/gpt-oss-20b` | 20B (MoE, 3.6B act) | `reasoning_effort: "low"` | full run ✓ |
| `openai/gpt-oss-120b` | 120B (MoE, 5.1B act) | `reasoning_effort: "low"` | 503s then ✓ full run |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` | 70B dense | none | 503 then ✓ full run |
| `Qwen/Qwen2.5-7B-Instruct-Turbo` | 7B dense | none | ✓ full run |
| `Qwen/Qwen3.5-9B` | 9B | `chat_template_kwargs:{enable_thinking:false}` | ✓ full run |
| `Qwen/Qwen3.6-Plus` | undisclosed | `enable_thinking:false` + **`stream:true` REQUIRED** | ✓ full run |
| `google/gemma-4-31B-it` | 31B | `chat_template_kwargs:{enable_thinking:false}` | ✓ full run |
| `google/gemma-3n-E4B-it` | ~4B eff | none | ✓ full run |
| `deepseek-ai/DeepSeek-V4-Pro` | undisclosed | `chat_template_kwargs:{thinking:false}` | ✓ full run |
| `moonshotai/Kimi-K2.6` | undisclosed | `chat_template_kwargs:{thinking:false}` | ✓ full run |
| `deepcogito/cogito-v2-1-671b` | 671B (MoE, 37B act) | none | ✓ full run |
| `MiniMaxAI/MiniMax-M2.7` | undisclosed | **cannot be disabled** → needs max_tokens≈1024 | usable (protocol deviation) |

## ✅ Serverless — non-chat (from docs; not re-probed this session)

| Model string | Type |
|---|---|
| `intfloat/multilingual-e5-large-instruct` | embedding |
| `meta-llama/Llama-Guard-4-12B` | moderation |

## ⛔ Exists but DEDICATED-ENDPOINT-ONLY (400 error on serverless)

Listed as "serverless" in the shared lists / docs, but the live API returns
*"Unable to access non-serverless model … create a dedicated endpoint"*:

- `Qwen/Qwen3.5-397B-A17B`
- `Qwen/Qwen3-235B-A22B-Instruct-2507-tput`
- `Qwen/Qwen3-235B-A22B-Instruct-2507-FP8`
- `zai-org/GLM-5`
- `zai-org/GLM-5.1`
- `deepseek-ai/DeepSeek-V3.1`
- `deepseek-ai/DeepSeek-R1`  (R1-0528)
- `moonshotai/Kimi-K2.5`
- `meta-llama/Meta-Llama-3-8B-Instruct-Lite`
- `LiquidAI/LFM2-24B-A2B`
- `essentialai/rnj-1-instruct`

## Corrections to the shared lists

- Pricing errors in list 1 (per live API response): `Llama-3.3-70B` is 1.04/1.04 not
  0.88/0.88; `Qwen3.5-9B` is 0.17/0.25 not 0.10/0.15; `gemma-4-31B` is 0.39/0.97 not
  0.20/0.50.
- `Kimi-K2.5` and the `-tput` variant of Qwen3-235B were flagged as nonexistent/misID
  earlier; live probe confirms they resolve but only as **dedicated-only**, not serverless.
