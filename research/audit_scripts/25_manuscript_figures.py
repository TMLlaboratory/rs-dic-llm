"""Figures of the manuscript draft (manuscript/draft_v0.md), drawn from the per-graph results of the null-model runs.

Fig. 1  pipeline (a drawing, no data).
Fig. 2  kernel ratio of each graph against its null mean (unfiltered and default filter): claim 1.
Fig. 3  cycle-length profile, observed / null, by group (default filter): claim 2.
Fig. 4  R against model size: (a) the Gemma3 pairs zero-shot and with three examples, (b) the instruct models by family: claims 2 and 3.
Fig. 5  R of the Gemma3 graphs as built and on the same entries (the zero-shot survivors, D029): coverage and the zero-shot gap: claim 3.
Error bars of R are the exact Poisson 95 % ranges of the observed number of mutual pairs divided by the null mean (floor 0.5).
Output: manuscript/figures/fig1_pipeline.png ... fig5_coverage.png (no random element: the figures are reproducible).
"""
import glob
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from scipy.stats import chi2  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
RES = ROOT / "results_2026-10-01_Local"
FIG = ROOT / "manuscript" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
RUNS = {"unfiltered": ("e1d_null_unfiltered_32x", "e1d_null_unfiltered_32x_controls"),
        "default": ("e2_filtered_default_main_32x", "e2_filtered_default_controls_32x")}
BLUE, VERMILLION, GREEN, ORANGE, PINK, GREY = "#0072B2", "#D55E00", "#009E73", "#E69F00", "#CC79A7", "#444444"
plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 7, "figure.dpi": 100})


def load(folder):
    out = {}
    for p in glob.glob(str(RES / folder / "results" / "*.json")):
        r = json.load(open(p, encoding="utf-8"))
        out[r["key"]] = r
    return out


DATA = {v: {**load(a), **load(b)} for v, (a, b) in RUNS.items()}


def r_range(rec):
    obs, null = rec["observed"]["cycles_2"], max(rec["null_mean"]["cycles_2"], 0.5)
    lo = 0.0 if obs == 0 else chi2.ppf(0.025, 2 * obs) / 2
    hi = chi2.ppf(0.975, 2 * (obs + 1)) / 2
    return obs / null, lo / null, hi / null


def size_b(key):
    m = re.search(r"-(\d+(?:\.\d+)?)([MB])", key)
    return float(m.group(1)) * (0.001 if m.group(2) == "M" else 1.0)


is_base = lambda k: k.endswith("-pt")
is_wn = lambda k: k.endswith("__wordnet")
main_keys = [k for k in DATA["default"] if k.startswith("main__")]
instruct = [k for k in main_keys if not is_base(k) and not is_wn(k)]
base = [k for k in main_keys if is_base(k)]
family = lambda k: k[6:].split("-")[0]
D = DATA["default"]

# ----------------------------------------------------------------------------------------------------------- Fig. 1
fig, ax = plt.subplots(figsize=(7.0, 1.9))
ax.set_xlim(0, 100)
ax.set_ylim(0, 22)
ax.axis("off")
boxes = [
    (0.5, "Prompt\n3,000 entries,\nzero-shot or with\nthree examples"),
    (17.0, "22 models +\nWordNet glosses\none run each\n(temperature 0.7)"),
    (33.5, "First sentence\nof each output"),
    (50.0, "Rule filter\n(keep unless a rule\nfires; dropped\nrecords keep\ntheir node)"),
    (66.5, "Definition graph\nu → v iff u is in\nthe definition of v\n(2,750 lemmas)"),
    (83.0, "Null model\n(degree-preserving)\nkernel, cycles,\nmutual pairs (R)"),
]
for x, text in boxes:
    ax.add_patch(FancyBboxPatch((x, 3.5), 14.5, 15, boxstyle="round,pad=0.2,rounding_size=1.0", fc="#EEF3F8", ec=GREY, lw=0.8))
    ax.text(x + 7.25, 11, text, ha="center", va="center", fontsize=5.4)
for x in (15.2, 31.7, 48.2, 64.7, 81.2):
    ax.annotate("", xy=(x + 1.6, 11), xytext=(x, 11), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.9))
