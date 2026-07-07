研究計画：辞書グラフ循環指標によるLLM概念理解の定量評価
概要

辞書を有向グラフとして捉え、その循環構造（SCC・閉路長分布・カーネル比率）をLLMが生成する定義文に適用することで、モデルの概念理解を定量的・構造的に評価する。特にQwen3ファミリー（0.6B〜32B）を用いてパラメータ数との関係を分析し、計量哲学としてのLLM評価フレームワークを確立することを目指す。
ターゲットジャーナル：Minds and Machines または Synthese（Q1）

1. 先行研究：辞書グラフ・語彙ネットワーク

1-1. 辞書グラフの構造分析

Vincent-Lamarre et al. (2016). "The Latent Structure of Dictionaries." Topics in Cognitive Science 8(3): 625–659. [論文] 4種の英語辞書を有向グラフとして分析。単語の約10%がKernelを形成し、その最大SCCがCore（Kernel内の約75%）を構成する。最小フィードバック頂点集合（全単語の約1%）で全定義を接地可能。Kernel単語は早期習得・高具体性・高頻度。本提案の方法論的先行研究として最重要。 信頼度：HIGH
Blondin Massé et al. (2008). "How Is Meaning Grounded in Dictionary Definitions?" TextGraphs-3 at COLING 2008. [論文] 辞書を有向グラフとしてモデル化し、最小接地集合の計算がNP完全（最小フィードバック頂点集合に等価）であることを証明。アルゴリズム的枠組みの基礎。信頼度：HIGH
Picard et al. (2009). "Hierarchies in Dictionary Definition Space." NIPS 2009 Workshop. [論文] CIDE・LDOCEのSCC階層構造を分析し、階層的位置と習得年齢・具体性・心像性を相関。LLM生成定義の複雑性指標としてSCC階層深度を活用する本提案の直接的先行研究。信頼度：HIGH
Levary et al. (2012). "Loops and Self-Reference in the Construction of Dictionaries." Physical Review X 2(3): 031018. [論文] 辞書グラフの閉路に焦点。意味のある閉路はランダムネットワークより著しく短く、同一閉路内の単語は同時期に英語に流入する傾向。閉路長分布を品質指標とする本提案の直接的根拠。信頼度：HIGH
Polguère (2014). "From Writing Dictionaries to Weaving Lexical Networks." International Journal of Lexicography 27(4): 396–418. [論文] フランス語語彙ネットワーク（fr-LN）に基づき、語彙システムのスモールワールド構造を特徴づける。辞書をグラフとして直接操作することの重要性を論じる権威的論考。信頼度：HIGH
Steyvers & Tenenbaum (2005). "The Large-Scale Structure of Semantic Networks." Cognitive Science 29(1): 41–78. [論文] 意味ネットワーク（単語連想・WordNet・Roget's）がスモールワールド構造とスケールフリー接続性を示すことを実証。LLM生成定義グラフの比較ベースラインとなる「正常な」グラフ特性を定義。信頼度：HIGH
Amsler (1980). "The Structure of the Merriam-Webster Pocket Dictionary." PhD Thesis, UT Austin. 辞書定義の分類語-種差構造を明らかにした計算語彙論の先駆的研究。辞書グラフ伝統の直接的祖先。信頼度：HIGH

1-2. 意味原始論（Natural Semantic Metalanguage）

Wierzbicka (1996). Semantics: Primes and Universals. Oxford University Press. [参照] 全意味が約65個の普遍的意味原始語に分解可能と主張。辞書循環問題への理論的解決策：原始語はこれ以上定義不要。LLMが暗黙的にこれらの原始語を「知っている」なら、生成された定義グラフはそれらに向かって収束すべき。信頼度：HIGH
Wierzbicka (1972). Semantic Primitives. Frankfurt: Athenäum Verlag. 14原始語提案。NSM研究プログラムの理論的起点。信頼度：HIGH

2. 先行研究：LLMの概念知識のプロービング

