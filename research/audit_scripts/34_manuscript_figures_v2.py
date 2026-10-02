"""Figures of manuscript/draft_v2.md (draft v1 and its figures in manuscript/figures/, made by script 25, are kept unchanged).

Fig. 1  is that of v1 (copied unchanged: the pipeline).
Fig. 2  kernel ratio of each graph against its null mean, default filter: (a) the three-edge null of our first analysis (100 replicates), (b) the double-edge null (D033, 20 replicates).
Fig. 3  cycle-length profile, observed / null summed over a group, default filter, against both nulls.
Fig. 4  R against the double-edge null versus R against the three-edge null for every graph of the default filter (D032): the graphs on the diagonal are the same under both nulls.
Fig. 5  scale (D031, D032): for each family of instruct models against parameter count: (a) R (double-edge null) with the exact Poisson 95 % range and WordNet's band, (b) the Jaccard index of the model's
        mutual pairs with WordNet's, (c) the observed mutual pairs, (d) the mean number of mutual pairs in the null (filled: double-edge, open: three-edge). Qwen3-4B-Instruct-2507, a second model at 4B,
        is drawn apart (open diamond) and left out of the trends.
Fig. 6  the zero-shot gap (D029, D032): (a) R of the Gemma 3 graphs as built, (b) R on the same entries (the zero-shot survivors) with five random halves of the few-shot graph, (c) the observed mutual
        pairs on the same entries. R against the double-edge null.
Output: manuscript/figures_v2/fig1_pipeline.png ... fig6_coverage.png (no random element: the figures are reproducible).
"""
import glob
import json
import re
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import chi2  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
RES = ROOT / "results_2026-10-01_Local"
R2 = ROOT / "results_2026-10-02_Local"
RUN = RES / "e2_filtered_default_main_32x"
FIG1 = ROOT / "manuscript" / "figures"
FIG = ROOT / "manuscript" / "figures_v2"
FIG.mkdir(parents=True, exist_ok=True)
BLUE, VERMILLION, GREEN, ORANGE, PINK, GREY = "#0072B2", "#D55E00", "#009E73", "#E69F00", "#CC79A7", "#444444"
plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 7, "figure.dpi": 100})
SZ = (("1B", 1.0), ("4B", 4.0), ("12B", 12.0), ("27B", 27.0))
LATER = "Qwen3-4B-Instruct-2507"
# remove figures of earlier builds that this build does not draw
for stale in ("fig4_scale.png", "fig5_coverage.png"):
    if (FIG / stale).exists():
        (FIG / stale).unlink()
shutil.copyfile(FIG1 / "fig1_pipeline.png", FIG / "fig1_pipeline.png")


def load_dir(folder):
    return {r["key"]: r for r in (json.load(open(p, encoding="utf-8")) for p in glob.glob(str(Path(folder) / "results" / "*.json")))}


def load_flat(folder):
    return {r["key"]: r for r in (json.load(open(p, encoding="utf-8")) for p in glob.glob(str(Path(folder) / "*.json")))}


OLD = {**load_dir(RUN), **load_dir(RES / "e2_filtered_default_controls_32x")}  # three-edge null
NEW = load_flat(R2 / "d032_double_swap_null" / "results")  # double-edge null
D33 = load_flat(R2 / "d033_double_swap_full_stats" / "results")
assert len(NEW) == 88 and len(D33) == 23


def r_range(rec):
    obs, null = rec["observed"]["cycles_2"], max(rec["null_mean"]["cycles_2"], 0.5)
    lo = 0.0 if obs == 0 else chi2.ppf(0.025, 2 * obs) / 2
    hi = chi2.ppf(0.975, 2 * (obs + 1)) / 2
    return obs / null, lo / null, hi / null


def count_range(rec):
    obs = rec["observed"]["cycles_2"]
    lo = 0.0 if obs == 0 else chi2.ppf(0.025, 2 * obs) / 2
    return obs, lo, chi2.ppf(0.975, 2 * (obs + 1)) / 2


def size_b(name):
    m = re.search(r"-(\d+(?:\.\d+)?)([MB])", name)
    return float(m.group(1)) * (0.001 if m.group(2) == "M" else 1.0)


def pairs(key):
    g = json.loads((RUN / "graphs" / f"{key}.json").read_text(encoding="utf-8"))
    edges = {tuple(e) for e in g["edges"]}
    return {tuple(sorted((u, v))) for (u, v) in edges if (v, u) in edges and u != v}


