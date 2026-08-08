"""Confound analysis: self-referential rate as a covariate.

The prompt instructs models: "Do not use the word itself in the definition."
The degree to which models follow this instruction (1 - sr_rate) is itself
a capability signal.  This script:

  1. Shows sr_rate variation across models and families
  2. Computes partial correlations (graph metric ~ log2(params) | sr_rate)
  3. Runs regression: graph metric ~ log2(params) + sr_rate
  4. Produces a summary table suitable for a paper

NOTE: This script reads from results/full_summary.json written by
run_experiment.py, which embeds display, param_b, family, and sr_rate
directly into each metrics dict. If the file is missing, run the
experiment first.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

SEED = 42
SUMMARY_PATH = "results/full_summary.json"


def load_rows() -> list[dict]:
    """Load all model rows from the experiment summary."""
    if not Path(SUMMARY_PATH).exists():
        print(f"ERROR: {SUMMARY_PATH} not found.", file=sys.stderr)
        print("Run experiments/run_experiment.py first.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(Path(SUMMARY_PATH).read_text())
    rows = []
    for m in data.get("models", []):
        # sr_rate is now written by run_experiment.py; fall back to JSONL if absent
        sr = m.get("sr_rate")
        if sr is None:
            display = m.get("display", "")
            dp = Path(f"data/definitions/{display}_{SEED}.jsonl")
            if dp.exists():
                recs = [json.loads(l) for l in dp.read_text().strip().splitlines()]
                sr = sum(1 for r in recs if r.get("status") == "self_referential") / len(recs)
            else:
                sr = float("nan")

        param_b = m.get("param_b")
        if param_b is None or np.isnan(float(param_b)):
            continue  # skip entries without known param count (Tier-2 API models)

        ks = m.get("kernel_size", 0) or 1
        ms = m.get("minset_size") or 0
        rows.append({
            "display":      m.get("display", m.get("model", "?")),
            "family":       m.get("family", "?"),
            "param_b":      float(param_b),
            "log2_b":       np.log2(float(param_b)),
            "sr_rate":      float(sr),
            "follow_rate":  1.0 - float(sr),
            "kernel_ratio": m["kernel_ratio"],
            "mset_k":       ms / ks,
            "out_deg":      m["mean_out_degree"],
            "circ":         m["circulation_rate"],
            "n_edges":      m["n_edges"],
        })
    return rows


def partial_corr(x, y, z):
    """Pearson r(x,y | z): correlation after partialing out z."""
    def _res(a, b):
        b_ = np.column_stack([b, np.ones(len(b))])
        beta = np.linalg.lstsq(b_, a, rcond=None)[0]
        return a - b_ @ beta
    return np.corrcoef(_res(x, z), _res(y, z))[0, 1]


def run():
    rows = load_rows()
    if len(rows) < 3:
        print(f"Only {len(rows)} rows with known param_b — need at least 3 for correlation.")
        return
    n = len(rows)

    log2  = np.array([r["log2_b"]      for r in rows])
    sr    = np.array([r["sr_rate"]      for r in rows])
    kr    = np.array([r["kernel_ratio"] for r in rows])
    mk    = np.array([r["mset_k"]       for r in rows])
    od    = np.array([r["out_deg"]      for r in rows])
    cc    = np.array([r["circ"]         for r in rows])

    # ── 1. Raw data table ─────────────────────────────────────────────────────
    print("=" * 78)
    print("TABLE 1: All models — raw metrics + instruction-following rate")
    print("=" * 78)
    print(f"  {'model':22} {'fam':8} {'B':>5} {'follow%':>8} {'kern%':>7} "
          f"{'mset/k%':>8} {'out_deg':>7} {'circ%':>6}")
    print("  " + "-" * 75)
    for r in sorted(rows, key=lambda x: (x["family"], x["param_b"])):
        print(f"  {r['display']:22} {r['family']:8} {r['param_b']:>5.1f} "
              f"{r['follow_rate']*100:>8.1f} "
              f"{r['kernel_ratio']*100:>7.1f} "
              f"{r['mset_k']*100:>8.1f} "
              f"{r['out_deg']:>7.2f} "
              f"{r['circ']*100:>6.1f}")

    # ── 2. Correlation table ──────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("TABLE 2: Correlation with log2(params) — raw vs. partial (controlling sr)")
    print("=" * 78)
    metrics = [("kernel_ratio", kr), ("mset_k", mk),
               ("out_deg", od), ("circ", cc), ("follow_rate", 1 - sr)]
    print(f"  {'metric':18} {'r_raw':>8} {'r_partial|sr':>13}  {'Δr':>6}  interpretation")
    print("  " + "-" * 72)
    for name, vals in metrics:
        r_raw = np.corrcoef(vals, log2)[0, 1]
        if name == "follow_rate":
            r_par = float("nan")
            delta = float("nan")
            interp = "(sr itself — not partialled)"
        else:
            r_par  = partial_corr(vals, log2, sr)
            delta  = r_par - r_raw
            interp = ("↑ sr was suppressing" if delta > 0.05
                      else "↓ sr was inflating" if delta < -0.05
                      else "sr has little effect")
        if np.isnan(r_par):
            print(f"  {name:18} {r_raw:>+8.3f}  {'—':>13}  {'—':>6}  {interp}")
        else:
            print(f"  {name:18} {r_raw:>+8.3f}  {r_par:>+13.3f}  {delta:>+6.3f}  {interp}")

    # ── 3. Regression: metric ~ log2(B) + sr_rate ────────────────────────────
    print(f"\n" + "=" * 78)
    print(f"TABLE 3: OLS — metric ~ log2(params) + sr_rate  (n={n})")
    print("=" * 78)
    for target_name, target in [("kernel_ratio", kr), ("mset_k", mk)]:
        X = np.column_stack([log2, sr, np.ones(n)])
        beta, _, _, _ = np.linalg.lstsq(X, target, rcond=None)
        y_hat  = X @ beta
        ss_res = np.sum((target - y_hat) ** 2)
        ss_tot = np.sum((target - target.mean()) ** 2)
        r2     = 1 - ss_res / ss_tot
        print(f"\n  {target_name} = {beta[0]:+.4f}·log2(B) "
              f"{beta[1]:+.4f}·sr_rate {beta[2]:+.4f}")
        print(f"  R² = {r2:.3f}")
        print(f"  Fitted vs actual:")
        for r, yh in zip(rows, y_hat):
            actual = r["kernel_ratio"] if target_name == "kernel_ratio" else r["mset_k"]
            print(f"    {r['display']:24} actual={actual*100:.1f}%  fit={yh*100:.1f}%  "
                  f"res={( actual - yh)*100:+.1f}pp")

    # ── 4. Family difference after sr control ────────────────────────────────
    print("\n" + "=" * 78)
    print("TABLE 4: Within-family scaling direction (all models, bf16)")
    print("=" * 78)
    for family in sorted({r["family"] for r in rows}):
        frows = sorted([r for r in rows if r["family"] == family],
                       key=lambda x: x["param_b"])
        if len(frows) < 2:
            continue
        print(f"\n  {family}:")
        for r in frows:
            print(f"    {r['display']:22} {r['param_b']:>5.1f}B  "
                  f"kern={r['kernel_ratio']*100:.1f}%  "
                  f"mset/k={r['mset_k']*100:.1f}%  "
                  f"sr={r['sr_rate']*100:.0f}%")
        kr_dir = "↑" if frows[-1]["kernel_ratio"] > frows[0]["kernel_ratio"] else "↓"
        mk_dir = "↑" if frows[-1]["mset_k"] > frows[0]["mset_k"] else "↓"
        print(f"    direction small→large: kernel_ratio {kr_dir}  mset_k {mk_dir}")

    # ── 5. Summary ────────────────────────────────────────────────────────────
    r_kr_raw = np.corrcoef(kr, log2)[0, 1]
    r_kr_par = partial_corr(kr, log2, sr)
    r_sr_log2 = np.corrcoef(1 - sr, log2)[0, 1]
    print(f"""
{'='*78}
SUMMARY: Key findings  (n={n} models, all bf16)
{'='*78}
  1. Instruction-following (1-sr_rate) vs log2(params): r={r_sr_log2:+.3f}
  2. kernel_ratio ~ log2(params):
       raw r = {r_kr_raw:+.3f}   partial r (controlling sr) = {r_kr_par:+.3f}
""")


if __name__ == "__main__":
    run()
