"""D030 (a): where do the null model's mutual pairs come from?

Reads results_2026-10-02_Local/d030_null_pairs/ (experiments/d030_null_pairs.py): for 40 graphs (per size the zero-shot, whole few-shot and whole instruct graph of the primary
run, and fsS, itS and fsR1..5 of D029) the mutual pairs of replicates 0-39 of the degree-preserving null, which equal the stored replicates (the run stops otherwise).

  1. per graph: mean number of null pairs (40 replicates) beside the stored mean of 100 replicates, the five nodes that occur most often in null pairs and the share of
     the null pair endpoints they carry; the same for the observed pairs
  2. reading (a): the null mean is hub-driven if the five most frequent nodes carry at least half of the null pair endpoints in at least three of the four fsS graphs,
     not hub-driven if they carry less than a third in at least three of the four, otherwise mixed
  3. descriptive: for the 20 random halves, the Spearman correlation between (null mean of the half / null mean of the whole few-shot graph of that size) and the number
     of the ten words with the largest d_out x d_in product in the whole few-shot graph that the half covers (has a surviving entry for)

The rules are fixed in research/DECISION_LOG.md D030. Output is recorded in outputs/29_null_pairs.txt.
"""
import collections
import json
import sys
from pathlib import Path

from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(ROOT))
PRIMARY = ROOT / "results_2026-10-01_Local"
D029 = ROOT / "results_2026-10-02_Local" / "d029_survivor_restriction"
D030 = ROOT / "results_2026-10-02_Local" / "d030_null_pairs"
SIZES = ("1B", "4B", "12B", "27B")
N_REPS = 40


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def graph_keys(s):
    return {"zs": f"main__Gemma3-{s}-pt", "fs": f"e3__Gemma3-{s}-pt", "it": f"main__Gemma3-{s}",
            "fsS": f"d029__fsS_{s}", "itS": f"d029__itS_{s}", **{f"fsR{k}": f"d029__fsR{k}_{s}" for k in range(1, 6)}}


FOLDER = {"main__": PRIMARY / "e2_filtered_default_main_32x", "e3__": PRIMARY / "e2_filtered_default_controls_32x", "d029__": D029}


def folder(key):
    return next(v for k, v in FOLDER.items() if key.startswith(k))


def read_pairs(key):
    out = {}
    path = D030 / "pairs" / f"{key}.jsonl"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            assert rec["matches_stored"], (key, rec["idx"])
            out[rec["idx"]] = rec["pairs"]
    return out


def observed_pairs(key):
    g = load(folder(key) / "graphs" / f"{key}.json")
    edges = {tuple(e) for e in g["edges"]}
    return sorted({tuple(sorted((u, v))) for (u, v) in edges if (v, u) in edges and u != v})


def stored_null(key):
    return load(folder(key) / "results" / f"{key}.json")["null_mean"]["cycles_2"]


def top_share(counter, k=5):
    total = sum(counter.values())
    top = counter.most_common(k)
    return (sum(v for _, v in top) / total if total else float("nan")), top


all_pairs = {}
for s in SIZES:
    for key in graph_keys(s).values():
        if not (D030 / "pairs" / f"{key}.jsonl").exists():
            print(f"NOT FINISHED: missing {key}")
            sys.exit(0)
        all_pairs[key] = read_pairs(key)
        if len(all_pairs[key]) < N_REPS:
            print(f"NOT FINISHED: {key} has {len(all_pairs[key])} of {N_REPS} replicates")
            sys.exit(0)

print("1. NULL PAIRS BY NODE (replicates 0-39 of the stored null; every rerun replicate equals the stored one)")
print("   'null' = mean pairs per replicate over these 40; 'stored' = the 100-replicate mean of the run that made the graph; share = the five most frequent nodes' share of the null pair endpoints\n")
shares = {}
for s in SIZES:
    for tag, key in graph_keys(s).items():
        reps = all_pairs[key]
        endpoints = collections.Counter()
        for idx in range(N_REPS):
            for u, v in reps[idx]:
                endpoints[u] += 1
                endpoints[v] += 1
        mean_null = sum(len(reps[i]) for i in range(N_REPS)) / N_REPS
        share, top = top_share(endpoints)
        obs_pairs = observed_pairs(key)
        obs_end = collections.Counter(w for p in obs_pairs for w in p)
        oshare, otop = top_share(obs_end)
        shares[(s, tag)] = share
        print(f"   {s:>4} {tag:<5} null {mean_null:5.2f} (stored {stored_null(key):5.2f})  top-5 share {share:5.2f}  " + ", ".join(f"{w} {c / N_REPS:.2f}" for w, c in top) +
              f"   | observed {len(obs_pairs):3d} pairs, top-5 share {oshare:5.2f}: " + ", ".join(f"{w} {c}" for w, c in otop))
    print()

