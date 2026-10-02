# F1〜F8 evidence inventory — 2026-09-30

範囲: [主稿](./2026-09-30-external-landscape-assumption-delta-audit.md) §2/3/10/11、および既存の [memory](./landscape-notes-memory-2026-09-30.md)、[events](./landscape-notes-events-2026-09-30.md)、[assets](./landscape-notes-assets-2026-09-30.md) notesのみ。新外部探索・実行・architecture選定はしていない。
以下のE/P番号は主稿の参照番号。contract＝公式仕様・API/設計文書、code＝固定版の読解、issue＝報告・議論、release＝作者の修正/移行記述。いずれも当方の実測とは分ける。
**全family共通: AKR上の実測、同条件の比較試験、長期保守費の測定はない。** コード読解は経路の存在、Issueは条件付きの反例を示す。family全体の有効性・優劣の実証ではない。

## F1 再構築可能なpackage / build graph
- **得た証拠:** contract＝DVC checkout/3.0移行（E12/E13）、controller reconciliation（E08）; code＝Letta repair claim/lock・skill解決（E03）; issue＝OpenLineageの依存粒度論争（E11）、controllerの自己更新（E08）。独立したAKR build実行記録はない。
- **支える部分問題:** 参照解決とpayload取得・展開の分離、旧cache/reader併存、repair競合の範囲、粗すぎる依存と再評価範囲。正確な依存graphや再現可能なbuildが成立すること自体は未検証。
- **不足する識別証拠:** 同じ改修で、graph経由の再構築と直接更新を比較する結果。隠れた依存・過大な依存・部分展開を与えたときの意味保全、影響閉包、再評価・回復費が必要。

## F2 Transactional semantic registry
- **得た証拠:** contract/code＝MCP Registryのpublication/statusとlatest修復SQL（E04）、LangMem purpose tool（E02）; migration/code/issue＝Mem0の更新・削除・history経路（E01）; issue＝MLflow alias cache（E10）。運用DBへのmigration適用結果は未確認。
- **支える部分問題:** action/schema/namespaceを制約する操作面、可変pointerの整合性修復、payloadとhistoryの部分成功、管理queryの鮮度。purpose toolの存在からstale-write拒否や意味transactionを推定できない。
- **不足する識別証拠:** expected-base付きcommandと汎用patchを同じ競合で試す結果。Git公開とbackend確定の間で停止し、二重確定・片側成功の検出/回復を行う契約と実測が必要。

## F3 受理済みeventを権威とする構成
- **得た証拠:** migration guide/code/issue＝Mem0のADD-onlyとcurrent-view、削除後再抽出、history欠落（E01）; release＝Restate v1.7.0のsignal欠落修正（E06）; contract＝Argo配送・trigger条件（E07）。受理済みdomain eventを意味のauthorityにするAKR相当実装は読んでいない。
- **支える部分問題:** append-only記録から現在状態を選ぶ責務、log保存と適用完了の差、dedupの境界。memory追加、実行journal、起動通知はいずれも、意味上受理されたeventと同一ではない。
- **不足する識別証拠:** event履歴を規範にした場合の受理規則・補正/撤回・projection再生成・解釈器移行。current-stateを規範にする案との比較で、何が復元でき、削除や旧解釈器維持に何を要するかが必要。

## F4 主張・証拠・採用判断の連邦
- **得た証拠:** contract/code/issue＝Mem0の相反記録とretrieval（E01）、Registryのidentity/locator移管（E04）; code＝Letta attachment基準の選択（E03）; contract/issue＝Automerge収束・耐久性（E09）; issue＝OpenLineage（E11）。連邦全体を試した根拠はない。
- **支える部分問題:** 保存と採用scope、名前/locatorの移管、複製収束と意味採用・永続化の分離。CRDTで同じ値へ収束することは、相反する主張から妥当なものを採用する証拠ではない。
- **不足する識別証拠:** 複数scope/authorityで同じ資産の相反する主張を保持し、照会・採用・撤回・移管を一巡させる結果。中央registryとの差を、意味対応の未判定・routing誤り・管理費で識別する必要がある。