Petroni et al. (2019). "Language Models as Knowledge Bases?" EMNLP-IJCNLP 2019, pp. 2463–2473. [論文] LAMAプローブを導入。穴埋め形式でBERTの関係的知識を検査し、伝統的知識ベースと競合する性能を確認。本提案が個別事実から定義グラフの構造的特性へ一般化する基盤手法。信頼度：HIGH
Elazar et al. (2021). "Measuring and Improving Consistency in Pretrained Language Models." TACL 9: 1012–1031. [論文] 38関係の328言い換えパラフレーズ集合ParaRelを構築。PLMの一貫性が低く関係間で高い分散があることを示す。本提案の動機：個別事実に不一貫ならば、生成定義グラフの構造的特性はどの程度一貫するか？信頼度：HIGH
Rogers et al. (2020). "A Primer in BERTology." TACL 8: 842–866. [論文] 150以上の研究を網羅するBERT分析サーベイ。プロービング文献が明らかにしたトランスフォーマー表現についての必須背景文献。信頼度：HIGH
Tenney et al. (2019). "What Do You Learn from Context?" ICLR 2019. [論文] エッジプロービング枠組みを導入。文脈モデルが統語的表現は強力だが意味的タスクでは非文脈的ベースラインに対して控えめな改善しか提供しないことを発見。信頼度：HIGH
Belinkov (2022). "Probing Classifiers: Promises, Shortcomings, and Advances." Computational Linguistics 48(1): 207–219. [論文] プロービング手法論の批判的レビュー。プローブ複雑性、符号化vs使用情報の乖離、因果的主張への懸念を指摘。本提案のグラフベース評価手法における重要な方法論的留意点。信頼度：HIGH
Bordes et al. (2013). "Translating Embeddings for Modeling Multi-relational Data." NeurIPS 2013. [参照] TransEを提案：埋め込み空間における関係の平行移動（h + ℓ ≈ t）。LLMが関係的知識を暗黙的にどのように符号化するかの幾何学的枠組み。信頼度：HIGH
Riedel et al. (2013). "Relation Extraction with Matrix Factorization and Universal Schemas." NAACL-HLT 2013. [参照] Universal Schemaを導入：表層テキストパターンと構造化KB関係の和集合。構造化・非構造化関係的知識の統合の先駆。信頼度：HIGH

3. 先行研究：スケーリング則と創発的能力

Kaplan et al. (2020). "Scaling Laws for Neural Language Models." arXiv:2001.08361. [論文] モデルサイズ・データセットサイズ・計算量とロスの間のべき乗則関係を7桁の範囲で確立。ただしこれらの則はパープレキシティを予測するのみ。本提案のグラフ指標が構造的理解のスケーリングを異なる形で明らかにできる可能性。信頼度：HIGH
Hoffmann et al. (2022). "Training Compute-Optimal Large Language Models." NeurIPS 2022 (Chinchillaペーパー). [論文] モデルサイズと訓練トークン数を等しくスケールすべきと示し、Kaplan et al.の推奨を覆す。概念理解のための「適切な」モデルサイズはパープレキシティのスケーリングが示すものと異なる可能性を示唆。信頼度：HIGH
Wei et al. (2022). "Emergent Abilities of Large Language Models." TMLR 2022. [論文] 特定の規模閾値を超えると現れる創発的能力を定義・カタログ化。本提案の問い：定義グラフの品質も同様の創発的遷移を示すか、それとも滑らかにスケールするか？信頼度：HIGH
Schaeffer et al. (2023). "Are Emergent Abilities of Large Language Models a Mirage?" NeurIPS 2023 Outstanding Paper. [論文] 見かけ上の創発は指標選択の人工物と主張：非線形指標（完全一致）が見かけの非連続性を生む一方、連続指標（トークン編集距離）は滑らかな改善を示す。本提案のグラフ指標は本質的に連続的（SCCサイズ、閉路長分布）であり「蜃気楼」問題を回避できる可能性。信頼度：HIGH
Allen-Zhu & Li (2024). "Physics of Language Models: Part 3.3, Knowledge Capacity Scaling Laws." ICLR 2025. [論文] 言語モデルは制御された合成実験を通じてパラメータあたり正確に2ビットの知識を格納することを確立。異なるモデルサイズがエンコードできる定義的知識の理論的上限を理解するために重要。信頼度：HIGH
Carlini et al. (2022). "Quantifying Memorization Across Neural Language Models." arXiv:2202.07646. [論文] 記憶がモデルサイズ・データ重複・プロンプト長に対して対数線形にスケールすることを示す。理解vs記憶の議論に直接関連：LLMは構造的理解から定義を生成しているのか、記憶した辞書エントリを取り出しているのか。グラフ循環指標がこれを区別できる可能性。信頼度：HIGH

