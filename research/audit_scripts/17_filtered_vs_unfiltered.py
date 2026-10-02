"""R on the filtered graphs against the unfiltered ones (E2 re-run; decisions D023, D024).

Reads the per-graph results of every run that exists (partial runs are used as far as they got) and
prints: R per main graph under each variant; the group ranges; the matched Gemma3 pairs with the
pre-registered reading of D024 applied; E3 against the instruct models; E4 and E5 against the main
run; claim 1 (z-scores) and the cycle-length profile under the default filter; the imperatives
sensitivity. Output is recorded in outputs/17_filtered_vs_unfiltered.txt.

Variants: unfiltered = E1d (stored text, node set of the records with a valid status); extract = first
sentence only, nothing dropped (this run was cancelled, so the column stays empty); default = default filter, first sentence (the primary analysis);
strict = the bracket of D024 (main graphs and the five E3 graphs); stored = default filter decisions, stored
text for kept records; frame = default filter with the frame words of D025 removed from every graph.
All variants except `unfiltered` use the fixed 2,750-lemma node set (D010).
"""
import glob
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
RES = ROOT / "results_2026-10-01_Local"
RUNS = {  # variant: (main folder, controls folder)
    "unfiltered": ("e1d_null_unfiltered_32x", "e1d_null_unfiltered_32x_controls"),
    "extract": ("e2_extract_only_main_32x", None),
    "default": ("e2_filtered_default_main_32x", "e2_filtered_default_controls_32x"),
    "strict": ("e2_filtered_strict_main_32x", "e2_filtered_strict_e3_32x"),
    "stored": ("e2_filtered_default_storedtext_main_32x", None),
    "frame": ("e2_frame_words_removed_default_main_32x", None),
}
IMPERATIVES = "e2_filtered_default_imperatives_Qwen3-0.6B_32x"
SIZES = ("1B", "4B", "12B", "27B")


def load_folder(folder):
    out = {}
    if folder:
        for p in glob.glob(str(RES / folder / "results" / "*.json")):
            r = json.load(open(p, encoding="utf-8"))
            out[r["key"]] = r
    return out


DATA = {}
for variant, (main, ctrl) in RUNS.items():
    DATA[variant] = {**load_folder(main), **load_folder(ctrl)}
IMP = load_folder(IMPERATIVES)
present = [v for v in RUNS if DATA[v]]
print("variants with results:", {v: len(DATA[v]) for v in RUNS}, "| imperatives run:", len(IMP), "graphs")


def R(variant, key):
    r = DATA[variant].get(key)
    return None if r is None else r["reciprocity_excess"]


def ci(variant, key):
    r = DATA[variant].get(key)
    return "" if r is None else "[%.1f, %.1f]" % tuple(r["R_ci95"])


def fmt(x, w=7):
    return f"{x:{w}.1f}" if x is not None else " " * (w - 2) + "--"


is_base = lambda k: k.endswith("-pt")
is_wn = lambda k: k.endswith("__wordnet")
main_keys = [k for k in (DATA["unfiltered"] or DATA["default"]) if k.startswith("main__")]
main_keys.sort(key=lambda k: -(R("unfiltered", k) or R("default", k) or 0))

print("\n1. R PER MAIN GRAPH (swap failures flagged with *; 100 replicates, 32 x edges swaps)")
print(f"   {'graph':26}{'unfilt.':>8}{'extract':>8}{'default':>8}{'default 95 % interval':>24}{'strict':>8}{'stored':>8}{'frame':>8}{'edges unf/def':>16}")
for k in main_keys:
    d = DATA["default"].get(k)
    flag = "*" if d and d["swap_failures"] else " "
    eu = DATA["unfiltered"].get(k, {}).get("n_edges")
    ed = d["n_edges"] if d else None
    print(f"   {k[6:]:26}{fmt(R('unfiltered', k), 8)}{fmt(R('extract', k), 8)}{fmt(R('default', k), 8)}{flag}{ci('default', k):>23}"
          f"{fmt(R('strict', k), 8)}{fmt(R('stored', k), 8)}{fmt(R('frame', k), 8)}{str(eu) + '/' + str(ed):>16}")


