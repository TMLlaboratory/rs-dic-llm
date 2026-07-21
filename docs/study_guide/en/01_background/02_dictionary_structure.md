# Dictionary Graph Intuition

**Time**: 45 min | **Prerequisites**: `01_graph_theory.md`

---

## What Happens When You Read a Dictionary

Look up "cat": "a furry four-legged animal."
Look up "animal": "a living organism."
Look up "living": "having life" ...

The chain of definitions always closes somewhere — or circles back. We capture this as a **directed graph**.

---

## Edge Direction Convention (CRITICAL)

```
"cat" is defined using "animal"
    → add_edge("animal", "cat")   # animal defines cat
    → direction:  animal ──→ cat
```

> **Why `animal → cat`?** The edge means "animal is USED TO DEFINE cat."
> **Not** the reverse.

```python
# "cat's definition contains 'animal'"
G.add_edge("animal", "cat")   # u=animal (defining word), v=cat (defined word)
```

---

## Kernel Intuition

A node with **out-degree 0** is a word that appears in nobody's definition — it plays no definitional role and can be removed without affecting the closure of the remaining vocabulary.

Repeat this removal until nothing can be removed: **the Kernel remains**.

```
vocab: {cat, animal, fur, big, run, jump}
definitions:
  cat  → needs animal, fur
  animal → needs big
  fur, big → no definitions (or empty after filtering)
  run → needs jump
  jump → needs run

Step 1: fur, big have out-degree 0 → remove
Step 2: animal has out-degree 0 (big removed) → remove
        cat has out-degree 0 (animal, fur removed) → remove
Step 3: run, jump point to each other → remain

Kernel = {run, jump}
```

---

## Sanity Check: 3-Node Chain

```python
G.add_edge("B", "A")   # "A" is defined using "B"
G.add_edge("C", "B")   # "B" is defined using "C"

# A has out-degree 0 → removed first
# B has out-degree 0 after A is gone → removed
# C has out-degree 0 after B is gone → removed
Kernel = {}  (empty — no cycles, so nothing is self-sufficient)
```

Human dictionaries retain ~10% in the kernel despite having cycles.

---

## Human Dictionary Benchmarks (Vincent-Lamarre et al., 2016)

| Metric | Longman | Cambridge | Webster | WordNet |
|---|---|---|---|---|
| Kernel rate | ~10% | ~10% | ~8% | ~15% |
| Core/Kernel | ~75% | ~70% | ~65% | ~90% |
| MinSet rate | ~1% | ~1% | ~1% | ~1% |

These are the **reference values** for this research.

---

Next: `03_llm_basics.md`
