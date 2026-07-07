# 交絡因子分析：sr_rate と指示追従体制

**所要時間**：45分

---

## 交絡因子とは

**交絡因子**（confound）：本当に知りたい関係（X→Y）に影響する第三の変数 Z。

```
本当に知りたい関係:
  モデルサイズ(X) ──→ カーネル率(Y)

潜在的な交絡:
  モデルサイズ(X) ──→ sr_rate(Z) ──→ カーネル率(Y)
  モデルサイズ(X) ──→ カーネル率(Y)  （直接効果）
```

もし sr_rate が高いモデルほどカーネル率が高いなら、
「スケールとカーネル率の相関」は「スケールと sr_rate の相関」による見せかけかもしれない。

---

## sr_rate：指示追従の失敗率

「定義に被定義語が現れる」定義の比率：

| モデル | sr_rate | follow_rate（指示追従率） |
|---|---|---|
| Qwen3.5-0.8B | 76.2% | 23.8% |
| Qwen3.5-2B | 92.2% | 7.8% |
| Qwen3.5-4B | 86.2% | 13.8% |
| Qwen3.5-9B | 75.9% | 24.1% |
| Qwen3.5-27B | 84.9% | 15.1% |
| Gemma-4-4B | **0.1%** | 99.9% |
| Gemma-4-31B | **0.1%** | 99.9% |

**発見 1**：Qwen3.5 の sr_rate はモデルサイズと相関しない（単調でない）。
**発見 2**：Gemma-4 は完全に異なる「指示追従体制」に属する。

---

## 偏相関分析

**偏相関**：Z（sr_rate）の影響を取り除いた上での X（スケール）と Y（カーネル率）の相関。

```python
import numpy as np

def partial_corr(x, y, z):
    def residual(a, b):
        B = np.column_stack([b, np.ones(len(b))])
        beta = np.linalg.lstsq(B, a, rcond=None)[0]
        return a - B @ beta
    return np.corrcoef(residual(x, z), residual(y, z))[0, 1]

r_raw = np.corrcoef(kern_all, log2_all)[0, 1]       # −0.757
r_partial = partial_corr(kern_all, log2_all, sr_all)  # −0.723

print(f"Δr = {r_partial - r_raw:.3f}")  # +0.034（sr の影響は小さい）
```

**Δr = +0.034** → sr_rate を制御しても相関がほぼ変わらない。
= 「カーネル率とスケールの関係は sr_rate による見せかけではない」

---

## 指示追従体制の構造的影響

Gemma-4-4B と Qwen3.5-4B を比べると：

| 指標 | Qwen3.5-4B | Gemma-4-4B | 差の解釈 |
|---|---|---|---|
| sr_rate | 86.2% | 0.1% | 定義スタイルの根本差 |
| n_edges | 6844 | 5025 | 自己参照減→辺少 |
| kern% | 10.8% | 7.3% | Gemma の方が小さいカーネル |
| mset/k% | 17.1% | 23.3% | Gemma の核は密 |

**解釈**：Gemma-4 は自己参照なしで定義を生成するため、
語のネットワークが Qwen3.5 より疎になる。
しかし残ったカーネルはより密に絡み合っている。

---

## 論文でどう報告するか

```
"We treat sr_rate as an instruction-regime covariate in cross-family comparisons.
Partial correlation analysis (controlling for sr_rate) shows Δr = +0.034
for kernel_ratio, confirming that the scale–kernel relationship is not
an artifact of differential instruction-following."
```

交絡因子を明示して報告することで、結果の解釈の信頼性が高まる。

---

次に読むファイル：`../04_future_plan/01_research_issues.md`
