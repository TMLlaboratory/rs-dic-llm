"""Stage 3: Build a directed definition graph from (word, definition) pairs.

Edge convention (Vincent-Lamarre 2016):
    add_edge(u, v)  ⟺  u appears in the definition of v
                         (u defines v; u → v)

Self-loops and multi-edges are removed (DiGraph handles multi-edges automatically).
"""

import networkx as nx

from .normalize import normalize


def build_graph(
    definitions: list[dict],
) -> nx.DiGraph:
    """Build a directed graph from a list of definition records.

    Args:
        definitions: list of dicts with keys "lemma", "definition".
                     Records with status != "ok" are silently skipped.

    Returns:
        nx.DiGraph where add_edge(u, v) means u appears in definition of v.
    """
    # Include self_referential definitions — they still yield valid edges to
    # OTHER words; only truly failed / empty records are excluded.
    valid_statuses = {"ok", "self_referential"}
    vocabulary: set[str] = {
        d["lemma"] for d in definitions
        if d.get("status", "ok") in valid_statuses
    }

    G = nx.DiGraph()
    G.add_nodes_from(vocabulary)

    for record in definitions:
        if record.get("status", "ok") not in valid_statuses:
            continue
        target = record["lemma"]
        defn = record.get("definition", "")
        if not defn:
            continue
        for source in normalize(defn, vocabulary):
            if source != target:          # no self-loops
                G.add_edge(source, target)

    return G
