"""Download all 17 model weights to the HuggingFace cache.

Run this on a CPU-only instance BEFORE attaching the GPU.
Models download to ~/.cache/huggingface — no GPU memory needed.

Usage:
    export HUGGINGFACE_HUB_TOKEN=hf_...
    python -m experiments.download_weights
    python -m experiments.download_weights --family Gemma3   # one family only
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import MODEL_REGISTRY

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("ERROR: huggingface_hub not found. Run: pip install huggingface_hub")
    sys.exit(1)

TOKEN = os.environ.get("HUGGINGFACE_HUB_TOKEN")


def main(family_filter: str | None = None) -> None:
    models = [
        (display, hf_id, pb, fam)
        for display, hf_id, pb, fam in MODEL_REGISTRY
        if family_filter is None or fam == family_filter
    ]

    total_gb = sum(pb * 2 for _, _, pb, _ in models)  # ~2 GB per billion params at bf16
    print(f"Downloading {len(models)} models  (~{total_gb:.0f} GB estimated)")
    print(f"Destination: ~/.cache/huggingface/hub/\n")

    if TOKEN is None:
        print("WARNING: HUGGINGFACE_HUB_TOKEN not set.")
        print("         Gemma models will fail. Set it with:")
        print("         export HUGGINGFACE_HUB_TOKEN=hf_...\n")

    for i, (display, hf_id, pb, fam) in enumerate(models, 1):
        print(f"[{i}/{len(models)}] {display}  ({pb}B, {fam})")
        try:
            snapshot_download(
                repo_id=hf_id,
                token=TOKEN,
                ignore_patterns=["*.msgpack", "*.h5", "flax_model*", "tf_model*"],
            )
            print(f"  ✓ done\n")
        except Exception as e:
            print(f"  ✗ FAILED: {e}\n")
            print("  Check the model ID exists on hf.co and that you have accepted")
            print("  the license if it's a gated model (e.g. Gemma).\n")

    print("All downloads complete.")
    print("You can now stop this instance, attach the GPU, and restart.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", default=None,
                        choices=["Qwen2.5", "Qwen3.5", "Gemma3"],
                        help="Download only one model family")
    args = parser.parse_args()
    main(args.family)