is_base = lambda k: k.endswith("-pt")
is_wn = lambda k: k.endswith("__wordnet")
main_keys = sorted(k for k in OLD if k.startswith("main__"))
instruct_keys = [k for k in main_keys if not is_base(k) and not is_wn(k)]
base_keys = [k for k in main_keys if is_base(k)]
fewshot_keys = sorted(k for k in OLD if k.startswith("e3__"))
assert len(instruct_keys) == 17 and len(base_keys) == 5 and len(fewshot_keys) == 5
instruct = [k[6:] for k in instruct_keys]
family = lambda n: n.split("-")[0]
FAM = (("Gemma3", BLUE, "o", "Gemma 3"), ("Qwen2.5", ORANGE, "s", "Qwen2.5"), ("Qwen3", PINK, "D", "Qwen3"))

# ----------------------------------------------------------------------------------------------------------- Fig. 2
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.1))
for ax, data, title in ((axes[0], OLD, "(a) three-edge null"), (axes[1], D33, "(b) double-edge null")):
    for keys, colour, label, marker in ((instruct_keys, BLUE, "instruct (17)", "o"), (base_keys, VERMILLION, "pretrained, zero-shot (5)", "s"), (["main__wordnet"], "black", "WordNet", "*")):
        pts = [(data[k]["null_mean"]["kernel_ratio"], data[k]["observed"]["kernel_ratio"], 2 * data[k]["null_sd"]["kernel_ratio"]) for k in keys]
        ax.errorbar([p[0] for p in pts], [p[1] for p in pts], xerr=[p[2] for p in pts], fmt=marker, color=colour, ms=7 if marker == "*" else 3.8, lw=0.6,
                    elinewidth=0.5, alpha=0.9, label=label, zorder=3)
    lim = (0.0, 0.31)
    ax.plot(lim, lim, color="#999999", lw=0.8, ls="--", zorder=1)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("kernel ratio in the null (mean ± 2 SD)")
    ax.set_title(title)
    ax.set_aspect("equal")
axes[0].set_ylabel("observed kernel ratio")
axes[0].legend(loc="upper left", frameon=False)
fig.tight_layout()
fig.savefig(FIG / "fig2_kernel_vs_null.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------------------------------------------- Fig. 3
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9), sharey=True)
groups = (("17 instruct models", instruct_keys, BLUE), ("5 pretrained models", base_keys, VERMILLION), ("WordNet", ["main__wordnet"], "black"))
width = 0.26
for ax, data, title in ((axes[0], OLD, "(a) three-edge null"), (axes[1], D33, "(b) double-edge null")):
    for j, (label, keys, colour) in enumerate(groups):
        ratios = []
        for L in range(2, 8):
            o = sum(data[k]["cycle_hist_observed_vs_null"][str(L)]["observed"] for k in keys)
            n = sum(data[k]["cycle_hist_observed_vs_null"][str(L)]["null_mean"] for k in keys)
            ratios.append(o / n if n > 0 else float("nan"))
        xs = [L + (j - 1) * width for L in range(2, 8)]
        ax.bar(xs, [max(r, 0.01) for r in ratios], width=width, color=colour, label=label)
    ax.axhline(1, color="#999999", lw=0.8, ls="--")
    ax.set_yscale("log")
    ax.set_ylim(0.05, 60)
    ax.set_xlabel("cycle length")
    ax.set_title(title)