def groups(variant):
    inst = [k for k in main_keys if not is_base(k) and not is_wn(k) and R(variant, k) is not None]
    base = [k for k in main_keys if is_base(k) and R(variant, k) is not None]
    return inst, base


print("\n2. GROUP RANGES (R)")
for variant in present:
    inst, base = groups(variant)
    if not inst or not base:
        continue
    ri, rb = [R(variant, k) for k in inst], [R(variant, k) for k in base]
    lo, hi = min(inst, key=lambda k: R(variant, k)), max(base, key=lambda k: R(variant, k))
    overlap = DATA[variant][lo]["R_ci95"][0] <= DATA[variant][hi]["R_ci95"][1]
    wn = R(variant, "main__wordnet")
    print(f"   {variant:11} instruct ({len(inst)}) {min(ri):5.1f}-{max(ri):5.1f} median {st.median(ri):5.1f} | base ({len(base)}) {min(rb):5.1f}-{max(rb):5.1f} median {st.median(rb):5.1f}"
          f" | WordNet {fmt(wn, 5)} | lowest instruct {lo[6:]} {R(variant, lo):.1f}, highest base {hi[6:]} {R(variant, hi):.1f}, intervals overlap: {overlap}")

print("\n3. MATCHED GEMMA3 PAIRS: instruct R / base R (ratio)")
print(f"   {'size':6}" + "".join(f"{v:>26}" for v in present))
ratios = {v: {} for v in present}
for s in SIZES:
    cells = []
    for v in present:
        i, b = R(v, f"main__Gemma3-{s}"), R(v, f"main__Gemma3-{s}-pt")
        if i is not None and b:
            ratios[v][s] = i / b
            cells.append(f"{i:7.1f} / {b:5.1f} = {i / b:5.1f}x")
        else:
            cells.append("--")
    print(f"   {s:6}" + "".join(f"{c:>26}" for c in cells))
if "default" in present and "strict" in present and len(ratios["default"]) == 4 and len(ratios["strict"]) == 4:
    rd, rs = ratios["default"], ratios["strict"]
    both = sum(rd[s] >= 2 and rs[s] >= 2 for s in SIZES)
    d_ge = sum(rd[s] >= 2 for s in SIZES)
    d_lt = sum(rd[s] < 2 for s in SIZES)
    s_lt = sum(rs[s] < 2 for s in SIZES)
    if d_lt >= 2:
        reading = "(iii) the pt/it contrast does not survive filtering"
    elif both >= 3:
        reading = "(i) the pt/it contrast survives filtering and is not explained by leaked junk"
    elif d_ge >= 3 and s_lt >= 2:
        reading = "(ii) the contrast depends on how much junk is removed"
    else:
        reading = "mixed"
    print(f"   pre-registered reading (D024): pairs with r_d >= 2 and r_s >= 2: {both} of 4; r_d >= 2: {d_ge}; r_d < 2: {d_lt}; r_s < 2: {s_lt}  ->  {reading}")
else:
    print("   (the pre-registered reading needs the default and the strict run on the main graphs)")
if "default" in present and "frame" in present:
    rf = ratios["frame"]
    if len(rf) == 4:
        ge, lt = sum(rf[s] >= 2 for s in SIZES), sum(rf[s] < 2 for s in SIZES)
        reading_f = ("(A) the zero-shot gap is largely phrasing" if lt >= 3 else
                     "(B) the gap does not depend on the frame words" if ge >= 3 else "mixed")
        print(f"   pre-registered reading (D025): pairs with r_f >= 2: {ge} of 4; r_f < 2: {lt}  ->  {reading_f}")
    print("   R before / after removing the frame words (default filter):")
    for k in main_keys:
        if R("default", k) and R("frame", k):
            print(f"     {k[6:]:26}{R('default', k):6.1f} -> {R('frame', k):6.1f}  ({100 * (R('frame', k) / R('default', k) - 1):+4.0f} %)")

