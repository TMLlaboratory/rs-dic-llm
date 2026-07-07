# Directed Graphs and Strongly Connected Components

**Time**: 60 min | **Prerequisites**: none

---

## What is a Graph?

A graph is a collection of **nodes** and **edges**. When edges have direction, it is a **directed graph** (digraph).

```
A ──→ B ──→ C
↑           │
└───────────┘

Nodes: {A, B, C}
Edges: A→B, B→C, C→A  (a cycle!)
```

In this research, **words** are nodes and **"x appears in y's definition"** is an edge.

---

## Degree

- **Out-degree**: number of edges leaving a node
- **In-degree**: number of edges entering a node

```python
import networkx as nx
G = nx.DiGraph()
G.add_edge("B", "A")   # B → A
G.add_edge("C", "A")   # C → A

print(G.out_degree("A"))   # → 0  (no edges leave A)
print(G.in_degree("A"))    # → 2  (B and C point to A)
```

> **Critical for this research**: the Kernel is computed by removing nodes with **out-degree = 0**. Do not confuse with in-degree!

---

## Strongly Connected Components (SCCs)

An SCC is a maximal set of nodes where **every node is reachable from every other**.

```
A ──→ B
↑     │
└─────┘
{A, B} is one SCC (you can go A→B→A)

A ──→ B ──→ C
Each of A, B, C is its own SCC (can't get back from C to A)
```

```python
sccs = list(nx.strongly_connected_components(G))
cyclic_nodes = {n for scc in sccs if len(scc) >= 2 for n in scc}
circulation_rate = len(cyclic_nodes) / G.number_of_nodes()
```

---

## Condensation Graph

Collapse each SCC into a single node → the result is always a **DAG** (directed acyclic graph). This is the **condensation**.

```
SCC_1 ──→ SCC_2 ──→ SCC_3
```

In the condensation:
- **Source SCC** (in-degree = 0): no edges come in from other SCCs
- **Sink SCC** (out-degree = 0): no edges go out to other SCCs

This research defines **Core = union of Source SCCs** in the Kernel's condensation.

---

## Feedback Vertex Set (FVS)

The **Minimum Feedback Vertex Set (MFVS)** is the smallest set of nodes whose removal makes the graph acyclic (breaks all cycles).

```
A → B → C → A   (one cycle)
FVS = {A}  (or {B} or {C} — any one suffices)
```

Finding the minimum FVS is **NP-complete**. We use Integer Linear Programming (ILP) to solve it exactly.

---

## Summary Table

| Concept | Definition |
|---|---|
| Out-degree 0 | Node that appears in no surviving definition |
| SCC | Maximally mutually-reachable node set |
| Source SCC | SCC with in-degree 0 in the condensation |
| FVS (MinSet) | Minimum node set that breaks all cycles |

---

Next: `02_dictionary_structure.md`
