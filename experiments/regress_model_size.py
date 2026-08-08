"""Regression: predict log(model_size) from graph + text metrics.

Reads from results/full_summary.json (written by run_experiment.py).
Uses LOO-CV (leave-one-out) since n is small.

Features: kernel_ratio, minset_kernel_ratio, mean_out_degree, oov_rate,
          tokens_per_word, circulation_rate
Target: log2(params_B)
"""

import json
import sys
from pathlib import Path
from itertools import combinations

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

SEED = 42
SUMMARY_PATH = "results/full_summary.json"


def load_features() -> dict[str, dict]:
    if not Path(SUMMARY_PATH).exists():
        print(f"ERROR: {SUMMARY_PATH} not found. Run run_experiment.py first.")
        sys.exit(1)

    summary = json.loads(Path(SUMMARY_PATH).read_text())
    rows = {}

    for m in summary.get("models", []):
        param_b = m.get("param_b")
        if param_b is None:
            continue  # skip models without known param count

        display = m.get("display", m.get("model", "?"))
        dpath = f"data/definitions/{display}_{SEED}.jsonl"

        if not Path(dpath).exists():
            print(f"  [skip] {display}: definition file missing")
            continue

        lines = Path(dpath).read_text(encoding="utf-8").strip().splitlines()
        recs = [json.loads(l) for l in lines]
        valid = [r for r in recs if r["status"] in ("ok", "self_referential")]
        all_tokens = [t.lower() for r in valid
                      for t in r["definition"].split() if t.isalpha()]
        vocab = {r["word"] for r in recs}
        unique_words = set(all_tokens)
        oov_rate = (sum(1 for w in unique_words if w not in vocab) / len(unique_words)
                    if unique_words else 0)
        tokens_per_word = len(all_tokens) / len(valid) if valid else 0

        ks = m.get("kernel_size") or 1
        ms = m.get("minset_size") or 0

        rows[display] = {
            "size_b":              float(param_b),
            "log2_size":           np.log2(float(param_b)),
            "family":              m.get("family", "?"),
            "kernel_ratio":        m["kernel_ratio"],
            "minset_kernel_ratio": ms / ks,
            "mean_out_degree":     m["mean_out_degree"],
            "oov_rate":            oov_rate,
            "tokens_per_word":     tokens_per_word,
            "circulation_rate":    m["circulation_rate"],
        }
    return rows


def loo_cv(X: np.ndarray, y: np.ndarray, feature_names: list[str]) -> dict:
    n = len(y)
    preds = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        Xtr, ytr = X[mask], y[mask]
        try:
            beta = np.linalg.lstsq(Xtr, ytr, rcond=None)[0]
            preds[i] = X[i:i+1] @ beta
        except Exception:
            preds[i] = np.mean(ytr)

    residuals = y - preds
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    q2  = 1 - ss_res / ss_tot
    mae = np.mean(np.abs(residuals))

    beta_full = np.linalg.lstsq(X, y, rcond=None)[0]
    y_hat = X @ beta_full
    r2 = 1 - np.sum((y - y_hat) ** 2) / ss_tot

    return {
        "q2_loo": q2, "r2_full": r2, "mae_loo_log2": mae,
        "beta": beta_full, "preds_loo": preds, "feature_names": feature_names,
    }


def run_regression(rows: dict) -> None:
    keys = list(rows.keys())
    y    = np.array([rows[k]["log2_size"] for k in keys])

    all_features = ["kernel_ratio", "minset_kernel_ratio", "mean_out_degree",
                    "oov_rate", "tokens_per_word", "circulation_rate"]
    feat_matrix  = np.array([[rows[k][f] for f in all_features] for k in keys])

    print("=" * 72)
    print("REGRESSION: log2(model_size_B) ~ graph + text metrics")
    print(f"Data: {len(keys)} models, LOO-CV")
    print("=" * 72)

    # ── 1. Single-feature ────────────────────────────────────────────────────
    print("\n── 1. Single-feature (+ intercept) ────────────────────────────────")
    print(f"{'feature':25} {'R²_full':>8} {'Q²_loo':>8} {'MAE_loo':>10}")
    print("-" * 56)
    for f in all_features:
        col = feat_matrix[:, all_features.index(f)]
        X1  = np.column_stack([col, np.ones(len(y))])
        res = loo_cv(X1, y, [f, "intercept"])
        print(f"  {f:23} {res['r2_full']:>8.3f} {res['q2_loo']:>8.3f} {res['mae_loo_log2']:>10.3f}")

    # ── 2. Best 3-feature combo ──────────────────────────────────────────────
    print("\n── 2. All 3-feature combinations (top 6 by Q²) ────────────────────")
    print(f"{'features':50} {'R²':>8} {'Q²':>8}")
    print("-" * 70)
    combos = []
    for combo in combinations(range(len(all_features)), 3):
        fnames = [all_features[i] for i in combo]
        X3 = np.column_stack([feat_matrix[:, i] for i in combo] + [np.ones(len(y))])
        res = loo_cv(X3, y, fnames + ["intercept"])
        combos.append((fnames, res))
    combos.sort(key=lambda x: x[1]["q2_loo"], reverse=True)
    for fnames, res in combos[:6]:
        print(f"  {' + '.join(fnames):50} {res['r2_full']:>8.3f} {res['q2_loo']:>8.3f}")

    # ── 3. Best combo detail ─────────────────────────────────────────────────
    best_fnames, best_res = combos[0]
    print(f"\n── 3. Best model: {' + '.join(best_fnames)} ──")
    for fname, b in zip(best_fnames + ["intercept"], best_res["beta"]):
        print(f"  {fname:30}: {b:+.4f}")
    print()
    print(f"{'model':30} {'actual':>8} {'pred_loo':>10} {'err(log2)':>10}")
    print("-" * 62)
    for i, k in enumerate(keys):
        print(f"  {k:28} {y[i]:>8.3f} {best_res['preds_loo'][i]:>10.3f} "
              f"{best_res['preds_loo'][i]-y[i]:>+10.3f}")

    # ── 4. Correlation with log2_size ────────────────────────────────────────
    print("\n── 4. Pearson r vs log2(size_B) ────────────────────────────────────")
    for f in all_features:
        col = feat_matrix[:, all_features.index(f)]
        r   = np.corrcoef(col, y)[0, 1]
        bar = "█" * int(abs(r) * 20)
        print(f"  {f:25} r={r:+.3f}  {'+-'[r<0]}{bar}")


if __name__ == "__main__":
    print("Loading features...")
    rows = load_features()
    if not rows:
        print("No data — run experiments/run_experiment.py first.")
        sys.exit(0)

    print(f"\nRaw features ({len(rows)} models):")
    header = f"  {'model':24} {'fam':8}" + "".join(
        f"{k:>12}" for k in ["kern%", "mset/k%", "out_deg", "oov%", "tok/word", "circ%"])
    print(header)
    for k, row in sorted(rows.items(), key=lambda x: (x[1]["family"], x[1]["size_b"])):
        print(f"  {k:24} {row['family']:8}"
              f"{row['kernel_ratio']*100:>12.1f}"
              f"{row['minset_kernel_ratio']*100:>12.1f}"
              f"{row['mean_out_degree']:>12.2f}"
              f"{row['oov_rate']*100:>12.1f}"
              f"{row['tokens_per_word']:>12.1f}"
              f"{row['circulation_rate']*100:>12.1f}")

    run_regression(rows)
