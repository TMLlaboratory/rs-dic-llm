"""Unit tests for Kernel and Core — pins the correct edge direction.

Graph convention:
    add_edge(u, v)  means  u appears in definition of v  (u defines v)

Three-node chain:  A  -->  B  -->  C
  A appears in definition of B (A defines B)
  B appears in definition of C (B defines C)
  A out-degree=2 ... wait: A-->B, B-->C, so:
    out_degree: A=1, B=1, C=0   => correct Kernel removes C first, then B(??)

Actually let's reason carefully:
  out_degree(A)=1 (A defines B)
  out_degree(B)=1 (B defines C)
  out_degree(C)=0 (C defines nothing)

Iteration 1: remove C (out-degree 0)
  => graph: A-->B
Iteration 2: remove B (out-degree 0 after C gone)... wait B still has out-degree 1 to nothing
  after C is removed, out_degree(B)=0 => remove B
  => graph: A
Iteration 3: out_degree(A)=0 => remove A
  => empty

That gives Kernel = {} for a simple chain. Let me rethink.

For a chain to have a non-empty kernel we need a cycle.
Example with a cycle + tail:

  D --> A --> B --> A (cycle: A<-->B, D is a tail)

In this graph:
  edges: D->A, A->B, B->A
  out_degree: D=1, A=1, B=1  => no node has out_degree=0
  => Kernel = {D, A, B}

But wait, D defines A, A defines B, B defines A.
D is defined by nothing (no one defines D), but D appears in nothing's definition
  in_degree(D)=0, out_degree(D)=1.
After the kernel algorithm, since no node has out_degree=0, Kernel = {D, A, B}.

Actually let me use the standard VL2016 example more carefully.
The key test is: does out_degree=0 node get removed (correct) vs in_degree=0 (buggy).

Let's use this graph:
  Nodes: "fast", "speed", "moving"
  "fast" appears in def of "speed": fast --> speed
  "speed" appears in def of "moving": speed --> moving
  "moving" appears in def of "fast": moving --> fast
  So: fast-->speed, speed-->moving, moving-->fast  (a 3-cycle)
  Plus an extra node "quickly" whose definition uses "fast": fast --> quickly
  wait, that means fast appears in def of quickly: add_edge("fast","quickly")

Graph:
  fast --> speed    (fast appears in def of speed)
  speed --> moving  (speed appears in def of moving)
  moving --> fast   (moving appears in def of fast)
  fast --> quickly  (fast appears in def of quickly)

out_degree: fast=2(speed,quickly), speed=1, moving=1, quickly=0

Iteration 1: remove "quickly" (out_degree=0)
  => out_degree: fast=1(speed), speed=1, moving=1
Iteration 2: no node has out_degree=0
  => Kernel = {fast, speed, moving}

Core: condensation of Kernel = {fast,speed,moving} which is one SCC (all in cycle)
  => condensation has 1 node with in_degree=0 => Core = {fast, speed, moving}

Buggy version (remove in_degree=0 nodes):
  in_degree: fast=1(moving), speed=1(fast), moving=1(speed), quickly=1(fast)
  => no node has in_degree=0 => buggy Kernel = {fast, speed, moving, quickly}
  (quickly would NOT be removed!)

That's a good demonstration. Let me code this.
"""

import networkx as nx
import pytest

from rs_dic_llm.metrics.kernel_core import compute_kernel, compute_core


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _chain_graph() -> nx.DiGraph:
    """Simple chain: A --defines--> B --defines--> C.

    No cycles, so every node eventually gets removed.
    Correct (out-degree=0):  Kernel = {}
    Buggy  (in-degree=0):   would try to remove A first (in_degree=0),
                             leaving B->C, then remove B, leaving C alone => {C}
    """
    G = nx.DiGraph()
    G.add_edges_from([("A", "B"), ("B", "C")])
    return G


def _cycle_plus_tail() -> nx.DiGraph:
    """Cycle {fast, speed, moving} plus peripheral node 'quickly'.

    Edges (u defines v  =>  add_edge(u, v)):
        fast   --> speed
        speed  --> moving
        moving --> fast
        fast   --> quickly   ('fast' appears in def of 'quickly')

    out_degree:  fast=2, speed=1, moving=1, quickly=0
    in_degree:   fast=1, speed=1, moving=1, quickly=1

    Correct Kernel (out-degree=0 removed):
        Step 1: remove 'quickly' (out_degree=0)
        Step 2: no more out_degree=0 nodes => Kernel = {fast, speed, moving}

    Buggy Kernel (in-degree=0 removed):
        No node has in_degree=0 => nothing is removed => Kernel = all four nodes
        (quickly is wrongly kept)
    """
    G = nx.DiGraph()
    G.add_edges_from([
        ("fast", "speed"),
        ("speed", "moving"),
        ("moving", "fast"),
        ("fast", "quickly"),
    ])
    return G


