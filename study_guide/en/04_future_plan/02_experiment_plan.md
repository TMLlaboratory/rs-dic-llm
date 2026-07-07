# Experiment Plan

**Time**: 30 min

---

## Top Priority: Increase n

| # | Experiment | Example models | Expected gain |
|---|---|---|---|
| A | Llama-4 family | Scout-17B, Maverick-17B | n+2, different family |
| B | Phi-4 family | 3.8B, 14B | n+2, Microsoft |
| C | Qwen3.5-72B | 72B (4-bit) | Qwen3.5 n=6, extended scale |
| D | Gemma-3 | 2B, 12B, 27B | Gemma family expansion |

Target: **n ≥ 15**, multiple families × multiple scales

---

## Task Table

| Task | Assignee | Deadline | Status | Effort |
|---|---|---|---|---|
| Re-run Qwen3.5×5 with seeds 123, 456 | Jose | 2026-06-01 | Not started | ~24h (automated) |
| Check mlx availability of Llama-4 Scout | Jose | 2026-05-25 | Not started | 2h |
| Implement few-shot prompt | Jose | 2026-06-07 | Not started | 4h |
| Run Qwen3.5-4B with few-shot (sr_rate control) | Jose | 2026-06-14 | Not started | 8h |
| Update paper Results section | Kumoi | 2026-06-30 | — | — |

---

## Code: Multi-Seed Run

```python
# experiments/run_multiseed.py
import subprocess

SEEDS = [42, 123, 456]
for seed in SEEDS:
    if seed == 42:
        continue   # skip existing data
    cmd = f"uv run python -m experiments.run_full --seed {seed}"
    subprocess.run(cmd.split(), check=True)
```

---

## Code: Few-Shot Prompt Skeleton

```python
FEW_SHOT_EXAMPLES = [
    ("noun", "table",
     "a flat surface supported by legs, used for placing objects on."),
    ("verb", "run",
     "to move quickly on foot by taking rapid steps."),
    ("adjective", "large",
     "greater than average in size, quantity, or extent."),
]

def make_few_shot_prompt(pos: str, word: str) -> str:
    examples = "\n".join(
        f'Define the {p} "{w}": {d}'
        for p, w, d in FEW_SHOT_EXAMPLES
    )
    return f"{examples}\nDefine the {pos} \"{word}\":"
```

---

## Learning Completion Checklist

- [ ] Can explain SCC and FVS from memory
- [ ] Verified that Kernel uses out-degree=0 removal (not in-degree) with code
- [ ] Read Vincent-Lamarre et al. (2016): arXiv:1411.0129
- [ ] Successfully ran `experiments/run_full.py` and generated data
- [ ] Ran `experiments/analyse_confound.py` and interpreted output
- [ ] Implemented partial correlation and confirmed Δr = +0.034
- [ ] Read the English paper draft: `docs/paper_en.md`
- [ ] Started at least one future experiment (multi-seed or few-shot)

---

Study guide complete. For questions, refer to Prof. Kumoi or `docs/paper_en.md`.
