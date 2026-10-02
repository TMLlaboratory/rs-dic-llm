"""Count-based uncertainty of R, and of the instruct / base ratios of the matched Gemma3 pairs.

The intervals of the null-model runs cover the sampling of the null only. The observed number of mutual
pairs is itself a count (3-14 in the filtered base graphs), so this script adds the exact 95 % Poisson
interval of that count, divided by the null mean (floor 0.5, as in R), and combines the two ends of a pair
conservatively: ratio range = [instruct low / base high, instruct high / base low]. The null mean is taken
as known, so the ranges are still too narrow if anything. Output: outputs/19_count_intervals.txt.
"""
import glob
import json
import sys
from pathlib import Path

from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
RES = ROOT / "results_2026-10-01_Local"
RUNS = {
    "unfiltered": ("e1d_null_unfiltered_32x", "e1d_null_unfiltered_32x_controls"),
    "default": ("e2_filtered_default_main_32x", "e2_filtered_default_controls_32x"),
    "strict": ("e2_filtered_strict_main_32x", "e2_filtered_strict_e3_32x"),
    "stored": ("e2_filtered_default_storedtext_main_32x", None),
    "frame": ("e2_frame_words_removed_default_main_32x", None),
}
SIZES = ("1B", "4B", "12B", "27B")


def load(folder):
    out = {}
    if folder:
        for p in glob.glob(str(RES / folder / "results" / "*.json")):
            r = json.load(open(p, encoding="utf-8"))
            out[r["key"]] = r
    return out


DATA = {v: {**load(a), **load(b)} for v, (a, b) in RUNS.items()}


def poisson_ci(k, level=0.95):
    a = (1 - level) / 2
    return (0.0 if k == 0 else chi2.ppf(a, 2 * k) / 2), chi2.ppf(1 - a, 2 * (k + 1)) / 2


def r_range(rec):
    obs, null = rec["observed"]["cycles_2"], max(rec["null_mean"]["cycles_2"], 0.5)
    lo, hi = poisson_ci(obs)
    return obs / null, lo / null, hi / null


print("1. R WITH ITS COUNT-BASED RANGE (default filter): observed pairs, null mean, R, 95 % Poisson range of R")
for key in sorted(DATA["default"], key=lambda k: -DATA["default"][k]["reciprocity_excess"]):
    if key.startswith("main__"):
        rec = DATA["default"][key]
        r, lo, hi = r_range(rec)
        print(f"   {key[6:]:26} obs {rec['observed']['cycles_2']:3d}  null {rec['null_mean']['cycles_2']:5.2f}  R {r:5.1f}   [{lo:5.1f}, {hi:5.1f}]   null-only interval {['%.1f' % x for x in rec['R_ci95']]}")

print("\n2. MATCHED GEMMA3 PAIRS, instruct R / base R with the conservative count-based range of the ratio")
print(f"   {'variant':11}{'size':>5}{'instruct R':>12}{'base R':>9}{'ratio':>8}   {'ratio range':>16}   range includes 2?")
for variant in ("unfiltered", "default", "strict", "stored", "frame"):
    for s in SIZES:
        i, b = DATA[variant].get(f"main__Gemma3-{s}"), DATA[variant].get(f"main__Gemma3-{s}-pt")
        if i and b:
            ri, ilo, ihi = r_range(i)
            rb, blo, bhi = r_range(b)
            lo, hi = ilo / bhi, ihi / blo if blo > 0 else float("inf")
            print(f"   {variant:11}{s:>5}{ri:12.1f}{rb:9.1f}{ri / rb:8.1f}   [{lo:6.1f}, {hi:7.1f}]   {'yes' if lo < 2 else 'no'}")

print("\n3. E3: few-shot base R against the instruct model of the same size, count-based ranges (default filter)")
for s in SIZES:
    f, i = DATA["default"].get(f"e3__Gemma3-{s}-pt"), DATA["default"].get(f"main__Gemma3-{s}")
    if f and i:
        rf, flo, fhi = r_range(f)
        ri, ilo, ihi = r_range(i)
        print(f"   {s:>4}: few-shot base {rf:5.1f} [{flo:5.1f}, {fhi:5.1f}] (obs {f['observed']['cycles_2']})   instruct {ri:5.1f} [{ilo:5.1f}, {ihi:5.1f}] (obs {i['observed']['cycles_2']})   "
              f"base / instruct {rf / ri:4.2f}, range [{flo / ihi:4.2f}, {fhi / ilo:4.2f}]")
g = DATA["default"].get("e3__Gemma3-270M-pt")
if g:
    r, lo, hi = r_range(g)
    print(f"   270M few-shot base: R {r:.1f} [{lo:.1f}, {hi:.1f}] (obs {g['observed']['cycles_2']}); zero-shot 270M-pt default R {r_range(DATA['default']['main__Gemma3-270M-pt'])[0]:.1f}")


