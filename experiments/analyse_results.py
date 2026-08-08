"""Deep analysis of full experiment results.

Reads from results/full_summary.json (written by run_experiment.py).
Run run_experiment.py first.

Analyses:
  A. Kernel Jaccard similarity across model pairs
  B. Stable / model-specific Kernel words
  C. Core word content + NSM overlap
  D. In-degree hubs (most-cited words in definitions)
  E. Vocabulary diversity (unique defining words per model)
  F. Monotone metric summary (kernel_ratio, minset/kernel vs model size)
"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rs_dic_llm.config import MODEL_REGISTRY, MODEL_DISPLAY
from rs_dic_llm.sampling import load_word_list
from rs_dic_llm.generation import load_definitions
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.metrics.kernel_core import compute_kernel, compute_core
from rs_dic_llm.wordnet_baseline import build_wordnet_graph

SEED = 42
SUMMARY_PATH = "results/full_summary.json"
NSM_PATH = "data/nsm_primes_65.json"


def _short(display: str) -> str:
    return display.replace("Qwen2.5-", "Q2.5-").replace("Qwen3.5-", "Q3.5-").replace("Gemma3-", "G3-")


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def load_all() -> tuple[dict, set]:
    """Load graphs, kernels, cores for all models in the experiment summary."""
    if not Path(SUMMARY_PATH).exists():
        print(f"ERROR: {SUMMARY_PATH} not found. Run run_experiment.py first.")
        sys.exit(1)

    summary = json.loads(Path(SUMMARY_PATH).read_text())
    words = load_word_list("data/sample_words/word_list_3k_v1.json")
    vocab = {w["lemma"] for w in words}

    data: dict[str, dict] = {}
    for m in summary.get("models", []):
        display = m.get("display", m.get("model", "?"))
        def_path = f"data/definitions/{display}_{SEED}.jsonl"
        if not Path(def_path).exists():
            print(f"  [skip] {display}: definition file missing ({def_path})")
            continue
        defs   = load_definitions(def_path)
        G      = build_graph(defs)
        kernel = compute_kernel(G)
        core   = compute_core(G, kernel)
        data[display] = {
            "G": G, "kernel": kernel, "core": core, "defs": defs,
            "param_b": m.get("param_b"), "family": m.get("family"),
        }
        print(f"  loaded {_short(display)}: kernel={len(kernel)}, core={len(core)}")

    # WordNet baseline
    wn_G, _ = build_wordnet_graph(words)
    wn_kernel = compute_kernel(wn_G)
    wn_core   = compute_core(wn_G, wn_kernel)
    data["wordnet"] = {
        "G": wn_G, "kernel": wn_kernel, "core": wn_core, "defs": None,
        "param_b": None, "family": "wordnet",
    }
    print(f"  loaded wordnet: kernel={len(wn_kernel)}, core={len(wn_core)}")
    return data, vocab


# ─── A. Kernel Jaccard ────────────────────────────────────────────────────────
def analysis_A(data: dict) -> None:
    print("\n" + "=" * 70)
    print("A. Kernel Jaccard similarity (rows × cols)")
    print("=" * 70)
    keys = list(data.keys())
    labels = [_short(k) for k in keys]
    header = f"{'':18}" + "".join(f"{l:>12}" for l in labels)
    print(header)
    for ki, li in zip(keys, labels):
        row = f"{li:18}"
        for kj in keys:
            j = jaccard(data[ki]["kernel"], data[kj]["kernel"])
            row += f"{j:>12.3f}"
        print(row)


# ─── B. Kernel stability ──────────────────────────────────────────────────────
def analysis_B(data: dict) -> None:
    print("\n" + "=" * 70)
    print("B. Kernel word stability across LLM models")
    print("=" * 70)
    llm_keys = [k for k in data if k != "wordnet"]
    n_llm = len(llm_keys)
    kernels = [data[k]["kernel"] for k in llm_keys]
    in_wn_kernel = data["wordnet"]["kernel"]

    counter: Counter = Counter()
    for k in kernels:
        counter.update(k)

    in_all = {w for w, c in counter.items() if c == n_llm}
    print(f"Words in ALL {n_llm} LLM kernels     : {len(in_all)}")
    print(f"  ∩ WordNet kernel               : {len(in_all & in_wn_kernel)}")
    if in_all:
        print(f"  Sample: {sorted(in_all)[:30]}")

    print(f"\nDistribution (in N of {n_llm} models):")
    for n in range(n_llm, 0, -1):
        words_n = {w for w, c in counter.items() if c == n}
        overlap_wn = words_n & in_wn_kernel
        print(f"  N={n}: {len(words_n):4d} words  (∩ WordNet kernel: {len(overlap_wn)})")

    print(f"\nTop 20 words by frequency in LLM kernels:")
    for word, cnt in counter.most_common(20):
        wn_flag = "✓WN" if word in in_wn_kernel else "   "
        print(f"  {cnt}/{n_llm}  {wn_flag}  {word}")


# ─── C. Core content + NSM ───────────────────────────────────────────────────
def analysis_C(data: dict) -> None:
    print("\n" + "=" * 70)
    print("C. Core word content + NSM overlap")
    print("=" * 70)
    nsm = set(json.load(open(NSM_PATH))) if Path(NSM_PATH).exists() else set()

    for key, d in sorted(data.items(), key=lambda x: (x[1].get("family",""), x[0])):
        core = d["core"]
        nsm_hit = core & nsm
        print(f"\n  {_short(key)} (core={len(core)}):")
        print(f"    NSM overlap: {len(nsm_hit)}/{len(nsm)} = {len(nsm_hit)/len(nsm):.1%}")
        if core:
            print(f"    Core words: {sorted(core)[:20]}" +
                  ("..." if len(core) > 20 else ""))


# ─── D. In-degree hubs ───────────────────────────────────────────────────────
def analysis_D(data: dict) -> None:
    print("\n" + "=" * 70)
    print("D. Top-25 in-degree hubs (most cited in definitions)")
    print("=" * 70)
    llm_keys = [k for k in data if k != "wordnet"]
    labels = [_short(k) for k in llm_keys]
    header = f"{'word':20}" + "".join(f"{l:>10}" for l in labels) + f"{'wordnet':>10}"
    print(header)
    print("-" * (20 + 10 * len(llm_keys) + 10))

    hub_scores: dict[str, dict] = {}
    all_hubs: set[str] = set()

    for key in llm_keys:
        G = data[key]["G"]
        top = sorted(G.nodes(), key=lambda n: G.in_degree(n), reverse=True)[:20]
        all_hubs.update(top)
        hub_scores[key] = {n: G.in_degree(n) for n in G.nodes()}

    wn_G = data["wordnet"]["G"]
    hub_scores["wordnet"] = {n: wn_G.in_degree(n) for n in wn_G.nodes()}

    total_score: Counter = Counter()
    for w in all_hubs:
        total_score[w] = sum(hub_scores[k].get(w, 0) for k in hub_scores)

    for word, _ in total_score.most_common(25):
        row = f"{word:20}"
        for key in llm_keys:
            row += f"{hub_scores[key].get(word, 0):>10}"
        row += f"{hub_scores['wordnet'].get(word, 0):>10}"
        print(row)


# ─── E. Vocabulary diversity ─────────────────────────────────────────────────
def analysis_E(data: dict, vocab: set) -> None:
    print("\n" + "=" * 70)
    print("E. Vocabulary diversity in definitions")
    print("=" * 70)
    print(f"{'model':24} {'unique_def_words':>16} {'total_tokens':>13} {'TTR':>6} {'OOV_rate':>9}")
    print("-" * 80)

    for key in sorted(data.keys()):
        if data[key]["defs"] is None:
            continue
        defs = data[key]["defs"]
        valid = [d for d in defs if d.get("status") in ("ok", "self_referential")]
        all_tokens: list[str] = []
        for d in valid:
            all_tokens.extend(t.lower() for t in d["definition"].split() if t.isalpha())
        if not all_tokens:
            continue
        unique = set(all_tokens)
        ttr = len(unique) / len(all_tokens)
        oov = sum(1 for t in unique if t not in vocab) / len(unique)
        print(f"  {_short(key):22} {len(unique):>16,} {len(all_tokens):>13,} {ttr:>6.3f} {oov:>9.1%}")


# ─── F. Monotone metrics ──────────────────────────────────────────────────────
def analysis_F(data: dict) -> None:
    print("\n" + "=" * 70)
    print("F. Monotone metric summary (model size vs. graph structure)")
    print("=" * 70)
    print(f"{'model':24} {'family':8} {'B':>6} {'kern%':>7} {'mset':>6} {'mset/k%':>8} {'circ%':>7} {'out_deg':>8}")
    print("-" * 80)

    if not Path(SUMMARY_PATH).exists():
        return
    summary = json.loads(Path(SUMMARY_PATH).read_text())
    model_rows = sorted(
        summary.get("models", []),
        key=lambda m: (m.get("family", ""), m.get("param_b", 0)),
    )
    for m in model_rows:
        display = m.get("display", m.get("model", "?"))
        ks = m.get("kernel_size", 0) or 1
        ms = m.get("minset_size") or 0
        print(f"  {_short(display):22} {m.get('family','?'):8} {m.get('param_b',0):>6.1f} "
              f"{m.get('kernel_ratio',0)*100:>7.1f} "
              f"{ms:>6} {ms/ks*100:>8.1f} "
              f"{m.get('circulation_rate',0)*100:>7.1f} "
              f"{m.get('mean_out_degree',0):>8.2f}")

    wn = summary.get("wordnet", {})
    if wn:
        ks = wn.get("kernel_size", 0) or 1
        ms = wn.get("minset_size") or 0
        print(f"  {'wordnet':22} {'---':8} {'---':>6} "
              f"{wn.get('kernel_ratio',0)*100:>7.1f} "
              f"{ms:>6} {ms/ks*100:>8.1f} "
              f"{wn.get('circulation_rate',0)*100:>7.1f} "
              f"{wn.get('mean_out_degree',0):>8.2f}")


if __name__ == "__main__":
    print("Loading graphs...")
    data, vocab = load_all()

    analysis_F(data)
    analysis_A(data)
    analysis_B(data)
    analysis_C(data)
    analysis_D(data)
    analysis_E(data, vocab)
    print("\nDone.")
