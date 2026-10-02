"""E1d (converged null: 32 x edges swaps, 300 tries per swap) against E1 (5 x), main graphs.

Audit script (2026-10-01). Reads the two result files and prints: R per graph at both
settings with the change; the groups' ranges; the matched Gemma pairs; where WordNet sits;
the kernel and circulation z-scores (claim 1); the cycle-length profile (observed / null) by
group. Output is recorded in outputs/12_e1d_vs_e1.txt.
"""
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
E1 = {r["key"]: r for r in json.load(open(ROOT / "results_2026-10-01_Local/e1_null_unfiltered/null_model_all.json", encoding="utf-8"))}
D = {r["key"]: r for r in json.load(open(ROOT / "results_2026-10-01_Local/e1d_null_unfiltered_32x/null_model_all.json", encoding="utf-8"))}

is_base = lambda k: k.endswith("-pt")
is_wn = lambda k: k == "main__wordnet"
inst = [k for k in D if not is_base(k) and not is_wn(k)]
base = [k for k in D if is_base(k)]
R = lambda r: r["reciprocity_excess"]

print("1. R PER GRAPH, 5 x (E1) AND 32 x (E1d); 95 % CI of E1d")
print(f"   {'graph':26}{'null 5x':>8}{'null 32x':>9}{'R 5x':>7}{'R 32x':>7}{'CI 32x':>16}{'change':>8}")
for k in sorted(D, key=lambda k: -R(D[k])):
    a, d = E1[k], D[k]
    lo, hi = d["R_ci95"]
    print(f"   {k[6:]:26}{a['null_mean']['cycles_2']:>8.2f}{d['null_mean']['cycles_2']:>9.2f}{R(a):>7.1f}{R(d):>7.1f}"
          f"{'[%.1f, %.1f]' % (lo, hi):>16}{100 * (R(d) / R(a) - 1):>+7.0f}%")
for lab, keys in (("all 23", list(D)), ("instruct 17", inst), ("base 5", base)):
    ch = [100 * (R(D[k]) / R(E1[k]) - 1) for k in keys]
    print(f"   change 5x -> 32x, {lab:12}: median {st.median(ch):+.0f}%, mean {st.mean(ch):+.0f}%, range {min(ch):+.0f}% to {max(ch):+.0f}%, "
          f"higher on {sum(c > 0 for c in ch)} of {len(ch)}")

print("\n2. RANGES AT 32 x (report: instruct 8.9-23.5, base 1.5-7.3, WordNet 10.0)")
ri, rb, rw = [R(D[k]) for k in inst], [R(D[k]) for k in base], R(D["main__wordnet"])
print(f"   instruct ({len(inst)}): {min(ri):.1f}-{max(ri):.1f}, median {st.median(ri):.1f};  base ({len(base)}): {min(rb):.1f}-{max(rb):.1f}, median {st.median(rb):.1f};  WordNet {rw:.1f} {D['main__wordnet']['R_ci95'][0]:.1f}-{D['main__wordnet']['R_ci95'][1]:.1f}")
lo = min(inst, key=lambda k: R(D[k])); hi = max(base, key=lambda k: R(D[k]))
print(f"   lowest instruct {lo[6:]} {R(D[lo]):.1f} {['%.1f' % x for x in D[lo]['R_ci95']]}; highest base {hi[6:]} {R(D[hi]):.1f} {['%.1f' % x for x in D[hi]['R_ci95']]}; "
      f"intervals overlap: {D[lo]['R_ci95'][0] <= D[hi]['R_ci95'][1]}")
print(f"   instruct graphs above WordNet ({rw:.1f}): {sum(r > rw for r in ri)} of {len(ri)}; WordNet rank among the {len(ri) + 1}: {1 + sum(r > rw for r in ri)}")

print("\n3. MATCHED GEMMA PAIRS AT 32 x (instruct vs base)")
for size in ("1B", "4B", "12B", "27B"):
    i, b = D[f"main__Gemma3-{size}"], D[f"main__Gemma3-{size}-pt"]
    print(f"   {size:4} instruct {R(i):5.1f} {['%.1f' % x for x in i['R_ci95']]}   base {R(b):4.1f} {['%.1f' % x for x in b['R_ci95']]}   ratio {R(i) / R(b):.1f}")
print(f"   270M base {R(D['main__Gemma3-270M-pt']):.1f} (the instruct 270M has no cycle and is not in E1d)")

print("\n4. CLAIM 1 AT 32 x: z-scores against the converged null (22 models + WordNet)")
for lab, key in (("kernel ratio", "kernel_ratio"), ("circulation rate", "circulation_rate")):
    z = [D[k]["z"][key] for k in D]
    z1 = [E1[k]["z"][key] for k in D]
    print(f"   {lab:17} E1d: median {st.median(z):+.2f}, mean {st.mean(z):+.2f}, range {min(z):+.2f}..{max(z):+.2f}, below -2: {sum(x < -2 for x in z)}, above +2: {sum(x > 2 for x in z)}"
          f"   | E1 (same graphs): median {st.median(z1):+.2f}, below -2: {sum(x < -2 for x in z1)}, above +2: {sum(x > 2 for x in z1)}")
print(f"   WordNet: kernel z {D['main__wordnet']['z']['kernel_ratio']:+.2f}, circulation z {D['main__wordnet']['z']['circulation_rate']:+.2f}")
print("   graphs with kernel z above +2:", [(k[6:], round(D[k]['z']['kernel_ratio'], 2)) for k in D if D[k]["z"]["kernel_ratio"] > 2])
print("   graphs with kernel z below -2:", [(k[6:], round(D[k]['z']['kernel_ratio'], 2)) for k in D if D[k]["z"]["kernel_ratio"] < -2])

print("\n5. CYCLE-LENGTH PROFILE AT 32 x (observed / null mean, summed over the graphs of a group)")
def prof(keys, length):
    o = sum(D[k]["cycle_hist_observed_vs_null"][str(length)]["observed"] for k in keys)
    n = sum(D[k]["cycle_hist_observed_vs_null"][str(length)]["null_mean"] for k in keys)
    return o, n
for lab, keys in (("instruct", inst), ("base zero-shot", base), ("WordNet", ["main__wordnet"])):
    print(f"   {lab:15}" + "  ".join(f"L{L}: {prof(keys, L)[0]}/{prof(keys, L)[1]:.0f} = {prof(keys, L)[0] / max(prof(keys, L)[1], 1e-9):.2f}x" for L in range(2, 8)))
print("   long cycles (5-7), observed / null per base graph:")
for k in base:
    o = D[k]["observed"]["cycles_long"]; n = D[k]["null_mean"]["cycles_long"]
    print(f"     {k[6:]:18} {o:4} / {n:6.1f} = {o / n:.2f}x")
