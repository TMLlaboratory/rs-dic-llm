# 実験パイプライン

**所要時間**：60分

---

## 全体の流れ

```
Stage 0: 語彙サンプリング    3000語を WordNet + Brown corpus から抽出
    ↓
Stage 1: 定義文生成          各モデルに 3000語 × 1定義を生成させる
    ↓
Stage 2: 前処理              レンマ化・ストップワード除去
    ↓
Stage 3: グラフ構築          nx.DiGraph に辺を張る
    ↓
Stage 4: 指標算出            Kernel / Core / MinSet / sr_rate
    ↓
Stage 5: WordNet ベースライン 比較のため WordNet の定義を同じパイプラインに通す
    ↓
Stage 6: 分析・比較          スケーリング関係・交絡分析・普遍カーネル
```

---

## Stage 0: なぜ 3000 語か

**予備実験（300語）で辺がほぼゼロになった**。

なぜか：300語では「cat の定義に animal が出ても、animal が選ばれた 300語に入っていない」ことが多い。
語彙サイズが大きいほど、定義語が語彙集合内に収まる確率が高くなる。

```
期待辺数 ≈ (1語の定義の平均語数) × (語彙サイズ / 全単語数) × 語彙サイズ
         ≈ 5語 × (3000 / 100000) × 3000 ≈ 450辺（実際は 5000〜10000辺）
```

フィルタリング条件：
- 品詞：名詞 1500 + 動詞 900 + 形容詞 600
- Brown Corpus 頻度 ≥ 5（一般語のみ）
- seed = 42（再現性確保）

---

## Stage 1: 定義文生成

```python
PROMPT = (
    'Define the {pos} "{word}" in one short sentence. '
    "Use only common English words. "
    "Do not use the word itself in the definition."
)
```

生成パラメータ：

| パラメータ | 値 | 理由 |
|---|---|---|
| temperature | 0.7 | Qwen3.5 公式推奨（non-thinking mode） |
| top_p | 0.8 | 公式推奨 |
| top_k | 20 | 公式推奨 |
| max_tokens | 80 | 1文に収める |
| enable_thinking | False | 必須（True だと数分かかる） |

定義のステータス分類：

| status | 内容 |
|---|---|
| `ok` | 問題なし |
| `self_referential` | 定義文に被定義語が現れた（指示違反） |
| `failed` | 3回連続で生成失敗 |

---

## Stage 2: 前処理

```python
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

def process(definition: str, vocab: set) -> list[str]:
    tokens = definition.lower().split()
    result = []
    for raw in tokens:
        token = raw.strip(".,;:!?\"'")
        if not token.isalpha(): continue
        if token in stopwords.words("english"): continue
        lemma = WordNetLemmatizer().lemmatize(token)
        if lemma in vocab:         # 語彙集合内の語のみ
            result.append(lemma)
    return result
```

---

## Stage 3: グラフ構築

```python
G = nx.DiGraph()
for rec in definitions:
    if rec["status"] not in {"ok", "self_referential"}:
        continue
    target = rec["word"]
    for source in process(rec["definition"], vocab):
        if source != target:           # 自己ループ除去
            G.add_edge(source, target)  # source が target の定義に使われる
```

> **self_referential を含める理由**：除外すると Qwen3.5 のグラフが不当に疎になる。
> 自己ループのみ除去し、他の有効な辺は保持する。

---

## 実際のグラフ規模

| モデル | ノード | 辺 | 平均出次数 |
|---|---|---|---|
| Qwen3.5-0.8B | 2750 | 10259 | 3.73 |
| Qwen3.5-27B | 2750 | 6927 | 2.52 |
| Gemma-4-4B | 2750 | 5025 | 1.83 |
| WordNet | — | — | 1.67 |

小さいモデルほど辺が多い（自己参照が多いため、同じ語を繰り返し使う傾向）。

---

次に読むファイル：`03_metrics.md`