def _isolated_node() -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_node("alone")
    return G


def _self_loop() -> nx.DiGraph:
    """Node 'x' has only a self-loop: x --> x."""
    G = nx.DiGraph()
    G.add_edge("x", "x")
    return G


# ---------------------------------------------------------------------------
# Kernel tests
# ---------------------------------------------------------------------------

class TestComputeKernel:

    def test_chain_kernel_is_empty(self):
        """Pure chain has no self-sustaining definitional core."""
        assert compute_kernel(_chain_graph()) == set()

    def test_cycle_plus_tail_kernel(self):
        """Only the cycle survives; 'quickly' (out_degree=0) is stripped."""
        expected = {"fast", "speed", "moving"}
        assert compute_kernel(_cycle_plus_tail()) == expected

    def test_cycle_plus_tail_buggy_would_differ(self):
        """Demonstrate that in-degree=0 removal gives a WRONG result.

        This is the bug in 20260512_ぺぺ.md.  The buggy version keeps
        'quickly' in the Kernel because it has in_degree=1 (not 0), so the
        in-degree algorithm never removes it.
        """
        G = _cycle_plus_tail()
        # Simulate the buggy algorithm (remove in-degree=0 nodes)
        def compute_kernel_buggy(g: nx.DiGraph) -> set:
            H = g.copy()
            while True:
                leaves = [n for n in H if H.in_degree(n) == 0]
                if not leaves:
                    break
                H.remove_nodes_from(leaves)
            return set(H.nodes())

        correct = compute_kernel(G)
        buggy = compute_kernel_buggy(G)
        assert "quickly" not in correct, "correct Kernel must not contain 'quickly'"
        assert "quickly" in buggy, "buggy Kernel wrongly retains 'quickly'"
        assert correct != buggy, "correct and buggy algorithms must diverge"

    def test_isolated_node_kernel_is_empty(self):
        """A single node with no edges has out_degree=0 and is removed."""
        assert compute_kernel(_isolated_node()) == set()

    def test_self_loop_kernel_contains_node(self):
        """A self-loop gives out_degree=1, so the node is never removed."""
        assert compute_kernel(_self_loop()) == {"x"}

    def test_empty_graph(self):
        assert compute_kernel(nx.DiGraph()) == set()

    def test_kernel_subset_of_nodes(self):
        G = _cycle_plus_tail()
        kernel = compute_kernel(G)
        assert kernel.issubset(set(G.nodes()))

    def test_kernel_is_unique(self):
        """Result is deterministic across multiple calls (order-independent)."""
        G = _cycle_plus_tail()
        assert compute_kernel(G) == compute_kernel(G)


# ---------------------------------------------------------------------------
# Core tests
# ---------------------------------------------------------------------------

class TestComputeCore:

    def test_core_subset_of_kernel(self):
        G = _cycle_plus_tail()
        kernel = compute_kernel(G)
        core = compute_core(G, kernel)
        assert core.issubset(kernel)

    def test_core_of_single_cycle(self):
        """A single cycle is its own Core."""
        G = nx.DiGraph()
        G.add_edges_from([("A", "B"), ("B", "C"), ("C", "A")])
        kernel = compute_kernel(G)
        assert kernel == {"A", "B", "C"}
        core = compute_core(G, kernel)
        assert core == {"A", "B", "C"}

    def test_core_excludes_satellite(self):
        """Satellite SCCs (non-Source in condensation) must not be in Core."""
        # Build: cycle1 {A,B} and cycle2 {C,D}, with A --> C
        # condensation: SCC{A,B} -> SCC{C,D}
        # Source (in_degree=0 in condensation) = SCC{A,B} only
        G = nx.DiGraph()
        G.add_edges_from([("A", "B"), ("B", "A"),   # cycle1
                          ("C", "D"), ("D", "C"),   # cycle2
                          ("A", "C")])              # bridge
        kernel = compute_kernel(G)
        assert kernel == {"A", "B", "C", "D"}
        core = compute_core(G, kernel)
        assert "A" in core and "B" in core
        assert "C" not in core and "D" not in core

    def test_core_accepts_none_kernel(self):
        """compute_core computes kernel internally when not provided."""
        G = _cycle_plus_tail()
        core_explicit = compute_core(G, compute_kernel(G))
        core_implicit = compute_core(G)
        assert core_explicit == core_implicit