print("\n4. E3: FEW-SHOT BASE R AGAINST THE INSTRUCT MODEL OF THE SAME SIZE")
print(f"   {'size':6}" + "".join(f"{v + ' few-shot':>16}{'instruct':>10}{'factor':>8}" for v in ("unfiltered", "default", "strict") if v in present))
within = {}
for s in SIZES:
    cells = []
    for v in ("unfiltered", "default", "strict"):
        if v not in present:
            continue
        f, i = R(v, f"e3__Gemma3-{s}-pt"), R(v, f"main__Gemma3-{s}")
        if f and i:
            factor = max(f, i) / min(f, i)
            within.setdefault(v, []).append(factor <= 2)
            cells.append(f"{f:16.1f}{i:10.1f}{factor:8.2f}")
        else:
            cells.append(f"{'--':>34}")
    print(f"   {s:6}" + "".join(cells))
for v, flags in within.items():
    if len(flags) == 4:
        print(f"   {v}: few-shot base within a factor 2 of the instruct model at {sum(flags)} of 4 sizes "
              f"({'reaches' if sum(flags) >= 3 else 'does not reach'} the instruct range by the D024 reading)")

print("\n5. E4 AND E5 AGAINST THE MAIN RUN (R of the control / R of the same model in the main run)")
for ds in ("e4", "e5"):
    for v in ("unfiltered", "default", "strict"):
        if v not in present:
            continue
        pairs = []
        for k, r in DATA[v].items():
            if k.startswith(ds + "__"):
                m = "main__" + k[len(ds) + 2:]
                if R(v, m) and r["reciprocity_excess"]:
                    pairs.append((k, r["reciprocity_excess"] / R(v, m)))
        if pairs:
            xs = [x for _, x in pairs]
            fac = [max(x, 1 / x) for x in xs]
            print(f"   {ds} {v:11} n={len(xs):2} median ratio {st.median(xs):5.2f} range {min(xs):.2f}-{max(xs):.2f}; "
                  f"median size of the change x{st.median(fac):.2f}, largest x{max(fac):.2f}")
if "default" in present:
    print("   E5 per model, default filter (ratio to the main run):")
    for k in sorted(k for k in DATA["default"] if k.startswith("e5__")):
        m = "main__" + k[4:]
        if R("default", m):
            u = R("unfiltered", k)
            print(f"     {k[4:]:24} R {R('default', k):6.1f} (unfiltered {fmt(u, 5)})  ratio {R('default', k) / R('default', m):5.2f}")

print("\n6. CLAIM 1: z-SCORES AGAINST THE NULL (all 23 main graphs pooled: 17 instruct, 5 base, WordNet; section 14 gives the groups)")
for v in ("unfiltered", "default", "strict"):
    if v not in present:
        continue
    for lab, key in (("kernel ratio", "kernel_ratio"), ("circulation", "circulation_rate")):
        z = [DATA[v][k]["z"][key] for k in main_keys if k in DATA[v]]
        if z:
            print(f"   {v:11} {lab:13} n={len(z):2} median {st.median(z):+5.2f} range {min(z):+.2f}..{max(z):+.2f} below -2: {sum(x < -2 for x in z)}, above +2: {sum(x > 2 for x in z)}")

if "default" in present:
    print("\n7. CYCLE-LENGTH PROFILE, default filter (observed / null, summed over the graphs of a group)")
    inst, base = groups("default")
    for lab, keys in (("instruct", inst), ("base", base), ("WordNet", ["main__wordnet"])):
        keys = [k for k in keys if k in DATA["default"]]
        cells = []
        for L in range(2, 8):
            o = sum(DATA["default"][k]["cycle_hist_observed_vs_null"][str(L)]["observed"] for k in keys)
            n = sum(DATA["default"][k]["cycle_hist_observed_vs_null"][str(L)]["null_mean"] for k in keys)
            cells.append(f"L{L}: {o}/{n:.0f} = {o / max(n, 1e-9):.2f}x")
        print(f"   {lab:9}" + "  ".join(cells))