axes[0].set_ylabel("observed / null (summed over the group)")
axes[0].legend(frameon=False, loc="upper right", fontsize=6)
fig.tight_layout()
fig.savefig(FIG / "fig3_cycle_profile.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------------------------------------------- Fig. 4
fig, ax = plt.subplots(figsize=(4.4, 4.2))
sets = (
    ("Gemma 3 instruct", [k for k in instruct_keys if family(k[6:]) == "Gemma3"], BLUE, "o"),
    ("Qwen2.5 instruct", [k for k in instruct_keys if family(k[6:]) == "Qwen2.5"], ORANGE, "s"),
    ("Qwen3 instruct", [k for k in instruct_keys if family(k[6:]) == "Qwen3"], PINK, "D"),
    ("pretrained, zero-shot", base_keys, VERMILLION, "v"),
    ("pretrained, few-shot", fewshot_keys, GREEN, "^"),
    ("WordNet", ["main__wordnet"], "black", "*"),
)
for label, keys, colour, marker in sets:
    xs = [r_range(OLD[k])[0] for k in keys]
    ys = [r_range(NEW[k])[0] for k in keys]
    lo = [y - r_range(NEW[k])[1] for y, k in zip(ys, keys)]
    hi = [r_range(NEW[k])[2] - y for y, k in zip(ys, keys)]
    ax.errorbar(xs, ys, yerr=[lo, hi], fmt=marker, color=colour, ms=7 if marker == "*" else 4.2, lw=0.5, elinewidth=0.4, alpha=0.9, label=label, zorder=3)
lim = (1.5, 90)
ax.plot(lim, lim, color="#999999", lw=0.8, ls="--", zorder=1)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(lim)
ax.set_ylim(lim)
ticks = [2, 5, 10, 20, 50]
ax.set_xticks(ticks)
ax.set_xticklabels([str(t) for t in ticks])
ax.set_yticks(ticks)
ax.set_yticklabels([str(t) for t in ticks])
ax.set_xlabel("R, three-edge null (our first analysis)")
ax.set_ylabel("R, double-edge null")
ax.legend(frameon=False, loc="upper left", fontsize=6)
ax.set_aspect("equal")
fig.tight_layout()
fig.savefig(FIG / "fig4_r_two_nulls.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------------------------------------------- Fig. 5
P_WN = pairs("main__wordnet")
fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.6), sharex=True)
wn, wlo, whi = r_range(NEW["main__wordnet"])
panels = {
    "R": (axes[0][0], "(a) R, with WordNet's range in grey", lambda n: r_range(NEW[f"main__{n}"])),
    "J": (axes[0][1], "(b) Jaccard index with WordNet's mutual pairs", lambda n: (len(pairs(f"main__{n}") & P_WN) / len(pairs(f"main__{n}") | P_WN),) * 3),
    "pairs": (axes[1][0], "(c) observed mutual pairs", lambda n: count_range(NEW[f"main__{n}"])),
    "null": (axes[1][1], "(d) mean mutual pairs in the null\n(filled: double-edge; open: three-edge)", lambda n: (NEW[f"main__{n}"]["null_mean"]["cycles_2"],) * 3),
}
for stat, (ax, title, fn) in panels.items():
    if stat == "R":
        ax.axhspan(wlo, whi, color="#DDDDDD", alpha=0.7, lw=0)
        ax.axhline(wn, color="black", lw=0.8, ls="--", label="WordNet")
    for fam, colour, marker, label in FAM:
        names = sorted((n for n in instruct if family(n) == fam and n != LATER), key=size_b)
        vals = [fn(n) for n in names]
        xs = [size_b(n) for n in names]
        if stat in ("R", "pairs"):
            ax.errorbar(xs, [v[0] for v in vals], yerr=[[v[0] - v[1] for v in vals], [v[2] - v[0] for v in vals]], fmt=marker + "-", color=colour, ms=3.5, lw=0.9,
                        elinewidth=0.6, capsize=1.5, label=label)
        else:
            ax.plot(xs, [v[0] for v in vals], marker + "-", color=colour, ms=3.5, lw=0.9, label=label)
        if stat == "null":  # the first null, open symbols
            ax.plot(xs, [OLD[f"main__{n}"]["null_mean"]["cycles_2"] for n in names], marker + ":", color=colour, ms=3.5, lw=0.7, mfc="white", alpha=0.9)
        if fam == "Qwen3" and LATER in instruct:
            v = fn(LATER)
            ax.plot([size_b(LATER) * 1.06], [v[0]], marker, mfc="white", color=colour, ms=4.5, label=LATER if stat == "R" else None)
            if stat == "null":
                ax.plot([size_b(LATER) * 1.06], [OLD[f"main__{LATER}"]["null_mean"]["cycles_2"]], marker, mfc="white", color=colour, ms=4.5, alpha=0.5)
    ax.set_xscale("log")
    if stat in ("R", "pairs", "null"):
        ax.set_yscale("log")
    ax.set_title(title)
    ax.set_xticks([0.5, 1, 4, 14, 72])
    ax.set_xticklabels(["0.5B", "1B", "4B", "14B", "72B"])
axes[0][0].set_yticks([10, 20, 50])
axes[0][0].set_yticklabels(["10", "20", "50"])
axes[0][0].set_ylim(8, 90)
axes[0][0].set_ylabel("R (reciprocity excess)")
axes[0][1].set_ylabel("Jaccard index")
axes[1][0].set_ylabel("mutual pairs")
axes[1][0].set_yticks([10, 20, 50, 100])
axes[1][0].set_yticklabels(["10", "20", "50", "100"])
axes[1][1].set_ylabel("pairs in the null")
axes[1][1].set_yticks([1, 2, 5])
axes[1][1].set_yticklabels(["1", "2", "5"])
for ax in axes[1]:
    ax.set_xlabel("model size (parameters)")
