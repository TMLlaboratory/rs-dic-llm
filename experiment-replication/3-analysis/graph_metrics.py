"""
Stages 2-4: preprocessing, graph construction, and metrics
(kernel / core / MinSet / circulation / out-degree / sr_rate).

Follows the pipeline in 03_this_research/02_pipeline.md and 03_metrics.md:
  - lowercase, strip punctuation, isalpha filter, stopword removal,
    WordNetLemmatizer, in-vocab filter, self-loops dropped
  - both "ok" and "self_referential" definitions contribute edges
  - kernel: iterative removal of out-degree-0 nodes
  - core:   union of source SCCs in the kernel subgraph's condensation
  - MinSet: exact MFVS via ILP (PuLP + HiGHS) with lazy cycle constraints,
    iterated to a convergence guarantee (removal set verified acyclic)

Also builds the WordNet baseline (--wordnet).

Usage:
    python graph_metrics.py --defs defs --words words.json --out metrics.json
    python graph_metrics.py --wordnet --words words.json --out metrics.json
"""

import argparse
import glob
import json
import os

import networkx as nx
import nltk

for pkg in ["wordnet", "stopwords", "omw-1.4"]:
    try:
        nltk.data.find(f"corpora/{pkg}")
    except LookupError:
        nltk.download(pkg, quiet=True)

from nltk.corpus import stopwords, wordnet as wn
from nltk.stem import WordNetLemmatizer

STOP_WORDS = set(stopwords.words("english"))
LEMMA = WordNetLemmatizer()


# ---------------------------------------------------------------- pipeline --
def lemmatize(token: str) -> str:
    for pos in ("n", "v", "a"):
        lem = LEMMA.lemmatize(token, pos)
        if lem != token:
            return lem
    return token


def build_graph(definitions: list, vocab: set) -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_nodes_from(vocab)
    for rec in definitions:
        if rec["status"] not in {"ok", "self_referential"}:
            continue
        target = rec["word"]
        if target not in vocab:
            continue
        for raw in rec["definition"].split():
            token = raw.lower().strip(".,;:!?\"'()[]")
            if not token.isalpha() or token in STOP_WORDS:
                continue
            source = lemmatize(token)
            if source in vocab and source != target:
                G.add_edge(source, target)
    return G


def compute_kernel(G: nx.DiGraph) -> set:
    H = G.copy()
    while True:
        leaves = [n for n in H if H.out_degree(n) == 0]
        if not leaves:
            return set(H.nodes())
        H.remove_nodes_from(leaves)


def compute_core(G: nx.DiGraph, kernel: set) -> set:
    K = G.subgraph(kernel).copy()
    cond = nx.condensation(K)
    core = set()
    for scc_id in cond.nodes():
        if cond.in_degree(scc_id) == 0:
            core |= set(cond.nodes[scc_id]["members"])
    return core


def _solver_factory():
    """Prefer HiGHS (needs `pip install highspy`); fall back to bundled CBC.
    Availability is only detectable at solve time, so test with a tiny problem."""
    from pulp import HiGHS, PULP_CBC_CMD, LpProblem, LpMinimize, LpVariable
    try:
        p = LpProblem("t", LpMinimize)
        v = LpVariable("v", cat="Binary")
        p += v
        p.solve(HiGHS(msg=False))
        return lambda: HiGHS(msg=False)
    except Exception:
        print("  (HiGHS unavailable -> using CBC. `pip install highspy` for speed)")
        return lambda: PULP_CBC_CMD(msg=False)


def compute_minset(G: nx.DiGraph, kernel: set) -> set:
    """Exact MFVS of the kernel subgraph: lazy-constraint ILP iterated until the
    removal set provably breaks all cycles (addresses the completeness issue in
    04_future_plan/01_research_issues.md)."""
    from pulp import LpMinimize, LpProblem, LpVariable, lpSum, value
    solver = _solver_factory()

    K = nx.DiGraph(G.subgraph(kernel))
    K.remove_edges_from(nx.selfloop_edges(K))
    if nx.is_directed_acyclic_graph(K):
        return set()

    def mfvs_scc(S: nx.DiGraph) -> set:
        """Exact MFVS of one strongly connected subgraph."""
        nodes = list(S.nodes())
        prob = LpProblem("MFVS", LpMinimize)
        x = {n: LpVariable(f"x_{i}", cat="Binary") for i, n in enumerate(nodes)}
        prob += lpSum(x.values())
        constraint_set = set()

        def add_cycles_by_peeling(H: nx.DiGraph) -> int:
            H = H.copy()
            added = 0
            while True:
                try:
                    cycle_edges = nx.find_cycle(H)
                except nx.NetworkXNoCycle:
                    return added
                cyc = frozenset(u for u, v in cycle_edges)
                if cyc not in constraint_set:
                    constraint_set.add(cyc)
                    prob.addConstraint(lpSum(x[n] for n in cyc) >= 1)
                    added += 1
                H.remove_node(next(iter(cyc)))

        for u, v in S.edges():                 # seed: 2-cycles
            if S.has_edge(v, u):
                cyc = frozenset((u, v))
                if cyc not in constraint_set:
                    constraint_set.add(cyc)
                    prob.addConstraint(x[u] + x[v] >= 1)
        add_cycles_by_peeling(S)

        while True:
            prob.solve(solver())
            chosen = {n for n in nodes if value(x[n]) > 0.5}
            R = S.copy()
            R.remove_nodes_from(chosen)
            if add_cycles_by_peeling(R) == 0:  # residual acyclic -> proven optimal
                return chosen

    # Cycles never span SCCs -> solve each SCC independently (much smaller ILPs)
    minset = set()
    for scc in nx.strongly_connected_components(K):
        if len(scc) >= 2:
            minset |= mfvs_scc(nx.DiGraph(K.subgraph(scc)))
    return minset


