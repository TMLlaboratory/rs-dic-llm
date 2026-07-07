# 今後の実験計画

**所要時間**：30分

---

## 最優先タスク：n を増やす

| # | 実験 | 追加モデル例 | 期待効果 |
|---|---|---|---|
| A | Llama-4 ファミリー | Scout-17B, Maverick-17B | n+2、異なるファミリー |
| B | Phi-4 ファミリー | 3.8B, 14B | n+2、Microsoft 系 |
| C | Qwen3.5-72B | 72B（4bit） | Qwen3.5 n=6、スケール拡張 |
| D | Gemma-3 | 2B, 12B, 27B | Gemma ファミリー拡張 |

目標：n ≥ 15、複数ファミリー × 複数スケール

---

## タスク管理表

| タスク | 担当 | 期限 | 状態 | 作業量目安 |
|---|---|---|---|---|
| seed=123, 456 で Qwen3.5×5 再実験 | ペペ | 2026-06-01 | 未着手 | 約 24h（自動） |
| Llama-4 Scout の mlx モデル確認 | ペペ | 2026-05-25 | 未着手 | 2h |
| few-shot プロンプトの実装 | ペペ | 2026-06-07 | 未着手 | 4h |
| sr_rate 低減後の Qwen3.5-4B 実験 | ペペ | 2026-06-14 | 未着手 | 8h |
| 論文 Results 節に表を追加 | 雲居 | 2026-06-30 | — | — |

---

## すぐ着手できるコード：複数シード実験

```python
# experiments/run_multiseed.py
import subprocess

SEEDS = [42, 123, 456]
for seed in SEEDS:
    if seed == 42:
        continue   # 既存データをスキップ
    cmd = f"uv run python -m experiments.run_full --seed {seed}"
    subprocess.run(cmd.split(), check=True)
```

---

## few-shot プロンプトの実装スケルトン

```python
FEW_SHOT_EXAMPLES = [
    ("noun", "table",
     "a flat surface supported by legs, used for placing objects on."),
    ("verb", "run",
     "to move quickly on foot by taking rapid steps."),
    ("adjective", "large",
     "greater than average in size, quantity, or extent."),
]

def make_few_shot_prompt(pos: str, word: str) -> str:
    examples = "\n".join(
        f'Define the {p} "{w}": {d}'
        for p, w, d in FEW_SHOT_EXAMPLES
    )
    return (
        f"{examples}\n"
        f'Define the {pos} "{word}":'
    )
```

---

## 学習の完了確認チェックリスト

- [ ] `01_graph_theory.md` を読んで SCC と FVS を説明できる
- [ ] カーネルが「出次数 0 の除去」で求まることを実装で確認した
- [ ] Vincent-Lamarre 2016 の原著を読んだ（arXiv:1411.0129）
- [ ] `experiments/run_full.py` を実行してデータを生成できた
- [ ] `experiments/analyse_confound.py` を実行して結果を読んだ
- [ ] 偏相関の計算コードを書いて動かせた
- [ ] 論文ドラフト（`docs/paper_ja.md`）を読んだ
- [ ] 今後の追実験（seed複数・few-shot）のうち 1 つ以上に着手した

---

学習ガイド完了。不明な点は雲居准教授か `docs/paper_ja.md` を参照すること。
