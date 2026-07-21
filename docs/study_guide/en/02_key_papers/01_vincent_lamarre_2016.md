# Key Paper: Vincent-Lamarre et al. (2016)

**Time**: 90 min | **Prerequisites**: all of `01_background/`

---

## Citation

> Vincent-Lamarre, P., Blondin Massé, A., Lepage, M., Lord, M., Harnad, S., & Marcotte, O. (2016).  
> **The latent structure of dictionaries.**  
> *Topics in Cognitive Science*, 8(3), 625–659.  
> arXiv:1411.0129 — https://arxiv.org/abs/1411.0129

---

## Problem the Paper Solved

Every word in a dictionary is defined using other words. Definitions eventually cycle. The paper asks: **what is the minimum vocabulary that is self-sufficient?** And how does it relate to cognitive primitives?

---

## Four Dictionaries Used

| Dictionary | Abbreviation |
|---|---|
| Longman Dictionary of Contemporary English | LDOCE |
| Cambridge International Dictionary of English | CIDE |
| Webster's Seventh New Collegiate | Webster |
| WordNet | WordNet |

---

## Approach

1. Build directed definition graph for each dictionary
2. Compute **Kernel** (iteratively remove out-degree-0 nodes)
3. Compute **Core** = union of Source SCCs in the Kernel condensation
4. Compute **MinSet** via ILP (CPLEX solver, exact solution)

---

## Key Findings

| Metric | Value |
|---|---|
| Kernel rate | ~10% across 4 dictionaries |
| Core/Kernel | 65–90% (avg ~75%) |
| MinSet/Kernel | ~1% |

**Interpretation**: just 1% of the kernel can break all definitional cycles. Meaning is anchored in a tiny set of primitive concepts.

---

## Common Misconceptions (Check Yourself)

| Item | Wrong | Correct |
|---|---|---|
| Kernel computation | Remove **in-degree** 0 nodes | Remove **out-degree** 0 nodes |
| Core definition | Largest SCC | **Union of Source SCCs** (those with in-degree 0 in condensation) |
| MinSet algorithm | Greedy approximation | **ILP (CPLEX)** — exact, took days |
| Preprocessing | Lemmatization | **Stemming** ("stemmatized") — this research uses lemmatization (noted as limitation) |

### Verify the Kernel Direction with Code

```python
import networkx as nx

def compute_kernel_CORRECT(G):
    H = G.copy()
    while True:
        leaves = [n for n in H if H.out_degree(n) == 0]
        if not leaves: break
        H.remove_nodes_from(leaves)
    return set(H.nodes())

def compute_kernel_BUGGY(G):
    H = G.copy()
    while True:
        leaves = [n for n in H if H.in_degree(n) == 0]  # WRONG
        if not leaves: break
        H.remove_nodes_from(leaves)
    return set(H.nodes())

G = nx.DiGraph()
G.add_edge("B", "A")   # "A" is defined using "B"
G.add_edge("C", "B")   # "B" is defined using "C"

print("Correct:", compute_kernel_CORRECT(G))  # {'C'}
print("Buggy:  ", compute_kernel_BUGGY(G))    # {'A'} ← reversed!
```

---

## Relationship to This Research

| Aspect | Original paper | This research |
|---|---|---|
| Source of definitions | Four human dictionaries | LLM-generated definitions |
| Vocabulary size | Full dictionary (tens of thousands) | 3,000 words |
| Comparison axis | Across dictionaries | Across model sizes and families |
| Baseline | Dictionaries vs each other | WordNet |

---

Next: `02_scaling_laws.md`
