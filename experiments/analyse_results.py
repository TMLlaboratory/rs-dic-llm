"""Deep analysis of full experiment results.

Analyses:
  A. Kernel Jaccard similarity across model pairs
  B. Stable / model-specific Kernel words
  C. Core word content + NSM overlap
  D. In-degree hubs (most-cited words in definitions)
  E. Vocabulary diversity (unique defining words per model)
  F. Monotone metric summary (kernel_ratio, minset/kernel)
"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.sampling import load_word_list
from rs_dic_llm.generation import load_definitions
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.metrics.kernel_core import compute_kernel, compute_core
from rs_dic_llm.normalize import normalize

SEED = 42
MODELS = [
    "mlx-community/Qwen3.5-0.8B-MLX-bf16",
    "mlx-community/Qwen3.5-2B-bf16",
    "mlx-community/Qwen3.5-4B-MLX-bf16",
    "mlx-community/Qwen3.5-9B-bf16",
    "mlx-community/Qwen3.5-27B-bf16",
]
MODEL_SIZES = {"0.8B-MLX-bf16": 0.8, "2B-bf16": 2, "4B-MLX-bf16": 4,
               "9B-bf16": 9, "27B-bf16": 27}
NSM_PATH = "data/nsm_primes_65.json"


def short(model_id: str) -> str:
    return model_id.split("/")[-1].replace("Qwen3.5-", "")


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def load_all() -> dict:
    """Load graphs, kernels, cores for all models + wordnet."""
    words = load_word_list(f"data/sample_words/word_list_3k_v1.json")
    vocab = {w["lemma"] for w in words}
    data = {}

    for model_id in MODELS:
        s = short(model_id)
        def_path = f"data/definitions/{model_id.split('/')[-1]}_{SEED}.jsonl"
        defs = load_definitions(def_path)
        G = build_graph(defs)
        kernel = compute_kernel(G)
        core = compute_core(G, kernel)
        data[s] = {"G": G, "kernel": kernel, "core": core, "defs": defs}
        print(f"  loaded {s}: kernel={len(kernel)}, core={len(core)}")

    # WordNet baseline
    from rs_dic_llm.wordnet_baseline import build_wordnet_graph
    wn_G, _ = build_wordnet_graph(words)
    wn_kernel = compute_kernel(wn_G)
    wn_core = compute_core(wn_G, wn_kernel)
    data["wordnet"] = {"G": wn_G, "kernel": wn_kernel, "core": wn_core, "defs": None}
    print(f"  loaded wordnet: kernel={len(wn_kernel)}, core={len(wn_core)}")
    return data, vocab


# ─── A. Kernel Jaccard ────────────────────────────────────────────────────────
def analysis_A(data: dict) -> None:
    print("\n" + "=" * 70)
    print("A. Kernel Jaccard similarity (rows × cols)")
    print("=" * 70)
    keys = [short(m) for m in MODELS] + ["wordnet"]
    header = f"{'':18}" + "".join(f"{k:>12}" for k in keys)
    print(header)
    for ki in keys:
        row = f"{ki:18}"
        for kj in keys:
            j = jaccard(data[ki]["kernel"], data[kj]["kernel"])
            row += f"{j:>12.3f}"
        print(row)


# ─── B. Kernel stability ──────────────────────────────────────────────────────
def analysis_B(data: dict) -> None:
    print("\n" + "=" * 70)
    print("B. Kernel word stability across LLM models")
    print("=" * 70)
    llm_keys = [short(m) for m in MODELS]
    kernels = [data[k]["kernel"] for k in llm_keys]

    # Count how many models each word appears in
    counter = Counter()
    for k in kernels:
        counter.update(k)

    in_all = {w for w, c in counter.items() if c == len(MODELS)}
    in_none = set(data[llm_keys[0]]["G"].nodes()) - set(counter.keys())
    in_wn_kernel = data["wordnet"]["kernel"]

    print(f"Words in ALL 5 LLM kernels     : {len(in_all)}")
    print(f"  ∩ WordNet kernel              : {len(in_all & in_wn_kernel)}")
    print(f"  Sample: {sorted(in_all)[:30]}")

    print(f"\nDistribution (in N of 5 models):")
    for n in range(5, 0, -1):
        words = {w for w, c in counter.items() if c == n}
        overlap_wn = words & in_wn_kernel
        print(f"  N={n}: {len(words):4d} words  (∩ WordNet kernel: {len(overlap_wn)})")

    print(f"\nTop 20 words by frequency in LLM kernels (with WordNet kernel flag):")
    for word, cnt in counter.most_common(20):
        wn_flag = "✓WN" if word in in_wn_kernel else "   "
        print(f"  {cnt}/5  {wn_flag}  {word}")


# ─── C. Core content + NSM ───────────────────────────────────────────────────
def analysis_C(data: dict) -> None:
    print("\n" + "=" * 70)
    print("C. Core word content + NSM overlap")
    print("=" * 70)
    nsm = set(json.load(open(NSM_PATH))) if Path(NSM_PATH).exists() else set()

    for key in [short(m) for m in MODELS] + ["wordnet"]:
        core = data[key]["core"]
        nsm_hit = core & nsm
        print(f"\n  {key} (core={len(core)}):")
        print(f"    NSM overlap: {len(nsm_hit)}/{len(nsm)} = {len(nsm_hit)/len(nsm):.1%}")
        if core:
            print(f"    Core words: {sorted(core)}")


# ─── D. In-degree hubs ───────────────────────────────────────────────────────
def analysis_D(data: dict) -> None:
    print("\n" + "=" * 70)
    print("D. Top-20 in-degree hubs per model (most cited in definitions)")
    print("=" * 70)
    print(f"{'word':20}" + "".join(f"{short(m):>10}" for m in MODELS) + f"{'wordnet':>10}")
    print("-" * 80)

    # Collect top hubs across all models
    all_hubs: set[str] = set()
    hub_scores: dict[str, dict] = {}

    for model_id in MODELS:
        s = short(model_id)
        G = data[s]["G"]
        top = sorted(G.nodes(), key=lambda n: G.in_degree(n), reverse=True)[:20]
        all_hubs.update(top)
        hub_scores[s] = {n: G.in_degree(n) for n in G.nodes()}

    wn_G = data["wordnet"]["G"]
    hub_scores["wordnet"] = {n: wn_G.in_degree(n) for n in wn_G.nodes()}

    # Show top 25 words by sum of in-degrees
    total_score = Counter()
    for w in all_hubs:
        total_score[w] = sum(hub_scores[s].get(w, 0) for s in hub_scores)

    for word, _ in total_score.most_common(25):
        row = f"{word:20}"
        for model_id in MODELS:
            s = short(model_id)
            row += f"{hub_scores[s].get(word, 0):>10}"
        row += f"{hub_scores['wordnet'].get(word, 0):>10}"
        print(row)


# ─── E. Vocabulary diversity ─────────────────────────────────────────────────
def analysis_E(data: dict, vocab: set) -> None:
    print("\n" + "=" * 70)
    print("E. Vocabulary diversity in definitions")
    print("=" * 70)
    print(f"{'model':32} {'unique_def_words':>16} {'total_tokens':>13} {'TTR':>6} {'OOV_rate':>9}")
    print("-" * 80)

    for model_id in MODELS:
        s = short(model_id)
        defs = data[s]["defs"]
        valid = [d for d in defs if d.get("status") in ("ok", "self_referential")]
        all_tokens: list[str] = []
        for d in valid:
            tokens = [t.lower() for t in d["definition"].split()
                      if t.isalpha()]
            all_tokens.extend(tokens)
        if not all_tokens:
            continue
        unique = set(all_tokens)
        ttr = len(unique) / len(all_tokens)
        oov = sum(1 for t in unique if t not in vocab) / len(unique)
        print(f"  {s:30} {len(unique):>16,} {len(all_tokens):>13,} {ttr:>6.3f} {oov:>9.1%}")


# ─── F. Monotone metrics ──────────────────────────────────────────────────────
def analysis_F() -> None:
    print("\n" + "=" * 70)
    print("F. Monotone metric summary (model size vs. graph structure)")
    print("=" * 70)
    print(f"{'model':32} {'size_B':>7} {'kernel%':>8} {'minset':>7} {'mset/k%':>8} {'circ%':>7} {'out_deg':>8}")
    print("-" * 80)
    sizes = {"0.8B-MLX-bf16": 0.8, "2B-bf16": 2.0, "4B-MLX-bf16": 4.0,
             "9B-bf16": 9.0, "27B-bf16": 27.0}
    for fname in sorted(Path("results/metrics").glob("Qwen3.5-*_42.json")):
        m = json.load(open(fname))
        s = fname.stem.replace("Qwen3.5-", "").replace("_42", "")
        sz = sizes.get(s, "?")
        ks = m.get("kernel_size", 0) or 1
        ms = m.get("minset_size") or 0
        print(f"  {s:30} {sz:>7} {m.get('kernel_ratio',0)*100:>8.1f} "
              f"{ms:>7} {ms/ks*100:>8.1f} "
              f"{m.get('circulation_rate',0)*100:>7.1f} "
              f"{m.get('mean_out_degree',0):>8.2f}")
    wn = json.load(open("results/metrics/wordnet_42.json"))
    ks = wn.get("kernel_size", 0) or 1
    ms = wn.get("minset_size") or 0
    print(f"  {'wordnet':30} {'---':>7} {wn.get('kernel_ratio',0)*100:>8.1f} "
          f"{ms:>7} {ms/ks*100:>8.1f} "
          f"{wn.get('circulation_rate',0)*100:>7.1f} "
          f"{wn.get('mean_out_degree',0):>8.2f}")


if __name__ == "__main__":
    print("Loading graphs...")
    data, vocab = load_all()

    analysis_F()
    analysis_A(data)
    analysis_B(data)
    analysis_C(data)
    analysis_D(data)
    analysis_E(data, vocab)

    print("\nDone.")