# ---------------------------------------------------------------------------------------------------------
# Exact conditional interval for a ratio of two counts with known exposures (the null means, floor 0.5):
# given n = x_a + x_b, x_a is binomial with p = rate_a e_a / (rate_a e_a + rate_b e_b); the Clopper-Pearson
# interval of p gives the interval of the rate ratio. Tighter than combining the two ends independently
# (section 2) and the usual way to compare two Poisson counts. The null means are taken as known.
from scipy.stats import beta  # noqa: E402


def ratio_ci(a, b, level=0.95):
    xa, xb = a["observed"]["cycles_2"], b["observed"]["cycles_2"]
    ea, eb = max(a["null_mean"]["cycles_2"], 0.5), max(b["null_mean"]["cycles_2"], 0.5)
    n = xa + xb
    alpha = (1 - level) / 2
    p_lo = beta.ppf(alpha, xa, n - xa + 1) if xa > 0 else 0.0
    p_hi = beta.ppf(1 - alpha, xa + 1, n - xa) if xb > 0 else 1.0
    odds = lambda p: p / (1 - p) if p < 1 else float("inf")
    scale = eb / ea
    return (xa / ea) / (xb / eb), odds(p_lo) * scale, odds(p_hi) * scale


print("\n4. MATCHED GEMMA3 PAIRS, exact conditional interval of the ratio instruct R / base R")
print(f"   {'variant':11}{'size':>5}{'pairs i/b':>11}{'ratio':>8}   {'95 % range':>16}   lower end below 2?")
for variant in ("unfiltered", "default", "strict", "stored", "frame"):
    for s in SIZES:
        i, b = DATA[variant].get(f"main__Gemma3-{s}"), DATA[variant].get(f"main__Gemma3-{s}-pt")
        if i and b:
            ratio, lo, hi = ratio_ci(i, b)
            print(f"   {variant:11}{s:>5}{str(i['observed']['cycles_2']) + '/' + str(b['observed']['cycles_2']):>11}{ratio:8.1f}   [{lo:6.1f}, {hi:7.1f}]   {'yes' if lo < 2 else 'no'}")

print("\n5. E3 (default filter): few-shot base R / instruct R of the same size, exact conditional interval")
for s in SIZES:
    f, i = DATA["default"].get(f"e3__Gemma3-{s}-pt"), DATA["default"].get(f"main__Gemma3-{s}")
    if f and i:
        ratio, lo, hi = ratio_ci(f, i)
        print(f"   {s:>4}: pairs {f['observed']['cycles_2']}/{i['observed']['cycles_2']}  base / instruct {ratio:4.2f}  [{lo:4.2f}, {hi:4.2f}]")

# ---------------------------------------------------------------------------------------------------------
# Added 2026-10-02 after a review. Sections 3 and 5 give E3 as base / instruct, the zero-shot pairs of sections 2 and 4 as
# instruct / base, and the two interval methods disagree at 1B (the exact conditional range excludes 1, the conservative one
# does not). This section gives E3 in one direction (instruct / few-shot base, as for the zero-shot pairs) with both methods named.
print("\n6. E3 AS instruct R / few-shot base R (the direction of the zero-shot pairs), default filter, both interval methods")
print(f"   {'size':>4}{'pairs i/f':>10}{'ratio':>7}   {'exact conditional (sections 4-5), inverted':>44}   {'conservative (sections 2-3), inverted':>40}")
verdict = lambda lo, hi: "excludes 1" if lo > 1 or hi < 1 else "includes 1"
for s in SIZES:
    f, i = DATA["default"].get(f"e3__Gemma3-{s}-pt"), DATA["default"].get(f"main__Gemma3-{s}")
    if f and i:
        ratio, lo, hi = ratio_ci(i, f)
        ri, ilo, ihi = r_range(i)
        rf, flo, fhi = r_range(f)
        clo, chi = ilo / fhi, ihi / flo
        allows = f"instruct up to {hi:.2f}x" + (f", base up to {1 / lo:.2f}x" if lo < 1 else "")
        print(f"   {s:>4}{str(i['observed']['cycles_2']) + '/' + str(f['observed']['cycles_2']):>10}{ratio:7.2f}   [{lo:5.2f}, {hi:5.2f}] {verdict(lo, hi):<10}   "
              f"[{clo:5.2f}, {chi:5.2f}] {verdict(clo, chi):<10}   exact range allows {allows}")
g = DATA["default"].get("e3__Gemma3-270M-pt")
instruct_keys = [k for k in DATA["default"] if k.startswith("main__") and not k.endswith("-pt") and not k.endswith("__wordnet")]
if g and instruct_keys:
    low = min(instruct_keys, key=lambda k: r_range(DATA["default"][k])[0])
    r, lo, hi = r_range(g)
    rl, llo, lhi = r_range(DATA["default"][low])
    print(f"   270M: few-shot base R {r:.1f} [{lo:.1f}, {hi:.1f}] (obs {g['observed']['cycles_2']}); Gemma3-270M instruct has no cycles and no comparison (D011); "
          f"the lowest of the {len(instruct_keys)} instruct models in the main run is {low[6:]}, R {rl:.1f} [{llo:.1f}, {lhi:.1f}]")
