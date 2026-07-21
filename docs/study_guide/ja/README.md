# rs-dic-llm 学習ガイド

**対象**：ロペスチャパホセ（卒業研究生）

---

## この研究を一言で言うと

> **「LLM に単語の定義を書かせ、その定義のネットワーク構造を調べることで、モデルの大きさ（パラメータ数）と概念の組織の仕方の関係を定量化する」**

---

## 研究のポイント（先に把握しておくこと）

| 発見 | 数値 |
|---|---|
| カーネル率がモデルサイズと逆相関 | Qwen3.5内 r = −0.862 |
| mset/k（不可約サイクル比率）が正相関 | Qwen3.5内 r = +0.982 |
| 全モデル共通の普遍カーネル語 | 92語（NSMと10語重複） |
| 指示追従率：Gemma-4 vs Qwen3.5 | 99.9% vs 76〜92% |
| 量子化による変動（4-8bit） | ±1pp 以内 |

---

## 学習ロードマップ

```
【ここから読む】
        ↓
01_background/01_graph_theory.md      （有向グラフ・SCC）       60分
        ↓
01_background/02_dictionary_structure.md （辞書グラフの直観）    45分
        ↓
01_background/03_llm_basics.md        （LLMとスケーリング則）    60分
        ↓
02_key_papers/01_vincent_lamarre_2016.md （元論文の解説）        90分
        ↓
02_key_papers/02_scaling_laws.md      （スケーリング則論文）      45分
        ↓
03_this_research/01_motivation.md     （研究動機）               30分
        ↓
03_this_research/02_pipeline.md       （実験の流れ）             60分
        ↓
03_this_research/03_metrics.md        （指標の詳細）             60分
        ↓
03_this_research/04_results.md        （結果の読み方）           60分
        ↓
03_this_research/05_confound_analysis.md （交絡因子分析）        45分
        ↓
04_future_plan/01_research_issues.md  （課題整理）               30分
        ↓
04_future_plan/02_experiment_plan.md  （今後の実験計画）         30分
```

合計目安：**約 10 時間**

---

## 用語クイックリファレンス

| 用語 | 一言説明 | 詳細 |
|---|---|---|
| 辞書グラフ | 定義の使われ方を有向グラフで表したもの | `01_background/02` |
| カーネル | 定義が閉じた最小語彙集合（出次数0を除去して残る） | `03_this_research/03` |
| コア | カーネル内の「意味の根」となる Source SCC の和集合 | `03_this_research/03` |
| MinSet / MFVS | カーネルのサイクルを最小個数で壊す語の集合 | `03_this_research/03` |
| SCC | 強連結成分 — 互いに到達可能なノードのグループ | `01_background/01` |
| sr\_rate | 自己参照率 — 定義文に被定義語が現れる割合 | `03_this_research/05` |
| mset/k | MinSet/Kernel 比率 — 核の循環密度の指標 | `03_this_research/03` |
| 指示追従体制 | Gemma-4（低sr） vs Qwen3.5（高sr）のファミリー差 | `03_this_research/05` |
| 偏相関 | 第三変数を取り除いた後の2変数間の相関 | `03_this_research/05` |

---

## 実験で使ったモデル一覧

| モデル | ファミリー | パラメータ |
|---|---|---|
| Qwen3.5-0.8B-MLX-bf16 | Qwen3.5 | 0.8B |
| Qwen3.5-2B-bf16 | Qwen3.5 | 2B |
| Qwen3.5-4B-MLX-bf16 | Qwen3.5 | 4B |
| Qwen3.5-9B-bf16 | Qwen3.5 | 9B |
| Qwen3.5-27B-bf16 | Qwen3.5 | 27B |
| gemma-4-e4b-bf16 | Gemma-4 | 4B |
| gemma-4-31b-8bit | Gemma-4 | 31B |

---

次に読むファイル：`01_background/01_graph_theory.md`
