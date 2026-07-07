"""Extended experiment: Gemma-4 cross-family + Qwen3.5-27B quantization ablation.

Run order (sequential, ~8-10 hours total):
  gemma-4-e4b-bf16      ~4B  bf16  → ~20 min
  gemma-4-31b-8bit      ~31B 8bit  → ~3 h
  Qwen3.5-27B-8bit      27B  8bit  → ~3 h
  Qwen3.5-27B-6bit      27B  6bit  → ~2.5 h
  Qwen3.5-27B-4bit      27B  4bit  → ~2 h

Research questions:
  RQ-A  Cross-family: does minset/kernel ~ log(params) hold for Gemma-4?
  RQ-B  Quantization: does 4/6/8bit shift graph metrics vs bf16?

Usage:
    uv run python -m experiments.run_extended [--seed 42]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import ExperimentConfig
from rs_dic_llm.sampling import load_word_list
from rs_dic_llm.generation import generate_definitions, load_definitions
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.analysis import compute_all_metrics, save_metrics

# (model_id, display_name, param_B, family, quant)
EXTENDED_MODELS = [
    ("mlx-community/gemma-4-e4b-it-bf16",   "gemma-4-e4b-bf16",  4.0,  "gemma4", "bf16"),
    ("mlx-community/gemma-4-31b-it-8bit",   "gemma-4-31b-8bit",  31.0, "gemma4", "8bit"),
    ("mlx-community/Qwen3.5-27B-8bit",      "Qwen3.5-27B-8bit",  27.0, "qwen35", "8bit"),
    ("mlx-community/Qwen3.5-27B-6bit",      "Qwen3.5-27B-6bit",  27.0, "qwen35", "6bit"),
    ("mlx-community/Qwen3.5-27B-4bit",      "Qwen3.5-27B-4bit",  27.0, "qwen35", "4bit"),
]


def run_one(model_id: str, display: str, cfg: ExperimentConfig,
            words: list[dict]) -> dict:
    def_path     = f"data/definitions/{display}_{cfg.seed}.jsonl"
    metrics_path = f"{cfg.output_dir}/metrics/{display}_{cfg.seed}.json"

    if Path(metrics_path).exists():
        print(f"  [skip] {display}: metrics already exist")
        return json.load(open(metrics_path))

    if not Path(def_path).exists():
        print(f"\n[extended] generating — {display}")
        defs = generate_definitions(words, model_id, cfg, output_path=def_path)
    else:
        print(f"\n[extended] loading existing: {def_path}")
        defs = load_definitions(def_path)

    print(f"[extended] building graph + metrics — {display}")
    G = build_graph(defs)
    m = compute_all_metrics(G, model_id=display)
    save_metrics(m, metrics_path)
    _print_row(m, def_path)
    return m


def _print_row(m: dict, def_path: str | None = None) -> None:
    ks = m.get("kernel_size", 0) or 1
    ms = m.get("minset_size") or 0
    sr_str = ""
    if def_path and Path(def_path).exists():
        lines = Path(def_path).read_text().strip().splitlines()
        recs  = [json.loads(l) for l in lines]
        sr    = sum(1 for r in recs if r["status"] == "self_referential") / len(recs)
        sr_str = f"  sr={sr:.0%}"
    print(f"    edges={m.get('n_edges',0):6}  out_deg={m.get('mean_out_degree',0):.2f}"
          f"  circ={m.get('circulation_rate',0)*100:.1f}%"
          f"  kern={m.get('kernel_ratio',0)*100:.1f}%"
          f"  mset/k={ms/ks*100:.1f}%{sr_str}")


def _load_existing(display: str, seed: int) -> dict | None:
    p = Path(f"results/metrics/{display}_{seed}.json")
    return json.load(open(p)) if p.exists() else None


def print_table(rows: list[tuple]) -> None:
    """rows: list of (family, param_b, quant, metrics_dict)"""
    hdr = f"  {'family':8} {'size':>6}B  {'quant':5}  {'edges':>7}  {'out_deg':>7}  {'circ%':>6}  {'kern%':>6}  {'mset/k%':>8}"
    print(hdr)
    print("  " + "-" * 72)
    for fam, pb, q, m in rows:
        ks = m.get("kernel_size", 0) or 1
        ms = m.get("minset_size") or 0
        print(f"  {fam:8} {pb:>6.1f}   {q:5}  "
              f"{m.get('n_edges',0):>7}  "
              f"{m.get('mean_out_degree',0):>7.2f}  "
              f"{m.get('circulation_rate',0)*100:>6.1f}  "
              f"{m.get('kernel_ratio',0)*100:>6.1f}  "
              f"{ms/ks*100:>8.1f}")


def run(seed: int = 42) -> None:
    cfg   = ExperimentConfig(n_words=3000, seed=seed)
    words = load_word_list(cfg.word_list_path)
    print(f"[extended] {len(words)} words loaded")

    results: dict[str, dict] = {}
    for model_id, display, param_b, family, quant in EXTENDED_MODELS:
        m = run_one(model_id, display, cfg, words)
        results[display] = {**m, "param_b": param_b, "family": family, "quant": quant}

    # ── Cross-family table ─────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("RQ-A  CROSS-FAMILY: Qwen3.5 (bf16) vs Gemma-4")
    print("=" * 78)
    qwen_bf16 = [
        ("Qwen3.5-0.8B-MLX-bf16", 0.8), ("Qwen3.5-2B-bf16", 2.0),
        ("Qwen3.5-4B-MLX-bf16",   4.0), ("Qwen3.5-9B-bf16", 9.0),
        ("Qwen3.5-27B-bf16",     27.0),
    ]
    rows = []
    for fname, pb in qwen_bf16:
        m = _load_existing(fname, seed)
        if m:
            rows.append(("Qwen3.5", pb, "bf16", m))
    for display, data in results.items():
        if data["family"] == "gemma4":
            rows.append(("Gemma-4", data["param_b"], data["quant"], data))
    rows.sort(key=lambda x: x[1])
    print_table(rows)

    # ── Quantization table ─────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("RQ-B  QUANTIZATION ABLATION: Qwen3.5-27B")
    print("=" * 78)
    quant_rows = []
    m_bf16 = _load_existing("Qwen3.5-27B-bf16", seed)
    if m_bf16:
        quant_rows.append(("Qwen3.5", 27.0, "bf16", m_bf16))
    for display, data in results.items():
        if data["family"] == "qwen35":
            quant_rows.append(("Qwen3.5", 27.0, data["quant"], data))
    quant_rows.sort(key=lambda x: {"bf16": 0, "8bit": 1, "6bit": 2, "4bit": 3}[x[2]])
    print_table(quant_rows)

    Path(f"{cfg.output_dir}/extended_summary.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n[extended] saved results/extended_summary.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run(args.seed)
