"""D034: the prompt controls (E4: 8 words or fewer; E5: no chat template) against the double-edge swap null.

Reads results_2026-10-02_Local/d034_controls_double_swap/results/ (the controls, experiments/d034_controls_double_swap.py), results_2026-10-02_Local/d032_double_swap_null/results/ (the main graphs
of the same models, D032) and the stored results of the paper's three-edge null (results_2026-10-01_Local/e2_filtered_default_{main,controls}_32x/results/). For each control and each null it
prints, per instruct model, R of the control, R of the main run and their ratio, and the summary of section 5 of 17_filtered_vs_unfiltered.py over the models where both R are above 0: median ratio,
range, median size of the change max(ratio, 1/ratio), its largest value, number of models within a factor 2. The one reading of D034: the factor 2 of the earlier readings is reconsidered if the
median size of the change of either control exceeds 2 under the double-edge null. Output is recorded in outputs/38_controls_double_swap.txt.
"""
import glob
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
OLD_MAIN = ROOT / "results_2026-10-01_Local" / "e2_filtered_default_main_32x" / "results"
OLD_CTRL = ROOT / "results_2026-10-01_Local" / "e2_filtered_default_controls_32x" / "results"
NEW_MAIN = ROOT / "results_2026-10-02_Local" / "d032_double_swap_null" / "results"
NEW_CTRL = ROOT / "results_2026-10-02_Local" / "d034_controls_double_swap" / "results"


def load(folder, prefix):
    return {Path(p).stem: json.loads(Path(p).read_text(encoding="utf-8")) for p in glob.glob(str(folder / f"{prefix}*.json"))}


old = {**load(OLD_MAIN, "main__"), **load(OLD_CTRL, "e3__"), **load(OLD_CTRL, "e4__"), **load(OLD_CTRL, "e5__")}
new = {**load(NEW_MAIN, "main__"), **load(NEW_MAIN, "e3__"), **load(NEW_CTRL, "e4__"), **load(NEW_CTRL, "e5__")}
models = sorted(k[6:] for k in old if k.startswith("main__") and not k.endswith("-pt") and not k.endswith("wordnet"))
assert len(models) == 17, models
missing = [f"{ds}__{m}" for ds in ("e4", "e5") for m in models if f"{ds}__{m}" not in new]
if missing:
    print(f"NOT FINISHED: {len(missing)} of 34 control graphs missing")
    sys.exit(0)

NAMES = {"e4": "E4 (answers of 8 words or fewer)", "e5": "E5 (no chat template)"}
summary = {}
for ds in ("e4", "e5"):
    print(f"\n{NAMES[ds]}: R of the control, R of the main run, ratio; observed pairs / null mean in the control. Left: the paper's three-edge null. Right: the double-edge null (D032, D034).")
    print(f"   {'model':26}{'R ctrl':>8}{'R main':>8}{'ratio':>7}{'pairs/null':>13}   |{'R_d ctrl':>9}{'R_d main':>9}{'ratio':>7}{'pairs/null':>13}")
    ratios = {"three-edge": [], "double-edge": []}
    for m in models:
        row = f"   {m:26}"
        for tag, data in (("three-edge", old), ("double-edge", new)):
            c, mn = data[f"{ds}__{m}"], data[f"main__{m}"]
            rc, rm = c["reciprocity_excess"], mn["reciprocity_excess"]
            ok = rc > 0 and rm > 0
            if ok:
                ratios[tag].append((m, rc / rm))
            row += f"{rc:8.1f}{rm:8.1f}{(rc / rm if ok else float('nan')):7.2f}{str(c['observed']['cycles_2']) + '/' + format(c['null_mean']['cycles_2'], '.2f'):>13}"
            row += "   |" if tag == "three-edge" else ""
        print(row)
    for tag in ("three-edge", "double-edge"):
        xs = [x for _, x in ratios[tag]]
        fac = [max(x, 1 / x) for x in xs]
        summary[(ds, tag)] = st.median(fac)
        print(f"   {tag:12} n={len(xs):2} median ratio {st.median(xs):5.2f} range {min(xs):.2f}-{max(xs):.2f}; median size of the change x{st.median(fac):.2f}, largest x{max(fac):.2f}; "
              f"within a factor 2 in {sum(f <= 2 for f in fac)} of {len(fac)}; control R higher in {sum(x > 1 for x in xs)} of {len(xs)}")
    if ds == "e5":
        zero = [m for m in models if new[f"e5__{m}"]["observed"]["cycles_2"] == 0 or new[f"main__{m}"]["observed"]["cycles_2"] == 0]
        print(f"   models without a usable ratio (no mutual pair in the control or the main graph): {', '.join(zero) if zero else 'none'}")