4. 先行研究：計算哲学・LLM理解論争

Bender & Koller (2020). "Climbing towards NLU: On Meaning, Form, and Understanding in the Age of Data." ACL 2020. [論文] 形式のみで訓練されたシステムは意味を学習できないという基礎的主張。"Octopus Test"思考実験を導入。本提案のグラフ指標は「形式を超えた意味」の具体的な操作化を提供する。信頼度：HIGH
Bender et al. (2021). "On the Dangers of Stochastic Parrots." ACM FAccT 2021. [参照] 「確率的オウム」比喩を提唱。本提案のグラフベース評価でこれを直接検証：確率的オウムならランダムな定義グラフを生成するはず。信頼度：HIGH
Mitchell & Krakauer (2023). "The Debate Over Understanding in AI's Large Language Models." PNAS 120(13): e2215907120. [論文] LLMの「理解」をめぐる論争を包括的にレビュー。本提案の定量的手法が提供するものを正確に求める：先験的立場ではなく実証的調査。信頼度：HIGH
Millière & Buckner (2024). "A Philosophical Introduction to Language Models — Part I." arXiv:2401.03910. [論文] LLMの最も包括的な哲学的論考。構成性、意味的能力（Marconiの推論的vs参照的枠組み）、接地、世界モデルを網羅。本提案の哲学的賭けを位置づけるために直接関連。信頼度：HIGH
Sambrotta (2025). "LLMs and the Logical Space of Reasons." Minds and Machines 35, Article 46. [論文] ターゲットジャーナルへの最近の掲載論文。推論主義的観点（Brandom、Wittgenstein）からLLMが言語使用者のシミュレーションであると結論。本提案の投稿文脈として重要。信頼度：HIGH
Brachman (1983). "What IS-A Is and Isn't." IEEE Computer 16(10): 30–36. [参照] 意味ネットワークにおけるIS-A関係の意味論的分類の古典的論考。LLM生成定義の階層評価に直接関連。信頼度：HIGH
Quillian (1968). "Semantic Memory." In Minsky (ed.), Semantic Information Processing, MIT Press. 意味ネットワークの計算モデルと型付きリンクによる関係グラフ構造を導入。意味は網络内の構造的関係によって構成されるというアイデアの知的始祖。信頼度：HIGH

5. 先行研究：Qwen3ファミリーとスケール横断評価

