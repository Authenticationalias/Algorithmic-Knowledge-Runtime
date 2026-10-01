# Semantic composition: 限定外部補完

調査開始: 2026-09-30 JST / 整理完了: 2026-10-01 JST。状態: 限定調査完了、採用判断なし。外部実装の導入・実行・GitHub変更なし。
固定codeとissue/PR状態は09-30の取得時点。10-01は既読記録の整理のみで、外部状態を再取得していない。
対象はUnified PlanningとCWL/cwltoolの2例。baselineのD02/03/08–11とF5/F8を再導出せず、意味の境界を比較する。
## 取得checkpoint
- GitHub repository metadata・default branchの固定head・treeを確認した。以下で固定codeと契約、issue/PR/releaseを読む。
- README説明だけを動作保証へ読み替えない。issueは報告、codeは読んだ経路、実行検証は未実施として分ける。

## 固定した対象
- Unified Planning: `aiplan4eu/unified-planning` master `ee5372efcba3209cf0c0c9bb682818002bf06909`、commit時刻2026-09-28 08:41:49 UTC。
- CWL reference runner: `common-workflow-language/cwltool` main `190415a46a7249ab85fde87d797ec1ea688a8cc5`、commit時刻2026-09-28 11:15:11 UTC。読んだ契約は同repoに保持されたCWL v1.2。