if IMP and "main__Qwen3-0.6B" in IMP:
    print("\n8. IMPERATIVES DROPPED (sensitivity, D023 item 4), Qwen3-0.6B")
    r = IMP["main__Qwen3-0.6B"]
    f = r["meta"]["filter"]
    print(f"   R default {fmt(R('default', 'main__Qwen3-0.6B'), 5)} {ci('default', 'main__Qwen3-0.6B')}; unfiltered {fmt(R('unfiltered', 'main__Qwen3-0.6B'), 5)}; "
          f"imperatives dropped {r['reciprocity_excess']:.1f} [{r['R_ci95'][0]:.1f}, {r['R_ci95'][1]:.1f}]; dropped {f['n_dropped']} of {f['n_valid_status']} records; edges {r['n_edges']}")

print("\n9. RECORDS DROPPED (default filter, share of records with a valid status)")
if "default" in present:
    for k in sorted(DATA["default"], key=lambda k: (k.split("__")[0], k)):
        f = DATA["default"][k]["meta"].get("filter")
        if f and f["n_dropped"] / max(f["n_valid_status"], 1) >= 0.05:
            print(f"   {k:34} {100 * f['n_dropped'] / f['n_valid_status']:5.1f} %  ({f['n_dropped']} of {f['n_valid_status']})  edges {DATA['default'][k]['n_edges']}  swap failures {DATA['default'][k]['swap_failures']}")
bad = [(v, k) for v in present for k, r in DATA[v].items() if r["swap_failures"]]
print("\nswap failures (graph not fully randomised):", bad if bad else "none")
zero = [(v, k) for v in present for k, r in DATA[v].items() if r["observed"]["cycles_2"] == 0]
print("graphs with no mutual pair (R = 0):", zero if zero else "none")

print("\n10. BASE GRAPHS AND THE LOWEST INSTRUCT GRAPH IN DETAIL (observed mutual pairs, null mean of mutual pairs, edges, R)")
detail_keys = [k for k in main_keys if is_base(k)] + ["main__Qwen3-0.6B"]
print(f"   {'graph':20}" + "".join(f"{v:>30}" for v in present))
for k in detail_keys:
    cells = []
    for v in present:
        r = DATA[v].get(k)
        cells.append("--" if r is None else f"obs {r['observed']['cycles_2']:3d} null {r['null_mean']['cycles_2']:5.2f} E {r['n_edges']:5d} R {r['reciprocity_excess']:5.1f}")
    print(f"   {k[6:]:20}" + "".join(f"{c:>30}" for c in cells))

print("\n11. GRAPHS BEYOND |z| = 2 (claim 1)")
for v in present:
    for lab, key in (("kernel", "kernel_ratio"), ("circulation", "circulation_rate")):
        beyond = [(k[6:], round(DATA[v][k]["z"][key], 1)) for k in main_keys if k in DATA[v] and abs(DATA[v][k]["z"][key]) > 2]
        if beyond:
            print(f"   {v:11} {lab:12} {beyond}")

print("\n12. HUBS IN THE FILTERED GRAPHS (default filter): words used in the most definitions, share of edges, words without incoming edges")
import collections  # noqa: E402

GRAPH_DIR = RES / RUNS["default"][0] / "graphs"
for key in ("main__Gemma3-270M-pt", "main__Gemma3-1B-pt", "main__Gemma3-4B-pt", "main__Gemma3-12B-pt", "main__Gemma3-27B-pt",
            "main__Gemma3-27B", "main__Qwen2.5-72B", "main__Qwen3-0.6B"):
    path = GRAPH_DIR / f"{key}.json"
    if not path.exists():
        continue
    g = json.load(open(path, encoding="utf-8"))
    out_deg = collections.Counter(u for u, v in g["edges"])
    in_deg = collections.Counter(v for u, v in g["edges"])
    total = len(g["edges"])
    top5 = sum(c for _, c in out_deg.most_common(5)) / total
    print(f"   {key[6:]:18} edges {total:5d}; top out-degree {out_deg.most_common(6)}; top-5 hubs carry {100 * top5:.0f} % of the edges; "
          f"{sum(1 for n in g['nodes'] if in_deg[n] == 0)} of {len(g['nodes'])} words have no incoming edge")