Qwen Team (2025). "Qwen3 Technical Report." arXiv:2505.09388. [論文] Qwen3ファミリー全体を提示：密なモデル（0.6B〜32B）とMoEモデル（30B-A3B、235B-A22B）、約36兆トークンで訓練、119言語対応。「思考」・「非思考」モードを統合。サイズの多様性が本提案のスケーリング分析に理想的。信頼度：HIGH
Qwen Team (2024). "Qwen2.5 Technical Report." arXiv:2412.15115. [論文] 7サイズ（0.5B〜72B）のQwen2.5を18兆トークンで事前訓練。72BフラッグシップはLlama-3-405Bと競合。異なるモデル世代間での定義グラフ品質の変化追跡に有用。信頼度：HIGH
Qwen Team (2024). "Qwen2 Technical Report." arXiv:2407.10671. [論文] Qwen2シリーズ（0.5B〜72B）とLLaMA-2、Mixtral、Gemmaとの体系的比較。マッチしたサイズでのモデル世代横断比較のベースライン。信頼度：HIGH
Jin et al. (2024). "Exploring Concept Depth: How Large Language Models Acquire Knowledge and Concept at Different Layers?" COLING 2025. [論文] 本提案の実験設計に最も近い既存研究。 Gemma（2B、7B）、LLaMA（7B、13B）、Qwen（0.5B、1.8B、4B、7B、14B）を概念的・意味的理解タスクで直接比較。「概念深度」を導入。本提案はこれをレイヤーワイズプロービングからグラフ構造全体の分析へと拡張。信頼度：HIGH
Cohen-Inger et al. (2025). "Forget What You Know about LLMs Evaluations." EMNLP 2025. [論文] ベンチマークプロンプトを意味的に等価に言い換えながら性能を検査するC-BODフレームワークを導入。32のLLMを評価し、平均2.75%の性能低下を発見。大型モデルほど感度が高く、真の理解ではなくベンチマーク依存を示唆。言い換え不変なグラフ構造特性を用いる本提案の代替評価手法の動機となる。信頼度：HIGH

6. 研究の空白（本提案の新規性）

Gap 1：辞書グラフ循環指標によるLLM評価が存在しない 辞書グラフ文献（Vincent-Lamarre et al.、Levary et al.）は人間の辞書を分析し、プロービング文献はLLMを個別事実でテストするが、LLM定義コーパスを生成してグラフ構造を分析した研究は存在しない。
Gap 2：WierzbickaのNSMをLLM評価に接続した研究がない NSMは辞書循環の理論的解決策（定義不要な原始語の有限集合）を提供するが、LLMベンチマークとして適用されたことはない。
Gap 3：連続的グラフ指標による創発「蜃気楼」回避 Schaeffer et al. (2023)の批判は非連続指標を用いるほとんどの創発能力主張に適用されるが、グラフ理論的指標（SCCサイズ、閉路長分布、カーネル比率）は本質的に連続的であり、概念的理解をスケール横断で計測する蜃気楼耐性の方法論を提供できる。

7. 実験計画

RQ（研究課題）

* RQ1：LLMが生成する定義文の辞書グラフ構造は、人間の辞書と比較してどの程度循環的か？
* RQ2：その構造的特性はパラメータ数に対してどのようにスケールするか？
* RQ3（発展）：循環率とカーネル比率において、スケールに伴う創発的遷移は観察されるか？

手順

1. 定義コーパス生成：WordNetの名詞・動詞・形容詞から約3,000語をサンプリングし、各Qwen3モデルに「Define: [word]」プロンプトで定義を生成させる
2. グラフ構築：定義文からエッジを抽出（定義中で言及された単語→被定義語）し、有向グラフを構築
3. 指標算出：SCC数・サイズ、閉路長分布、カーネル比率、最小フィードバック頂点集合サイズを算出
4. ベースラインとの比較：人間辞書（LDOCE等）の同一指標と比較
5. スケーリング分析：モデルサイズ（0.6B〜32B）と各指標の関係を回帰分析

対象モデル

モデル
	パラメータ数

Qwen3-0.6B
	0.6B

Qwen3-1.7B
	1.7B

Qwen3-4B
	4B

Qwen3-8B
	8B

Qwen3-14B
	14B

Qwen3-32B
	32B


評価指標

指標
	説明

SCC循環率
	閉路に含まれる単語数 / 全単語数

カーネル比率
	LLM定義グラフのKernelサイズ / 人間辞書のKernelサイズ

閉路長分布
	平均・分散・最小閉路長

DAG性スコア
	有向非循環グラフにどれだけ近いか

意味原始語収束率
	WierzbickaのNSM原始語（65語）がKernelに含まれる割合


WierzbickaのNSM原始語（65語）がKernelに含まれる割合
