from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple

# Central model registry — (display_name, hf_model_id, param_b, family)
# All instruct variants, all bf16, no quantization, no exceptions.
# VERIFY these HuggingFace IDs before running: search each on hf.co/models
MODEL_REGISTRY: List[Tuple[str, str, float, str]] = [
    # Qwen2.5 — 7 sizes
    ("Qwen2.5-0.5B",  "Qwen/Qwen2.5-0.5B-Instruct",   0.5,  "Qwen2.5"),
    ("Qwen2.5-1.5B",  "Qwen/Qwen2.5-1.5B-Instruct",   1.5,  "Qwen2.5"),
    ("Qwen2.5-3B",    "Qwen/Qwen2.5-3B-Instruct",     3.0,  "Qwen2.5"),
    ("Qwen2.5-7B",    "Qwen/Qwen2.5-7B-Instruct",     7.0,  "Qwen2.5"),
    ("Qwen2.5-14B",   "Qwen/Qwen2.5-14B-Instruct",   14.0,  "Qwen2.5"),
    ("Qwen2.5-32B",   "Qwen/Qwen2.5-32B-Instruct",   32.0,  "Qwen2.5"),
    ("Qwen2.5-72B",   "Qwen/Qwen2.5-72B-Instruct",   72.0,  "Qwen2.5"),
    # Qwen3 — 5 sizes
    ("Qwen3-0.6B",    "Qwen/Qwen3-0.6B",               0.6,  "Qwen3"),
    ("Qwen3-1.7B",    "Qwen/Qwen3-1.7B",               1.7,  "Qwen3"),
    ("Qwen3-4B",      "Qwen/Qwen3-4B",                 4.0,  "Qwen3"),
    ("Qwen3-8B",      "Qwen/Qwen3-8B",                 8.0,  "Qwen3"),
    ("Qwen3-14B",     "Qwen/Qwen3-14B",               14.0,  "Qwen3"),
    # Gemma 3 — 5 sizes
    ("Gemma3-270M",   "google/gemma-3-270m-it",        0.27, "Gemma3"),
    ("Gemma3-1B",     "google/gemma-3-1b-it",          1.0,  "Gemma3"),
    ("Gemma3-4B",     "google/gemma-3-4b-it",          4.0,  "Gemma3"),
    ("Gemma3-12B",    "google/gemma-3-12b-it",        12.0,  "Gemma3"),
    ("Gemma3-27B",    "google/gemma-3-27b-it",        27.0,  "Gemma3"),
    # Gemma 3 base / pre-trained (無印) — 5 sizes
    ("Gemma3-270M-pt", "google/gemma-3-270m",          0.27, "Gemma3-pt"),
    ("Gemma3-1B-pt",   "google/gemma-3-1b-pt",         1.0,  "Gemma3-pt"),
    ("Gemma3-4B-pt",   "google/gemma-3-4b-pt",         4.0,  "Gemma3-pt"),
    ("Gemma3-12B-pt",  "google/gemma-3-12b-pt",       12.0,  "Gemma3-pt"),
    ("Gemma3-27B-pt",  "google/gemma-3-27b-pt",       27.0,  "Gemma3-pt"),
    # Qwen3 Instruct-2507 — 4B only
    ("Qwen3-4B-Instruct-2507", "Qwen/Qwen3-4B-Instruct-2507", 4.0, "Qwen3-Instruct"),
]

# Convenient lookups keyed by hf_model_id
MODEL_DISPLAY = {hf: display for display, hf, _, _f in MODEL_REGISTRY}
MODEL_PARAM_B = {hf: pb     for _d,    hf, pb, _f in MODEL_REGISTRY}
MODEL_FAMILY  = {hf: fam    for _d,    hf, _p, fam in MODEL_REGISTRY}

# Ordered list of all HF model IDs for sequential runs
FULL_MODELS: List[str] = [hf for _, hf, _, _ in MODEL_REGISTRY]

# Instruct-only models (exclude base / pretrained)
INSTRUCT_MODELS: List[str] = [
    hf for _, hf, _, fam in MODEL_REGISTRY
    if not fam.endswith("-pt")
]

# Base / pretrained models only
BASE_MODELS: List[str] = [
    hf for _, hf, _, fam in MODEL_REGISTRY
    if fam.endswith("-pt")
]

# Smoke-test subset: one small model from each family
SMOKE_MODELS: List[str] = [
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen3-0.6B",
    "google/gemma-3-1b-it",
]


@dataclass
class ExperimentConfig:
    models: List[str] = field(default_factory=lambda: FULL_MODELS)
    n_words: int = 3000
    seed: int = 42              # word-sampling seed (fixed, never changes)
    generation_seed: int = 0    # base seed for generation; per-word = generation_seed + word_index
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 20
    max_tokens: int = 200       # raised from 80; avg definition is 11-16 tokens, max ~39
    max_retries: int = 3
    output_dir: str = "results"
    word_list_path: str = "data/sample_words/word_list_3k_v1.json"
