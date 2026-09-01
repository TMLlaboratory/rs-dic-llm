"""Degree-preserving null model for definition graphs.

Answers the question the pipeline never asked: is the observed kernel / cycle
structure more than what the degree sequence alone (i.e. how long and how
in-vocabulary-dense the definitions are) already implies?

For each model we rewire the definition graph with `directed_edge_swap`, which
preserves every node's in- and out-degree exactly, and compare:

    kernel_ratio      observed vs null  -> z-score
    2-cycle count     observed vs null  -> Reciprocity Excess R
    long cycles (>=5) observed vs null  -> loop compactness

Usage:
    uv run python -m experiments.null_model                 # every *_42.jsonl
    uv run python -m experiments.null_model Gemma3-27B ...  # selected models
    R=100 uv run python -m experiments.null_model           # more replicates
"""

import glob
import json
import os
import random
import statistics
import sys

import networkx as nx

from src.graph_build import build_graph
from src.wordnet_baseline import build_wordnet_graph

CYCLE_BOUND = 7
DEFS_DIR = "data/definitions"
WORD_LIST = "data/sample_words/word_list_3k_v1.json"


def compute_kernel(G: nx.DiGraph) -> nx.DiGraph:
    """Iteratively drop out-degree-0 nodes (Vincent-Lamarre 2016)."""
    H = G.copy()
    while True:
        drop = [n for n in H if H.out_degree(n) == 0]
        if not drop:
            return H
        H.remove_nodes_from(drop)


def summarize(G: nx.DiGraph, n_nodes: int) -> dict:
    hist: dict[int, int] = {}
    for cycle in nx.simple_cycles(G, length_bound=CYCLE_BOUND):
        hist[len(cycle)] = hist.get(len(cycle), 0) + 1
    sccs = [c for c in nx.strongly_connected_components(G) if len(c) > 1]
    return {
        "kernel_ratio": len(compute_kernel(G)) / n_nodes,
        "circulation_rate": sum(len(c) for c in sccs) / n_nodes,
        "cycles_total": sum(hist.values()),
        "cycles_2": hist.get(2, 0),
        "cycles_long": sum(v for k, v in hist.items() if k >= 5),
    }


def rewire(G: nx.DiGraph, seed: int) -> nx.DiGraph:
    """Degree-preserving randomization. Sparse graphs may randomize partially."""
    H = G.copy()
    try:
        nx.directed_edge_swap(
            H,
            nswap=5 * H.number_of_edges(),
            max_tries=300 * H.number_of_edges(),
            seed=seed,
        )
    except nx.NetworkXAlgorithmError:
        pass
    return H


def analyse(name: str, G: nx.DiGraph, n_replicates: int, rng: random.Random) -> dict:
    n = G.number_of_nodes()
    obs = summarize(G, n)
    nulls = [summarize(rewire(G, rng.randint(0, 10**6)), n) for _ in range(n_replicates)]

    null_mean = {k: statistics.mean(d[k] for d in nulls) for k in obs}
    null_sd = {k: statistics.pstdev([d[k] for d in nulls]) for k in obs}
    return {
        "model": name,
        "n_nodes": n,
        "n_edges": G.number_of_edges(),
        "observed": obs,
        "null_mean": null_mean,
        "null_sd": null_sd,
        "kernel_z": (obs["kernel_ratio"] - null_mean["kernel_ratio"])
        / (null_sd["kernel_ratio"] or 1e-9),
        # Reciprocity Excess: mutual-definition pairs relative to chance.
        "reciprocity_excess": obs["cycles_2"] / max(null_mean["cycles_2"], 0.5),
    }


def main(argv: list[str]) -> None:
    n_replicates = int(os.environ.get("R", "10"))
    rng = random.Random(0)

    if argv:
        paths = [f"{DEFS_DIR}/{name}_42.jsonl" for name in argv]
    else:
        paths = sorted(glob.glob(f"{DEFS_DIR}/*_42.jsonl"))

    results = []
    for path in paths:
        name = os.path.basename(path)[: -len("_42.jsonl")]
        definitions = [json.loads(line) for line in open(path)]
        results.append(analyse(name, build_graph(definitions), n_replicates, rng))
        print(json.dumps(results[-1]), flush=True)

    if not argv:
        words = json.load(open(WORD_LIST))["words"]
        wn_graph, _ = build_wordnet_graph(words)
        results.append(analyse("wordnet", wn_graph, n_replicates, rng))
        print(json.dumps(results[-1]), flush=True)

    with open("results/null_model.json", "w") as fh:
        json.dump(results, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
