"""D033: claim 1 (kernel ratio, circulation rate) and the cycle profile against the directed double-edge swap null.

Reads results_2026-10-02_Local/d033_double_swap_full_stats/results/ (experiments/d033_double_swap_full_stats.py: 23 main graphs, 20 replicates, default filter, first sentence) and the
results of the paper's three-edge null (results_2026-10-01_Local/e2_filtered_default_main_32x/results/). Prints the z-scores of the kernel ratio and the circulation rate by group under both
nulls (median, with the number of graphs below 0 / beyond -2 / beyond +2), the cycle-length profile (observed / null summed over the graphs of a group), and applies the readings k1 to k3
of research/DECISION_LOG.md D033. Output is recorded in outputs/37_double_swap_claim1.txt.
"""
import glob
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
NEW = ROOT / "results_2026-10-02_Local" / "d033_double_swap_full_stats" / "results"
OLD = ROOT / "results_2026-10-01_Local" / "e2_filtered_default_main_32x" / "results"


def load(folder):
    return {r["key"]: r for r in (json.loads(Path(p).read_text(encoding="utf-8")) for p in glob.glob(str(folder / "main__*.json")))}


new, old = load(NEW), load(OLD)
if len(new) != 23:
    print(f"NOT FINISHED: {len(new)} of 23")
    sys.exit(0)
is_pt = lambda k: k.endswith("-pt")
inst = [k for k in new if not is_pt(k) and k != "main__wordnet"]
pre = [k for k in new if is_pt(k)]
assert len(inst) == 17 and len(pre) == 5
groups = (("17 instruct models", inst), ("5 pretrained models", pre), ("WordNet", ["main__wordnet"]))


def cell(data, keys, metric):
    z = [data[k]["z"][metric] for k in keys]
    return f"{st.median(z):+.2f} ({sum(x < 0 for x in z)} / {sum(x < -2 for x in z)} / {sum(x > 2 for x in z)})"


print("1. Z-SCORES OF THE KERNEL RATIO AND THE CIRCULATION RATE (default filter): median (graphs below 0 / beyond -2 / beyond +2)")
print(f"   {'measure':18}{'group':22}{'three-edge null (paper)':>26}{'double-edge null (D033)':>26}")
for label, metric in (("kernel ratio", "kernel_ratio"), ("circulation rate", "circulation_rate")):
    for gname, keys in groups:
        print(f"   {label:18}{gname:22}{cell(old, keys, metric):>26}{cell(new, keys, metric):>26}")
print("\n   instruct models beyond +-2 in the kernel ratio, double-edge null: " + (", ".join(f"{k[6:]} {new[k]['z']['kernel_ratio']:+.1f}" for k in inst if abs(new[k]['z']['kernel_ratio']) > 2) or "none"))
print("   instruct models beyond +-2 in the kernel ratio, three-edge null:  " + (", ".join(f"{k[6:]} {old[k]['z']['kernel_ratio']:+.1f}" for k in inst if abs(old[k]['z']['kernel_ratio']) > 2) or "none"))

print("\n2. CYCLE-LENGTH PROFILE (default filter): observed / null, summed over the graphs of a group")
print(f"   {'group':22}{'null':>14}" + "".join(f"{L:>20}" for L in range(2, 8)))
ratio = {}
for gname, keys in groups:
    for tag, data in (("three-edge", old), ("double-edge", new)):
        cells = []
        for L in range(2, 8):
            o = sum(data[k]["cycle_hist_observed_vs_null"][str(L)]["observed"] for k in keys)
            n = sum(data[k]["cycle_hist_observed_vs_null"][str(L)]["null_mean"] for k in keys)
            ratio[(gname, tag, L)] = o / max(n, 1e-9)
            cells.append(f"{o} / {n:.0f} = {o / max(n, 1e-9):.2f}x")
        print(f"   {gname:22}{tag:>14}" + "".join(f"{c:>20}" for c in cells))

print("\n3. THE READINGS OF D033 (double-edge null)")
zk = [new[k]["z"]["kernel_ratio"] for k in inst]
k1 = abs(st.median(zk)) <= 1 and sum(abs(x) > 2 for x in zk) <= 4 and abs(new["main__wordnet"]["z"]["kernel_ratio"]) < 2
print(f"   (k1) kernel: median z of the 17 instruct models {st.median(zk):+.2f}; beyond +-2: {sum(abs(x) > 2 for x in zk)} of 17; WordNet z {new['main__wordnet']['z']['kernel_ratio']:+.2f}  ->  {'CLAIM 1 (KERNEL AT CHANCE) HOLDS' if k1 else 'DOES NOT HOLD'}")
zc = [new[k]["z"]["circulation_rate"] for k in inst]
k2 = st.median(zc) < 0 and sum(x < 0 for x in zc) >= 12
print(f"   (k2) circulation: median z {st.median(zc):+.2f}; below 0: {sum(x < 0 for x in zc)} of 17  ->  {'STAYS BELOW THE NULL' if k2 else 'DOES NOT STAY BELOW THE NULL'}")
r2 = ratio[("17 instruct models", "double-edge", 2)]
longs = [ratio[("17 instruct models", "double-edge", L)] for L in (5, 6, 7)]
k3 = r2 >= 5 and all(x < 1 for x in longs)
print(f"   (k3) profile: instruct 2-cycles {r2:.1f}x the null; cycles of length 5, 6, 7: " + ", ".join(f"{x:.2f}x" for x in longs) + f"  ->  {'THE PROFILE OF V1 HOLDS' if k3 else 'THE PROFILE CHANGES'}")
