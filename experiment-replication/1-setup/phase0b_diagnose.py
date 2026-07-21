"""
Phase 0b: diagnose the empty-definition problem and finalize the usable model set.

Phase 0 findings this script addresses:
  1. Six "working" models returned empty content: reasoning tokens ate max_tokens=80.
  2. gpt-oss-120b / Llama-3.3-70B returned transient 503 -> retry with backoff.
  3. Qwen3.6-Plus requires stream=true -> streamed here.

For each model we try, in order, until one yields non-empty content:
  attempt 1: paper protocol (max_tokens=80) + model-specific "disable thinking" switch
  attempt 2: same switch, max_tokens=1024 (check whether reasoning can't be disabled)
  attempt 3: no switch, max_tokens=1024 (capture reasoning length + final content)

Records everything (raw response fields included) to phase0b_results.json.

Usage:
    $env:TOGETHER_API_KEY = "tgp_v1_..."
    python phase0b_diagnose.py
"""

import json
import os
import time

import requests

API_URL = "https://api.together.xyz/v1/chat/completions"
API_KEY = os.environ.get("TOGETHER_API_KEY", "").strip()
assert API_KEY, "Set TOGETHER_API_KEY environment variable first."

TEST_PROMPT = (
    'Define the noun "table" in one short sentence. '
    "Use only common English words. "
    "Do not use the word itself in the definition."
)

BASE = {"temperature": 0.7, "top_p": 0.8, "top_k": 20}

# Model-specific switches that plausibly disable thinking/reasoning.
# Each entry: list of extra-payload dicts to try (first = most likely).
THINK_OFF = {
    "openai/gpt-oss-20b":       [{"reasoning_effort": "low"}],
    "openai/gpt-oss-120b":      [{"reasoning_effort": "low"}],
    "Qwen/Qwen3.5-9B":          [{"chat_template_kwargs": {"enable_thinking": False}},
                                 {"enable_thinking": False}],
    "Qwen/Qwen3.6-Plus":        [{"chat_template_kwargs": {"enable_thinking": False}},
                                 {"enable_thinking": False}],
    "google/gemma-4-31B-it":    [{"chat_template_kwargs": {"enable_thinking": False}}],
    "deepseek-ai/DeepSeek-V4-Pro": [{"chat_template_kwargs": {"thinking": False}},
                                    {"reasoning_effort": "none"}],
    "MiniMaxAI/MiniMax-M2.7":   [{"chat_template_kwargs": {"enable_thinking": False}},
                                 {"reasoning_effort": "none"}],
    "moonshotai/Kimi-K2.6":     [{"chat_template_kwargs": {"thinking": False}},
                                 {"reasoning_effort": "none"}],
}

MODELS = [
    # needs_stream, model_id
    (False, "openai/gpt-oss-20b"),
    (False, "openai/gpt-oss-120b"),          # retry the 503
    (False, "meta-llama/Llama-3.3-70B-Instruct-Turbo"),  # retry the 503
    (False, "Qwen/Qwen2.5-7B-Instruct-Turbo"),
    (False, "Qwen/Qwen3.5-9B"),
    (True,  "Qwen/Qwen3.6-Plus"),
    (False, "google/gemma-4-31B-it"),
    (False, "google/gemma-3n-E4B-it"),
    (False, "deepseek-ai/DeepSeek-V4-Pro"),
    (False, "MiniMaxAI/MiniMax-M2.7"),
    (False, "moonshotai/Kimi-K2.6"),
    (False, "deepcogito/cogito-v2-1-671b"),
]


def call(model_id, max_tokens, extra, stream, retries=3):
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": TEST_PROMPT}],
        "max_tokens": max_tokens,
        **BASE,
        **(extra or {}),
    }
    if stream:
        payload["stream"] = True
    for attempt in range(retries):
        try:
            r = requests.post(API_URL, headers={"Authorization": f"Bearer {API_KEY}"},
                              json=payload, timeout=180, stream=stream)
        except requests.RequestException as e:
            return {"error": f"network: {e}"}
        if r.status_code == 503:
            time.sleep(5 * (attempt + 1))
            continue
        break
    if r.status_code != 200:
        try:
            msg = r.json().get("error", {}).get("message", r.text[:200])
        except Exception:
            msg = r.text[:200]
        return {"error": f"http_{r.status_code}: {str(msg)[:200]}"}

    if stream:
        content, reasoning = [], []
        for line in r.iter_lines():
            if not line or not line.startswith(b"data: "):
                continue
            chunk = line[6:]
            if chunk == b"[DONE]":
                break
            try:
                delta = json.loads(chunk)["choices"][0]["delta"]
            except Exception:
                continue
            if delta.get("content"):
                content.append(delta["content"])
            if delta.get("reasoning_content") or delta.get("reasoning"):
                reasoning.append(delta.get("reasoning_content") or delta.get("reasoning"))
        return {"content": "".join(content).strip(),
                "reasoning_len": len("".join(reasoning)), "usage": None}

    d = r.json()
    msg = d["choices"][0]["message"]
    reasoning_text = msg.get("reasoning_content") or msg.get("reasoning") or ""
    return {
        "content": (msg.get("content") or "").strip(),
        "reasoning_len": len(reasoning_text),
        "usage": d.get("usage"),
        "finish_reason": d["choices"][0].get("finish_reason"),
        "raw_message_keys": list(msg.keys()),
    }


def main():
    results = []
    for needs_stream, model_id in MODELS:
        switches = THINK_OFF.get(model_id, [])
        attempts = []
        # Build attempt ladder
        ladder = []
        for sw in switches:
            ladder.append(("switch+80tok", 80, sw))
        for sw in switches:
            ladder.append(("switch+1024tok", 1024, sw))
        ladder.append(("plain+1024tok", 1024, None))
        if not switches:
            ladder.insert(0, ("plain+80tok", 80, None))

        final = None
        for label, mt, sw in ladder:
            res = call(model_id, mt, sw, needs_stream)
            res["attempt"] = label
            res["switch"] = sw
            attempts.append(res)
            if res.get("content"):
                final = res
                break
            time.sleep(1)

        ok = final is not None
        summary = {
            "model": model_id,
            "usable": ok,
            "winning_attempt": final["attempt"] if ok else None,
            "winning_switch": final["switch"] if ok else None,
            "definition": final["content"][:200] if ok else None,
            "reasoning_len": final.get("reasoning_len") if ok else None,
            "protocol_80tok_ok": ok and "80tok" in final["attempt"],
            "attempts": attempts,
        }
        results.append(summary)
        flag = "OK " if ok else "FAIL"
        proto = "(80tok protocol)" if summary["protocol_80tok_ok"] else "(needs deviation)" if ok else ""
        print(f"{flag} {model_id:45s} {summary['winning_attempt'] or '-':16s} {proto}")
        if ok:
            print(f"     -> {summary['definition'][:100]}")
        time.sleep(1)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase0b_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
