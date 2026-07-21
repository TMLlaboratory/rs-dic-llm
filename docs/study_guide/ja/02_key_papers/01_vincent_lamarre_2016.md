# 原著論文：Vincent-Lamarre et al. (2016)

**所要時間**：90分  
**前提知識**：`01_background/` 3ファイル

---

## 文献情報

> Vincent-Lamarre, P., Blondin Massé, A., Lepage, M., Lord, M., Harnad, S., & Marcotte, O. (2016).  
> **The latent structure of dictionaries.**  
> *Topics in Cognitive Science*, 8(3), 625–659.  
> arXiv:1411.0129 — https://arxiv.org/abs/1411.0129

---

## この論文が解決した問題

辞書は定義の連鎖でできている。連鎖はどこかで必ず循環する——
「犬 → 動物 → 生き物 → 存在 → … → ?」。
この循環の構造を計量化し、「どの語が意味の根幹を担うか」を明らかにしようとした。

---

## 使った辞書 4 種

| 辞書 | 略称 | 特徴 |
|---|---|---|
| Longman Dictionary of Contemporary English | LDOCE | 定義語彙を 2000 語に制限 |
| Cambridge International Dictionary of English | CIDE | 学習者向け |
| Webster's Seventh New Collegiate Dictionary | — | 標準的な英語辞書 |
| WordNet | — | 機械可読な概念ネットワーク |

---

## アプローチ

1. 各辞書をグラフ化（本研究と同じ手順）
2. **カーネル**を求める（出次数 0 の反復除去）
3. **コア** = カーネルの縮約 DAG で Source SCC の和集合
4. **MinSet** = ILP（CPLEX）で厳密計算

---

## 主要な発見

| 指標 | 値 |
|---|---|
| カーネル率 | 約 10%（4辞書平均） |
| Core / Kernel 比 | 65〜90%（平均 75%） |
| MinSet 率（カーネル内） | 約 1% |

**解釈**：語彙のたった 1% を覚えれば、残りのすべての循環を「ほどける」。
語の意味は最終的に非常に少数の基本概念に依存している。

---

## 学生資料との重要な差異

あなた（ロペスチャパホセ）が書いた資料（`20260512_ぺぺ.md`）にいくつかの誤りがあった。
確認して理解しよう。

| 項目 | 資料の記述 | 原著の正しい内容 |
|---|---|---|
| カーネル計算 | **入次数 0** を除去 | **出次数 0** を除去 ← 最重要 |
| コア定義 | 最大 SCC | **Source SCC の和集合** |
| MinSet 計算 | greedy 近似 | **ILP（CPLEX）で厳密解** |
| 前処理 | レンマ化 | 原著は **ステミング**（本研究は limitation に記載） |

### カーネルの誤りを確認する実験

```python
import networkx as nx

def compute_kernel_CORRECT(G):
    H = G.copy()
    while True:
        leaves = [n for n in H if H.out_degree(n) == 0]  # 出次数 0
        if not leaves: break
        H.remove_nodes_from(leaves)
    return set(H.nodes())

def compute_kernel_BUGGY(G):
    H = G.copy()
    while True:
        leaves = [n for n in H if H.in_degree(n) == 0]   # 入次数 0（誤り）
        if not leaves: break
        H.remove_nodes_from(leaves)
    return set(H.nodes())

# テストグラフ: B→A, C→B  (A の定義に B, B の定義に C)
G = nx.DiGraph()
G.add_edge("B", "A")
G.add_edge("C", "B")

print("正規:", compute_kernel_CORRECT(G))  # {'C'}
print("バグ:", compute_kernel_BUGGY(G))    # {'A'} ← 逆！
```

---

## この研究との関係

本研究は Vincent-Lamarre et al. の手法を **LLM 生成定義** に適用した拡張研究である。

| 側面 | 原著 | 本研究 |
|---|---|---|
| 辞書の出所 | 人間が書いた辞書 4 種 | LLM が生成した定義 |
| 語彙数 | 辞書全体（数万語） | 3000 語のサブセット |
| 比較軸 | 辞書間の比較 | モデルサイズ・ファミリー間の比較 |
| ベースライン | 辞書同士 | WordNet |

---

次に読むファイル：`02_scaling_laws.md`
