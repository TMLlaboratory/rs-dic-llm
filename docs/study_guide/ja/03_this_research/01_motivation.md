# 研究動機：なぜ定義グラフか

**所要時間**：30分  
**前提知識**：`02_key_papers/` 2ファイル

---

## 出発点となる直観

> **「小さなモデルは概念を循環参照で定義しがちではないか？」**

例：0.8B モデルが生成した定義（架空の例）

```
cat  → "a cat-like animal with fur"  （cat が cat を使っている！）
dog  → "an animal like a dog"
fur  → "the fur-like material of animals"
```

大きなモデルなら：

```
cat  → "a small domesticated carnivore kept as a pet or for pest control"
dog  → "a domesticated mammal of the genus Canis"
```

大きなモデルの方が語彙を豊富に使い、循環が少ないという仮説を**定量的に検証**したい。

---

## 研究の位置づけ（地図）

```
LLM の能力評価
    │
    ├── ベンチマーク（MMLU等）── タスク性能を測る
    ├── 損失（perplexity） ── 言語モデリング性能を測る
    └── 【本研究】定義グラフ ── 概念知識の組織構造を測る（新しい軸）
                    │
                    ├── カーネル率（語彙的効率）
                    ├── mset/k（概念核の循環密度）
                    └── circulation_rate（全体的な循環性）
```

---

## 3 つの研究課題

| RQ | 問い | 答え（先取り） |
|---|---|---|
| RQ1 | カーネル率・循環率はモデルサイズと関係するか？ | Qwen3.5 内で r=−0.862 の単調減少 |
| RQ2 | 複数ファミリー比較で sr_rate はどう影響するか？ | ファミリー固有の交絡因子として偏相関で制御 |
| RQ3 | 全モデル共通のカーネル語は存在するか？ | 92 語（NSM と 10 語重複） |

---

次に読むファイル：`02_pipeline.md`