print("\n13. E3 270M AND THE E5 GRAPHS THE FILTER CHANGES MOST (unfiltered -> default: edges, observed mutual pairs, null mean, R, share dropped)")
if "default" in present:
    for v in ("unfiltered", "default", "strict"):
        if v in present and R(v, "e3__Gemma3-270M-pt") is not None:
            print(f"   E3 Gemma3-270M-pt, {v}: R {R(v, 'e3__Gemma3-270M-pt'):.1f}")
    for k in sorted(k for k in DATA["default"] if k.startswith("e5__")):
        a, b = DATA["unfiltered"].get(k), DATA["default"][k]
        f = b["meta"]["filter"]
        share = 100 * f["n_dropped"] / max(f["n_valid_status"], 1)
        if a and (share >= 25 or b["swap_failures"]):
            print(f"   {k:28} edges {a['n_edges']:5d} -> {b['n_edges']:5d}; pairs {a['observed']['cycles_2']:3d} -> {b['observed']['cycles_2']:3d}; "
                  f"null {a['null_mean']['cycles_2']:5.2f} -> {b['null_mean']['cycles_2']:5.2f}; R {a['reciprocity_excess']:5.1f} -> {b['reciprocity_excess']:5.1f}; "
                  f"dropped {share:3.0f} %; swap failures {b['swap_failures']}/100"
                  f"{'; null mean below the floor of 0.5' if b['null_mean']['cycles_2'] < 0.5 else ''}")

# Added 2026-10-02 after a review found that the medians of section 6 pool all 23 graphs, while claim 1 had quoted them
# as medians of the instruct models.
print("\n14. CLAIM 1 BY GROUP: z-scores against the null, instruct models only (17), base models only (5) and WordNet (section 6 pools all 23)")
GROUPS14 = (("instruct", lambda k: not is_base(k) and not is_wn(k)), ("base", is_base), ("WordNet", is_wn))
for lab, key in (("circulation", "circulation_rate"), ("kernel ratio", "kernel_ratio")):
    for gname, pred in GROUPS14:
        for v in ("unfiltered", "default", "strict"):
            if v not in present:
                continue
            z = [DATA[v][k]["z"][key] for k in main_keys if k in DATA[v] and pred(k)]
            if z:
                print(f"   {lab:13} {gname:9} {v:11} n={len(z):2} median {st.median(z):+5.2f} range {min(z):+.2f}..{max(z):+.2f} "
                      f"below 0: {sum(x < 0 for x in z):2}, below -2: {sum(x < -2 for x in z)}, above +2: {sum(x > 2 for x in z)}")

# Added 2026-10-02: a draft amendment of D026 said that R does not rise with size among the instruct models. It does within Qwen3.
import re  # noqa: E402

from scipy.stats import spearmanr  # noqa: E402

print("\n15. R AGAINST MODEL SIZE, instruct models, default filter (descriptive; Spearman rank correlation of R with the size in billions of parameters)")


def size_b(key):
    return float(re.search(r"-(\d+(?:\.\d+)?)B", key).group(1))


inst15 = [k for k in main_keys if not is_base(k) and not is_wn(k) and k in DATA["default"]]
families = {}
for k in inst15:
    families.setdefault(k[6:].split("-")[0], []).append(k)
for fam, keys in sorted(families.items()):
    keys.sort(key=lambda k: (size_b(k), k))
    rho, p = spearmanr([size_b(k) for k in keys], [R("default", k) for k in keys])
    print(f"   {fam:8} " + "  ".join(f"{k[6:].split('-', 1)[1]} {R('default', k):.1f}" for k in keys) + f"   rho {rho:+.2f} (n={len(keys)}, p={p:.2f})")
rho, p = spearmanr([size_b(k) for k in inst15], [R("default", k) for k in inst15])
print(f"   all {len(inst15)} instruct models: rho {rho:+.2f} (p={p:.2f})")
