# AKR: 意味・評価の限定補完と小比較の結果

2026-10-01 JST · upstream analysis draft · research delta

## 0. 結論

**今回選んだ意味・合成と評価lifecycleの外部補完は、次の実例比較に使える条件まで具体化できた。この二領域の探索を広げるより、R0/R2/R4の小さな判別事例を作り、同じ課題で操作・context・checkerの経路を替える段階へ進む価値が高い。**

ここで区切るのは今回の限定調査であり、Architecture探索空間のclosureではない。D01〜D49、F1〜F8は維持する。最終Architecture、Canonical format、DB、IR、schema、製品採用は決定しない。

今回減らせた不確実性は、次の範囲である。

- 適用性には、形式の受理、処理系の対応範囲、入力・状態での前提成立がある。合成には型接続に加え、評価順、skip、null、変換と元問題への結果対応の単位が関わる。
- 評価対象の版、要求した設定、実際に使った入力、checkerの定義、採点値、採否規則を区別する必要がある。名前・version・digestの存在だけでは、これらの固定や再取得を保証しない。
- 固定したAKR資産を使う人工故障で、**最新parent＋古い全文はGitのfast-forwardでも変更を失う**こと、**clean mergeでも依存参照が壊れる**ことを観測した。
- 宣言済み依存closureを取得すると、今回の2seedでは全登録資産より本文量を減らし、1seedでは全件と同じになる。保存した取得目的・固定版・期待集合があれば、別processから不足や違う本文を検出・復元できた。

これらは機構の反例と取得・復元の有限検査である。自然言語algorithmの意味保存、modelの実効能力、Family順位、長期保守費はまだ測れていない。

## 1. 基準、範囲、成果物

基準は[研究境界評価](./2026-09-30-research-frontier-and-evidence-value-assessment.md)、[Assumption Delta Audit](./2026-09-30-external-landscape-assumption-delta-audit.md)、[Coverage Audit](./2026-09-29-architecture-search-space-coverage-audit.md)。既済みの全面auditは再実行していない。

今回は前回の「続行」により、限定外部補完、既存資産からのR0事例、小さなR1/R5/R3比較を実行した。外部探索は対照的な4例に限定した。

| 成果物 | 役割 |
|---|---|
| [意味・合成の証拠ノート](./semantic-composition-evidence-2026-09-30.md) | Unified Planning、CWL/cwltoolの契約・固定code・Issue/PRと限界 |
| [評価lifecycleの証拠ノート](./evaluation-lifecycle-evidence-2026-09-30.md) | lm-evaluation-harness、MLflowの入力・cache・dataset・scorer契約と限界 |
| [小比較README](./research-pilot-2026-10-01/README.md) | 入力、共通oracle、故障条件、再実行方法、測定の射程 |
| [source snapshot](./research-pilot-2026-10-01/source-snapshot.json) / [oracle](./research-pilot-2026-10-01/oracle.json) | 固定入力の証拠copyと、実行前に独立に確認した期待値 |
| [比較手順](./research-pilot-2026-10-01/run_pilot.py) / [結果](./research-pilot-2026-10-01/results.json) | 一時Gitと取得bundleだけを操作する有限検査、機械可読観測 |

外部調査は09-30に開始し、上限による中断を経て10-01に整理完了。Issue/PR状態はノートの取得時点に限る。leadは10-01に重要な4箇所の固定code/記述を再確認したが、最新releaseの再現やIssueの現在状態は調べ直していない。外部softwareの導入・実行はない。

AKRの入力は `0f22fec375af8001afa4a2cd948ba205c409ad3d` のregistry、algorithm 3件、policy 2件。本文とGit blob SHAを照合した。snapshotは研究用の固定copyであり、別のCanonical authorityではない。現行のファイル形式・分類を上流設計の前提へ昇格させない。

## 2. 限定外部補完で変わった問い

### 2.1 適用・合成・変換