## F5 仕様・制約・生成中心
- **得た証拠:** 今回のE群には、仕様から生成し独立checkerで意味を確認する候補構成の直接読解がない。model/harness交換（P群）やMLIRの版別責任（E14）は周辺条件であり、F5のgenerator/checkerの証拠に数えない。
- **支える部分問題:** 生成物と仕様/生成器/評価器を別に固定して交換を問う必要性まで。生成中心方式が保守費や意味変質を減らすという実証はなく、根拠の薄さは今回の探索範囲を表す。
- **不足する識別証拠:** 同じ仕様でgenerator/modelを交換した生成物と、独立した評価根拠。generatorとcheckerの共通誤り、仕様変更時の再検証範囲、直接資産改修との費用差を識別する必要がある。

## F6 Durable workflow中心
- **得た証拠:** contract＝Temporal replay/worker互換性（E05）、Argo相関・ack/trigger（E07）; release＝Restate v1.7.0のsignal修正とseed/rollback制約（E06）; contract/issue＝controller-runtime（E08）。関連Restate PR本文や実行試験は未確認。
- **支える部分問題:** 定義revisionと進行中instanceの互換性、journal/identity/乱数の結合、配送と効果確定の差、起動条件の時間相関。外部作用やLLM判断を含むAKR作業が安全に再開できる保証はまだない。
- **不足する識別証拠:** 同じ短い/長い保守作業を静的再実行とdurable instanceで比較し、効果後停止・重複・遅着・upgrade時の意味保全と回復費を測ること。旧worker/journal維持費も必要。

## F7 不変object graph / 公開root
- **得た証拠:** contract/code＝Registry不変publicationとlatest修復（E04）、Letta attachment/repair（E03）; contract＝DVC checkout/移行（E12/E13）、OCFL 1.1 inventory（E15）、Automerge sync（E09）; issue＝MLflow alias（E10）とAutomerge耐久性（E09）。OCFL実装は未評価。
- **支える部分問題:** 不変本文と可変採用情報、物理存在と利用許可、公開集合と展開状態、論理pathと保存bytes、冗長inventoryの一致。これらを一体にした公開root/GC/repair機構の保証は未確認。
- **不足する識別証拠:** stale root、detach、部分取得、廃止、最後の保持copy喪失を通した公開・利用・回復の一巡。root確定とGit commitの対応、GC安全性、offline利用時の採用鮮度を同条件で比較する必要がある。

## F8 複数IR / 限定rewrite
- **得た証拠:** contract＝MLIR BytecodeFormatのdialect不変条件とversion/upgrade hook（E14）; issue＝OpenLineageのfacet優先順位・旧consumer解釈（E11）。変換器code、等価性証明、AKR algorithmのlowering結果は今回得ていない。
- **支える部分問題:** serializationの互換性とoperationの意味互換性の分離、reader/dialect/変換器の責任。upgrade hookの存在は変換の意味保存、逆変換可能性、未知operationへの完全対応を保証しない。
- **不足する識別証拠:** 対象意味を限定した複数表現間の変換と検査根拠。旧reader・未知operation・部分変換・adapter除去で、保存/変更/未判定を区別し、直接profile適応との差と変換器維持費を測る必要がある。

## 重複・相関と、このinventoryから言えないこと
- E01の複数観察は同じMem0世代のmigration/実装に依存する。本文と関連Issueが一致しても、独立したAKR再現件数ではない。
- E03/E04/E10の可変採用情報はF2/F4/F7へ跨る。複数familyへのmappingは複数の勝ち票ではなく、共有する部分問題への根拠である。
- E06のsignalとseedは同じRestate v1.7.0 release; E07は同じArgo系の契約; E12/E13は同じDVC系の展開/移行。別の故障境界を示すが、独立した方式比較ではない。
- E11の粒度とfacet互換性、E15の論理配置と冗長inventoryはそれぞれ同じIssue/仕様の再利用。F1/F4/F6/F8やF7の支持件数として加算しない。
- P群は公開interface・配置・contextの選択肢を増やす契約であり、当該accountでの能力確認やfamilyの実現性検証ではない。CACや§11の試験案も未実施である。
- F5の直接証拠不足、F8の契約中心、他familyの反例の多さから順位は作れない。次の判断には、family間で異なる予測を生む条件と、その同条件の観測が必要。
