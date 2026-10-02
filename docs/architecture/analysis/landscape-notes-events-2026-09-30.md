# AKR External Landscape Scan — 起動・継続実行・状態同期

調査日: 2026-09-30。対象: Temporal、Restate、Argo Events、Kubernetes/controller-runtime、Automerge。

基準文書: [Architecture Search Space Coverage Audit](./2026-09-29-architecture-search-space-coverage-audit.md)。同文書の設計地図を継承し、目的や設計軸を再導出しない。本稿は製品選定ではなく、既存実装から取り出した設計上の差分である。GitHubへの変更、実装、障害注入、性能測定は行っていない。

## 証拠の扱い

このノートは、この分担で既に読了した公式文書・GitHub Issue本文とコメント・固定版リリースノートを保存したもの。保存に際して追加探索は行っていない。版を固定していない公式文書は、2026-09-30の取得内容として扱う。Issueの状態は同日の確認値であり、過去の報告から現在の全リリースの挙動を推定しない。

- **公式記述**: 開発元が説明する契約・設計・挙動。AKRの環境での実証とは区別する。
- **不具合・利用報告**: 特定時点の事象。メンバーやコントリビューターの回答と報告者の観測を分ける。
- **AKRへの推論**: 以下の比較項目、検証案、D/F/R対応。採用決定ではない。

基準文書の主な対応先は、D12 実行状態・失敗、D19 同期、D20 並行性・整合性、D22 競合、D33 migration、D35 rollback、D38 操作面、D39 接続protocol、D42 scheduling、D43 耐久性・可用性、D47 時間意味。F3はcommand/event authority、F4は分散した主張・証拠・採用、F6はdurable workflow、F7はimmutable object graph。R3は実行・中断・rollback、R5は派生物・配布・鮮度、R6は履歴・移行・保存を比較する研究束である。

## 1. Temporal — 実行中の履歴とコード変更には別の互換性がある

