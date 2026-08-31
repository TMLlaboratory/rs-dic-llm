"""
Stage 6: analysis — scaling correlations, partial correlation vs sr_rate,
universal kernel, and comparison with the prior local (RunPod) results.

Usage:
    python analyse.py --metrics metrics.json
    python analyse.py --metrics metrics.json --no-prior   # API models only
"""

import argparse
import json
import math

import numpy as np

from models_config import MODELS, PRIOR_RESULTS


def pearson(x, y):
    if len(x) < 3:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def partial_corr(x, y, z):
    def residual(a, b):
        B = np.column_stack([b, np.ones(len(b))])
        beta = np.linalg.lstsq(B, a, rcond=None)[0]
        return a - B @ beta
    return float(np.corrcoef(residual(np.array(x, float), np.array(z, float)),
                             residual(np.array(y, float), np.array(z, float)))[0, 1])


def model_id_from_slug(name: str) -> str | None:
    base = name.split(".seed")[0].replace("__", "/")
    return base if base in MODELS else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", default="metrics.json")
    ap.add_argument("--no-prior", action="store_true")
    ap.add_argument("--out", default="analysis.json")
    args = ap.parse_args()

    with open(args.metrics, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    kernels = {}
    for name, m in raw.items():
        if name == "wordnet_baseline":
            continue
        mid = model_id_from_slug(name)
        cfg = MODELS.get(mid, {})
        rows.append(dict(
            model=name, family=cfg.get("family", "?"),
            params_B=cfg.get("params_B"), stack="together-api",
            kernel_ratio=m["kernel_ratio"], mset_k=m["mset_k"],
            circ=m["circ"], sr_rate=m["sr_rate"],
        ))
        kernels[name] = set(m.get("kernel_words", []))

    if not args.no_prior:
        rows += [dict(r) for r in PRIOR_RESULTS]

    # ---- table ----
    print(f"\n{'model':48s} {'family':9s} {'B':>6s} {'kern%':>6s} "
          f"{'mset/k%':>8s} {'circ%':>6s} {'sr%':>6s} {'stack':>12s}")
    for r in sorted(rows, key=lambda r: (r["family"], r["params_B"] or 1e9)):
        b = f"{r['params_B']:g}" if r["params_B"] else "?"
        print(f"{r['model']:48s} {r['family']:9s} {b:>6s} "
              f"{r['kernel_ratio']*100:6.1f} {r['mset_k']*100:8.1f} "
              f"{r['circ']*100:6.1f} {r['sr_rate']*100:6.1f} {r['stack']:>12s}")

    # ---- scaling correlations ----
    analysis = {"rows": rows, "correlations": {}}
    usable = [r for r in rows if r["params_B"]]

    def corr_block(label, subset):
        if len(subset) < 3:
            return
        lg = [math.log2(r["params_B"]) for r in subset]
        block = {}
        for metric in ("kernel_ratio", "mset_k", "circ"):
            vals = [r[metric] for r in subset]
            block[metric] = dict(
                r=round(pearson(lg, vals), 3),
                r_partial_sr=round(partial_corr(lg, vals,
                                                [r["sr_rate"] for r in subset]), 3),
                n=len(subset))
        analysis["correlations"][label] = block
        print(f"\n[{label}] n={len(subset)}")
        for metric, c in block.items():
            print(f"  {metric:13s} r={c['r']:+.3f}  r_partial|sr={c['r_partial_sr']:+.3f}")

    corr_block("pooled_all_known_params", usable)
    for fam in sorted({r["family"] for r in usable}):
        corr_block(f"within_{fam}", [r for r in usable if r["family"] == fam])

    # ---- within-family direction checks (2-point families) ----
    print("\n[2-point direction checks]")
    for fam in sorted({r["family"] for r in usable}):
        sub = sorted([r for r in usable if r["family"] == fam],
                     key=lambda r: r["params_B"])
        if len(sub) == 2:
            dk = sub[1]["kernel_ratio"] - sub[0]["kernel_ratio"]
            dm = sub[1]["mset_k"] - sub[0]["mset_k"]
            ok_k = "matches" if dk < 0 else "CONTRADICTS"
            ok_m = "matches" if dm > 0 else "CONTRADICTS"
            print(f"  {fam}: kern {dk*100:+.1f}pp ({ok_k} paper), "
                  f"mset/k {dm*100:+.1f}pp ({ok_m} paper)")

    # ---- universal kernel across API models ----
    if len(kernels) >= 3:
        inter = set.intersection(*kernels.values())
        union = set.union(*kernels.values())
        analysis["universal_kernel_api"] = sorted(inter)
        print(f"\n[universal kernel, all {len(kernels)} API graphs] "
              f"{len(inter)} words (union {len(union)})")
        print("  " + ", ".join(sorted(inter)[:30]) + (" ..." if len(inter) > 30 else ""))

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=1, ensure_ascii=False)
    print(f"\nsaved {args.out}")


if __name__ == "__main__":
    main()
