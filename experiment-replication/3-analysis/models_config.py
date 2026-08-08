"""
Model matrix from Phase 0/0b probes (see ../phase0_model_matrix.md).

Each entry:
    family        : model family label
    params_B      : total parameters in billions (None = undisclosed -> excluded
                    from scaling regression, kept for sr_rate regime analysis)
    active_B      : active params for MoE (informational)
    switch        : extra payload needed to disable thinking (verified in Phase 0b)
    stream        : True if the endpoint only supports streaming
    max_tokens    : per-definition budget (80 = paper protocol)
    tier          : 1 = scaling regression, 2 = sr_rate regime only,
                    3 = protocol deviation (off by default)
"""

MODELS = {
    # ---- Tier 1: scaling regression (known params, paper protocol) ----
    "openai/gpt-oss-20b": dict(
        family="gpt-oss", params_B=20, active_B=3.6,
        switch={"reasoning_effort": "low"}, stream=False, max_tokens=80, tier=1),
    "openai/gpt-oss-120b": dict(
        family="gpt-oss", params_B=120, active_B=5.1,
        switch={"reasoning_effort": "low"}, stream=False, max_tokens=80, tier=1),
    "meta-llama/Llama-3.3-70B-Instruct-Turbo": dict(
        family="llama", params_B=70, active_B=None,
        switch=None, stream=False, max_tokens=80, tier=1),
    "Qwen/Qwen2.5-7B-Instruct-Turbo": dict(
        family="qwen2.5", params_B=7, active_B=None,
        switch=None, stream=False, max_tokens=80, tier=1),
    "deepcogito/cogito-v2-1-671b": dict(
        family="cogito", params_B=671, active_B=37,
        switch=None, stream=False, max_tokens=80, tier=1),
    "google/gemma-3n-E4B-it": dict(
        family="gemma3n", params_B=4, active_B=None,   # ~4B effective (8B raw)
        switch=None, stream=False, max_tokens=80, tier=1),

    # ---- Tier 1b: cross-stack validation vs local RunPod runs ----
    "Qwen/Qwen3.5-9B": dict(
        family="qwen3.5", params_B=9, active_B=None,
        switch={"chat_template_kwargs": {"enable_thinking": False}},
        stream=False, max_tokens=80, tier=1),
    "google/gemma-4-31B-it": dict(
        family="gemma4", params_B=31, active_B=None,
        switch={"chat_template_kwargs": {"enable_thinking": False}},
        stream=False, max_tokens=80, tier=1),

    # ---- Tier 2: sr_rate regime analysis only (params undisclosed) ----
    "moonshotai/Kimi-K2.6": dict(
        family="kimi", params_B=None, active_B=None,
        switch={"chat_template_kwargs": {"thinking": False}},
        stream=False, max_tokens=80, tier=2),
    "deepseek-ai/DeepSeek-V4-Pro": dict(
        family="deepseek", params_B=None, active_B=None,
        switch={"chat_template_kwargs": {"thinking": False}},
        stream=False, max_tokens=80, tier=2),
    "Qwen/Qwen3.6-Plus": dict(
        family="qwen3.6", params_B=None, active_B=None,
        switch={"chat_template_kwargs": {"enable_thinking": False}},
        stream=True, max_tokens=80, tier=2),

    # ---- Tier 3: protocol deviation (thinking cannot be disabled) ----
    "MiniMaxAI/MiniMax-M2.7": dict(
        family="minimax", params_B=None, active_B=None,
        switch={"chat_template_kwargs": {"enable_thinking": False}},  # ignored by model
        stream=False, max_tokens=1024, tier=3),
}

GEN_PARAMS = {"temperature": 0.7, "top_p": 0.8, "top_k": 20}

PROMPT_TEMPLATE = (
    'Define the {pos} "{word}" in one short sentence. '
    "Use only common English words. "
    "Do not use the word itself in the definition."
)

# Local RunPod results — loaded from results/full_summary.json after the experiment.
# Fill these in from full_summary.json once the RunPod run is complete,
# then pool with the API runs in analyse.py.
# Values below are STALE (old runs, different model families) — update before use.
PRIOR_RESULTS = [
    dict(model="local/Qwen3.5-0.8B", family="qwen3.5", params_B=0.8,
         kernel_ratio=None, mset_k=None, circ=None, sr_rate=None, stack="hf_bf16"),
    dict(model="local/Qwen3.5-2B", family="qwen3.5", params_B=2,
         kernel_ratio=None, mset_k=None, circ=None, sr_rate=None, stack="hf_bf16"),
    dict(model="local/Qwen3.5-4B", family="qwen3.5", params_B=4,
         kernel_ratio=None, mset_k=None, circ=None, sr_rate=None, stack="hf_bf16"),
    dict(model="local/Qwen3.5-9B", family="qwen3.5", params_B=9,
         kernel_ratio=None, mset_k=None, circ=None, sr_rate=None, stack="hf_bf16"),
    dict(model="local/Qwen3.5-27B", family="qwen3.5", params_B=27,
         kernel_ratio=None, mset_k=None, circ=None, sr_rate=None, stack="hf_bf16"),
]
