# Start Here — rs-dic-llm · ここから読む

**Pepe — read this page first.** It tells you what changed, what to read, in what
order, and what to do next. Everything is available in English and Japanese.

**ぺぺへ。まずこのページを読むこと。** 何が変わり、何をどの順で読み、
次に何をするかが書いてある。すべて英語版と日本語版がある。

*Last updated / 最終更新: 2026-09-01*

---

## The one-paragraph version · 一段落での要約

**EN** — Your 17-model study and the base-vs-instruct run gave us enough for a real
paper, but a check that had never been run — a **degree-preserving null model** —
showed that `kernel_ratio` is indistinguishable from chance (WordNet included). It
measures definition length, not conceptual organization. One thing does survive the
correction: **mutual definitions occur 9–24× more often than chance**, and that
excess separates instruction-tuned models from base models completely (8.9–23.5 vs
1.5–7.3, with WordNet at 10.0). The paper is now about that, and about instruction
tuning being what creates it.

**JA** — 17モデルの統制実験と base vs instruct のランで論文の材料は揃った。
ただし一度も走らせていなかった検証 ──**次数保存ヌルモデル**── にかけると、
`kernel_ratio` は偶然と区別がつかない（WordNet を含めて）。
測っているのは定義文の長さであって概念組織ではない。
補正しても残るものが一つある ──**相互定義が偶然の9〜24倍出現する**。
この過剰度は instruction-tuned と base を完全に分離する
（8.9〜23.5 対 1.5〜7.3、WordNet は 10.0）。論文はこれと、
それを作っているのが指示チューニングであることについて書く。

---

## Read in this order · この順で読む