def metrics_for(definitions: list, vocab: set) -> dict:
    G = build_graph(definitions, vocab)
    kernel = compute_kernel(G)
    core = compute_core(G, kernel)
    minset = compute_minset(G, kernel) if kernel else set()
    n = G.number_of_nodes()
    sccs = [s for s in nx.strongly_connected_components(G) if len(s) >= 2]
    cyclic = {x for s in sccs for x in s}
    statuses = [d["status"] for d in definitions]
    n_def = sum(1 for s in statuses if s in ("ok", "self_referential"))
    return dict(
        n_nodes=n,
        n_edges=G.number_of_edges(),
        n_definitions=n_def,
        n_failed=sum(1 for s in statuses if s == "failed"),
        sr_rate=round(sum(1 for s in statuses if s == "self_referential")
                      / max(n_def, 1), 4),
        kernel_ratio=round(len(kernel) / n, 4),
        core_kernel=round(len(core) / max(len(kernel), 1), 4),
        mset_k=round(len(minset) / max(len(kernel), 1), 4),
        circ=round(len(cyclic) / n, 4),
        out_deg=round(G.number_of_edges() / n, 3),
        kernel_words=sorted(kernel),
        minset_words=sorted(minset),
    )


# ------------------------------------------------------------------ inputs --
def load_defs(path: str) -> list:
    """Load JSONL, deduping on (word,pos): reruns retry failed words, so keep
    the latest non-failed record if one exists."""
    best = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            key = (rec["word"], rec["pos"])
            if key not in best or best[key]["status"] == "failed":
                best[key] = rec
    return list(best.values())


def wordnet_defs(entries: list) -> list:
    POS = {"noun": wn.NOUN, "verb": wn.VERB, "adjective": wn.ADJ}
    out = []
    for e in entries:
        synsets = wn.synsets(e["word"], POS[e["pos"]])
        if not synsets:
            out.append(dict(word=e["word"], pos=e["pos"], status="failed",
                            definition=""))
            continue
        d = synsets[0].definition()
        sr = e["word"] in d.lower().split()
        out.append(dict(word=e["word"], pos=e["pos"],
                        status="self_referential" if sr else "ok", definition=d))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--defs", default="defs", help="dir with *.jsonl definition files")
    ap.add_argument("--words", default="words.json")
    ap.add_argument("--wordnet", action="store_true", help="also compute WordNet baseline")
    ap.add_argument("--out", default="metrics.json")
    args = ap.parse_args()

    with open(args.words, encoding="utf-8") as f:
        entries = json.load(f)
    vocab = {e["word"] for e in entries}

    results = {}
    if os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as f:
            results = json.load(f)

    for path in sorted(glob.glob(os.path.join(args.defs, "*.jsonl"))):
        name = os.path.basename(path).replace(".jsonl", "")
        print(f"computing metrics: {name}")
        m = metrics_for(load_defs(path), vocab)
        m["source_file"] = path
        results[name] = m
        print(f"  kern%={m['kernel_ratio']*100:.1f} mset/k%={m['mset_k']*100:.1f} "
              f"circ%={m['circ']*100:.1f} sr%={m['sr_rate']*100:.1f} "
              f"edges={m['n_edges']}")

    if args.wordnet:
        print("computing metrics: WordNet baseline")
        m = metrics_for(wordnet_defs(entries), vocab)
        results["wordnet_baseline"] = m
        print(f"  kern%={m['kernel_ratio']*100:.1f} mset/k%={m['mset_k']*100:.1f}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, ensure_ascii=False)
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
