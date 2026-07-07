# 有向グラフと強連結成分

**所要時間**：60分  
**前提知識**：なし（グラフとは何かから説明する）

---

## グラフとは

グラフは「点（ノード）」と「線（エッジ）」の集まりである。
エッジに向きがあるものを**有向グラフ**と呼ぶ。

```
A ──→ B ──→ C
↑           │
└───────────┘

ノード: {A, B, C}
エッジ: A→B, B→C, C→A（閉路！）
```

本研究では「単語」がノード、「x の定義に y が現れる」という関係がエッジになる。

---

## 次数（degree）

- **出次数（out-degree）**：あるノードから出るエッジの数
- **入次数（in-degree）**：あるノードに入るエッジの数

```python
import networkx as nx
G = nx.DiGraph()
G.add_edge("B", "A")   # B → A
G.add_edge("C", "A")   # C → A

print(G.out_degree("A"))   # → 0（A から出るエッジがない）
print(G.in_degree("A"))    # → 2（B と C から入ってくる）
```

> **この研究で最重要**：カーネルの計算に使うのは **out-degree = 0** のノードの除去。in-degree との混同に注意！

---

## 強連結成分（SCC）

**強連結成分**（Strongly Connected Component; SCC）とは、
「どのノードからどのノードへも到達できる」最大のノード集合である。

```
A ──→ B
↑     │
└─────┘

{A, B} は SCC（A→B→A と辿れる）

A ──→ B ──→ C

A, B, C はそれぞれ別の SCC（C から A に戻れない）
```

NetworkX での計算：

```python
sccs = list(nx.strongly_connected_components(G))
# SCC サイズ ≥ 2 のものが「循環」している部分
cyclic_nodes = {n for scc in sccs if len(scc) >= 2 for n in scc}
circulation_rate = len(cyclic_nodes) / G.number_of_nodes()
```

---

## 縮約 DAG（condensation graph）

各 SCC をひとつのノードとしてまとめると、SCC 間の関係が**非巡回有向グラフ**（DAG）になる。
これを**縮約グラフ**と呼ぶ。

```
SCC_1 ──→ SCC_2 ──→ SCC_3
```

縮約 DAG では：
- **Source SCC**（入次数 = 0）：他の SCC から入ってくるエッジがない「根」の SCC
- **Sink SCC**（出次数 = 0）：他の SCC へ出るエッジがない「末端」の SCC

本研究では **Source SCC の和集合 = コア** と定義する（後述）。

---

## フィードバック頂点集合（FVS）

有向グラフのすべての閉路を壊すための最小ノード集合を
**最小フィードバック頂点集合**（Minimum Feedback Vertex Set; MFVS）と呼ぶ。

```
A → B → C → A  ←── この閉路を壊すには A, B, C のいずれか1つを除けばいい
↑
FVS = {A}  （または {B} または {C}）
```

MFVS を求めることは **NP 完全問題**（計算量的に難しい）なので、
本研究では整数線形計画法（ILP）を使って厳密解を求める。

---

## まとめ

| 概念 | 定義 |
|---|---|
| 出次数 0 | どのノードも指さない（誰の定義にも使われない） |
| SCC | 互いに到達可能なノード群 |
| Source SCC | 縮約 DAG で入次数 = 0 の SCC |
| FVS | すべての閉路を壊す最小ノード集合（MinSet） |

---

次に読むファイル：`02_dictionary_structure.md`
