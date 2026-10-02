"""Build and cache every definition graph (main 23, WordNet, E3, E4, E5).

Audit script (2026-10-01). Run from anywhere; paths are derived from this file.
Order: 1_build_graphs.py -> 2_compare_R.py -> 3_mixing_test.py (graphs are cached in ./_cache).
Recorded outputs are in ./outputs/.
"""
from pathlib import Path
import sys, json, os, pickle, time, glob
from multiprocessing import Pool
REPO = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, os.path.join(REPO, "src"))
os.chdir(REPO)
SP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache")
os.makedirs(os.path.join(SP, "graphs"), exist_ok=True)
from rs_dic_llm.config import MODEL_REGISTRY
from rs_dic_llm.graph_build import build_graph
from rs_dic_llm.wordnet_baseline import build_wordnet_graph
from rs_dic_llm.sampling import load_word_list

NAMES = [d for d, *_ in MODEL_REGISTRY]
E_DIRS = {
  'e3': 'results_2026-09-09_Runpod/results_e3 (fewshot)/definitions',
  'e4': 'results_2026-09-09_Runpod/results_e4 (lenght)/definitions',
  'e5': 'results_2026-09-09_Runpod/results_e5 (no template)/definitions',
}
def jobs():
    for n in NAMES: yield ('main', n, f'data/definitions/{n}_42.jsonl')
    for k, d in E_DIRS.items():
        for p in sorted(glob.glob(os.path.join(d, '*_42.jsonl'))):
            yield (k, os.path.basename(p)[:-len('_42.jsonl')], p)

def work(job):
    ds, name, path = job
    out = os.path.join(SP, 'graphs', f'{ds}__{name}.pkl')
    t = time.time()
    recs = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    G = build_graph(recs)
    pickle.dump(G, open(out, 'wb'))
    return ds, name, G.number_of_nodes(), G.number_of_edges(), round(time.time() - t, 1)

if __name__ == '__main__':
    t0 = time.time()
    J = list(jobs())
    print('graphs to build:', len(J) + 1, flush=True)
    with Pool(8) as p:
        for r in p.imap_unordered(work, J): print(*r, flush=True)
    words = load_word_list('data/sample_words/word_list_3k_v1.json')
    G, _ = build_wordnet_graph(words)
    pickle.dump(G, open(os.path.join(SP, 'graphs', 'main__wordnet.pkl'), 'wb'))
    print('main wordnet', G.number_of_nodes(), G.number_of_edges())
    print('total seconds', round(time.time() - t0, 1))
