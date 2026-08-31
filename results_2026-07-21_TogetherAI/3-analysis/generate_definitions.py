"""
Stage 1: generate one definition per (word, pos) for each model via Together AI.

Paper protocol: T=0.7, top_p=0.8, top_k=20, max_tokens=80, thinking disabled
(per-model switch from models_config), 3 consecutive failures -> status "failed".
Status labels: ok | self_referential | failed.

Features:
  - checkpoint/resume: output is JSONL, existing words are skipped on rerun
  - concurrency: --workers (default 4) with per-request retry/backoff
  - per-model output: defs/<model_slug>.seed<gen_seed>.jsonl

Usage:
    $env:TOGETHER_API_KEY = "tgp_v1_..."
    python generate_definitions.py --words words.json --models tier1
    python generate_definitions.py --models "openai/gpt-oss-20b,Qwen/Qwen3.5-9B"
    python generate_definitions.py --models all --gen-seed 123
"""

import argparse
import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from models_config import GEN_PARAMS, MODELS, PROMPT_TEMPLATE

API_URL = "https://api.together.xyz/v1/chat/completions"
API_KEY = os.environ.get("TOGETHER_API_KEY", "").strip()
assert API_KEY, "Set TOGETHER_API_KEY environment variable first."

write_lock = threading.Lock()


def slug(model_id: str) -> str:
    return model_id.replace("/", "__")


def call_once(model_id: str, cfg: dict, prompt: str, gen_seed: int | None):
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": cfg["max_tokens"],
        **GEN_PARAMS,
    }
    if cfg["switch"]:
        payload.update(cfg["switch"])
    if gen_seed is not None:
        payload["seed"] = gen_seed
    if cfg["stream"]:
        payload["stream"] = True

    r = requests.post(API_URL, headers={"Authorization": f"Bearer {API_KEY}"},
                      json=payload, timeout=180, stream=cfg["stream"])
    if r.status_code == 429 or r.status_code >= 500:
        raise RuntimeError(f"retryable http_{r.status_code}")
    if r.status_code != 200:
        raise ValueError(f"http_{r.status_code}: {r.text[:200]}")

    if cfg["stream"]:
        parts = []
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
                parts.append(delta["content"])
        return "".join(parts).strip(), None
    d = r.json()
    msg = d["choices"][0]["message"]
    return (msg.get("content") or "").strip(), d.get("usage")


def generate_one(model_id: str, cfg: dict, entry: dict, gen_seed):
    word, pos = entry["word"], entry["pos"]
    prompt = PROMPT_TEMPLATE.format(pos=pos, word=word)
    retryable = 0   # 429/5xx/network: be patient, the endpoint may be overloaded
    empty = 0       # model responded but with empty content
    while retryable < 8 and empty < 3:
        try:
            text, usage = call_once(model_id, cfg, prompt, gen_seed)
        except (RuntimeError, requests.RequestException):
            retryable += 1
            time.sleep(min(5 * 2 ** (retryable - 1), 120))   # 5s .. 120s
            continue
        except ValueError as e:
            return dict(word=word, pos=pos, status="failed", definition="",
                        error=str(e)[:200])
        if not text:
            empty += 1
            time.sleep(1)
            continue
        sr = bool(re.search(rf"\b{re.escape(word)}\b", text.lower()))
        return dict(word=word, pos=pos,
                    status="self_referential" if sr else "ok",
                    definition=text, usage=usage)
    return dict(word=word, pos=pos, status="failed", definition="",
                error=f"gave up: {retryable} retryable / {empty} empty")


def run_model(model_id: str, entries: list, gen_seed, workers: int, out_dir: str):
    cfg = MODELS[model_id]
    out_path = os.path.join(out_dir, f"{slug(model_id)}.seed{gen_seed}.jsonl")
    done = set()
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("status") != "failed":     # failed words are retried
                    done.add((rec["word"], rec["pos"]))
    todo = [e for e in entries if (e["word"], e["pos"]) not in done]
    print(f"\n=== {model_id} | done {len(done)} | todo {len(todo)} ===")
    if not todo:
        return

    n_done = 0
    t0 = time.time()
    with open(out_path, "a", encoding="utf-8") as f, \
         ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(generate_one, model_id, cfg, e, gen_seed): e for e in todo}
        for fut in as_completed(futures):
            rec = fut.result()
            with write_lock:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
            n_done += 1
            if n_done % 100 == 0:
                rate = n_done / (time.time() - t0)
                eta = (len(todo) - n_done) / max(rate, 0.01) / 60
                print(f"  {n_done}/{len(todo)} ({rate:.1f}/s, ETA {eta:.0f} min)")
    print(f"  finished -> {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", default="words.json")
    ap.add_argument("--models", default="tier1",
                    help='"tier1", "tier12", "all", or comma-separated model IDs')
    ap.add_argument("--gen-seed", type=int, default=42)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out-dir", default="defs")
    args = ap.parse_args()

    with open(args.words, encoding="utf-8") as f:
        entries = json.load(f)

    if args.models == "tier1":
        model_ids = [m for m, c in MODELS.items() if c["tier"] == 1]
    elif args.models == "tier12":
        model_ids = [m for m, c in MODELS.items() if c["tier"] in (1, 2)]
    elif args.models == "all":
        model_ids = list(MODELS)
    else:
        model_ids = [m.strip() for m in args.models.split(",")]
        unknown = [m for m in model_ids if m not in MODELS]
        assert not unknown, f"Unknown models: {unknown}"

    os.makedirs(args.out_dir, exist_ok=True)
    for m in model_ids:
        run_model(m, entries, args.gen_seed, args.workers, args.out_dir)


if __name__ == "__main__":
    main()