fig.savefig(FIG / "fig1_pipeline.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------------------------------------------- Fig. 2
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.1), sharex=False, sharey=False)
for ax, variant, title in ((axes[0], "unfiltered", "(a) unfiltered graphs"), (axes[1], "default", "(b) default filter, first sentence")):
    for keys, colour, label, marker in ((instruct, BLUE, "instruct (17)", "o"), (base, VERMILLION, "pretrained, zero-shot (5)", "s"), (["main__wordnet"], "black", "WordNet", "*")):
        pts = [(DATA[variant][k]["null_mean"]["kernel_ratio"], DATA[variant][k]["observed"]["kernel_ratio"], 2 * DATA[variant][k]["null_sd"]["kernel_ratio"]) for k in keys if k in DATA[variant]]
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
fig, ax = plt.subplots(figsize=(4.6, 2.9))
groups = (("17 instruct models", instruct, BLUE), ("5 pretrained models", base, VERMILLION), ("WordNet", ["main__wordnet"], "black"))
width = 0.26
for j, (label, keys, colour) in enumerate(groups):
    ratios = []
    for L in range(2, 8):
        o = sum(D[k]["cycle_hist_observed_vs_null"][str(L)]["observed"] for k in keys)
        n = sum(D[k]["cycle_hist_observed_vs_null"][str(L)]["null_mean"] for k in keys)
        ratios.append(o / n if n > 0 else float("nan"))
    xs = [L + (j - 1) * width for L in range(2, 8)]
    ax.bar(xs, [max(r, 0.01) for r in ratios], width=width, color=colour, label=label)
ax.axhline(1, color="#999999", lw=0.8, ls="--")
ax.set_yscale("log")
ax.set_ylim(0.05, 40)
ax.set_xlabel("cycle length")
ax.set_ylabel("observed / null (summed over the group)")
ax.set_title("Short cycles are in excess, long ones are not (default filter)")
ax.legend(frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig(FIG / "fig3_cycle_profile.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------------------------------------------- Fig. 4
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2))
ax = axes[0]
wn, wlo, whi = r_range(D["main__wordnet"])
ax.axhspan(wlo, whi, color="#DDDDDD", alpha=0.7, lw=0)
ax.axhline(wn, color="black", lw=0.8, ls="--", label="WordNet (grey: 95 % range)")
series = (
    ("instruct", [(size_b(k), D[k]) for k in instruct if family(k) == "Gemma3"], BLUE, "o", 0.93),
    ("pretrained, zero-shot", [(size_b(k), D[k]) for k in base], VERMILLION, "s", 1.0),
    ("pretrained, three examples (E3)", [(size_b(k), D[k]) for k in D if k.startswith("e3__")], GREEN, "^", 1.07),
)
for label, pts, colour, marker, shift in series:
    pts.sort(key=lambda p: p[0])
    xs = [p[0] * shift for p in pts]
    rs = [r_range(p[1]) for p in pts]
    ax.errorbar(xs, [r[0] for r in rs], yerr=[[r[0] - r[1] for r in rs], [r[2] - r[0] for r in rs]], fmt=marker + "-", color=colour, ms=4, lw=1.0,
                elinewidth=0.7, capsize=1.8, label=label)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xticks([0.27, 1, 4, 12, 27])
ax.set_xticklabels(["270M", "1B", "4B", "12B", "27B"])
ax.set_yticks([1, 2, 5, 10, 20, 50])
ax.set_yticklabels(["1", "2", "5", "10", "20", "50"])
ax.set_ylim(0.6, 80)
ax.set_xlabel("Gemma 3 size")
ax.set_ylabel("R (reciprocity excess)")
ax.set_title("(a) Gemma 3: zero-shot and three examples")
ax.legend(frameon=False, loc="lower right")
ax = axes[1]
ax.axhspan(wlo, whi, color="#DDDDDD", alpha=0.7, lw=0)
ax.axhline(wn, color="black", lw=0.8, ls="--", label="WordNet (grey: 95 % range)")
for fam, colour, marker, label in (("Gemma3", BLUE, "o", "Gemma 3"), ("Qwen2.5", ORANGE, "s", "Qwen2.5"), ("Qwen3", PINK, "D", "Qwen3")):
    pts = sorted(((size_b(k), D[k]) for k in instruct if family(k) == fam), key=lambda p: p[0])
    rs = [r_range(p[1]) for p in pts]
    ax.errorbar([p[0] for p in pts], [r[0] for r in rs], yerr=[[r[0] - r[1] for r in rs], [r[2] - r[0] for r in rs]], fmt=marker + "-", color=colour, ms=3.5,
                lw=0.9, elinewidth=0.6, capsize=1.5, label=label)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xticks([0.5, 1, 4, 14, 72])
