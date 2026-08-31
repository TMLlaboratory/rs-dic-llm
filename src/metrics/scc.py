"""SCC analysis and cycle-length distribution."""

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
