# External Landscape Scan — assets / registry / provenance の既読記録

記録日: 2026-09-30。上限到達前に取得・読取済みの根拠を保存したもの。再探索・追加検証は行っていない。GitHubへの書込みなし。

基準: [Architecture Search-space Coverage Audit](./2026-09-29-architecture-search-space-coverage-audit.md)。以下の D / F / R は同稿の探索次元・候補 family・研究課題への対応であり、採用決定ではない。

## 結論と充足範囲

既読の具体事例から追加できるのは、主に次の3点である。

1. **固定 version で取得する本文と、その本文に付随する可変の管理情報は、別の鮮度契約を必要とする。** MLflowのprompt aliasに具体的な利用者報告がある。
2. **一回の実行に含まれる入出力の集合だけでは、どの入力がどの出力に寄与したかは定まらない。** OpenLineageの実装者間の議論は、実行単位を細分化する方法と、依存関係を明示する方法の条件を示す。
3. **保存された内容と、あるversionで見せる論理的な配置は別に管理できる。** OCFLはこの部分問題を規定済みだが、AIの稼働中の作業状態や公開時の並行制御まで解決するものとは今回の根拠から言えない。

具体的にIssue本文・コメントを読んだ実装は **MLflow / OpenLineageの2件**。加えてOCFL 1.1の一次仕様から抽出された本文の一部を読んだ。要求されていた3〜5件の実装比較には未達であり、OCFL仕様を3件目の実装に数えない。DVCのcheckout、MLflowのstage移行、OpenLineageの後続PRは調査候補に留まる。製品実行・再現試験・性能測定は実施していない。

## A1. 固定versionのキャッシュが可変alias一覧を古くする

