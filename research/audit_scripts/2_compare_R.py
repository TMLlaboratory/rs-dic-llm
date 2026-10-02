"""Compare empirical-null R (null_model.py style) with the analytic R stored in the E3/E4/E5 metrics JSONs.

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
from rs_dic_llm.metrics.scc import reciprocity_excess as R_analytic

def mutual_pairs(G):
    return sum(1 for u, v in G.edges() if G.has_edge(v, u)) // 2

def rewire(G, seed, mult):
    H = G.copy(); failed = False
    try:
        nx.directed_edge_swap(H, nswap=mult * H.number_of_edges(),
                              max_tries=300 * H.number_of_edges(), seed=seed)
    except nx.NetworkXAlgorithmError:
        failed = True
    return H, failed

def job(args):
    key, mult, K = args
    G = pickle.load(open(os.path.join(SP, 'graphs', key + '.pkl'), 'rb'))
    rng = random.Random(0)
    t = time.time(); vals = []; fails = 0
    for _ in range(K):
        H, f = rewire(G, rng.randint(0, 10**6), mult)
        vals.append(mutual_pairs(H)); fails += f
    obs = mutual_pairs(G)
    # sanity: mutual pairs == 2-cycle count from simple_cycles
    c2 = sum(1 for c in nx.simple_cycles(G, length_bound=2) if len(c) == 2)
    m = statistics.mean(vals)
    return dict(key=key, mult=mult, K=K, E=G.number_of_edges(), obs=obs, c2=c2,
                null_mean=round(m, 2), null_sd=round(statistics.pstdev(vals), 2),
                R_emp=round(obs / max(m, 0.5), 2), R_analytic=round(R_analytic(G), 2),
                fails=fails, sec=round(time.time() - t, 1))

if __name__ == '__main__':
    keys = ['main__Gemma3-27B', 'main__Gemma3-27B-pt', 'main__Gemma3-4B-pt', 'main__Gemma3-4B',
            'main__Qwen2.5-72B', 'main__wordnet', 'e3__Gemma3-27B-pt', 'e4__Gemma3-27B', 'e5__Qwen3-0.6B']
    tasks = [(k, 5, 20) for k in keys]
    with Pool(8) as p: res = p.map(job, tasks)
    print(f"{'graph':24}{'E':>6}{'obs':>5}{'c2':>5}{'null_mean':>10}{'null_sd':>8}{'R_emp':>8}{'R_anal':>8}{'fails':>6}{'sec':>6}")
    for r in res:
        print(f"{r['key']:24}{r['E']:>6}{r['obs']:>5}{r['c2']:>5}{r['null_mean']:>10}{r['null_sd']:>8}{r['R_emp']:>8}{r['R_analytic']:>8}{r['fails']:>6}{r['sec']:>6}")
