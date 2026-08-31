"""HuggingFace transformers client for RunPod.

Requires (pre-installed in most RunPod CUDA images, otherwise):
    pip install transformers>=4.40 accelerate>=0.30

For quantization side-study only (not used in the main experiment):
    pip install bitsandbytes>=0.43    # Linux/CUDA only

Usage:
    hf_client.load_model(model_id)                        # bf16 (default)
    hf_client.load_model(model_id, quantization="int8")   # 8-bit (side study only)
    hf_client.load_model(model_id, quantization="int4")   # 4-bit (side study only)
    text = hf_client.generate(prompt, temperature=..., seed=...)
    hf_client.unload_model()
"""

import gc
import os
import sys
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Set HUGGINGFACE_HUB_TOKEN in your environment before running.
# Required for Gemma models (gated — must accept license on hf.co first).
# export HUGGINGFACE_HUB_TOKEN=hf_...
_HF_TOKEN: str | None = os.environ.get("HUGGINGFACE_HUB_TOKEN")

_model: "AutoModelForCausalLM | None" = None
_tokenizer: "AutoTokenizer | None" = None
_current_model_id: str | None = None
_current_quantization: str = "bf16"


def load_model(model_id: str, quantization: str = "bf16") -> None:
    """Load model and tokenizer into module-level state.

    quantization: "bf16" (default, main experiment), "int8", or "int4"
                  (int8/int4 require bitsandbytes on Linux/CUDA — side study only)
    """
    global _model, _tokenizer, _current_model_id, _current_quantization

    if _current_model_id == model_id and _current_quantization == quantization and _model is not None:
        print(f"  [hf] already loaded: {model_id} ({quantization})")
        return

    if _model is not None:
        unload_model()

    if _HF_TOKEN is None and "gemma" in model_id.lower():
        print("  [hf] WARNING: HUGGINGFACE_HUB_TOKEN not set — Gemma download will fail.",
              file=sys.stderr)

    print(f"  [hf] loading {model_id} [{quantization}] ...", end=" ", flush=True)
    _tokenizer = AutoTokenizer.from_pretrained(model_id, token=_HF_TOKEN)

    load_kwargs: dict = {"device_map": "auto", "token": _HF_TOKEN}

    if quantization == "bf16":
        load_kwargs["torch_dtype"] = torch.bfloat16
    elif quantization == "int8":
        try:
            from transformers import BitsAndBytesConfig
        except ImportError:
            raise ImportError("bitsandbytes is required for int8. Run: pip install bitsandbytes")
        load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
    elif quantization == "int4":
        try:
            from transformers import BitsAndBytesConfig
        except ImportError:
            raise ImportError("bitsandbytes is required for int4. Run: pip install bitsandbytes")
        load_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
    else:
        raise ValueError(f"Unknown quantization: {quantization!r}. Use 'bf16', 'int8', or 'int4'.")

    _model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)
    _model.eval()
    _current_model_id = model_id
    _current_quantization = quantization

    vram_gb = (
        sum(p.element_size() * p.numel() for p in _model.parameters()) / 1e9
    )
    print(f"OK  ({vram_gb:.1f} GB bf16)")


def unload_model() -> None:
    """Free the current model from GPU memory."""
    global _model, _tokenizer, _current_model_id
    _model = None
    _tokenizer = None
    _current_model_id = None
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _format_prompt(prompt: str) -> str:
    """Apply chat template, or return raw text for base models with no template."""
    messages = [{"role": "user", "content": prompt}]
    try:
        return _tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        try:
            return _tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            return messages[-1]["content"]


def generate(
    prompt: str,
    *,
    temperature: float = 0.7,
    top_p: float = 0.8,
    top_k: int = 20,
    max_tokens: int = 200,
    seed: int = 0,
    max_retries: int = 3,
) -> str:
    """Generate one completion for the loaded model."""
    if _model is None or _tokenizer is None:
        raise RuntimeError("No model loaded — call load_model() first")

    text = _format_prompt(prompt)

    for attempt in range(max_retries):
        try:
            torch.manual_seed(seed)
            inputs = _tokenizer(text, return_tensors="pt").to(_model.device)
            with torch.no_grad():
                output = _model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    do_sample=temperature > 0,
                    pad_token_id=_tokenizer.eos_token_id,
                )
            new_tokens = output[0][inputs["input_ids"].shape[1]:]
            return _tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        except Exception as e:
            print(
                f"  [hf error] attempt {attempt + 1}/{max_retries}: {e}",
                file=sys.stderr,
            )
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

    raise RuntimeError(f"hf generation failed after {max_retries} retries")


def generate_batch(
    prompts: "list[str]",
    *,
    temperature: float = 0.7,
    top_p: float = 0.8,
    top_k: int = 20,
    max_tokens: int = 200,
    seed: int = 0,
) -> "list[str]":
    """Generate completions for a batch of prompts in one GPU call.

    Uses left-padding so all sequences start generating at the same position.
    Returns one decoded string per prompt in the same order.
    """
    if _model is None or _tokenizer is None:
        raise RuntimeError("No model loaded — call load_model() first")

    texts = [_format_prompt(p) for p in prompts]

    orig_padding_side = _tokenizer.padding_side
    _tokenizer.padding_side = "left"
    if _tokenizer.pad_token_id is None:
        _tokenizer.pad_token_id = _tokenizer.eos_token_id

    try:
        torch.manual_seed(seed)
        inputs = _tokenizer(
            texts, return_tensors="pt", padding=True, truncation=True
        ).to(_model.device)
        input_len = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = _model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=temperature > 0,
                pad_token_id=_tokenizer.eos_token_id,
            )

        results = []
        for i in range(len(prompts)):
            new_tokens = outputs[i][input_len:]
            results.append(
                _tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            )
        return results
    finally:
        _tokenizer.padding_side = orig_padding_side


def health() -> dict:
    return {
        "backend": "ok" if _model is not None else "no_model",
        "model_id": _current_model_id,
    }
