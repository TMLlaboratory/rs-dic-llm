"""mlx-proxy client — adapted from rs-it-llm/experiments/filter_paradox_llm.py."""

import sys
import time

import requests

from .config import MLX_PROXY_URL


def load_model(model_id: str) -> None:
    """Load a model into mlx-proxy (enable_thinking=False).

    Skips if the requested model is already loaded to avoid proxy hang.
    """
    try:
        health = requests.get(f"{MLX_PROXY_URL}/health", timeout=10).json()
        loaded = health.get("model_id") or ""
        if health.get("backend") == "ok" and model_id in loaded:
            print(f"  [mlx-proxy] already loaded: {loaded}")
            return
    except Exception:
        pass

    print(f"  [mlx-proxy] loading {model_id} ...", end=" ", flush=True)
    r = requests.post(
        f"{MLX_PROXY_URL}/v1/models/load",
        json={"model_id": model_id, "enable_thinking": False},
        timeout=600,
    )
    r.raise_for_status()
    print(r.json().get("status", "OK"))


def unload_model() -> None:
    try:
        requests.post(f"{MLX_PROXY_URL}/v1/models/unload", timeout=30)
    except Exception:
        pass


def generate(
    prompt: str,
    *,
    temperature: float = 0.7,
    top_p: float = 0.8,
    top_k: int = 20,
    max_tokens: int = 80,
    max_retries: int = 3,
) -> str:
    """Generate one completion via the loaded model (non-streaming).

    Returns the stripped response text, or raises on repeated failure.
    """
    for attempt in range(max_retries):
        try:
            r = requests.post(
                f"{MLX_PROXY_URL}/v1/chat/completions",
                json={
                    "model": "any",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "max_tokens": max_tokens,
                },
                timeout=120,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  [mlx-proxy error] attempt {attempt + 1}/{max_retries}: {e}",
                  file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"mlx-proxy failed after {max_retries} retries")


def health() -> dict:
    """Return the raw /health response dict."""
    return requests.get(f"{MLX_PROXY_URL}/health", timeout=10).json()