**根拠・状態**: [Workflow Definition](https://docs.temporal.io/workflow-definition)。公式文書、版非固定、2026-09-30読了。baselineにもTemporalへの言及はあるが、本調査ではreplayと変更の具体的制約を確認した。

Workflowのreplayでは、履歴に対応するcommand列との整合性が必要になる。文書はtimerとactivityの順序変更などが非決定性エラーを生む例を説明する。コードの分岐を維持するpatchingやWorker Versioningは、実行中の履歴と新しいコードを扱うための仕組みである。

**AKRへの差分**: アルゴリズムのsemantic revision、実行用コードのrevision、進行中instanceが継続可能なrevisionを区別する。新しいCanonical定義を採用しても、既存instanceの自動移行が安全になるとは限らない。LLMや外部検索の結果をreplay対象にする場合、どの結果を保存し、どの段階を再実行するかも契約になる。

**比較・検証**: 処理順序変更、モデル変更、依存API変更を挟んで既存instanceを再開する。成功・拒否・旧実行環境の維持・明示migrationのどれになるかを比較する。旧workerの保守コストも記録する。

**対応**: D11/D12/D15/D33/D35/D43/D45、F6、R3/R6。APIや対応範囲はSDK・versionで異なり、今回実行確認はしていない。

## 2. Restate — 重複除去は、誤るとlog保存済みsignalを消す

**根拠・状態**: [v1.7.0 release](https://github.com/restatedev/restate/releases/tag/v1.7.0)、[固定版release notes](https://github.com/restatedev/restate/blob/v1.7.0/release-notes/v1.7.0.md) の「Awakeable Signal Loss During Leadership Transitions」。公開日2026-06-18。release本文と固定版ノートを読了。以下は同releaseが説明する修正であり、AKR側の再現結果ではない。

旧leaderが出したAppendSignal等が新leaderのAnnounceLeaderより後にlogへcommitされる場合、古いcommandと判定して重複除去し、awakeableの解決やsignalを失う問題が記録されている。修正では対象commandにdedup metadataを付けず、残る重複をSDK側で扱う。ノートは関連変更として#4566を挙げるが、そのPR本文・merge状態は独立に確認していない。

**AKRへの差分**: logへの保存、consumerへの適用、重複除去、実行再開を別の境界として扱う。event IDだけでなく、leader epoch、発生元、再送時のidentityなど、重複判定が依存する条件を明示する。基準のD43の「durability」だけでは、この間の欠落を検証しきれない。

**比較・検証**: ownership切替中に同じsignalを遅延・再送し、欠落と二重適用を別々に数える。永続logに存在するのに待機instanceが進まない状態を検出できるかを見る。

**対応**: D12/D19/D20/D38/D39/D43、F3/F6、R3/R5。成熟パターンは、重複をすべて排除することではなく、責任を持つ層とidentityを定め、欠落を生まない処理にすること。

## 3. Restate — restart時のidentityと乱数、rollback可能性が結び付く

**根拠・状態**: 同じ[固定版v1.7.0 release notes](https://github.com/restatedev/restate/blob/v1.7.0/release-notes/v1.7.0.md) の「Deterministic Random Seeds for Restart-From-Prefix」。公開日2026-06-18、修正と導入条件の記述を読了。

prefixからのrestartで新しいinvocation IDが発行されると、そこに依存する乱数seedが、コピーしたjournalのprefixと食い違う問題を説明している。修正はseedを保存して引き継ぐ方式で、v1.7ではopt-in。機能を有効にした後はv1.7未満へのrollbackができず、既存invocationへ遡ってseedを補うものでもない。関連変更#4750のPR本文・merge状態は未確認。

**AKRへの差分**: 再実行可能性は入出力とアルゴリズムrevisionだけでは決まらない。乱数、実行identity、journal、runtime設定の結合を保存契約に含める必要がある。Gitで定義を戻せても、durable stateの形式や意味を戻せるとは限らない。

**比較・検証**: upgrade前後、機能flag切替前後、旧instanceと新instanceを分け、prefix restartの同等性とdowngrade可能範囲を検証する。rollback不能境界はmigrationの受入条件として扱う。

**対応**: D12/D15/D26/D33/D35/D43/D45、F6、R3/R6。このreleaseを現時点の最新版とは主張しない。

## 4. Argo Events — busの配送保証とtrigger実行保証は別である

**根拠・状態**: [Sensors and Triggers](https://argoproj.github.io/argo-events/sensors/more-about-sensors-and-triggers/)、[API reference](https://argoproj.github.io/argo-events/APIs/)。公式文書、版非固定、2026-09-30読了。

NATS Streamingについての説明はat-least-once配送、再配送による順序逆転の可能性、sensorが直近5分のevent IDを使う重複除去を記載する。一方、API referenceのtrigger `atLeastOnce` は既定でfalseであり、trigger実行の保証はbusの保証から自動的には引き継がれない。retryと、retry終了後に使うDLQも別の設定である。

**AKRへの差分**: event受領、trigger判定、job作成、外部効果の確定、完了通知を分け、各段階でackの意味を定める。一定期間の重複除去を、無期限のexactly-onceや外部処理の一回限り実行として扱わない。上記5分や順序の説明はNATS Streamingの項目に限定し、他busへ一般化しない。

**比較・検証**: 外部処理の成功直後・ack前に停止する場合と、ack直後・実行前に停止する場合を比較する。再送、重複実行、欠落、DLQ到達を分けて測る。下流のidempotency keyや状態照会が必要になる条件も確認する。

**対応**: D11/D12/D38/D39/D42/D43、F3/F6、R3/R5。AKRでの障害注入は未実施である。

## 5. Argo Events — A AND Bだけでは、どのAとBを結ぶか決まらない

**根拠・状態**: [Trigger Conditions](https://argoproj.github.io/argo-events/sensors/trigger-conditions/)。公式文書はv1.0以降の仕組みとして説明。2026-09-30読了、文書自体の版は非固定。

boolean条件によるeventの組合せに加え、文書は昨日のAと今日のBが結び付く例を示し、cronとtimezoneを使う`conditionsReset`を説明する。

**AKRへの差分**: 起動条件の意味には、event種類だけでなくcorrelation key、時間窓、event時刻と受領時刻、未完了の条件を残す期間、reset、遅着時の扱いが含まれる。例えば「asset改修」と「評価完了」が、異なるrevisionの事象同士で結合されると、誤った昇格を起こし得る。これはAKRへの推論である。

**比較・検証**: revision Aの変更とrevision Bの評価、日付境界、遅着、複数同時変更を混ぜ、意図したinstanceだけが起動するか確認する。calendar resetだけでrevision相関が解決するとは仮定しない。

**対応**: D09/D12/D38/D39/D42/D47、F3/F6、R3/R5。baselineとの差分は、起動条件を時間・identityを持つ明示的な意味として比較する点。

## 6. Kubernetes — state reconciliationでは通知と実行回数が一致しない

**根拠・状態**: [Controller Runtime Cache Explained](https://kubernetes.io/blog/2026/07/29/controller-runtime-cache-explained/)。公式説明。公開日2026-07-29、2026-09-30読了。

controllerは望ましい状態と観測状態の差を埋める。controller-runtimeの説明ではreadがlocal cache、writeがAPI serverへ向かうため、write直後のreadに即時反映を仮定できない。通知を受けること、最新状態が観測できること、望ましい状態へ収束することは異なる。

**AKRへの差分**: 「event一件につき一回の操作」と、「変更通知で対象をdirtyにし、現在状態を再照合する操作」を別候補として比較する。後者はeventそのものを処理履歴の権威にしない。通知欠落からの回復を主張するなら、再listや再走査で権威ある状態を取得できる条件まで必要になる。

**比較・検証**: cacheの遅れ、通知の重複・欠落、依存assetの連続変更を与え、最終状態と回復時間を見る。event数と実行数の一致率だけを正確性指標にしない。

**対応**: D18/D19/D20/D31/D34/D38/D42/D43、F1/F2/F6、R1/R5。成熟パターンは、再照合を繰り返しても状態が収束する設計と、観測の鮮度を独立に扱うこと。

## 7. controller-runtime — 自分の状態更新が次の起動を生む

**根拠・状態**: [Issue #2831](https://github.com/kubernetes-sigs/controller-runtime/issues/2831)、[member回答1](https://github.com/kubernetes-sigs/controller-runtime/issues/2831#issuecomment-2113144411)、[member回答2](https://github.com/kubernetes-sigs/controller-runtime/issues/2831#issuecomment-2114796619)。本文と全5コメント読了。2024-05-15起票、2024-07-01 closed。報告対象v0.16.3。

報告者はstatus更新に伴うreconcileの再実行を観測した。memberは想定された挙動と回答し、status subresourceとGenerationChangedPredicateによる絞込みを案内した。別memberはobjectが変わる間はupdate eventを受け、変わらなくなれば発生しないことを説明する。未解決の無限loop欠陥として扱う証拠ではない。

**AKRへの差分**: AIがstatus・評価・index・修復記録を更新し、その更新を起動条件が再び拾う循環を設計対象にする。status起因eventの一律除外が正解とは限らず、どの変化がどの操作を起動すべきかを先に定義する。

**比較・検証**: 自己更新、同じ内容の再書込み、評価結果だけの変更、semantic revision変更を区別する。no-opが再更新を生まず、必要な状態遷移は起動を失わないかを見る。budgetによる打切りと、意味上の収束は別々に測る。

**対応**: D18/D20/D36/D38/D42/D44、F1/F2/F6、R1/R5。baselineとの差分は、維持管理行為そのものが作るtrigger循環を明示した点。

## 8. Automerge — CRDTにもtransportの前提と意味上の競合が残る

**根拠・状態**: [Rust sync module](https://automerge.org/automerge/automerge/sync/index.html)、[Core concepts](https://automerge.org/docs/reference/concepts/)、[Conflicts](https://automerge.org/docs/reference/documents/conflicts/)。公式文書、版非固定、2026-09-30読了。

sync protocolの説明はpeer間のreliableな順序付きstreamを前提にする。複数transportへの対応から、任意の欠落・順序逆転に対応することまでは導けない。また同じpropertyへの並行代入では各nodeが同じ勝者を選ぶが、それがAKRの意味上望ましい改修であるという判定とは別である。

**AKRへの差分**: offlineで編集できること、再接続して複製が収束すること、変更を採用できること、依存・意味のvalidationを通ることを分ける。複数AIの編集を自動収束させる候補では、削除と参照追加、signature変更とcall更新等の意味競合を別途検査する。

**比較・検証**: 独立peerで互換性を壊す変更を加えて同期し、同じ状態への収束と、その状態の受入判定を別々に確認する。transportの保証はadapter契約として確認する。

**対応**: D19/D20/D22/D25/D32/D39、F4/F7、R5/R6。CRDT導入の推奨ではなく、収束保証の射程を明確にする知見。

## 9. Automerge-repo — 同期上の受領と永続化完了の間に隙間がある

**根拠・状態**: [Issue #264 Data durability question](https://github.com/automerge/automerge-repo/issues/264)、[contributor回答 2024-01-16](https://github.com/automerge/automerge-repo/issues/264#issuecomment-1893569990)、[追加回答 2024-01-25](https://github.com/automerge/automerge-repo/issues/264#issuecomment-1910315922)。本文と全8コメント読了。2023-12-31起票、最終更新2024-03-26、2026-09-30確認時open。起票時参照はcommit 5269a79f4f472a0653f39888b8941e49a4586226。

利用者は非同期storage書込み前にpeerが受領した扱いになることを懸念した。contributorは、その後にpeerが落ち得ることを認め、再接続で再同期できるのは内容を保持するpeerが残っている場合だと説明した。storage障害後の回復について、durableな内容の再読込みと関連peerのsync state resetを伴う案も議論している。これは当時の説明・提案であり、現在releaseに同じ欠陥が残ることや、提案が実装済みであることの証明ではない。

**AKRへの差分**: 「送信済み」「peerが知っている」「durableに複製済み」「採用済み」を分ける。offline・分散候補では、最後のcopyを失う前にどこまで確定を待つか、同期状態とstorage状態がずれたとき何からrepairするかを比較する。

**比較・検証**: 受領後・storage flush前の停止、storageだけの失敗、最後の保持peerの消失、再接続時のsync state resetを試す。正常な再接続だけで耐久性を評価しない。

**対応**: D19/D20/D25/D34/D43、F4/F7、R5/R6。成熟パターンとして、transportの回復とstorageの回復を別経路で設計する必要性が見える。

## Activation / Trigger Modelを独立に比較する価値

**判断**: 新たな必須subsystemを定める段階ではない。ただし、baselineの横断的な比較質問として明示する価値がある。既存Dへ対応付けるだけで見落とさないなら、新しい番号を追加する必要はない。

比較する内容は、何が仕事を発生させるか、何を同一の起動とするか、いつ条件が満たされたとするか、誰の権限で開始するか、いつ起動を取り消すかである。候補には直接request、schedule、edge event、現在状態の再照合、依存変更によるdirty化、観測値の条件、採用・承認状態の遷移がある。

**既存Dだけでは漏れ得る反例**: 同じ通知protocol（D39）、同じアルゴリズム（D11）、同じretry/checkpoint（D12）を使う二つの実装でも、片方がeventごとに開始し、もう片方が対象をdirtyにしてまとめて再照合するなら、実行回数、途中revisionの扱い、順序依存、必要な履歴は異なる。AとBの結合条件も、revision対応と時間窓が異なれば、boolean式だけが同じでも別の意味になる。

**既存Dへ吸収できる条件**: D12にinstance生成・相関・取消、D38/39に受領とack、D42にcoalescing・debounce・優先度、D43に欠落回復、D47に時間窓を明記し、それらの結合を一つの起動契約として検査する。独立した比較軸と独立した実装componentを混同しない。

## 今回の範囲と未確認事項

- 5実装、9知見に絞った。GitHub一次記録として、controller-runtime #2831、automerge-repo #264、Restate v1.7.0のreleaseと固定版migration記述を実読した。
- Restate #4566/#4750はrelease notesからの参照であり、各PR本文・merge状態は未確認。本文の根拠はrelease notesに限定する。
- Temporal、Argo Events、Automerge、controller-runtimeの現在の全version・SDK・adapterに対する再現は行っていない。仕様説明・過去の障害・修正済みの障害を横断して一つの現在保証にまとめない。
- 上記の比較・検証はAKR向けの次段階の案であり、測定結果ではない。処理量、latency、費用、運用難度の優劣は未評価。
- OpenAI MCP Eventsはroot側の分担。本ノートから同機能の実装・配送・起動保証は推定しない。
- baselineのF群を置き換える必要は現時点では導けない。F6には履歴互換性と外部効果境界、F3にはackとdedupの責任分担、F4/F7には収束と採用・耐久性の分離を比較項目として加える根拠が得られた。
