"""SCC analysis, cycle-length distribution, and reciprocity excess."""

from collections import Counter

import networkx as nx


def circulation_rate(G: nx.DiGraph) -> float:
    """Fraction of nodes that participate in at least one cycle (SCC size >= 2)."""
    if G.number_of_nodes() == 0:
        return 0.0
    cyclic = sum(
        len(comp) for comp in nx.strongly_connected_components(G) if len(comp) >= 2
    )
    return cyclic / G.number_of_nodes()


def cycle_length_distribution(G: nx.DiGraph, max_length: int = 7) -> dict:
    """Count simple cycles up to max_length; return length -> count mapping.

    Longer cycles are expensive to enumerate, so we cap at max_length.
    """
    counts: Counter = Counter()
    for cycle in nx.simple_cycles(G, length_bound=max_length):
        counts[len(cycle)] += 1
    return dict(sorted(counts.items()))


def reciprocity_excess(G: nx.DiGraph) -> float:
    """Analytic configuration-model estimate of reciprocity excess (R_analytic).

    NOT the R reported in the paper. The paper's R is observed mutual pairs divided by
    their mean over degree-preserving rewirings (experiments/null_model.py,
    experiments/e1_full_null.py). This function is a cheap approximation that disagrees
    with that R by a factor that varies between 0.5 and 2.4 across graphs
    (research/RESEARCH_AUDIT.md F1): a factor 2 is missing (the denominator below counts
    ordered pairs, the numerator unordered pairs), and the leading-order formula
    underestimates the null for graphs with very large hubs. Kept for diagnostics only;
    compute_all_metrics stores it as "R_analytic".

        E[mutual_pairs] ~ ((sum_i k_i^out k_i^in)^2 - sum_i (k_i^out k_i^in)^2) / E^2

    Mutual pairs are counted once per pair (nx.simple_cycles also yields each mutual pair
    as one 2-cycle).

    Returns float (1.0 = same as the approximate null, >1 = more reciprocity).
    """
    E = G.number_of_edges()
    if E <= 1:
        return 0.0

    # Count observed mutual pairs
    n_mutual = sum(1 for u, v in G.edges() if G.has_edge(v, u)) // 2

    # Configuration-model expected mutual pairs (leading term)
    sum_out_in = sum(G.out_degree(n) * G.in_degree(n) for n in G.nodes())
    sum_out_in_sq = sum((G.out_degree(n) * G.in_degree(n)) ** 2 for n in G.nodes())
    E_null_pairs = (sum_out_in ** 2 - sum_out_in_sq) / (E ** 2)

    if E_null_pairs <= 0:
        return float("inf") if n_mutual > 0 else 1.0

    return n_mutual / E_null_pairs


def scc_summary(G: nx.DiGraph) -> dict:
    """Return a dict of SCC statistics for graph G."""
    sccs = list(nx.strongly_connected_components(G))
    sizes = sorted((len(s) for s in sccs), reverse=True)
    nontrivial = [s for s in sizes if s >= 2]
    return {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "n_sccs": len(sccs),
        "largest_scc": sizes[0] if sizes else 0,
        "n_nontrivial_sccs": len(nontrivial),
        "circulation_rate": circulation_rate(G),
    }