print("2. READING (a): is the null mean hub-driven?  share of null pair endpoints carried by the five most frequent nodes, fsS graphs")
sh = [shares[(s, "fsS")] for s in SIZES]
print("   fsS: " + ", ".join(f"{s} {x:.2f}" for s, x in zip(SIZES, sh)))
n_hub = sum(x >= 0.5 for x in sh)
n_not = sum(x < 1 / 3 for x in sh)
verdict = "HUB-DRIVEN" if n_hub >= 3 else ("NOT HUB-DRIVEN" if n_not >= 3 else "MIXED")
print(f"   at least one half: {n_hub} of 4; below one third: {n_not} of 4  ->  {verdict}")
print("   for comparison, the same share in the other graphs: " + "; ".join(f"{tag} " + ", ".join(f"{shares[(s, tag)]:.2f}" for s in SIZES) for tag in ("zs", "fs", "it", "itS")))

print("\n3. DESCRIPTIVE: null mean of the random halves against how many of the ten largest hubs they cover")
sets = load(D029 / "restriction_sets.json")
xs, ys = [], []
print(f"   {'size':>4}{'hubs (largest d_out x d_in in the whole few-shot graph)':>64}")
for s in SIZES:
    g = load(PRIMARY / "e2_filtered_default_controls_32x" / "graphs" / f"e3__Gemma3-{s}-pt.json")
    dout, din = collections.Counter(), collections.Counter()
    for u, v in g["edges"]:
        dout[u] += 1
        din[v] += 1
    hubs = sorted(g["nodes"], key=lambda w: (-dout[w] * din[w], w))[:10]
    lemma = {}
    for i, line in enumerate(open(ROOT / f"data/definitions/Gemma3-{s}-pt_42.jsonl", encoding="utf-8")):
        if line.strip():
            lemma[i] = json.loads(line)["lemma"]
    whole_null = stored_null(f"e3__Gemma3-{s}-pt")
    print(f"   {s:>4}  {', '.join(hubs)}")
    for k in range(1, 6):
        covered = {lemma[i] for i in sets[s]["random_indices"][str(k)]}
        n_cov = sum(h in covered for h in hubs)
        ratio = stored_null(f"d029__fsR{k}_{s}") / whole_null
        xs.append(n_cov)
        ys.append(ratio)
        print(f"        half {k}: covers {n_cov:2d} of the 10 hubs; null mean {stored_null(f'd029__fsR{k}_{s}'):5.2f} = {ratio:5.2f} x the whole graph's")
rho, p = spearmanr(xs, ys)
print(f"\n   Spearman correlation over the 20 halves between hubs covered and null mean / whole null mean: {rho:+.2f} (p = {p:.2f})")

# Added 2026-10-02, after sections 1-3 had been read (post hoc, descriptive): how many of the null's pairs are pairs of the observed graph?
print("\n4. POST HOC: OBSERVED PAIRS THAT THE NULL KEEPS (the 40 replicates of each graph)")
print("   kept = mean number of the observed pairs that a replicate contains; never broken = observed pairs present in all 40 replicates; share = kept / mean null pairs\n")
print(f"   {'size':>4} {'graph':<5}{'observed':>9}{'null':>7}{'kept':>7}{'share':>7}{'never broken':>14}{'present in some':>17}")
agg = {}
for s in SIZES:
    for tag, key in graph_keys(s).items():
        reps = all_pairs[key]
        obs_set = {tuple(p) for p in observed_pairs(key)}
        per_pair = collections.Counter()
        kept_total = 0
        for idx in range(N_REPS):
            present = {tuple(sorted(p)) for p in reps[idx]} & obs_set
            kept_total += len(present)
            per_pair.update(present)
        mean_null = sum(len(reps[i]) for i in range(N_REPS)) / N_REPS
        kept = kept_total / N_REPS
        never = sum(1 for p in obs_set if per_pair[p] == N_REPS)
        some = sum(1 for p in obs_set if per_pair[p] > 0)
        agg.setdefault(tag, []).append((len(obs_set), mean_null, kept, never))
        print(f"   {s:>4} {tag:<5}{len(obs_set):>9}{mean_null:>7.2f}{kept:>7.2f}{(kept / mean_null if mean_null else float('nan')):>7.2f}{never:>14}{some:>17}")
    print()
print("   summed over the four sizes: " + "; ".join(f"{tag}: {sum(a[0] for a in v)} observed pairs, null {sum(a[1] for a in v):.1f}, kept {sum(a[2] for a in v):.1f}, never broken {sum(a[3] for a in v)}" for tag, v in agg.items()))
