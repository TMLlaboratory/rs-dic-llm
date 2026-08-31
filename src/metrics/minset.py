"""Stage 4: Minimum Feedback Vertex Set (MinSet) via ILP + CBC.

MinSet == minimum FVS  (Blondin Massé 2008, Theorem 7)

Strategy:
  - Decompose into SCCs; only nontrivial SCCs (size >= 2) need FVS computation.
  - For each nontrivial SCC, solve ILP with lazy-constraint cycle enumeration:
      1. Seed constraints from all simple cycles of length <= seed_length.
      2. Solve; check residual graph for remaining cycles.
      3. Add violated constraints, re-solve. Repeat until acyclic.
  - Fallback to greedy if wall-clock time exceeds timeout_s.
"""

import time
from typing import Any

import networkx as nx


def _greedy_fvs(G: nx.DiGraph) -> set:
    """Greedy FVS: repeatedly remove the highest-degree node in a cycle."""
    H = G.copy()
    fvs: set = set()
    while True:
        try:
            cycle = next(nx.simple_cycles(H))
        except StopIteration:
            break
        # pick node with highest total degree within cycle
        node = max(cycle, key=lambda n: H.in_degree(n) + H.out_degree(n))
        fvs.add(node)
        H.remove_node(node)
    return fvs


def _ilp_fvs(G: nx.DiGraph, seed_length: int = 5, timeout_s: float = 1800.0) -> tuple[set, bool]:
    """Solve minimum FVS as ILP using PuLP + CBC.

    Returns (fvs_set, is_optimal).
    Falls back to greedy if timeout is exceeded.
    """
    try:
        import pulp  # noqa: F401
    except ImportError:
        return _greedy_fvs(G), False

    import pulp

    t_start = time.time()
    nodes = list(G.nodes())
    node_idx = {n: i for i, n in enumerate(nodes)}

    prob = pulp.LpProblem("MinFVS", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(len(nodes))]
    prob += pulp.lpSum(x)

    # Seed constraints from short cycles
    added: set[frozenset] = set()

    def _add(cycles: list) -> None:
        """Add cycle-cover constraints to prob in-place (nonlocal write)."""
        nonlocal prob
        for cycle in cycles:
            key = frozenset(cycle)
            if key not in added:
                added.add(key)
                prob += pulp.lpSum(x[node_idx[n]] for n in cycle) >= 1

    seed_cycles = list(nx.simple_cycles(G, length_bound=seed_length))
    _add(seed_cycles)

    while True:
        if time.time() - t_start > timeout_s:
            return _greedy_fvs(G), False

        # Prefer HiGHS Python API (works on Apple Silicon); CBC binary is x86-only
        if pulp.HiGHS(msg=False).available():
            solver = pulp.HiGHS(msg=False, timeLimit=60)
        else:
            solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=60)
        status = prob.solve(solver)
        if status not in (pulp.LpStatusOptimal, 1):
            return _greedy_fvs(G), False

        removed = {nodes[i] for i, v in enumerate(x) if pulp.value(v) > 0.5}
        residual = G.copy()
        residual.remove_nodes_from(removed)

        new_cycles = list(nx.simple_cycles(residual, length_bound=seed_length + 2))
        if not new_cycles:
            try:
                remaining = next(nx.simple_cycles(residual))
                new_cycles = [remaining]
            except StopIteration:
                return removed, True

        _add(new_cycles)


def compute_minset(G: nx.DiGraph, timeout_s: float = 1800.0) -> dict[str, Any]:
    """Compute MinSet for graph G.

    Returns:
        {
            "minset": set of words,
            "size": int,
            "optimal": bool,
            "scc_count": int,
        }
    """
    from .kernel_core import compute_kernel

    kernel = compute_kernel(G)
    K = G.subgraph(kernel).copy()

    minset: set = set()
    optimal = True
    nontrivial_sccs = [
        comp for comp in nx.strongly_connected_components(K) if len(comp) >= 2
    ]

    for scc_nodes in nontrivial_sccs:
        subG = K.subgraph(scc_nodes).copy()
        fvs, is_opt = _ilp_fvs(subG, timeout_s=timeout_s)
        minset.update(fvs)
        if not is_opt:
            optimal = False

    return {
        "minset": minset,
        "size": len(minset),
        "optimal": optimal,
        "scc_count": len(nontrivial_sccs),
    }
