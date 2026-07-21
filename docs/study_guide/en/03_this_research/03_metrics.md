# Metrics: Kernel / Core / MinSet / sr_rate

**Time**: 60 min

---

## Metrics at a Glance

| Metric | Symbol | Meaning |
|---|---|---|
| Kernel ratio | kern% | Fraction of vocabulary in the self-sufficient core |
| MinSet/Kernel | mset/k% | Fraction of kernel that is irreducibly cyclic |
| Circulation rate | circ% | Fraction of nodes in SCCs of size ≥ 2 |
| Mean out-degree | out_deg | Average definitional usage per word |
| Self-referential rate | sr_rate | Fraction of definitions containing the target word |

---

## Kernel (code)

```python
def compute_kernel(G: nx.DiGraph) -> set:
    H = G.copy()
    while True:
        leaves = [n for n in H if H.out_degree(n) == 0]
        if not leaves:
            break
        H.remove_nodes_from(leaves)
    return set(H.nodes())
```

**Results (kernel ratio by model):**

| Model | Params | kern% |
|---|---|---|
| Qwen3.5-0.8B | 0.8B | **17.9** |
| Qwen3.5-2B | 2B | 11.1 |
| Qwen3.5-4B | 4B | 10.8 |
| Qwen3.5-9B | 9B | 10.1 |
| Qwen3.5-27B | 27B | **8.6** |
| Gemma-4-4B | 4B | 7.3 |
| WordNet | — | 15.5 |

Monotone decrease with scale: r = −0.862 within Qwen3.5.

---

## MinSet (ILP)

```python
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, HiGHS

def compute_minset(G):
    nodes = list(G.nodes())
    prob = LpProblem("MFVS", LpMinimize)
    x = {n: LpVariable(f"x_{i}", cat="Binary") for i, n in enumerate(nodes)}
    prob += lpSum(x[n] for n in nodes)
    for cycle in find_short_cycles(G):
        prob += lpSum(x[n] for n in cycle) >= 1
    HiGHS(msg=False).solve(prob)
    return {n for n in nodes if value(x[n]) > 0.5}
```

> **Apple Silicon note**: CBC solver does not work on M4 Max (x86_64 binary). Use **HiGHS** solver.

**mset/k results:**

| Model | mset/k% |
|---|---|
| Qwen3.5-0.8B | 14.4 |
| Qwen3.5-27B | 20.3 |
| Gemma-4-4B | **23.3** |

Monotone increase with scale: r = +0.982 within Qwen3.5.

---

## Universal Kernel: 92 Words

```python
from collections import Counter
counter = Counter()
for kernel in all_kernels.values():
    counter.update(kernel)
universal = {w for w, c in counter.items() if c == 5}  # all 5 Qwen3.5 models
# → 92 words
```

Sample: go, hold, move, use, feel, allow, build, different, flat, high, small, idea, image, true, future, energy, body, people, place, time, touch, two, like...

NSM overlap: body, feel, like, people, place, small, time, touch, true, two (10/65 = 15.4%)

These 92 words persist across a 34× parameter range — determined by English lexical structure, not LLM scale.

---

Next: `04_results.md`
