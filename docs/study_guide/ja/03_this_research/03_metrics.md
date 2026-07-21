# 指標の詳細：Kernel / Core / MinSet / sr_rate

**所要時間**：60分

---

## 指標一覧

| 指標 | 記号 | 意味 |
|---|---|---|
| カーネル率 | kern% | 定義が閉じた最小語彙の比率 |
| Core/Kernel 比 | c/k% | カーネル内の「意味の根」比率 |
| MinSet/Kernel 比 | mset/k% | カーネルの不可約循環比率 |
| 循環率 | circ% | SCC（サイズ≥2）に属するノード比率 |
| 平均出次数 | out_deg | 語当たりの平均定義使用回数 |
| 自己参照率 | sr_rate | 被定義語が定義文に現れる比率 |

---

## カーネル（Kernel）

```python
def compute_kernel(G: nx.DiGraph) -> set:
    H = G.copy()
    while True:
        leaves = [n for n in H if H.out_degree(n) == 0]
        if not leaves: break
        H.remove_nodes_from(leaves)
    return set(H.nodes())
```

**直観**：カーネルは「自己完結した定義の島」。
カーネルに属する語は、互いの定義だけで閉じている。

実験結果（カーネル率）：

| モデル | パラメータ | kern% |
|---|---|---|
| Qwen3.5-0.8B | 0.8B | **17.9** |
| Qwen3.5-2B | 2B | 11.1 |
| Qwen3.5-4B | 4B | 10.8 |
| Qwen3.5-9B | 9B | 10.1 |
| Qwen3.5-27B | 27B | **8.6** |
| Gemma-4-4B | 4B | 7.3 |
| WordNet | — | 15.5 |

→ 大きいモデルほどカーネルが小さい（r = −0.862）

---

## コア（Core）

```python
def compute_core(G: nx.DiGraph, kernel: set) -> set:
    K = G.subgraph(kernel).copy()
    condensation = nx.condensation(K)
    # Source SCC = 縮約 DAG で入次数 0 の SCC
    source_sccs = [n for n in condensation if condensation.in_degree(n) == 0]
    core = set()
    for scc_node in source_sccs:
        core.update(condensation.nodes[scc_node]["members"])
    return core
```

**直観**：コアはカーネルの「根」。他から参照されるが、自分は独立した閉じた概念群。

---

## MinSet（最小フィードバック頂点集合）

カーネルからすべてのサイクルを壊す最小のノード集合。
ILP（整数線形計画法）で解く。

```python
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value, HiGHS

def compute_minset(G: nx.DiGraph) -> set:
    nodes = list(G.nodes())
    prob = LpProblem("MFVS", LpMinimize)
    x = {n: LpVariable(f"x_{i}", 0, 1, cat="Binary") for i, n in enumerate(nodes)}
    prob += lpSum(x[n] for n in nodes)
    for cycle in find_short_cycles(G):
        prob += lpSum(x[n] for n in cycle) >= 1
    HiGHS(msg=False).solve(prob)
    return {n for n in nodes if value(x[n]) > 0.5}
```

> **Apple Silicon 注意**：CBC ソルバーは M4 Max で動作しない（x86_64 バイナリのため）。
> 必ず **HiGHS** ソルバーを使うこと。

実験結果（mset/k 比）：

| モデル | mset/k% | 解釈 |
|---|---|---|
| Qwen3.5-0.8B | 14.4 | カーネルの 14% がサイクルの「鍵」 |
| Qwen3.5-27B | 20.3 | カーネルの 20% がサイクルの「鍵」 |
| Gemma-4-4B | **23.3** | 小さいカーネルに密なサイクル |

mset/k は r = +0.982 でモデルサイズと強い正相関（Qwen3.5 内）。

---

## 普遍カーネル：92 語

全 5 モデル（Qwen3.5）に共通してカーネルに現れる語：

```python
from collections import Counter
counter = Counter()
for model_kernel in all_kernels.values():
    counter.update(model_kernel)
universal = {w for w, c in counter.items() if c == 5}
# → 92 語
```

サンプル：go, hold, move, use, feel, allow, build, different, flat, high, small, idea, image, true, future, energy, body, people, place, time, touch, two, like ...

NSM 65 語との重複：body, feel, like, people, place, small, time, touch, true, two（10語 = 15.4%）

---

次に読むファイル：`04_results.md`