- **一次根拠・読取範囲:** [MLflow #17066](https://github.com/mlflow/mlflow/issues/17066) の本文および4件のコメント。[詳細な再現手順](https://github.com/mlflow/mlflow/issues/17066#issuecomment-3173414482) と [maintainerの応答](https://github.com/mlflow/mlflow/issues/17066#issuecomment-3195986291) を実読。
- **version / date / state:** 報告環境 MLflow 3.1.4、Python 3.12.3。Issue作成 2025-08-05、取得時の最終更新 2026-01-18、取得時 open。これは当該報告環境の情報であり、最新versionの再現確認ではない。
- **短いclaim:** 利用者は、promptをversion指定でloadした後に同じversionへ別aliasを追加すると、再度version指定でloadしたobjectの `.aliases` が古いままになり、alias指定でloadしたobjectと一致しないと報告している。利用者は `MLFLOW_PROMPT_CACHE_MAX_SIZE=0` を回避策として挙げている。
- **証拠区分:** 利用者の再現手順と原因説明。maintainerは説明に理解を示すが、今回current codeや実行結果は確認していない。Issue冒頭のtag更新要望と、このalias/cache報告は分けて読む。
- **AKRへの転用仮説:** `algorithm revision` により本文を固定しても、同じ取得結果へ `approved / deprecated / aliases / superseded` を埋め込むなら、その管理情報のversionや取得時点が必要になる。本文hashをキャッシュkeyにするだけでは、可変情報の鮮度を保証できない。実行receiptには解決後revisionを残し、管理操作は管理情報の鮮度も確認する、という分離を比較対象に加える。
- **前回からの差分:** 一般的なcache invalidation論から進み、「同じ資産に対するversion経由とalias経由の取得結果が食い違う」という具体的なinterface間の整合性問題を得た。
- **対応:** D15 revision/compatibility、D24 addressing、D31 cache、D38 interface、D44 lifecycle。F2 transactional semantic registry / F7 immutable object graph。R1 mutation×interface×transaction / R5 derived×distribution×freshness。
- **限界・逆転条件:** 管理情報を本文から分離して常に別取得すると負荷と操作数は増える。取得のまとまり、鮮度上限、同時点snapshotを要する操作を先に定義する必要がある。MLflowの現在の欠陥として一般化しない。

## A2. 実行利用者向けの契約は、AI maintainerが必要とする契約を覆わないことがある

- **一次根拠・読取範囲:** A1と同じIssueの [maintainer応答](https://github.com/mlflow/mlflow/issues/17066#issuecomment-3195986291)。aliasからtemplateを利用する一般的な使い方に対し、loadしたobjectのaliasesを確認する理由を尋ねている。
- **version / date / state:** A1と同じIssue。追加の製品仕様を確認したものではない。
- **短いclaim:** 当該議論では、templateを実行する利用経路と、alias集合を観測・管理する経路で、必要な情報が異なっている。
- **証拠区分:** 個別のmaintainer応答という観察。その応答からMLflow全体の設計思想を断定しない。
- **AKRへの転用仮説:** AIが主保守者なら、`load→execute` だけでinterface coverageを判断できない。たとえば「このrevisionを参照するaliasを列挙→公開先を変更→旧aliasが残っていないか確認」も独立した管理シナリオとなる。
- **前回からの差分:** AI-nativeを抽象的なread/write APIの有無から、管理作業で必要な観測情報・操作後の確認可能性へ具体化した。A1と同一の根拠なので、独立した障害件数には数えない。
- **対応:** D18 mutation、D30 retrieval/select、D36 observability、D38 interface、D44 lifecycle。F2。R1。
- **限界:** すべての実行loadに全管理情報を付けることを推奨するものではない。必要な管理操作を別経路で満たしてもよい。

## A3. 実行の入出力集合と、資産間の依存関係は同じ情報ではない

- **一次根拠・読取範囲:** [OpenLineage #4359](https://github.com/OpenLineage/OpenLineage/issues/4359) の提案本文を実読。コメント20件を取得し、下記で参照する表示済みの主要議論を読んだ。全コメントの精読完了は主張しない。
- **version / date / state:** Issue作成 2026-02-25、取得時の最終更新 2026-06-25、取得時 open、proposal。提案はOpenLineageの確定仕様や実装済み機能と同一ではない。
- **短いclaim:** 提案者は、実際には A→C と B→D の二つの関係であっても、一つのrunへ inputs=[A,B] / outputs=[C,D] を載せると、consumerに不要な交差関係まで推定される問題を挙げる。column lineageが得られないETL工程も理由としている。
- **対立する具体策:** [別実装者のコメント](https://github.com/OpenLineage/OpenLineage/issues/4359#issuecomment-3962252931) は、ETLのtaskごとにlineageを発行しeventをbatch化する方法を使い、未解決の問題はないと述べる。提案者は、全工程を人工的なchild runへ分割すると実際の実行・transaction単位とのずれを生む場合があると応じている。
- **証拠区分:** 前者は提案者による問題報告と設計主張、後者は別実装者の利用報告。両者のworkloadを同条件で検証した比較ではない。
- **AKRへの転用仮説:** 一つのAI作業が多数のalgorithm / evaluation / adapterを読み書きしても、すべてが互いに依存したとは扱わない。観測されたアクセス、実際の変換依存、評価に使った入力、採用の根拠を必要に応じて区別する。作業を細かく区切れる場合はrun分割、区切ると実行の意味が崩れる場合は明示的な依存関係を検討する。
- **前回からの差分:** provenanceという一般概念から、「記録の粒度によって不要な依存が増え、影響範囲を過大に扱う」具体的なfailureへ進んだ。
- **対応:** D03 granularity、D09 dependency、D10 composition、D11 execution semantics、D17 provenance、D21 transaction、D28 indexing。F1 reproducible packages / F4 claims-evidence / F6 durable workflow。R2 granularity×dependency×composition。
- **限界:** Issueの例はOpenLineageの全consumerが必ず同じ推論を行う証拠ではない。AKRで細かな依存を取得するcostと、過大な影響範囲を許容するcostは未測定。

## A4. 依存記述を追加できても、producer・consumer・解釈規則が揃うまで意味は揃わない

- **一次根拠・読取範囲:** #4359の [custom facet利用の説明](https://github.com/OpenLineage/OpenLineage/issues/4359#issuecomment-3972138709)、[標準facet案と既存consumerへの配慮](https://github.com/OpenLineage/OpenLineage/issues/4359#issuecomment-3996849681)、[解釈の優先順位案](https://github.com/OpenLineage/OpenLineage/issues/4359#issuecomment-4010672505)、[後続PRへの言及とconsumer対応の質問](https://github.com/OpenLineage/OpenLineage/issues/4359#issuecomment-4794895183) を実読。
- **version / date / state:** #4359は取得時open。コメントで参照された [PR #4468](https://github.com/OpenLineage/OpenLineage/pull/4468) は未読で、state / merge / release / 最終schemaは未確認。この記録から「未実装」「まだ仕様化されていない」と結論しない。
- **短いclaim:** 議論はroot property追加だけでなくdataset-level facet案へ進み、column lineage、新しいdataset-level lineage、従来の入出力集合からの推定に優先順位を設ける案がある。最後のコメントはproducerでの利用とMarquez consumer側の対応を尋ねている。
- **証拠区分:** 設計提案と実装状況を尋ねるコメント。質問の存在は、consumerが未対応であることの確定証拠ではない。
- **AKRへの転用仮説:** schemaに新fieldを追加できることと、古いreaderも含めて意味が整合することを分ける。必要なら「欠落時の解釈」「複数の記述がある場合の優先順位」「readerが理解しない重要fieldの扱い」を変更契約へ含める。未知fieldを無視できる構文互換性だけでは依存関係の解釈を保証しない。
- **前回からの差分:** forward/backward compatibilityの一般論から、粗い依存・細かな依存・fallbackが同時に存在する場合の具体的な解釈差を得た。
- **対応:** D07 unknown/logic、D15 compatibility、D17 provenance、D33 migration、D38 interface、D39 protocol、D46 derived representations。F2 / F4 / F8 multi IR。R4 authority×conversion contract×uncertainty / R5 / R6 history×migration×preservation。
- **限界:** 優先順位の明示自体が、元の依存情報の正しさを保証するわけではない。後続PRを読まず、議論時点の案を現在のOpenLineage仕様として採用しない。

## A5. versionの論理的な配置を、保存bytesの場所から分離する

- **一次根拠・読取範囲:** [OCFL 1.1 specification](https://ocfl.io/1.1/spec/) の一次仕様本文から検索ツールで抽出された、inventory、manifest、version state、digest sidecar、inventory整合性、version例の部分を読んだ。全文を開いて精読したものではなく、実装code・release・Issueも読んでいない。
- **version / date / state:** OCFL 1.1。仕様に記された日付 2022-10-07、更新 2024-11-07。実装製品のversionではない。
- **短いclaim:** manifestはcontent digestと物理的なcontent pathを結び、各versionのstateはdigestと論理pathを結ぶ。仕様例には、あるversionで論理stateから外した内容を、後のversionで既存bytesを再利用して戻す構成がある。
- **証拠区分:** 仕様で定義された構造と例。稼働システムの性能・安全性を検証した結果ではない。
- **AKRへの転用仮説:** 資産本文の保存、ある公開revisionにおける名前・配置、AIが使う作業状態への展開を別の層として比較できる。rename / removal / restorationの度に同じ本文を複製する必要がない構成を、F7の具体的な実現候補として検討する。
- **前回からの差分:** content addressability一般から、「versionごとの論理配置を定義するinventory」という既に明文化された部分問題へ進んだ。新規アルゴリズムとして設計する必要があるかを再考できる。
- **対応:** D04 identity、D16 history、D23 storage、D24 addressing、D26 packaging/release、D35 rollback、D41 preservation、D46 derived。F7 immutable object graph/published root。R5 / R6。
- **限界:** bytesを復元できることはalgorithmの意味、依存先、実行環境まで復元できることと同じではない。OCFLをAKRのruntime、registry transaction、materialized working contextの完成形と見なさない。

## A6. 意図した冗長保存は、二重管理と同じではない

- **一次根拠・読取範囲:** A5と同じ仕様のinventory整合性規則。root inventoryと各version inventory、sidecar、過去versionのstate整合性に関する抽出本文を読んだ。
- **version / date / state:** OCFL 1.1、A5と同じ。特定実装のvalidatorは未読・未実行。
- **短いclaim:** root inventoryは最新versionを表し、最新version内のinventoryが存在する場合はrootと一致しなければならない。各versionのinventoryは推奨され、過去inventoryと最新inventoryで共有するversionの論理stateの整合性が要求される。inventoryにはdigest sidecarを置く。
- **証拠区分:** 規範的仕様。どの実装がどこまで検査するかは未確認。
- **AKRへの転用仮説:** 「意味情報の二重管理を避ける」を、全冗長コピーの禁止として解釈しない。独立に編集するauthorityを増やさず、生成・一致条件・検証方法を定めるなら、保存と復旧のための冗長化は比較対象に残る。逆に、コピーが存在するだけでrepairできるとは言えず、信頼する基点を定める必要がある。
- **前回からの差分:** 再構築可能なindexという一般論から、履歴ごとに固定したinventoryを保持しつつ最新inventoryとの一致を検査する、具体的な保存契約を得た。
- **対応:** D05 semantic authority、D16 history、D32 validation、D34 repair、D41 preservation、D43 durability/failure。F7。R6。
- **限界:** digestはbytesの破損検出を支えるが、内容の意味の正しさや攻撃者による一貫した改変への信頼を単独では保証しない。並行更新のtransaction設計はこの読取範囲からは評価できない。

## 未確認事項と担当完了時の境界

以下は再探索せず、根拠として使用しない。

- **MLflowの現在の挙動:** #17066のcurrent code、修正PR・release、最新版での再現。stageからalias/tagsへの移行docsは検索結果を発見しただけで、詳細未読。
- **OpenLineageの後続:** #4468のdiff、merge状態、release、確定facet、producer / consumerの実装状況。Issueのopen状態だけで後続の未完了を判定しない。
- **DVC:** checkout / fetch / cacheのdocs候補は検索結果で見たが、本文精読に至らず。GitHub connectorの `iterative/dvc` 検索が422を返したが、repo不存在や公開情報不存在の証拠にはしない。Git参照変更とmaterializationの差をDVCの確定した事例としては本稿に計上しない。
- **OCFL実装:** ocfl-java等の具体的なimplementation、staging / publish / locking / mutable head、validatorの実装は未読。OCFL仕様から実装の成熟度や運用実績を推定しない。
- **coverage不足:** 3〜5実装に対する比較、package/build領域の追加実装、materialized working contextの具体的なcheckout障害、定量的な保守costは未充足。既出規格を並べて件数を埋めない。

以上を既読範囲での担当成果とする。Change Absorption Capacity、および分業の振り返りへの統合判断は主担当へ委ねる。