## 第1checkpoint: 契約とcodeから直接分かったこと
- [UP compiler contract](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/mixins/compiler.py)、[results.py](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/results.py)を読んだ。CompilerResultは変換先problemだけでなくactionまたはplanを元へ戻す写像を要求し、前向き変換はoptional。変換するデータと結果を元の意味へ接続する写像を別artifactにする例（D09/10/14/33、F5/F8）。写像の存在は意味保存の証明ではない。
- [UP validator mixin](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/mixins/plan_validator.py)を全体読解。problem.kindとplan.kindのsupportを別に確認する。skip_checksやerror_on_failed_checksで拒否/警告の挙動が変わるため、validator名だけで適用可能性を保証できない（D08/11/32/38）。
- UP results.pyはVALID/INVALID/UNKNOWNを定義し、無解の証明・不完全探索・timeout・unsupportedを別statusにする。ただしValidationResult/Statusのbool変換はVALID以外false。AKRのtool adapterがboolへ縮めるとUNKNOWNとINVALIDを失う（D07/11/32/38）。
- [CWL Workflow v1.2契約](https://github.com/common-workflow-language/cwltool/blob/190415a46a7249ab85fde87d797ec1ea688a8cc5/cwltool/schemas/v1.2/Workflow.yml)と[checker.py](https://github.com/common-workflow-language/cwltool/blob/190415a46a7249ab85fde87d797ec1ea688a8cc5/cwltool/checker.py)の関連箇所を読んだ。`when`、`scatter`、`pickValue`、nullable outputの組合せを単なる型接続とは別に検査する例（D08–12、F6/F8）。契約の評価順とissueは次のcheckpointで照合する。
- issue照合: [UP #811](https://github.com/aiplan4eu/unified-planning/issues/811)は2026-08-24作成、open、コメントなし。bounded action parameterが残るのに変換後kindがboundedなしと報告するという**投稿者の静的解析報告**。投稿者も実行していない。feature区分と実体の照合が必要で、現行バグと断定しない。
- [cwltool #1969](https://github.com/common-workflow-language/cwltool/issues/1969)は2024-01-21作成、open。報告版`3.1.20240112164112`で、`when`によるskip前の`loadContents`がnull入力に失敗したと報告。workaroundは投稿者のdummy file生成・pickValue利用。現在版での再現は未確認。
- [cwltool #2219](https://github.com/common-workflow-language/cwltool/issues/2219)は2026-03-16作成、2026-04-11にclosed/completed。`pickValue: all_non_null`を単一sourceに用いた時の型検査・実行不一致の報告。コメントなし。closedだけを修正・release保証にしない。

## 第2checkpoint: 評価順と結果契約
- CWL v1.2 Workflow契約L354–367は`pickValue`を`linkMerge`後、`scatter/valueFrom`前に評価し、型検査もpick後の型で行うと規定。L528–549は`when`をscatter後の各jobで評価し、skipした出力はnull、非booleanはerrorとする。つまり「事前条件がfalseなら入力処理全体が実行されない」という一般的guardへ置換できない。
- 同契約L585–608では未充足・未認識requirementsは原則fatal（user optionのoverride留保あり）、hintsは未対応でもerrorではない。AKRのrequired/optional capability宣言へ移せるが、自然言語の適用条件まで自動決定可能になるわけではない。
- [固定workflow_job.py](https://github.com/common-workflow-language/cwltool/blob/190415a46a7249ab85fde87d797ec1ea688a8cc5/cwltool/workflow_job.py)のpostScatterEval周辺では、L634が`v is not None`を確認してloadContentsへ進む。旧issue #1969の報告と現行codeは同じではない。報告がopenでも、現在も同一故障があると結論しない。
- [UP CompilersPipeline](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/compilers/compilers_pipeline.py)全体を読んだ。各stageで実際の`new_problem.kind`のsupportを確認し、各actionの逆写像を逆順で合成する。CompilerResult一般はplan単位逆変換も受け付ける一方、このpipelineは`map_back_action_instance is not None`をassertする。どの変換単位を合成できるかをinterface契約に含める必要がある。
- [UP bounded_types_remover.py](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/compilers/bounded_types_remover.py)と[utils.py](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/compilers/utils.py)関連箇所を確認。fluent型の変換、`BOUNDED_TYPES`flag除去、action parameter型をそのまま複製する処理はある。ただしbounded parameter featureと数値featureの意味区分を未検証のため、#811の不具合主張全体を当方確認済みにはしない。
- [UP TimedToSequential](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/compilers/timed_to_sequential.py#L497)のreturnを確認。`plan_back_conversion`を返し、`map_back_action_instance=None`を明記する。一般のCompilerResultとして有効でもaction単位写像を要求するpipelineにはそのまま入らないという、変換単位の境界がcode上にある。実行確認は未実施。

## 第3checkpoint: 修正の履歴と追加の反例
- [CWL PR #2220](https://github.com/common-workflow-language/cwltool/pull/2220)本文・file diffを確認。2026-03-16作成、2026-04-11 15:26:07 UTC merge、commit `55223a62a79aa39f2e61aab3d1154f1a7a2050a5`。checkerでall_non_null時のmerge_nestedを補い、runtime呼出しと単一sourceの成功/null/型不一致の3経路のtestsを追加。testsの記載・mergeを確認したのであり、当方実行や特定package releaseへの配布確認ではない。
- [UP #768](https://github.com/aiplan4eu/unified-planning/issues/768): 2026-07-27作成、07-31 closed/completed、コメントなし。変換で使わなくなったduration専用fluentが宣言と初期値に残り、kind matchingでは不要に見えてもPDDL serializationで非対応numeric値が出ると報告。
- 同問題に関して、固定版TimedToSequential L491–495にはmetric依存のfluentを保ち、unused fluentを除去する経路がある。issueで提案された方向と整合するが、この調査で修正PR・release・再現試験までは確認していない。metadata capabilityとserialized payloadが一致するかという比較課題を得た。

## 完了整理: AKRの次の比較へ加える4差分

### 1. 適用可能性を、処理系の対応範囲と、入力状態での前提成立に分ける
- **根拠**: UP validator mixinのproblem/plan kind照合と、既読の[SequentialPlanValidator](https://github.com/aiplan4eu/unified-planning/blob/ee5372efcba3209cf0c0c9bb682818002bf06909/unified_planning/engines/plan_validator.py#L117)。後者は初期状態からactionごとの未充足条件、状態遷移、最後のgoalを扱う。CWLのrequirements/hintsはさらに実行環境側の要求を分ける。
- **差分**: 「schema・型が受理された」「checkerが対象を扱える」「この入力・状態で手順の前提が成立する」を別結果にする（D08/11/14/32、F5/F8）。次の比較は型適合だが前提不成立、処理系未対応、要求capability欠落の3ケースを含める。
- **限界**: 証拠は契約と固定codeの読解。形式モデルで表現されない外部世界の事実や、自然言語の適用条件まで検証されたことにはならない。

### 2. 合成契約に評価順・skip・nullの意味を含める
- **根拠**: CWL v1.2のpickValue→scatter/valueFrom→各jobのwhenという契約、#2219とmerged PR #2220の修正・tests。guardをどこへ置くかで、入力前処理と出力の形が変わる。
- **差分**: 入出力型の接続試験に、条件false、null、単一/複数source、scatter後の部分skipを加える（D03/08–12、F6/F8）。required capabilityとhintの区別もadapterが保持する。
- **限界**: CWLのnull/skipは特定workflow意味論であり、AKR全資産のUNKNOWNや失敗へ統一しない。古いopen issue #1969を現在版の故障と見なさない。

### 3. 変換の単位と、結果を元へ戻す単位を明示する
- **根拠**: UP CompilerResultはaction単位またはplan全体の逆変換を認めるが、固定版CompilersPipelineはaction写像を要求する。TimedToSequentialはplan全体写像を返す。#768はkind判定とserialized artifactの食い違いを示す過去報告である。
- **差分**: 「converterがある」だけでchain可能とは扱わず、写像の入力/出力単位と合成条件を検査する。変換後に生成した結果を元へ戻し、元問題のcheckerへ渡す比較を用意する（D02/03/09/10/14/33、F5/F8、R2/R4）。宣言したfeatureと実体・出力encodingの整合性も確認する。
- **限界**: ここでいう逆写像は元問題への結果対応であり、数学的な逆関数・可逆性を要求しない。対応写像が存在しても全入力での意味保存証明ではない。自然言語手順に同じ写像を作れるとは仮定しない。#811の静的報告は確認候補に留める。

### 4. UNKNOWNをtool境界まで保持し、再試行と意味変更を分ける
- **根拠**: UP results.pyのVALID/INVALID/UNKNOWN、探索のtimeout・unsupported・無解証明等と、bool化では非VALIDがfalseへ縮む実装。
- **差分**: AKRのtool返却・台帳・後続AIまで元statusと理由を保持する。UNKNOWN/timeoutは追加資源や別checker、INVALIDは反例に基づく改修、unsupportedは別profile等へ分岐させる比較を行う（D07/11/32/38、F5/F8、R1/R4）。
- **限界**: これらは問題・validatorの結果であり、algorithm全体の正しさ・採用状態・安全性の共通ラベルではない。どの分岐が安価かは未測定。

## 終了時の境界
- 2例から得たのは既存D/F/Rを具体化する契約・反例であり、新family、共通DSL、CWL/UP採用を決める根拠ではない。
- 実行再現、性能、修正のpackage releaseへの配布、長期保守費、AKR資産の形式化費は未確認のまま残す。
- 次の比較を変える材料は揃ったため、この担当の追加探索は終了した。
