"""Stage 6: Compute all metrics for one graph and return a summary dict."""

import json
from pathlib import Path

import networkx as nx

from .metrics.kernel_core import compute_kernel, compute_core
from .metrics.scc import scc_summary, cycle_length_distribution, reciprocity_excess
from .metrics.minset import compute_minset
from .metrics.nsm import nsm_coverage


def compute_all_metrics(
    G: nx.DiGraph,
    model_id: str,
    run_minset: bool = True,
    nsm_path: str = "data/nsm_primes_65.json",
    minset_timeout_s: float = 1800.0,
) -> dict:
    """Return a flat dict of all graph metrics for one (model, word-set) pair."""
    kernel = compute_kernel(G)
    core = compute_core(G, kernel)
    scc = scc_summary(G)
    cycle_dist = cycle_length_distribution(G)
    R = reciprocity_excess(G)

    n_nodes = G.number_of_nodes() or 1  # avoid division by zero
    kernel_ratio = len(kernel) / n_nodes
    core_kernel_ratio = len(core) / len(kernel) if kernel else 0.0

    minset_result = {"size": None, "optimal": None, "scc_count": None}
    if run_minset:
        minset_result = compute_minset(G, timeout_s=minset_timeout_s)
        minset_result["minset_ratio"] = (
            minset_result["size"] / n_nodes if minset_result["size"] is not None else None
        )

    nsm = nsm_coverage(kernel, core, primitives_path=nsm_path)

    n_edges = G.number_of_edges()
    max_edges = n_nodes * (n_nodes - 1)
    edge_density = n_edges / max_edges if max_edges > 0 else 0.0
    mean_out_degree = n_edges / n_nodes  # = mean in-degree for DiGraph

    return {
        "model": model_id,
        **scc,
        "n_edges": n_edges,
        "edge_density": edge_density,
        "mean_out_degree": mean_out_degree,
        "kernel_size": len(kernel),
        "kernel_ratio": kernel_ratio,
        "core_size": len(core),
        "core_kernel_ratio": core_kernel_ratio,
        "reciprocity_excess": R,
        "cycle_length_dist": cycle_dist,
        "minset_size": minset_result.get("size"),
        "minset_ratio": minset_result.get("minset_ratio"),
        "minset_optimal": minset_result.get("optimal"),
        **{f"nsm_{k}": v for k, v in nsm.items()
           if k not in ("kernel_hit_words", "core_hit_words")},
    }


def save_metrics(metrics: dict, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    # cycle_length_dist has int keys; JSON requires string keys
    m = dict(metrics)
    if "cycle_length_dist" in m and isinstance(m["cycle_length_dist"], dict):
        m["cycle_length_dist"] = {str(k): v for k, v in m["cycle_length_dist"].items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
