# 大規模言語モデル（LLM）とスケーリング則

**所要時間**：60分  
**前提知識**：確率の基礎（高校数学レベル）

---

## LLM とは

LLM（Large Language Model）は大量のテキストで学習した**確率モデル**で、
「次に来る単語の確率を予測する」ことを繰り返して文章を生成する。

```
入力: "Define the noun 'cat':"
予測: P("a" | 入力) = 0.12
     P("an" | 入力) = 0.08
     P("the" | 入力) = 0.05
     ...
→ 確率の高い単語を選んで生成を続ける
```

**パラメータ数** = モデルの「重み」の個数。
0.8B = 8億個、27B = 270億個のパラメータを持つ。

---

## 生成パラメータ：temperature

同じ入力でも毎回違う出力が得られるのは **temperature** パラメータによる。

```
temperature → 0.0: 毎回同じ単語（最高確率を選ぶ greedy decoding）
temperature = 0.7: 確率に応じてサンプリング（適度な多様性）
temperature = 2.0: ほぼランダム（ハチャメチャな出力）
```

> **本研究の選択**：Qwen3.5 公式の非 thinking モード推奨値 **temperature = 0.7** を使用。
> temperature = 0.0 では「cat is a cat」のような自己参照定義が急増することを確認済み。

---

## モデルファミリーとは

複数サイズのモデルが同じアーキテクチャ・事前学習データで作られたものを
**ファミリー**と呼ぶ。

本研究で使用：
- **Qwen3.5 ファミリー**：0.8B, 2B, 4B, 9B, 27B（全て同一アーキテクチャ系）
- **Gemma-4 ファミリー**：4B, 31B（Google DeepMind 製）

異なるファミリーは「別の世界観」を持つ——同じ問いへの答え方が根本的に違うことがある。

---

## スケーリング則（Scaling Laws）

「大きいモデルほど性能が良い」という直観は **スケーリング則** として定式化されている。

```
Loss ≈ (C/Compute)^α

パラメータ数 N が増えると損失が下がる：
  0.8B → 27B で損失は約 40% 低下（Chinchilla, 2022）
```

### 知識容量の推定

arXiv:2404.05405 は「1 パラメータあたり約 2 ビットの事実知識を記憶できる」と推定する。

| モデル | パラメータ | 推定知識容量 |
|---|---|---|
| 0.8B | 8億 | ~1.6 Gbit |
| 27B | 270億 | ~54 Gbit |

> **本研究の問い**：パラメータ数が増えると「概念をどう定義するか」も変わるか？
> それをグラフ構造で測れるか？

---

## instruction following（指示追従）

LLM へのプロンプトには「指示」を含められる：

```
"Do not use the word itself in the definition."
```

指示をどれだけ守るかが **指示追従能力（instruction following）**。
本研究では、この指示を守らなかった定義を `self_referential` と分類した。

**発見**：指示追従率はモデルサイズと無関係で、**ファミリー固有**。
- Qwen3.5: 76〜92% の定義で指示を無視（自己参照）
- Gemma-4: 99.9% の定義で指示に従う

---

## mlx-proxy：ローカル LLM の動かし方

本研究では Apple M4 Max 搭載 Mac を使ってローカルで LLM を動かした。

```python
# mlx-proxy 経由の API 呼び出し（OpenAI 互換）
import requests
response = requests.post("http://localhost:8080/v1/chat/completions", json={
    "model": "mlx-community/Qwen3.5-4B-MLX-bf16",
    "messages": [{"role": "user", "content": "Define the noun 'cat'..."}],
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 20,
    "max_tokens": 80,
    "enable_thinking": False,    # 必須！True だと数分かかる
})
```

---

次に読むファイル：`../02_key_papers/01_vincent_lamarre_2016.md`