| # | Document | 文書 | Why · なぜ | Time |
|---|---|---|---|---|
| 1 | **[`roadmap_en.md`](roadmap_en.md)** | **[`roadmap_ja.md`](roadmap_ja.md)** | The plan: what to run, what to learn, the schedule. **This is your working document.** · 計画：何を回し何を学ぶか、日程。**これが君の作業文書** | 30 min |
| 2 | [`../research-direction-2026-09_en.md`](../research-direction-2026-09_en.md) | [`../research-direction-2026-09.md`](../research-direction-2026-09.md) | The full analysis behind the plan: every number, the related-work survey, the code audit · 計画の根拠：全数値、関連研究調査、コード監査 | 60 min |
| 3 | [Visual report (EN)](https://claude.ai/code/artifact/f8a88e8a-d660-44ca-b925-502fa7ccf4ca) | [視覚版レポート (JA)](https://claude.ai/code/artifact/d5ab870c-34d5-440f-bc43-01d9f64ea1fc) | Same content as #2 as a web page, with the interactive chart · #2 と同内容の図付きWebページ | 20 min |
| 4 | [`../correction_ja.md`](../correction_ja.md) | 同左 | The kernel out-degree correction from May. Still the single most important implementation detail · 5月のカーネル出次数の訂正。いまも最重要の実装事項 | 15 min |

Then start on **E1** in the roadmap. It needs no GPU.
そのあとロードマップの **E1** に着手すること。GPU は不要。

---

## What is where in this repository · リポジトリのどこに何があるか

### Read before E1 · E1 の前に読む

| Path | What it is · 内容 |
|---|---|
| `experiments/null_model.py` | **New.** The degree-preserving null model. Read it line by line — you must be able to explain what `nx.directed_edge_swap` preserves · **新規**。次数保存ヌルモデル。一行ずつ読み、何が保存されるか説明できるように |
| `src/metrics/kernel_core.py` | Kernel (iterative out-degree-0 removal) and Core. **Sound**, and the Core definition is the open question in the roadmap · カーネルとコア。**健全**。Core の定義はロードマップの未決事項 |
| `src/metrics/minset.py` | Minimum feedback vertex set by ILP. **Sound** — a genuinely correct implementation · ILPによる最小FVS。**健全**、正しい実装 |
| `tests/test_kernel_outdegree.py` | Why out-degree and not in-degree, as an executable test · 出次数であって入次数でない理由を実行可能なテストにしたもの |

### Read before E2 · E2 の前に読む

| Path | What it is · 内容 |
|---|---|
| `src/graph_build.py` | Graph construction. **Note:** records marked `self_referential` are still fed into the graph · グラフ構築。**注意**：`self_referential` のレコードもグラフに入っている |
| `src/generation.py` | Generation and status labelling. The self-reference check is token membership only — that is why prompt echoes slip through · 生成とステータス付与。自己参照判定はトークン包含のみ。だからプロンプトエコーが通ってしまう |
| `src/normalize.py` | Lemmatization, stopwords, vocabulary filter · レンマ化・ストップワード・語彙フィルタ |
| `data/definitions/*_42.jsonl` | 23 models × 3,000 definitions. Compare `Gemma3-27B_42.jsonl` with `Gemma3-27B-pt_42.jsonl` and see the problem for yourself · 23モデル×3,000定義。両者を並べて問題を自分の目で見ること |

### Results · 結果

| Path | What it is · 内容 |
|---|---|
| `results_2026-08-09_Runpod/summaries/full_summary.json` | **The main dataset.** 17 models, uniform bf16, frozen word list, WordNet baseline · **主データ**。17モデル、bf16統一、凍結語リスト、WordNetベースライン |
| `results_2026-08-31_Runpod/` | Gemma3 base (pt) × 5 sizes + Qwen3-4B-Instruct-2507. The new contrast · 新しい対照軸 |
| `results_2026-07-21_TogetherAI/1-setup/cross_family_replication_report.md` | The cross-family replication. Still the best-written document in this repo — reread its §5 on density mediation · 交差ファミリー再現。このリポジトリで最もよく書けた文書。§5の密度媒介の議論を読み直すこと |
| `results_2026-08-09_Runpod/summaries/quantization_study.json` | ⚠️ **Do not cite.** Identical to 15 significant figures across bf16/int8/int4 · ⚠️ **引用しないこと**。3精度で有効数字15桁まで一致 |

### Your own slides · 君自身のスライド

`docs/results-slides.md` and `docs/style-findings-slides.md` are still good. The
"style drives topology" argument in the second one is **correct and now confirmed
by the null model** — that part of your analysis holds up completely. What changes
is that we can now say it with a chance baseline instead of a correlation.

`docs/results-slides.md` と `docs/style-findings-slides.md` はいまも有効である。
後者の「文体が位相を駆動する」という論証は**正しく、ヌルモデルで裏付けられた**。
君のあの分析はそのまま生きている。変わるのは、相関ではなく偶然水準を基準にして
それを言えるようになったことである。

### Do not use · 使わないもの

| Path | Why · 理由 |
|---|---|
| `docs/paper_ja.md`, `docs/paper_en.md` | Based on Qwen3.5, which turned out to be a VLM and incompatible with this pipeline. Their central correlation has the **opposite sign** to current results. To be moved to `docs/archive/` · Qwen3.5（VLMで本パイプライン非対応と判明）に基づく。中心的相関の符号が現在と**逆**。`docs/archive/` へ移す予定 |
| `plan.md` | The original 2026-05 research plan. Historical only · 2026年5月の当初計画。歴史的記録のみ |

---

## The three things to carry forward · 持ち越すべき三つのこと

**EN**

1. **A number without a comparison is not evidence.** This is the whole lesson of
   this round. `kernel_ratio = 12.5%` meant nothing until we knew what chance
   looked like. Every metric from now on gets a null or a control.
2. **Your style-fingerprint finding survived.** Out-degree, OOV rate and tokens/word
   predicting model scale is real work and it becomes your thesis. The one fix it
   needs is in the roadmap §4.
3. **We are correcting our own published claims.** That is not a setback; it is the
   most credible thing a paper can do. Half of this manuscript is "we checked our
   earlier result properly and here is what is actually true."

**JA**

1. **比較のない数値は証拠にならない。** 今回の教訓はこれに尽きる。
   `kernel_ratio = 12.5%` は、偶然水準を知るまで何も意味していなかった。
   これ以降、すべての指標にヌルか統制を付ける。
2. **君の文体指紋の発見は生き残った。** 出次数・OOV率・tokens/word でモデル規模を予測できるのは
   本物の仕事であり、卒論になる。必要な修正はロードマップ §4 に一つだけ書いた。
3. **我々は自分自身の公表済みの主張を訂正する。** これは後退ではなく、
   論文ができる最も信頼に値することである。この原稿の半分は
   「以前の結果をきちんと検証し直した。正しくはこうである」になる。

---

## Questions · 質問

Bring results with the four things listed in roadmap §9 — the number, the
comparison, what would have falsified it, and the reproducing command. If a result
contradicts the plan, bring it **early**; that is the most valuable thing you can
find.

ロードマップ §9 の4点 ──数値、比較対象、何が観測されたら主張を捨てたか、再現コマンド──
を揃えて持ってくること。計画と矛盾する結果が出たら**早く**持ってくること。
それが最も価値のある発見である。