ax.set_xticklabels(["0.5B", "1B", "4B", "14B", "72B"])
ax.set_yticks([1, 2, 5, 10, 20, 50])
ax.set_yticklabels(["1", "2", "5", "10", "20", "50"])
ax.set_ylim(0.6, 80)
ax.set_xlabel("model size (parameters)")
ax.set_title("(b) instruct models by family")
ax.legend(frameon=False, loc="lower right")
fig.tight_layout()
fig.savefig(FIG / "fig4_R_vs_size.png", dpi=220, bbox_inches="tight")
plt.close(fig)
# ----------------------------------------------------------------------------------------------------------- Fig. 5
D029 = ROOT / "results_2026-10-02_Local" / "d029_survivor_restriction" / "results"
X = {}
for p in glob.glob(str(D029 / "*.json")):
    r = json.load(open(p, encoding="utf-8"))
    X[r["key"]] = r
assert len(X) == 28, len(X)
SZ = (("1B", 1.0), ("4B", 4.0), ("12B", 12.0), ("27B", 27.0))
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2), sharey=True)


def draw(ax, label, recs, colour, marker, shift, filled=True):
    rs = [r_range(r) for r in recs]
    xs = [v * shift for _, v in SZ]
    ax.errorbar(xs, [r[0] for r in rs], yerr=[[r[0] - r[1] for r in rs], [r[2] - r[0] for r in rs]], fmt=marker + "-", color=colour, ms=4, lw=1.0,
                elinewidth=0.7, capsize=1.8, label=label, mfc=colour if filled else "white")


ax = axes[0]
draw(ax, "instruct, all entries", [D[f"main__Gemma3-{s}"] for s, _ in SZ], BLUE, "o", 0.93)
draw(ax, "pretrained, three examples, all entries", [D[f"e3__Gemma3-{s}-pt"] for s, _ in SZ], GREEN, "^", 1.07)
draw(ax, "pretrained, zero-shot (about half of the entries)", [D[f"main__Gemma3-{s}-pt"] for s, _ in SZ], VERMILLION, "s", 1.0)
ax.set_title("(a) graphs as built")
ax = axes[1]
draw(ax, "instruct, same entries", [X[f"d029__itS_{s}"] for s, _ in SZ], BLUE, "o", 0.93, filled=False)
draw(ax, "pretrained, three examples, same entries", [X[f"d029__fsS_{s}"] for s, _ in SZ], GREEN, "^", 1.07, filled=False)
draw(ax, "pretrained, zero-shot", [D[f"main__Gemma3-{s}-pt"] for s, _ in SZ], VERMILLION, "s", 1.0)
for i, (s, v) in enumerate(SZ):
    rands = [X[f"d029__fsR{k}_{s}"]["reciprocity_excess"] for k in range(1, 6)]
    ax.plot([v * 1.16] * 5, rands, ".", color=GREY, ms=3, alpha=0.8, label="three examples, five random halves" if i == 0 else None)
ax.set_title("(b) the same entries (the zero-shot survivors)")
for ax in axes:
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([1, 4, 12, 27])
    ax.set_xticklabels(["1B", "4B", "12B", "27B"])
    ax.set_xlim(0.7, 40)
    ax.set_yticks([1, 2, 5, 10, 20, 50])
    ax.set_yticklabels(["1", "2", "5", "10", "20", "50"])
    ax.set_ylim(0.6, 80)
    ax.set_xlabel("Gemma 3 size")
    ax.legend(frameon=False, loc="upper right", fontsize=6)
axes[0].set_ylabel("R (reciprocity excess)")
fig.tight_layout()
fig.savefig(FIG / "fig5_coverage.png", dpi=220, bbox_inches="tight")
plt.close(fig)
print("figures written to", FIG)
