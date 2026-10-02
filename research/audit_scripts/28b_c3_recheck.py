"""D029 (c3), second derivation of the counts of script 28.

Script 28 reads graph snapshots (the zero-shot and instruct graphs of the primary run, the fsS graph of the D029 run). This script
does not: it rebuilds all three graphs from the records (filter, build_graph, restriction to the zero-shot survivors) and counts again
which of the instruct graph's mutual pairs, among those whose two words both have a surviving zero-shot entry, each graph contains.
The counts should equal those of script 28 section 3 (|T| 12 / 12 / 19 / 19, zero-shot 0 / 1 / 2 / 2, few-shot 0 / 6 / 8 / 6).
Output is recorded in outputs/28b_c3_recheck.txt.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(ROOT)

from rs_dic_llm.filtered_definitions import VALID_STATUSES, filter_records, fixed_vocabulary  # noqa: E402
from rs_dic_llm.graph_build import build_graph  # noqa: E402
from rs_dic_llm.sampling import load_word_list  # noqa: E402

E3 = "results_2026-09-09_Runpod/results_e3 (fewshot)/definitions"
vocab = fixed_vocabulary(load_word_list("data/sample_words/word_list_3k_v1.json"))


def load(p):
    return [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]


def mutual(G):
    return {tuple(sorted((u, v))) for u, v in G.edges() if G.has_edge(v, u) and u != v}


tot = {"n": 0, "zs": 0, "fs": 0}
for s in ("1B", "4B", "12B", "27B"):
    zs = filter_records(load(f"data/definitions/Gemma3-{s}-pt_42.jsonl"))[0]
    fs = filter_records(load(f"{E3}/Gemma3-{s}-pt_42.jsonl"))[0]
    it = filter_records(load(f"data/definitions/Gemma3-{s}_42.jsonl"))[0]
    S = {i for i, r in enumerate(zs) if r["status"] in VALID_STATUSES and r["definition"].strip()}
    covered = {zs[i]["lemma"] for i in S}
    fs_s = [dict(r, definition=r["definition"] if i in S else "") for i, r in enumerate(fs)]
    pz, pf, pi = mutual(build_graph(zs, vocab)), mutual(build_graph(fs_s, vocab)), mutual(build_graph(it, vocab))
    T = {p for p in pi if p[0] in covered and p[1] in covered}
    a, b = len(T & pz), len(T & pf)
    print(f"{s:>4}  survivors {len(S)}  instruct pairs {len(pi)}  at risk {len(T)}  zero-shot {a}  few-shot (same entries) {b}   "
          f"(mutual pairs in the graphs: zero-shot {len(pz)}, few-shot same entries {len(pf)}, instruct {len(pi)})")
    tot["n"] += len(T)
    tot["zs"] += a
    tot["fs"] += b
print(f"pooled: at risk {tot['n']}, zero-shot {tot['zs']}, few-shot (same entries) {tot['fs']}")
