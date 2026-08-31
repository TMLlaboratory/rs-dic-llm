"""Kernel and Core computation following Vincent-Lamarre et al. 2016.

Edge convention (origin-paper):
    add_edge(u, v)  means  u APPEARS IN the definition of v
    i.e. u --defines--> v

Kernel  = iteratively remove nodes with out-degree == 0
          ("words that define nothing"; Blondin Massé 2008, Algorithm 2)
Core    = union of Sources in the condensation of Kernel
          where Source == SCC with in-degree 0 in the condensation DAG
          (NOT necessarily the single largest SCC; VL 2016 §3.2)
"""

import networkx as nx


def compute_kernel(G: nx.DiGraph) -> set:
    """Return the Kernel of G (Vincent-Lamarre 2016, §2).

    Iteratively removes nodes whose out-degree is zero — words that never
    appear in any other word's definition and therefore contribute nothing
    to the definitional network.  The result is unique regardless of
    removal order (Blondin Massé 2008, Prop. 4).
    """
    H = G.copy()
    while True:
        leaves = [n for n in H if H.out_degree(n) == 0]
        if not leaves:
            break
        H.remove_nodes_from(leaves)
    return set(H.nodes())


def compute_core(G: nx.DiGraph, kernel: set | None = None) -> set:
    """Return the Core of G (Vincent-Lamarre 2016, §3).

    Core = union of all Source SCCs in the condensation of the Kernel,
    where a Source SCC has in-degree 0 in the condensation DAG.

    If kernel is None, compute_kernel(G) is called first.
    """
    if kernel is None:
        kernel = compute_kernel(G)
    K = G.subgraph(kernel).copy()
    C = nx.condensation(K)
    source_sccs = {n for n in C.nodes() if C.in_degree(n) == 0}
    core: set = set()
    for scc_id in source_sccs:
        core.update(C.nodes[scc_id]["members"])
    return core
