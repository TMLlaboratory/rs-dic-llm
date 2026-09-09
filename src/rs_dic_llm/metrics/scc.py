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
    """Compute reciprocity excess R = observed_2cycles / null_expected_2cycles.

    Uses the configuration-model (degree-preserving null) analytical approximation:
        E[mutual_pairs] = (sum_i k_i^out * k_i^in)^2 / E^2   (leading term)

    Observed 2-cycles: pairs (i,j) where both i→j and j→i exist.
    In nx.simple_cycles each mutual pair contributes 2 directed cycles,
    so observed_2cycles = 2 * number_of_mutual_pairs.

    Returns float (1.0 = same as chance, >1 = more reciprocity than null).
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
