"""Regression: predict log(model_size) from graph + text metrics.

5 data points only → use LOO-CV (leave-one-out cross-validation).
Features: kernel_ratio, minset_kernel_ratio, mean_out_degree, oov_rate, tokens_per_word
Target: log2(params_B)
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

SEED = 42
MODELS = [
    ("mlx-community/Qwen3.5-0.8B-MLX-bf16",  0.8),
    ("mlx-community/Qwen3.5-2B-bf16",         2.0),
    ("mlx-community/Qwen3.5-4B-MLX-bf16",     4.0),
    ("mlx-community/Qwen3.5-9B-bf16",         9.0),
    ("mlx-community/Qwen3.5-27B-bf16",       27.0),
]


def load_features() -> dict[str, dict]:
    rows = {}
    for model_id, size_b in MODELS:
        short = model_id.split("/")[-1]
        mpath = f"results/metrics/{short}_{SEED}.json"
        dpath = f"data/definitions/{short}_{SEED}.jsonl"
        m = json.load(open(mpath))

        # text-level features from JSONL
        lines = Path(dpath).read_text().strip().splitlines()
        recs = [json.loads(l) for l in lines]
        valid = [r for r in recs if r["status"] in ("ok", "self_referential")]
        all_tokens = [t.lower() for r in valid
                      for t in r["definition"].split() if t.isalpha()]
        vocab_3k = {r["word"] for r in recs}
        unique_words = set(all_tokens)
        oov_rate = sum(1 for w in unique_words if w not in vocab_3k) / len(unique_words)
        tokens_per_word = len(all_tokens) / len(valid) if valid else 0

        ks = m["kernel_size"] or 1
        ms = m["minset_size"] or 0

        rows[short] = {
            "size_b": size_b,
            "log2_size": np.log2(size_b),
            "kernel_ratio": m["kernel_ratio"],
            "minset_kernel_ratio": ms / ks,
            "mean_out_degree": m["mean_out_degree"],
            "oov_rate": oov_rate,
            "tokens_per_word": tokens_per_word,
            "circulation_rate": m["circulation_rate"],
        }
    return rows


def loo_cv(X: np.ndarray, y: np.ndarray, feature_names: list[str]) -> dict:
    """Leave-one-out CV with ordinary least squares. Returns metrics."""
    n = len(y)
    preds = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        Xtr, ytr = X[mask], y[mask]
        Xte = X[i:i+1]
        # OLS: beta = (X'X)^{-1} X'y  (with intercept column already in X)
        try:
            beta = np.linalg.lstsq(Xtr, ytr, rcond=None)[0]
            preds[i] = Xte @ beta
        except Exception:
            preds[i] = np.mean(ytr)

    residuals = y - preds
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    q2 = 1 - ss_res / ss_tot   # LOO Q² (predictive R²)
    mae = np.mean(np.abs(residuals))

    # Full-data fit for coefficients + R²
    beta_full = np.linalg.lstsq(X, y, rcond=None)[0]
    y_hat_full = X @ beta_full
    r2_full = 1 - np.sum((y - y_hat_full)**2) / ss_tot

    return {
        "q2_loo": q2,
        "r2_full": r2_full,
        "mae_loo_log2": mae,
        "beta": beta_full,
        "preds_loo": preds,
        "feature_names": feature_names,
    }


def run_regression(rows: dict) -> None:
    keys = list(rows.keys())
    y = np.array([rows[k]["log2_size"] for k in keys])   # log2(B)

    all_features = ["kernel_ratio", "minset_kernel_ratio", "mean_out_degree",
                    "oov_rate", "tokens_per_word", "circulation_rate"]

    feature_matrix = np.array([[rows[k][f] for f in all_features] for k in keys])

    print("=" * 72)
    print("REGRESSION: log2(model_size_B) ~ graph + text metrics")
    print(f"Data: {len(keys)} models, LOO-CV (leave-one-out)")
    print("=" * 72)
    print(f"\nTarget y = log2(size_B):  " +
          "  ".join(f"{rows[k]['size_b']:.1f}B→{rows[k]['log2_size']:.2f}" for k in keys))

    # ── 1. Single-feature regressions ─────────────────────────────────────────
    print("\n── 1. Single-feature (+ intercept) ────────────────────────────────")
    print(f"{'feature':25} {'R²_full':>8} {'Q²_loo':>8} {'MAE_loo(log2)':>14}")
    print("-" * 60)
    single_results = []
    for f in all_features:
        col = feature_matrix[:, all_features.index(f)]
        X1 = np.column_stack([col, np.ones(len(y))])
        res = loo_cv(X1, y, [f, "intercept"])
        single_results.append((f, res))
        print(f"  {f:23} {res['r2_full']:>8.3f} {res['q2_loo']:>8.3f} {res['mae_loo_log2']:>14.3f}")

    # ── 2. Best 3-feature combo (by Q²) ──────────────────────────────────────
    print("\n── 2. All 3-feature combinations ──────────────────────────────────")
    print(f"{'features':50} {'R²_full':>8} {'Q²_loo':>8}")
    print("-" * 72)
    from itertools import combinations
    combo_results = []
    for combo in combinations(range(len(all_features)), 3):
        fnames = [all_features[i] for i in combo]
        X3 = np.column_stack([feature_matrix[:, i] for i in combo] + [np.ones(len(y))])
        res = loo_cv(X3, y, fnames + ["intercept"])
        combo_results.append((fnames, res))
    combo_results.sort(key=lambda x: x[1]["q2_loo"], reverse=True)
    for fnames, res in combo_results[:6]:
        label = " + ".join(fnames)
        print(f"  {label:50} {res['r2_full']:>8.3f} {res['q2_loo']:>8.3f}")

    # ── 3. Best combo: detail ─────────────────────────────────────────────────
    best_fnames, best_res = combo_results[0]
    print(f"\n── 3. Best model detail: {' + '.join(best_fnames)} ──")
    beta = best_res["beta"]
    for fname, b in zip(best_fnames + ["intercept"], beta):
        print(f"  {fname:30}: {b:+.4f}")
    print()
    print(f"{'model':32} {'actual':>8} {'pred_loo':>10} {'err(log2)':>10} {'err_B':>10}")
    print("-" * 72)
    for i, k in enumerate(keys):
        act = y[i]
        pred = best_res["preds_loo"][i]
        err_b = 2**pred - 2**act
        print(f"  {k:30} {act:>8.3f} {pred:>10.3f} {pred-act:>10.3f} {err_b:>+10.1f}B")

    # ── 4. User-specified combo: kernel_ratio + oov_rate + tokens_per_word ───
    print(f"\n── 4. Specified combo: kernel_ratio + oov_rate + tokens_per_word ──")
    fnames_spec = ["kernel_ratio", "oov_rate", "tokens_per_word"]
    idx = [all_features.index(f) for f in fnames_spec]
    X_spec = np.column_stack([feature_matrix[:, i] for i in idx] + [np.ones(len(y))])
    res_spec = loo_cv(X_spec, y, fnames_spec + ["intercept"])
    print(f"  R²_full = {res_spec['r2_full']:.3f}   Q²_loo = {res_spec['q2_loo']:.3f}   MAE = {res_spec['mae_loo_log2']:.3f} (log2)")
    for fname, b in zip(fnames_spec + ["intercept"], res_spec["beta"]):
        print(f"  {fname:30}: {b:+.4f}")
    print()
    print(f"{'model':32} {'actual_B':>9} {'pred_B_loo':>11} {'err_B':>9}")
    print("-" * 65)
    for i, k in enumerate(keys):
        act_b = rows[k]["size_b"]
        pred_b = 2 ** best_res["preds_loo"][i]  # use best for comparison
        pred_b_spec = 2 ** res_spec["preds_loo"][i]
        print(f"  {k:30} {act_b:>9.1f} {pred_b_spec:>11.1f} {pred_b_spec-act_b:>+9.1f}")

    # ── 5. Interpretation ─────────────────────────────────────────────────────
    print("\n── 5. Correlation matrix (Pearson r with log2_size) ────────────────")
    for f in all_features:
        col = feature_matrix[:, all_features.index(f)]
        r = np.corrcoef(col, y)[0, 1]
        bar = "█" * int(abs(r) * 20)
        sign = "+" if r > 0 else "-"
        print(f"  {f:25} r={r:+.3f}  {sign}{bar}")


if __name__ == "__main__":
    print("Loading features...")
    rows = load_features()

    print(f"\nRaw features:")
    header = f"  {'model':30}" + "".join(f"{k:>18}" for k in [
        "kernel%", "mset/k%", "out_deg", "oov%", "tok/word", "circ%"])
    print(header)
    for short, row in rows.items():
        print(f"  {short:30}"
              f"{row['kernel_ratio']*100:>18.1f}"
              f"{row['minset_kernel_ratio']*100:>18.1f}"
              f"{row['mean_out_degree']:>18.2f}"
              f"{row['oov_rate']*100:>18.1f}"
              f"{row['tokens_per_word']:>18.1f}"
              f"{row['circulation_rate']*100:>18.1f}")

    run_regression(rows)