axes[0][0].legend(frameon=False, loc="upper right", fontsize=6)
fig.tight_layout()
fig.savefig(FIG / "fig5_scale.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------------------------------------------- Fig. 6
fig, axes = plt.subplots(1, 3, figsize=(7.4, 3.2))


def draw(ax, label, recs, colour, marker, shift, kind, filled=True):
    rs = [(r_range if kind == "R" else count_range)(r) for r in recs]
    xs = [v * shift for _, v in SZ]
    ax.errorbar(xs, [r[0] for r in rs], yerr=[[r[0] - r[1] for r in rs], [r[2] - r[0] for r in rs]], fmt=marker + "-", color=colour, ms=4, lw=1.0,
                elinewidth=0.7, capsize=1.8, label=label, mfc=colour if filled else "white")


ax = axes[0]
draw(ax, "instruct, all entries", [NEW[f"main__Gemma3-{s}"] for s, _ in SZ], BLUE, "o", 0.93, "R")
draw(ax, "pretrained, few-shot, all entries", [NEW[f"e3__Gemma3-{s}-pt"] for s, _ in SZ], GREEN, "^", 1.07, "R")
draw(ax, "pretrained, zero-shot (about half of the entries)", [NEW[f"main__Gemma3-{s}-pt"] for s, _ in SZ], VERMILLION, "s", 1.0, "R")
ax.set_title("(a) R, graphs as built")
ax = axes[1]
draw(ax, "instruct, same entries", [NEW[f"d029__itS_{s}"] for s, _ in SZ], BLUE, "o", 0.93, "R", filled=False)
draw(ax, "few-shot, same entries", [NEW[f"d029__fsS_{s}"] for s, _ in SZ], GREEN, "^", 1.07, "R", filled=False)
draw(ax, "zero-shot", [NEW[f"main__Gemma3-{s}-pt"] for s, _ in SZ], VERMILLION, "s", 1.0, "R")
for i, (s, v) in enumerate(SZ):
    rands = [r_range(NEW[f"d029__fsR{k}_{s}"])[0] for k in range(1, 6)]
    ax.plot([v * 1.16] * 5, rands, ".", color=GREY, ms=3, alpha=0.8, label="few-shot, five random halves" if i == 0 else None)
ax.set_title("(b) R, the same entries")
ax = axes[2]
draw(ax, "instruct, same entries", [NEW[f"d029__itS_{s}"] for s, _ in SZ], BLUE, "o", 0.93, "pairs", filled=False)
draw(ax, "few-shot, same entries", [NEW[f"d029__fsS_{s}"] for s, _ in SZ], GREEN, "^", 1.07, "pairs", filled=False)
draw(ax, "zero-shot", [NEW[f"main__Gemma3-{s}-pt"] for s, _ in SZ], VERMILLION, "s", 1.0, "pairs")
for i, (s, v) in enumerate(SZ):
    rands = [NEW[f"d029__fsR{k}_{s}"]["observed"]["cycles_2"] for k in range(1, 6)]
    ax.plot([v * 1.16] * 5, rands, ".", color=GREY, ms=3, alpha=0.8, label="few-shot, five random halves" if i == 0 else None)
ax.set_title("(c) observed mutual pairs, the same entries")
for j, ax in enumerate(axes):
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([1, 4, 12, 27])
    ax.set_xticklabels(["1B", "4B", "12B", "27B"])
    ax.set_xlim(0.7, 40)
    ax.set_xlabel("Gemma 3 size")
    if j < 2:
        ax.set_yticks([2, 5, 10, 20, 50])
        ax.set_yticklabels(["2", "5", "10", "20", "50"])
        ax.set_ylim(1.2, 250)
    else:
        ax.set_yticks([2, 5, 10, 20, 50])
        ax.set_yticklabels(["2", "5", "10", "20", "50"])
        ax.set_ylim(1.5, 250)
    ax.legend(frameon=False, loc="upper center", fontsize=5.5)
axes[0].set_ylabel("R (reciprocity excess)")
axes[2].set_ylabel("mutual pairs")
fig.tight_layout()
fig.savefig(FIG / "fig6_coverage.png", dpi=220, bbox_inches="tight")
plt.close(fig)
print("figures written to", FIG)