print("\nREADING OF D034")
for ds in ("e4", "e5"):
    v = summary[(ds, "double-edge")]
    print(f"   {NAMES[ds]}: median size of the change x{v:.2f} under the double-edge null (x{summary[(ds, 'three-edge')]:.2f} under the three-edge null)  ->  "
          f"{'ABOVE 2: the factor 2 is to be reconsidered with the researcher' if v > 2 else 'not above 2: the factor 2 stands'}")


# Added after the comparison above had been read (post hoc, descriptive; not part of the reading of D034): the E4 control moved R upward for most models against
# the double-edge null, so the relation of R to definition length of script 13 (first null, unfiltered graphs) is repeated for both nulls on the default-filter graphs.
import math  # noqa: E402

from scipy import stats  # noqa: E402

PATHS = {
    "main": "data/definitions/{}_42.jsonl",
    "e3": "results_2026-09-09_Runpod/results_e3 (fewshot)/definitions/{}_42.jsonl",
    "e4": "results_2026-09-09_Runpod/results_e4 (lenght)/definitions/{}_42.jsonl",
    "e5": "results_2026-09-09_Runpod/results_e5 (no template)/definitions/{}_42.jsonl",
}


def words(key):
    ds, name = key.split("__")
    recs = [json.loads(l) for l in open(ROOT / PATHS[ds].format(name), encoding="utf-8") if l.strip()]
    w = [len((r.get("definition") or "").split()) for r in recs if (r.get("definition") or "").strip()]
    return sum(w) / len(w)


print("\nHOW R MOVES WITH DEFINITION LENGTH (post hoc, descriptive; default-filter graphs, mean words of the stored text, as in script 13)")
print(f"   mean words per definition, instruct models: main {st.mean(words('main__' + m) for m in models):.1f}, E4 {st.mean(words('e4__' + m) for m in models):.1f}, E5 {st.mean(words('e5__' + m) for m in models):.1f}")
sys.path.insert(0, str(ROOT / "src"))
from rs_dic_llm.wordnet_baseline import wordnet_definitions  # noqa: E402

_wl = json.loads((ROOT / "data" / "sample_words" / "word_list_3k_v1.json").read_text(encoding="utf-8"))
_wl = _wl.get("words", _wl) if isinstance(_wl, dict) else _wl
_wn = [len(r["definition"].split()) for r in wordnet_definitions(_wl) if r["definition"].strip()]
print(f"   WordNet glosses of the 3,000 entries: {sum(_wn) / len(_wn):.1f} words on average")
for tag, data in (("three-edge", old), ("double-edge", new)):
    Rk = lambda k: data[k]["reciprocity_excess"]
    allk = [k for k in data if Rk(k) > 0 and not k.endswith("wordnet")]
    rho, p = stats.spearmanr([words(k) for k in allk], [Rk(k) for k in allk])
    print(f"   {tag:11} all {len(allk)} graphs: Spearman rho(mean words, R) = {rho:+.2f} (p = {p:.3g})")
    ik = [k for k in data if (k.startswith("main__") or k.startswith("e4__")) and not k.endswith("-pt") and not k.endswith("wordnet") and Rk(k) > 0]
    rho, p = stats.spearmanr([words(k) for k in ik], [Rk(k) for k in ik])
    print(f"   {tag:11} instruct, main + E4 (n={len(ik)}): rho = {rho:+.2f} (p = {p:.3g})")
    bk = [k for k in data if k.endswith("-pt") and Rk(k) > 0]
    rho, p = stats.spearmanr([words(k) for k in bk], [Rk(k) for k in bk])
    print(f"   {tag:11} pretrained, zero-shot + few-shot (n={len(bk)}): rho = {rho:+.2f} (p = {p:.3g})")
    for ds in ("e4", "e5"):
        dl = [(math.log(words(f"{ds}__{m}") / words(f"main__{m}")), math.log(Rk(f"{ds}__{m}") / Rk(f"main__{m}"))) for m in models if Rk(f"{ds}__{m}") > 0 and Rk(f"main__{m}") > 0]
        rho, p = stats.spearmanr([x for x, _ in dl], [y for _, y in dl])
        print(f"   {tag:11} within a model, {ds.upper()} against main (n={len(dl)}): rho(change in log words, change in log R) = {rho:+.2f} (p = {p:.3g})")
print("   mutual pairs (they do not depend on the null): control higher than main for "
      + "; ".join(f"{ds.upper()} {sum(new[f'{ds}__{m}']['observed']['cycles_2'] > new[f'main__{m}']['observed']['cycles_2'] for m in models)} of 17 (median ratio "
                  f"{st.median(new[f'{ds}__{m}']['observed']['cycles_2'] / new[f'main__{m}']['observed']['cycles_2'] for m in models):.2f})" for ds in ("e4", "e5")))