**S1 — 適用性の検査対象を分ける。** Unified Planningのvalidatorはproblem/plan kindの対応を確認し、別の経路で初期状態からactionの前提・状態遷移・goalを検査する。CWLのrequired capabilityとhintにも異なる契約がある。「受理できる表現」「扱える処理系」「この状態で実行できる方法」は一つのbooleanにしない。[UP validator契約](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/mixins/plan_validator.py)、[状態検査の実装](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/plan_validator.py#L117)、[CWL v1.2契約](https://github.com/common-workflow-language/cwltool/blob/190415a46a7249ab85fde87d797ec1ea688a8cc5/cwltool/schemas/v1.2/Workflow.yml)

**S2 — 条件の評価位置が合成結果を変える。** CWLはpickValue、scatter/valueFrom、各jobのwhenに順序を持ち、skipした出力をnullとする。型が接続できても「条件falseなら入力処理全体を飛ばす」というguardと同じにはならない。単一sourceのall_non_nullには型検査・実行の不一致報告と修正PRがある。契約、過去の故障、修正差分を読んだのであり、こちらでrunnerを実行していない。[CWL契約](https://github.com/common-workflow-language/cwltool/blob/190415a46a7249ab85fde87d797ec1ea688a8cc5/cwltool/schemas/v1.2/Workflow.yml)、[Issue #2219](https://github.com/common-workflow-language/cwltool/issues/2219)、[merged PR #2220](https://github.com/common-workflow-language/cwltool/pull/2220)

**S3 — converterの存在とchain可能性を分ける。** UPのCompilerResult一般はactionまたはplan全体を元へ戻す写像を受け付ける。一方、読取版のCompilersPipelineはaction写像を要求し、TimedToSequentialはplan全体写像を返す。変換する単位、戻す単位、chainの契約を確認し、戻した結果を元問題のcheckerへ接続する必要がある。この対応は数学的な逆関数や可逆性を要求せず、写像の存在は全入力での意味保存証明ではない。元問題へ結果を対応付けられないprojection等は、別の対応契約で検査する。[results.py](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/results.py)、[pipeline](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/compilers/compilers_pipeline.py)、[TimedToSequential](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/compilers/timed_to_sequential.py#L497)

**S4 — 判定statusはinterfaceの縮約で失われ得る。** UPはVALID/INVALID/UNKNOWNを区別するが、読取版ではbool化すると非VALIDがfalseになる。AKRで同じ縮約を行うと、追加調査、別checker、改修の分岐に必要な情報を失う。このことはUPの仕様が誤りという主張ではなく、adapterが何を保存すべきかという問いである。[ValidationResultStatus](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/results.py#L30)

適用・合成の形式モデルが外部世界の事実や自然言語のすべてを検証するとは仮定しない。S1〜S4はD02/03/07〜14/32/33/38の検査条件を具体化する差分であり、新しい共通DSLを要求しない。

### 2.2 評価のidentity、入力、由来

**V1 — 記録した設定と実入力を照合する。** lm-evaluation-harnessには、同じtask名でprompt/datasetを変えると旧request cacheを使いながら新configを記録するという報告がある。固定codeの読取keyにもtask config digestは含まれず、原因説明と整合する。ただし全cache経路・最新releaseの不具合を実証したものではない。次のAKR比較では要求条件・実入力・結果に残る記録の一致を検査する。[Issue #4084](https://github.com/EleutherAI/lm-evaluation-harness/issues/4084)、[task.py L288](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/lm_eval/api/task.py#L288)

**V2 — hashの射程を確認する。** lm-evalの読取版task hashはdoc/prompt/targetをまとめるもので、評価契約全体のhashではない。MLflowの読取版SQL storeではdataset digestが名前＋更新時刻のSHA-256先頭8文字であり、同repo conceptsのcontent hashという説明との差がある。field名やhash方式だけで内容同一性を推定できない。この差はleadも固定版で確認した。すべてのMLflow Datasetやmutation経路へ一般化しない。[lm-eval hash構築](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/lm_eval/loggers/evaluation_tracker.py#L249)、[MLflow digest関数](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/mlflow/store/tracking/sqlalchemy_store.py#L7740)、[同版concepts](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/docs/docs/genai/concepts/evaluation-datasets.mdx)

**V3 — 記録、再取得、再実行を分ける。** MLflowの読取OSS経路ではdataset sourceがIDを持ち、loadは現在のstoreへIDを渡す。list_versionsはDatabricks以外で未対応で、旧runのdataset snapshotを戻したいというfeature requestもある。全artifactに旧入力が残らないとは断定しないが、runへの関連付けだけで旧入力復元を保証できない。[EvaluationDatasetSource](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/mlflow/data/evaluation_dataset_source.py)、[version API](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/mlflow/genai/datasets/evaluation_dataset.py#L225)、[Issue #25313](https://github.com/mlflow/mlflow/issues/25313)

**V4 — scorerの固定と採否規則の固定を分ける。** MLflowはscorer版を指定できる一方、version省略時のlatestは可変である。読取Scorerの `_pass_if` はprocess内限定で非serializeと明示される。scoreとrelease採否を決める規則を分離し、実際に解決したchecker定義・model・rubric等の範囲を記録する。非serializeという設計を登録欠陥とは呼ばない。[scorer versioning](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/docs/docs/genai/eval-monitor/scorers/versioning.mdx)、[Scorer](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/mlflow/genai/scorers/base.py#L318)

**V5 — checkerも評価対象になる。** 公式judge alignmentは参照feedbackとheld-out dataを使う。これにより生成器とcheckerの共通誤りまで自動検出できるとは確認できない。また、評価packageのload修正がmergedでも、外部metricの実行・採点値の同等性まで検証済みとは限らない。F5を比較するには、独立した反例や期待値と未判定を含む検査が必要である。[judge alignment](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/docs/docs/genai/eval-monitor/scorers/llm-judge/alignment.mdx)、[lm-eval PR #4076](https://github.com/EleutherAI/lm-evaluation-harness/pull/4076)

V1〜V5はD04/09/15/17/24/31〜33/36/37/41/45/46へ吸収する。評価器・dataset・期待値等を識別できる対象として扱う案は強まるが、独立assetとして保存する粒度は未決定である。

### 2.3 証拠 → 既存探索地図のmapping

| 入力 | Delta判定 | 主なD / Family / R | 変更する検査条件 |
|---|---|---|---|
| S1 対応範囲と状態前提 | strengthens existing conclusion / expands option set | D08/11/14/32、F5/F8、R0/R2/R4 | 受理・未対応・前提不成立を別に検査 |
| S2 評価順・skip・null | expands option set | D03/08〜12、F6/F8、R2/R4 | 型適合でも順序で結果が変わる対照 |
| S3 変換単位・元問題への結果対応写像 | expands option set / changes research priority | D02/03/09/10/14/33/46、F5/F8、R2/R4 | action単位と全体単位、元問題への検査接続 |
| S4 UNKNOWNの縮約 | strengthens existing conclusion | D07/11/32/38、F5/F8、R1/R4/R7 | status・理由が後続主体まで届くか |
| V1 設定とcache実入力 | strengthens existing conclusion | D17/31/36/37/46、F1/F2/F7、R5/R6 | 要求・実使用・記録の不一致検出 |
| V2 hash/digestの射程 | strengthens existing conclusion | D04/17/24/32/37、F2/F5/F7/F8、R4/R6 | 内容、変更識別、評価契約のidentityを分ける |
| V3 旧dataset再取得 | strengthens existing conclusion | D15/17/33/37/41、F2/F5/F7、R5/R6 | 旧runの入力を実際に取り戻す |
| V4 scorerと採否規則 | strengthens existing conclusion / expands option set | D15/17/32/37/45、F2/F5/F8、R4/R6/R7 | 採点と採用判断の由来を別に照合 |
| V5 checkerの妥当性 | changes research priority | D07/09/17/32/37、F5/F8、R0/R4 | 独立反例、false accept/reject、未判定 |
| P1 stale全文 / clean merge | strengthens existing conclusion | D18/20〜22/32、F1/F2/F7、R1/R2 | Git受理とpayload/参照契約を別に観測 |
| P2 宣言closure / 復元 | strengthens existing conclusion | D09/24/30/31/43/46/49、F1/F6/F7、R3/R5 | job目的、固定版、期待集合、完了receipt |

新しい独立次元は追加しない。S/V/Pは今回の追補内のラベルであり、baseline E01〜E15/P01〜P07を改番しない。この補完は過去の中核前提を反証していない。MLflowのdocs/code差は外部記述への限定であって、AKR baselineの撤回ではない。

## 3. R0: 既存資産と今回の作業から得た判別事例

固定入力では、3つのalgorithmは自然言語の判断・調査手順で、policy 2件は証拠状態とmodalityの保持規則である。これは現在のsampleの性質であり、AKR全対象の境界ではない。

| 観測した対象 | 現在確認できる区別 | 次に必要な判別事例 |
|---|---|---|
| ALG-RES-001 | 探索を広げる手順と、material decisionが変わらなければ止める条件を併せ持つ | 同じ入力で追加探索が有益/無益な対照。件数の増加を成功にしない |
| ALG-GOV-001 | 情報価値はactor・authority・actionabilityに依存し、式は未校正の概念モデル | 同じ情報がactorにより価値を変える例。数値式へ変換した際の未根拠な精密化を検出 |
| ALG-SEC-001 | RES/GOVを呼び出す段階と、重大なunknownやhard gateを平均scoreで相殺しない規則 | 部分入力・前提欠落・局所改修で、scopeとunknownを保持できるか |
| POL-EVID/POL-MOD | 判断手順への制約として働く。単純な関数呼出しとは役割が違う | 委任・圧縮・低能力profileで、条件や証拠状態が強い指示へ変わる反例 |
| 今回の証拠回収 | 固定code、Issue報告、merge、こちらの実行を区別して統合する実作業 | 不足/相反する根拠の引継ぎと、誤った「確認済み」への昇格を検査 |
| 今回の公開・復元検査 | 有限の参照・byte・完了検査は自然言語意味判断と異なる | 決定的checkerで判定できる領域と、その外側のUNKNOWNの接続 |

前半4行は既存本文からの観察と次の実験案であり、各algorithmの有用性を実測した結果ではない。後半2行は今回の実作業だが、汎用algorithmとして新規登録していない。

宣言requiresだけでは、制約policy、常時必要な方法、条件付き呼出し、評価器、環境依存の役割は同じにはならない。D09/10の関係種別とD08/11の適用・実行条件として扱えるかを実例で調べる。今回のclosure検査は現在の宣言を尊重したもので、宣言が意味上十分だという証明ではない。

## 4. P1: mutation・公開の小比較

### 4.1 実行条件

一時Git repositoryへ固定入力をcopyし、同じ元本文に独立なA/B markerを挿入した。実行前の共通oracleは「両変更を保持して受理するか、公開を拒否し、受理後に片方を黙って失わない」。判定は公開先本文のmarkerを読む。方式ごとの拒否機構の有無を成功定義にせず、共通の損失条件で観測した。

拒否した経路では、公開先の本文とcommitが既受理Aのまま保持されたことも検査する。独立レビューで、拒否の成否だけを判定していたpredicateをこの保存条件へ合わせ、再実行した。今回の拒否2条件の観測・結論は変わらなかった。

追加の対照は、AがGOVのIDを参照元とregistryも含めて変更し、旧baseからBが旧IDを要求するcallerを追加するケース。merge後の実際のalgorithm ID集合とcaller要求を照合した。これは構造的参照契約の検査である。

Python 3.9.6、Git 2.54.0 (Apple Git-157)。一つのhostで決定的なscheduleを実行した。実Gitのmerge・local push・ref更新を使用し、GitHubの並行操作、purpose-oriented mutation tool、DB transactionを実装した比較ではない。

### 4.2 観測

| 条件 | 実際の受理 | 公開先のA/B | 共通oracle / 判別できたこと |
|---|---|---|---|
| 古いparentからBをpush | 拒否（non-fast-forward） | Aのみ | 満たす。今回の古い履歴の受理を拒否 |
| Aをparentにし、旧base由来のB全文を書き戻す | 受理（fast-forward） | Bのみ | **満たさない。Aの変更消失** |
| A/B独立編集を実際に3-way merge | 受理 | A/B両方 | 満たす。この非重複text編集では保持 |
| expected old refをbaseとしてref更新 | 拒否（old value不一致） | Aのみ | 満たす。refの比較更新で今回のstale提案を拒否 |
| ID改名と旧ID callerをclean merge | merge成功 | 別oracle | **ALG-GOV-001参照欠落。構造oracleを満たさない** |

「拒否できた」だけでは再baseやrepairが安価とは言えない。また、3-way mergeの1例が意味改修を安全に合成する証拠でもない。refの比較更新はsemantic transactionとは別である。

### 4.3 上流設計への差分

- Gitの管理基盤としての採用は維持する。その受理条件だけで、payloadの由来・依存整合性・意味保存を判定しない。
- AIが最新parentを取り直してcommitする経路でも、作成した変更がどのbaseの内容に基づくかを失うとstale全文を受理できる。D18/20/21/22の比較では**parent、変更の根拠base、操作範囲、検証した集合、公開結果**を対応付ける。
- clean merge後の依存検査が必要という機構条件は具体化できた。自然言語の適用・stop・hard gateまで同じcheckerで検証できるとは言えない。
- F1/F2/F7のいずれも、この境界を実現する候補になる。今回比較したのはGit操作経路であり、Familyの実装や順位ではない。

## 5. P2: working contextの取得・復元

### 5.1 宣言closureと本文量

手確認した期待集合をoracleに保存し、手順側のclosure関数が同じ集合を得るかを確認した。期待値をその関数から生成していない。

| seed | seed本文のみ | 宣言closure | 全登録asset本文 | closure外として追加されるもの |
|---|---:|---:|---:|---|
| ALG-RES-001 | 2,003 bytes / 1件 / policy 2件欠落 | 4,117 bytes / 3件 / 欠落0 | 11,732 bytes / 5件 | GOV、SEC |
| ALG-GOV-001 | 2,365 bytes / 1件 / policy 2件欠落 | 4,479 bytes / 3件 / 欠落0 | 11,732 bytes / 5件 | RES、SEC |
| ALG-SEC-001 | 5,250 bytes / 1件 / 依存4件欠落 | 11,732 bytes / 5件 / 欠落0 | 11,732 bytes / 5件 | なし |

registryは全方式で1,845 UTF-8 bytesを別に数える。上表はasset本文bytesであり、token数、modelが読んだ量、tool呼出し費、回答品質ではない。全件側の追加分は**宣言closure外**という意味で、実taskに意味上不要と判定したわけではない。

このsampleで選択取得の差が観測できた一方、SECではclosureが全件になる。大規模化後の平均closureサイズや、semantic依存の抽出漏れは不明である。単一seedの結果を全利用へ外挿しない。

### 5.2 保存fileのみからの別process復元

SECの5assetを期待集合とし、取得目的・固定source ref・ID/version/blob SHA・期待pathを持つintake manifestと、取得物を保存した。復元は新しいPython child processに保存pathだけを渡した。親の途中memoryは渡していない。

| 人工条件 | 結果 | 検出・復元 | 修復用上流entry検査数 |
|---|---|---|---:|
| 5件＋manifestが完了状態 | COMPLETE | 既存byteとclosure確認 | 0 |
| 2件＋manifestの途中状態 | COMPLETE | 欠落3件を固定snapshotから取得 | 3 |
| 2件のみ、manifestなし | UNKNOWN_INTAKE | job目的・期待集合・source版を確定しない | 0 |
| 同IDだがPOL-MODのversion違い | COMPLETE | header不一致を検出し固定本文へ復元 | 1 |
| 同ID/versionだが本文だけ変更 | COMPLETE | blob不一致を検出し固定本文へ復元 | 1 |
| 2件＋manifest、固定上流からMODを除去 | INCOMPLETE | 他2件を復元、MOD欠落を残す | 2 |

repair_source_entries_checkedは修復のため存在する上流entryを検査した件数である。手順はmanifestがあればsource cache file全体を毎回読み込むため、0はsource I/Oが0という意味ではない。network/MCP tool回数・bytesでもない。COMPLETEの各結果は期待ID集合と全blob SHAを独立に照合した。UNKNOWN_INTAKE/INCOMPLETEは復元手順の正しい拒否・未完了だが、job完了ではない。

今回は途中状態を人工的に用意した。実processの強制停止、書込途中の切断、power loss、fsync、悪意あるmanifest、重複worker、外部作用の再実行は試していない。source/manifestはこの比較で信頼するfixtureであり、hash自体がauthorityや許可を証明するとは扱わない。復元手順も固定frontmatterの限定readerで、汎用runtimeではない。

### 5.3 D49、D48、CACへの影響

**D49は維持する。** 今回は、taskと固定asset版を結ぶintake、現在の取得物、完了receiptを区別すると、別processから再開時のscopeを確定できる例を得た。取得物だけでは作業目的を確定できないという境界が具体化した。

byte検査はD24/32、鮮度・旧版はD20/31、派生物はD46、authorityはD05/40、復元はD43に引き続き分担する。D49へすべてのmaterializationを集約しない。今回検査していない主体変更、権限失効、contextの残存・unbind、writebackを追加課題として残す。

**D48は今回の直接実験による変更なし。** 取得・検査をeventで起動する構成でも、受領は完了ではなく、起動対象のscopeや受理条件は別途必要になる。上表はevent deliveryやdedupの試験ではない。event-driven maintenanceは作業起動・再評価の入口として既存の位置付けを維持し、通知をsemantic authorityにしない。

**Change Absorption Capacityは共通評価属性のまま。** source意味とintake/receiptを分離する案は、reader・harness交換時に意味を固定して再取得する比較へつながる。しかし今回は同じreaderで新processを起動しただけで、harness/model/protocol交換への吸収能力を測ったものではない。

## 6. Interface Capacity / Realization Efficiencyの差分

経路は従来の

`Backend × Representation × Tool exposure × Protocol × Permissions × Harness × Working Context × Execution Environment`

を維持する。各項の理論能力と、経路を通じて対象modelが利用できる能力を区別する。今回得た具体的な損失点を加える。

| 境界 | backend等に存在しても失われるもの | 次の経路比較で確認すること |
|---|---|---|
| result → tool返値 | UNKNOWN、timeout、unsupportedの理由がbool化で消える | 元statusと理由、対象版が後続AIまで届く |
| converter → chain | 全体単位逆変換をaction単位interfaceへ接続できない | 入出力・変換単位・元問題への結果対応写像の適合、元問題での再検査 |
| versioned store → acquisition | digest/IDはあっても旧snapshotの取得契約がない | 実際に固定本文/評価入力を取り戻せる |
| cache → execution receipt | configの記録と実使用requestがずれる | 要求・実使用・記録を独立に照合 |
| Git → mutation tool | latest parentを使えてもstale payloadの由来を失う | base・patch/command・検証集合・公開を結ぶ |
| context → handoff | 本文が残ってもtaskの目的・期待集合が不明 | intakeと完了を別に引き継ぎ、未知を拒否/未完とする |

Interface Capacityには結果表現の精度、参照固定・再取得、拒否理由の到達を加えて検査する。これは新次元ではない。Realization Efficiencyについて、今回測ったのは本文bytesと修復用上流entry検査数の限定proxyだけで、model別の達成率・総費用・context利用率は未測定である。

同じalgorithm意味をchat/agent/local等へ適応する際は、実行profileやadapterで対応範囲・資源・取得方式を替える案を維持する。低能力環境でmandatory policyや条件を落として同一意味を名乗るdegradeは、今回の宣言closure oracleとも整合しない。表現を短くする場合は条件・modalityの保持を別に検査する。実現できない範囲をUNKNOWN/unsupportedとして扱うことと、Canonicalの意味を変更することを分ける。

## 7. F1〜F8への必要な差分

| Family | 今回の更新 | 依然不足する識別証拠 |
|---|---|---|
| F1 build/package | 宣言closure、評価器の共有依存、実使用入力receiptの検査を具体化 | 局所改修の再build費、依存抽出の十分性、実query |
| F2 semantic transactional registry | Gitと意味受理の境界、ID/版/digest/snapshotの違い、scorer版の保証範囲を具体化 | semantic transaction＋Git公開を含む経路と費用 |
| F3 accepted event authority | 今回は中核について新しい直接証拠なし | domain eventをauthorityにする適合性、event版の意味migration |
| F4 claims/evidence federation | 相反・未判定を縮約しないinterfaceと、評価根拠の対象版を具体化 | 異なるauthorityの採用・撤回・query費、ontology evolution |
| F5 specification/generator/checker | generator/checker境界を扱う直接code・契約を補完。対応範囲、元問題での検査、checker自身の反例が必要 | AKR判断手順の仕様化費、共通誤り、実改修時の便益。優位性は未判定 |
| F6 durable workflow | evaluation order/skipと、途中取得の復元条件を具体化 | durable instanceなしのbundle再開では足りない実作業、外部作用の保証 |
| F7 immutable graph/published roots | 固定byteの取得、closure、可変公開refの境界を小例で確認 | GC・offline・旧reader・取消・root公開全体の保証 |
| F8 multiple IR/rewrite | 変換単位・元問題への結果対応写像・feature宣言と実体の照合、形式化できる部分の検査を具体化 | AKRで扱える部分集合、意味保存根拠、変換器の維持費 |

F5/F8の証拠は前回より具体的になった。ただしplanning/workflowの形式化範囲をAKRの自然言語資産へ移せるかは未確認で、証拠密度をFamily順位へ変換しない。F3/F4の中核の薄さは残る。Familyは併用可能な比較観点であり、今回の5/9/6条件は各Familyを等条件で競わせた件数ではない。

## 8. 評価証拠を扱うための次の比較条件

ここは外部根拠から導いた**未実行の比較設計**である。新しい評価schemaの採用や自然言語checker実験を行った結果ではない。

### 8.1 一つのscoreの意味を限定する

少なくとも、評価対象の意味・版、実入力/期待値、前処理とprompt、生成経路とworking context、checker/rubricと依存、採点・集約、採否規則を区別できる必要がある。全項を一つの巨大hashや同一保存単位へ固定する決定はしない。

receiptは要求configをcopyするだけでは足りず、実際に解決・使用した内容と、取得できなかった範囲を示す。外部modelサービス等で同一実体を取り戻せない場合は、その制約を残す。完全再実行、旧出力への再採点、由来の説明は異なる能力である。

### 8.2 version変化を一律失効にしない

| 対照条件 | 判断したいこと |
|---|---|
| 表示名・説明だけの変更 | 判定に使った意味・入力・checkerが不変と確認できれば、根拠付きで再利用可能か |
| 同じ入力・期待値でalgorithmだけ改修 | 旧結果を保持し、新版について再実行が必要な範囲を識別できるか |
| 期待値/caseを更新 | 旧結果は旧契約への記録として残し、新契約での有効性を別に検査できるか |
| 出力は保存済み、rubric/metricだけ変更 | 新checkerの入力が足りれば再採点できるか。生成の再実行と分ける |
| 出力/score/checkerは不変、採否規則だけ変更 | 保存scoreへ新版の規則を再適用し、生成・採点をやり直さず、旧採否を旧policyの記録として保持できるか |
| 同じtask名、実requestは旧cache | 記録と実使用の不一致を検出し、新設定の結果として採用しないか |
| model/reader/依存が取得不能 | 再実行可能性、旧結果の由来/有効性、今回の比較可能性を別判定できるか。保存された入力・出力・scoreだけで比較/再採点できる範囲を残す |

判断結果は「同じ契約」「根拠付きで再利用可能」「新たな実行/再採点が必要」「判定不能」等を区別して比較する。これは暫定的な試験上の分類であり、共通ontologyや固定status schemaではない。表の条件だけで自動判定できるとは仮定せず、表示変更に見える差が意味へ波及していないかの確認も必要になる。

### 8.3 checkerの検査

有限で独立に答えを得られる領域では、既知の正誤・境界・未対応・不足根拠の対照を用意する。生成・調整に使った集合と分け、false accept/reject、UNKNOWNを別に観測する。同じmodelによる相互同意やversion管理を独立正解へ読み替えない。

既知の反例を再利用するregression検査と、checker調整に未使用のheld-out検証は目的を分ける。固定反例を調整に使った場合、その反例で改善しても未知caseへの改善を示さない。

自然言語判断手順では独立oracleの成立自体が研究課題である。判定できた構造条件と、未判定の意味条件を混ぜず、checkerの契約変更でも同じ反例へアクセスできるようにする。

## 9. OSS overlap / reuse / integrate / buildの具体化

今回は部品の採用・導入は行っていない。重複評価を能力一覧から、今回の作業で生じた接続境界へ絞れるようになった。

| 作業 | 既存機構で確認できた部分 | AKRのために定義・接続が必要な境界 | 現時点の扱い |
|---|---|---|---|
| 改修提案→公開 | Git履歴、non-FF拒否、merge、ref比較更新 | 根拠base、payloadの由来、依存/意味検証、採用集合との対応 | Gitはhard constraint。意味受理を補う経路を比較 |
| 適用可能な方法の合成 | planning/workflowの対応範囲・順序・結果/逆変換契約 | AKR対象を表す範囲、自然言語条件、元意味への検査 | 契約を再利用候補とする。形式化費を先に測る |
| 評価と履歴 | task設定、run、dataset/source、scorer版、結果記録 | 実入力、旧snapshot、採否規則、checkerの妥当性 | 統合経路を試す前に要求保証を固定 |
| 小さなcontext取得・再開 | 固定file、依存探索、manifest、byte検査で今回の条件を処理 | task/主体とのbinding、権限、失効、semantic依存、writeback | 今回未検査の必要保証や故障条件が具体化した範囲で比較する |

意味policyをAKR側で決める必要があることは、独自softwareを作る必要があることと同じではない。逆に、部品が各fieldを持つことは、接続された保証があることと同じではない。独自実装率やOSSで代替できる割合は出さない。

## 10. R0〜R7の優先順位差分と探索の停止条件

研究束の定義は維持する。今回、R1の基本stale/ref条件とR5の宣言closure・固定byte復元の対照を実行できたため、次の増分を同種の外部repoへ使う情報価値は下がった。

| R | 今回の進展 | 次に情報価値が高いこと |
|---|---|---|
| R0 capture | 現在の判断手順/policyと、決定的検査・証拠handoffを区別 | 自然に生じた入力・局所改修・失敗を少数固定。件数競争にしない |
| R1 mutation/interface | Gitのstale全文・clean merge反例を実行 | 同じ改修のpatch/command経路で、受理・拒否理由・repair・総費用を比較。semantic条件はR2/R4と共有 |
| R2 granularity/composition | precondition、順序、変換単位という対照を補完 | 実assetの制約・呼出し・局所変更を区別し、合成/変換の費用を比べる |
| R3 interruption/restart | 保存fileのみから6条件を別processで復元 | 実際の委任/intake中断やtool部分成功へ進む。外部作用やevent履歴が必要なら、その契約だけ補完 |
| R4 authority/conversion/uncertainty | UNKNOWN縮約、評価の実入力・checker・採否境界が具体化 | **次の比較の前提として前へ出す。** 意味上の反例と独立oracle、評価変更の再利用条件を定める |
| R5 derived/distribution/context | 3seedのclosure/全件差、固定byte・版の復元を観測 | task/主体scope、失効、stale検索結果・実ロード、context圧縮/handoffを同条件で比べる |
| R6 history/migration/preservation | 旧入力の記録と取得を分離 | 保存対象を失うcold restore、旧reader/評価契約の再取得。用途が具体化した保存規格だけ追加調査 |
| R7 query/retrieval/portability | 返すstatusと本当に取得可能な版の境界を具体化 | 実query/no-matchと同じmodelの経路交換。model能力差の比較は経路と課題を固定して別に行う |

**次の狭い研究単位は、既存の一つの判断手順で、条件・modality・unknownを変える局所改修の対照を作り、構造検査と意味検査の境界を定めること。** R0/R2/R4を共通入力にし、R1/R5の操作経路比較へ接続する。自然言語意味の独立oracleが成立しない範囲を明示すること自体が結果になる。今回の計測だけで自動判定可能と決めない。

新しい対立仮説が出ない間は、今回選んだ4repoの探索を止める。追加外部調査へ戻る条件は以下に限る。

- 実例の必要な適用・合成意味が既存の対照では表せない。
- checker/評価根拠の有効性を既存契約で区別できない。
- 共有、自動採用、配布、撤回に入るため、authority/trustの契約が具体的に必要になる。
- durable execution、ontology evolution、長期baseline保存等に固有の失敗が実例に現れる。

広いgap closure、全Family同量の外部探索、製品の一括選定を再開する根拠は今回得ていない。

## 11. 研究の分担とcontext allocationの観測

意味/合成と評価lifecycleを別workerへ委任し、leadが基準地図、対立仮説、共通oracle、次元/Family/Rの判断を保持した。事前の実験設計と実行結果は別担当が監査する。重要なdocs/code差とinterface縮約はleadも固定版を直接確認した。

上限で停止した際、workerが先に保存したcheckpointから未完部分だけを再開できた。これは成果の保存と再開についての実観測である。一方、leadは統合のため両ノートと重要codeを読み、委任は統合費を消さなかった。

このrunはSol/Astra等のmodelを揃えた対照でも、単独実行との費用比較でもない。委任で何token/時間を節約したか、どのmodelが適任かは測れない。証拠抽出を限定委任し、高い影響を持つ矛盾・意味境界をleadが直接確認する方式を次の研究候補として残す。固定routing ruleにはしない。

## 12. 維持する原則と残る未知

Purpose / Principles / Constraintsに変更なし。AI primary maintainer、model/environment independence、GitHub管理、selective loading、explicit semantics、validation/repair、migration可能性、意味の二重管理回避、現行実装への非anchoringを維持する。今回のJSON・Markdown・Pythonは研究artifactの形式であり、Canonical/runtime形式の採用ではない。

未確認事項は次のとおり。

- 自然言語algorithmのmanaged boundary、意味上の依存、適用不能・UNKNOWNの独立判定。
- 形式化できる範囲、形式化・generator/checker/adapterの維持費、共通誤り。
- actual model trialでの出力品質、経路到達性、context消費、総費用とrouting条件。
- 本番の並行AI更新、GitHub/DB/toolをまたぐ部分成功、semantic transaction、repair費。
- event delivery/dedup、権限失効、offline、GC、強制中断・電源断、旧readerの保存。
- 大規模時のclosure分布、index/queryと実ロードの鮮度、sample selection effectの大きさ。
- 外部Issueの最新release再現、未読の修正PR、配布済みversionでの保証。

今回確認したのは、有限の人工条件での構造・byte・取得scopeである。これらの判定基準を満たすことと、AKRの意味・有用性・長期保守性を満たすことを区別して次の研究へ引き継ぐ。
