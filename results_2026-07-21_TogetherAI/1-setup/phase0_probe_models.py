"""
Phase 0: probe Together AI serverless catalog for the dictionary-graph replication.

Sends one cheap definition-style prompt (matching the paper's exact prompt template)
to every candidate model and records: works / dedicated-only / nonexistent,
plus response text, latency, and token usage.

Usage:
    export TOGETHER_API_KEY=tgp_v1_...          # or set in .env
    python phase0_probe_models.py

Output:
    phase0_probe_results.json   (raw per-model records)
    stdout                      (verdict table)

Requires: pip install requests
"""

import json
import os
import time

import requests

API_URL = "https://api.together.xyz/v1/chat/completions"
API_KEY = os.environ.get("TOGETHER_API_KEY", "").strip()
assert API_KEY, "Set TOGETHER_API_KEY environment variable first."

# Exact prompt template from the paper (Section 3.2)
TEST_PROMPT = (
    'Define the noun "table" in one short sentence. '
    "Use only common English words. "
    "Do not use the word itself in the definition."
)

# --- Candidate models -------------------------------------------------------
# status_hint: prior evidence from (a) Prof. Kumoi's live-API verification
# 2 days ago, and (b) docs.together.ai/docs/serverless-models fetched 2026-07-16.
CANDIDATES = [
    # (model_id, family, total_params_B or None if undisclosed, status_hint)
    ("openai/gpt-oss-20b",                        "gpt-oss",   20,   "verified both"),
    ("openai/gpt-oss-120b",                       "gpt-oss",   120,  "verified both"),
    ("meta-llama/Llama-3.3-70B-Instruct-Turbo",   "llama",     70,   "verified both"),
    ("meta-llama/Meta-Llama-3-8B-Instruct-Lite",  "llama",     8,    "docs only, untested"),
    ("Qwen/Qwen2.5-7B-Instruct-Turbo",            "qwen2.5",   7,    "verified both"),
    ("Qwen/Qwen3.5-9B",                           "qwen3.5",   9,    "verified both"),
    ("Qwen/Qwen3.5-397B-A17B",                    "qwen3.5",   397,  "docs yes / live 400 - CONFLICT"),
    ("Qwen/Qwen3.6-Plus",                         "qwen3.6",   None, "docs only, params undisclosed"),
    ("Qwen/Qwen3-235B-A22B-Instruct-2507-tput",   "qwen3",     235,  "live said nonexistent"),
    ("Qwen/Qwen3-235B-A22B-Instruct-2507-FP8",    "qwen3",     235,  "live said -FP8 exists"),
    ("google/gemma-4-31B-it",                     "gemma4",    31,   "verified both"),
    ("google/gemma-3n-E4B-it",                    "gemma3n",   4,    "verified both"),
    ("zai-org/GLM-5.1",                           "glm",       None, "docs yes / live 400 - CONFLICT"),
    ("zai-org/GLM-5",                             "glm",       None, "docs only, untested"),
    ("deepseek-ai/DeepSeek-V3.1",                 "deepseek",  671,  "docs yes / live 400 - CONFLICT"),
    ("deepseek-ai/DeepSeek-R1",                   "deepseek",  671,  "docs yes / live 400 - CONFLICT"),
    ("deepseek-ai/DeepSeek-V4-Pro",               "deepseek",  None, "docs only, untested"),
    ("MiniMaxAI/MiniMax-M2.7",                    "minimax",   None, "docs only, untested"),
    ("moonshotai/Kimi-K2.6",                      "kimi",      None, "docs only, untested"),
    ("moonshotai/Kimi-K2.5",                      "kimi",      None, "docs yes / live nonexistent - CONFLICT"),
    ("deepcogito/cogito-v2-1-671b",               "cogito",    671,  "docs only, untested"),
    ("LiquidAI/LFM2-24B-A2B",                     "lfm",       24,   "docs only, untested"),
    ("essentialai/rnj-1-instruct",                "rnj",       None, "docs only, untested"),
]

GEN_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 20,
    "max_tokens": 80,
}


def probe(model_id: str) -> dict:
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": TEST_PROMPT}],
        **GEN_PARAMS,
    }
    t0 = time.time()
    try:
        r = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json=payload,
            timeout=120,
        )
    except requests.RequestException as e:
        return {"model": model_id, "verdict": "network_error", "detail": str(e)}
    latency = round(time.time() - t0, 2)

    if r.status_code == 200:
        d = r.json()
        text = d["choices"][0]["message"]["content"]
        return {
            "model": model_id,
            "verdict": "WORKS",
            "latency_s": latency,
            "usage": d.get("usage"),
            "definition": text.strip()[:300],
        }
    # Classify the failure
    try:
        err = r.json().get("error", {})
    except Exception:
        err = {"message": r.text[:300]}
    msg = str(err.get("message", ""))[:300]
    if r.status_code == 400 and ("dedicated" in msg.lower() or "not available" in msg.lower()):
        verdict = "dedicated_only"
    elif r.status_code == 404 or "model" in msg.lower() and "not found" in msg.lower():
        verdict = "nonexistent"
    elif r.status_code == 429:
        verdict = "rate_limited"
    else:
        verdict = f"http_{r.status_code}"
    return {"model": model_id, "verdict": verdict, "detail": msg, "latency_s": latency}


def main():
    results = []
    for model_id, family, params, hint in CANDIDATES:
        rec = probe(model_id)
        rec.update({"family": family, "params_B": params, "prior_hint": hint})
        results.append(rec)
        status = rec["verdict"]
        print(f"{status:16s} {model_id:50s} ({hint})")
        if status == "WORKS":
            print(f"    -> {rec['definition'][:110]}")
        time.sleep(1.0)  # be gentle with rate limits

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase0_probe_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    working = [r for r in results if r["verdict"] == "WORKS"]
    print(f"\n{len(working)}/{len(results)} models usable serverless.")
    print(f"Results saved to {out}")


if __name__ == "__main__":
    main()
