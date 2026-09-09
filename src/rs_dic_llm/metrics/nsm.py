"""NSM (Natural Semantic Metalanguage) coverage metric.

Wierzbicka (1996) proposes ~65 universal semantic primitives.
This module measures how many of those primitives land inside the
Kernel and Core of a definition graph.

The JSON file data/nsm_primes_65.json must be prepared manually from
Wierzbicka (1996) Table 2.1.  Each entry is the canonical English lemma.
"""

import json
from pathlib import Path

_DEFAULT_PATH = "data/nsm_primes_65.json"
_CACHE: list[str] | None = None


def load_primitives(path: str = _DEFAULT_PATH) -> list[str]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"NSM primitives file not found: {path}\n"
            "Create data/nsm_primes_65.json from Wierzbicka 1996 Table 2.1."
        )
    with open(p, encoding="utf-8") as f:
        _CACHE = json.load(f)
    return _CACHE


def nsm_coverage(
    kernel: set,
    core: set,
    primitives_path: str = _DEFAULT_PATH,
) -> dict:
    """Return NSM coverage fractions for Kernel and Core."""
    try:
        primitives = set(load_primitives(primitives_path))
    except FileNotFoundError:
        return {"kernel_coverage": None, "core_coverage": None,
                "note": "nsm_primes_65.json not found"}

    n = len(primitives)
    k_hit = primitives & kernel
    c_hit = primitives & core
    return {
        "n_primitives": n,
        "kernel_hits": len(k_hit),
        "core_hits": len(c_hit),
        "kernel_coverage": len(k_hit) / n,
        "core_coverage": len(c_hit) / n,
        "kernel_hit_words": sorted(k_hit),
        "core_hit_words": sorted(c_hit),
    }
