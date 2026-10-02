"""Does the null mean of mutual pairs depend on the number of edge swaps (nswap multiplier)?

Audit script (2026-10-01). Run from anywhere; paths are derived from this file.
Order: 1_build_graphs.py -> 2_compare_R.py -> 3_mixing_test.py (graphs are cached in ./_cache).
Recorded outputs are in ./outputs/.
"""
from pathlib import Path
import sys, os, pickle, time, random, statistics
from multiprocessing import Pool
import networkx as nx
REPO = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, os.path.join(REPO, "src")); os.chdir(REPO)
SP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache")
os.makedirs(os.path.join(SP, "graphs"), exist_ok=True)

def mutual_pairs(G): return sum(1 for u, v in G.edges() if G.has_edge(v, u)) // 2

def job(args):
    key, mult, K = args
    G = pickle.load(open(os.path.join(SP, 'graphs', key + '.pkl'), 'rb'))
    rng = random.Random(123); vals = []; fails = 0; t = time.time()
    for _ in range(K):
        H = G.copy()
        try:
            nx.directed_edge_swap(H, nswap=mult * H.number_of_edges(),
                                  max_tries=300 * H.number_of_edges(), seed=rng.randint(0, 10**6))
        except nx.NetworkXAlgorithmError:
            fails += 1
        vals.append(mutual_pairs(H))
    return key, mult, K, mutual_pairs(G), round(statistics.mean(vals), 2), round(statistics.pstdev(vals), 2), fails, round(time.time() - t)

if __name__ == '__main__':
    tasks = [(k, m, 12) for k in ['main__Gemma3-27B', 'main__Qwen2.5-72B'] for m in (2, 5, 15)]
    with Pool(6) as p:
        rows = p.map(job, tasks)
    print('graph, nswap_mult, K, observed_pairs, null_mean, null_sd, swap_failures, seconds')
    for r in sorted(rows): print(*r)
