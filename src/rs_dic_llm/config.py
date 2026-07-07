from dataclasses import dataclass, field

MLX_PROXY_URL = "http://localhost:8080"

PILOT_MODELS = [
    "mlx-community/Qwen3.5-0.8B-MLX-bf16",
    "mlx-community/Qwen3.5-27B-bf16",
]

FULL_MODELS = [
    "mlx-community/Qwen3.5-0.8B-MLX-bf16",
    "mlx-community/Qwen3.5-2B-bf16",
    "mlx-community/Qwen3.5-4B-MLX-bf16",
    "mlx-community/Qwen3.5-9B-bf16",
    "mlx-community/Qwen3.5-27B-bf16",
]


@dataclass
class ExperimentConfig:
    models: list[str] = field(default_factory=lambda: PILOT_MODELS)
    n_words: int = 3000         # total words (pilot proved 300 too sparse; use 3000)
    seed: int = 42
    # Qwen3.5 official non-thinking instruct settings (never use greedy T=0)
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 20
    max_tokens: int = 80
    max_retries: int = 3
    output_dir: str = "results"
    word_list_path: str = "data/sample_words/word_list_3k_v1.json"
