# External Landscape Scan: agent memory / skill registry / MCP registry

調査日: 2026-09-30 JST  
状態: 担当調査メモ。採用判断・AKR実装・外部書込みなし。  
範囲: 既読の一次資料を保存。新たな探索は行わず、未確認を残して担当完了。  
基準: [Architecture Search-Space Coverage Audit](2026-09-29-architecture-search-space-coverage-audit.md)のD01–47 / F1–8 / R0–7。設計次元の再導出はしない。

## 0. 読んだ対象と証拠の境界

GitHub connectorでrepository metadata、固定head、tree、対象ファイル、issue/PR本文と一部コメントを取得した。外部実装の実行、package導入、再現試験はしていない。以下の「コード確認」は記載された処理経路を読んだ意味であり、運用上の発生頻度・全経路の保証・releaseへの配布を確認した意味ではない。

| Project / repository | 固定headとcommit時刻（UTC） | 読んだ範囲 |
|---|---|---|
| Mem0: `mem0ai/mem0` | `94c3fe9f238f3dbf29c9ce98643bd71eb13077cd` / 2026-09-25 17:34:12 | migration guide、`mem0/memory/main.py`の抽出・検索・削除・履歴・close関連、issues #5867/#7440/#7452とコメント |
| LangMem: `langchain-ai/langmem` | `9d033b47d9ce53e37e92c92241b0496c0278932e` / 2026-09-09 06:44:42 | `src/langmem/knowledge/tools.py`全体と`extraction.py`冒頭・抽出関連の部分。issue #11は検索本文のみで、採用知見の根拠にはしない |
| Letta現行: `letta-ai/letta-code` | `039cd6af623c24d1e88531325117d053e78d1615` / 2026-09-29 22:15:24 | memory operation / conflict repair / shared memory skills / skill sourcesの4ファイル |
| Letta旧入口: `letta-ai/letta` | `5bcdd177d70fa2b31a754cfcd801e77b2e1ab16a` / 2026-09-10 17:59:06 | README、tree、直近4commit、PR #3430。旧serverコード自体は未読 |
| MCP Registry: `modelcontextprotocol/registry` | `bf4e88cbe8d1a635c06144ccea1d24cb52fa6186` / 2026-09-22 15:11:18 | versioning/FAQ、`internal/service/versioning.go`、DB migrations 013/014、issues #1106/#1193/#1623、#1106コメント |

4 project、5 repositoryを対象とした。README以外のコードを4 projectで読み、migration・issue・PRも確認した。repositoryの星数・有名さ・READMEの性能宣伝を成熟度やAKR適合性の根拠にしていない。

## 1. Mem0: ADD-onlyへの変更は、更新の意味をretrieval側へ移す

**読んだ根拠**

- [固定版migration guide](https://github.com/mem0ai/mem0/blob/94c3fe9f238f3dbf29c9ce98643bd71eb13077cd/docs/migration/oss-v2-to-v3.mdx)。ADD/UPDATE/DELETEを選ぶ旧抽出から、1回のLLM呼出しによるADD-onlyへ変更したと説明。旧値と新値を併存させ、retrieval rankingで現在情報を表出する設計を明記している。
- [issue #5867](https://github.com/mem0ai/mem0/issues/5867)。2026-06-25作成、2026-09-03更新、調査時open。好みの変更後に旧新の値が残るとの利用者報告。
- 実際に読んだコメントの取得先は [comments API](https://api.github.com/repos/mem0ai/mem0/issues/5867/comments)。2026-07-17の`kartik-mem0`コメントは、ADD-onlyが意図した挙動であり、現行beliefと全履歴の両立は設計・feature上の問題と説明。PR #6017は提案として言及されるが、PR本体・merge状態は未確認。

**確認できること**: これは「LLMがUPDATEに失敗した」だけの問題ではない。更新判断を省く設計により、相反する記録の扱いが読取経路の責務になる。migration guide掲載のbenchmark改善値は作者側の主張であり、この調査で検証していない。

**Baselineからの増分**: D18 mutation / D22 conflict / D30 retrieval / D44 lifecycle / D47 time、F3/F4、R4/R7。既存の「履歴と採用状態を分ける」という論点を補強し、ADD-only→current-viewという具体的な代案と、旧記録が検索を通じて復活する失敗例を加える。AKRで同じ意味方針を採用する根拠にはしない。

## 2. Mem0: 削除対象はmemory recordだけでなく、再抽出に入る原資料の閉包に及ぶ

**根拠と状態**

- [issue #7452](https://github.com/mem0ai/mem0/issues/7452): 2026-09-25作成、2026-09-29更新、open。報告者は`a39a802b`、Python 3.12、stub LLM/embedderで、`delete_all`後もhistory DBの最近10件のmessagesが次の抽出promptへ入ると報告。
- [固定版main.py](https://github.com/mem0ai/mem0/blob/94c3fe9f238f3dbf29c9ce98643bd71eb13077cd/mem0/memory/main.py): L922は過去messagesの取得、L990等は保存。L1904–1958の同期`delete_all`はvector memoryの列挙・削除を行い、この関数中にsession messagesの削除呼出しはない。読んだコードは報告と整合するが、こちらで再現はしていない。
- [comments API](https://api.github.com/repos/mem0ai/mem0/issues/7452/comments): 修正案について、単一の完全一致scope keyでは`user_id=alice`の削除が`user_id=alice + run_id=r1`を取りこぼすと指摘されている。構造化filterのAND/subset判定、区切り文字とpercentのdecode順、SQL prefilterによるfalse-negativeが議論された。

2026-09-29コメントへの後続追記（記載日2026-09-30 KST）では、第三者がfork `2bdfb63e`でPython公開APIを試験したと報告。raw-messageの次prompt経路は20/20、完全結果はsync 10/10・async 8/10で、再open後にvectorが再出現する別問題を報告している。これは当該投稿者の限定試験結果であり、maintainerのrelease認証でも当方の再現でもない。TypeScript、live model、並行add/delete、crash consistencyはその報告でも未試験と明記されている。fork修正のmainへのmergeは確認していない。

**増分**: D01/D09/D21/D22/D31/D34/D44/D46、F1/F2/F3、R1/R5/R6。単なる「派生index削除」では不十分で、原資料→抽出→再生成の経路を辿らないと廃止した知識が再登録される。namespaceの構造とscope包含は、metadata整理の問題に留まらず削除・撤回の正しさを決める。まずscope集合から期待削除対象を作る試験を置く価値がある。

## 3. Mem0: 検索できることと、変更証拠が残ったことは別の成功条件

- [issue #7440](https://github.com/mem0ai/mem0/issues/7440): 2026-09-24作成、2026-09-25更新、open。報告対象はmem0 2.0.10、Python 3.12、Linux/WSL2。`close()`とwriteの重なりでvector insertが残り、history rowが失われると報告。
- [固定版main.py](https://github.com/mem0ai/mem0/blob/94c3fe9f238f3dbf29c9ce98643bd71eb13077cd/mem0/memory/main.py): L2176–2180の`close()`はhistory DBをcloseして`self.db=None`にする。L1078–1098はvector保存済み記録のhistory batch失敗を個別書込へfallbackし、その失敗をlogに残す。読んだ範囲にはvector/historyを不可分に受理する処理はない。
- [comments API](https://api.github.com/repos/mem0ai/mem0/issues/7440/comments): 2026-09-25の`kartik-mem0`コメントは、close後のwriteがvectorだけ残ることを再現したと述べ、PR #7448の適用で試験が通ると報告。別コメントは「close後writeのfail-fast」と「既に走っているwriteのquiesced shutdown」を分け、後者とasyncを当該修正範囲外とする。PR本体・最終mergeは未確認。

**増分**: D20/D21/D34/D36/D43、F2/F3、R1/R3/R6。baselineの二重確定問題に、process shutdownという具体的triggerを追加する。成功の定義をpayload保存、履歴保存、可視化、index更新で分け、partial successを観測・再照合できる必要がある。fail-fastを足しただけではin-flight mutationの原子性を示せない。

## 4. Mem0: 「hybrid search」の名前だけでは候補発見能力は分からない

- [migration guide](https://github.com/mem0ai/mem0/blob/94c3fe9f238f3dbf29c9ce98643bd71eb13077cd/docs/migration/oss-v2-to-v3.mdx)はBM25をrecall拡張ではなくsemantic候補へのboostと明記。spaCy等の有無とbackend能力によって利用するsignalが変わることも記載している。
- [固定版検索実装](https://github.com/mem0ai/mem0/blob/94c3fe9f238f3dbf29c9ce98643bd71eb13077cd/mem0/memory/main.py#L1645): `internal_limit=max(limit*4,60)`でsemantic searchを行い、keyword scoreは別に計算するが、L1680–1691の候補集合はsemantic結果から作る。L1694以降でscoreを融合する。

**増分**: D28/D29/D30/D38/D45、F2/F4、R7。Interface Capacityの評価に「公開名がhybridでも、keywordのみ一致する資産を候補に追加できるか」という具体的counterexampleを与える。runtime依存package・backend変更により同じAPIが異なる能力になるため、構成manifestには実際に有効なsignalを記録する。AKR上の性能比較は未実施。

## 5. LangMem: 目的別toolの有無と、変更保証の強さは分ける

- [固定版tools.py](https://github.com/langchain-ai/langmem/blob/9d033b47d9ce53e37e92c92241b0496c0278932e/src/langmem/knowledge/tools.py): `create_manage_memory_tool`は許可action、runtime namespace、structured content schema、IDの有無を扱う。L271–337のcreate/update/delete経路を読んだ。
- 同toolのupdateは`content + id`を受けて`store.put/aput(namespace,key,value)`へ渡す。tool signatureにexpected revisionはなく、読んだ経路では更新対象の旧版照合をしていない。`actions_permitted`は生成schemaだけでなく実行時にも検査される。
- [固定版extraction.py](https://github.com/langchain-ai/langmem/blob/9d033b47d9ce53e37e92c92241b0496c0278932e/src/langmem/knowledge/extraction.py)は冒頭・抽出関連部分のみを読んだ。全memory store managerを監査したとはしない。

**増分**: D18/D20/D21/D38/D40、F2、R1。成熟した部分問題は、action・namespace・schemaを絞ったmemory tool生成である。一方、名称が「manage/update」でもstale-write拒否やsemantic transactionを備えるとは限らない。AKRで必要ならexpected-baseをwrapper/backendへ追加する比較対象になる。任意のBaseStore側に追加保証がある可能性は否定せず、toolで公開・要求される保証だけを判定する。

## 6. Letta Code: repair自体の競合と、同じ失敗を毎turn繰り返す問題への実装

- [memory-conflict-repair.ts](https://github.com/letta-ai/letta-code/blob/039cd6af623c24d1e88531325117d053e78d1615/src/agent/memory-conflict-repair.ts)全体。repair attemptに状態signature、unique token、process ID/start time、launching/doneを保持。markerをlock下で比較して更新し、遅れて終わる旧workerが新claimを消さないようtokenを照合する。同じ状態で既に修復を試みた場合は毎turn自動再起動せず、`attempted`を返す。
- [memory-operation.ts](https://github.com/letta-ai/letta-code/blob/039cd6af623c24d1e88531325117d053e78d1615/src/agent/memory-operation.ts)全体。checkoutをharness-owned writer間でlock。年齢だけでlockを回収せず、所有processがなくなったことを判定する。コメントはprimary agent自身の編集がこのlock外であることも明記し、workerは変更fileだけをstageし、競合はGit conflictへ落とす設計を説明。

**増分**: D20/D22/D34/D42/D43、F1/F7、R1/R3。baselineの「AIがrepairする」に、repair attemptのidentity、所有権、遅延完了の隔離、再試行停止条件を加える具体的実装例。万能な同時編集保証ではなく、lock参加者の範囲を明示する点が重要。対応testsの存在はtreeで確認したが、tests本文の読解・実行はしていない。

## 7. Letta Code: diskに残っているskillと、現在参照してよいskillは別

- [shared-memory-skills.ts](https://github.com/letta-ai/letta-code/blob/039cd6af623c24d1e88531325117d053e78d1615/src/agent/shared-memory-skills.ts)全体。server-attached repository mountsだけからskill directoryを解決する。detach後もlocal checkoutが残るため、local sibling directoryの列挙をauthorityにしないとコメントに明記。attached repository一覧はagent単位で5秒cache、明示invalidatorもある。pending checkoutはskipし、mount欠損はerrorとして返す。
- [skill-sources.ts](https://github.com/letta-ai/letta-code/blob/039cd6af623c24d1e88531325117d053e78d1615/src/agent/skill-sources.ts)全体。bundled/global/agent/projectのsource選択を明示し、source集合を正規化する。内容の同値性を検証する仕組みではない。

**増分**: D05/D24/D25/D30/D31/D38/D44、F4/F7、R5/R7。baselineの廃止情報確認に対し、「detachしてもfileは残る」という実装上の具体例を加える。物理存在、attachment、採用、context注入を別に扱い、取消後にlocal探索経路から再露出しないことを試験する価値がある。5秒cacheがAKRに適切とは評価していない。

## 8. Letta: repository URLを固定しても、研究対象の世代は固定されない

- [旧入口の固定README](https://github.com/letta-ai/letta/blob/5bcdd177d70fa2b31a754cfcd801e77b2e1ab16a/README.md)は現行sourceを`letta-ai/letta-code`へ案内し、旧V1 serverをarchive branch・既存tags/releasesへ保持すると説明。
- [PR #3430](https://github.com/letta-ai/letta/pull/3430): 2026-08-16作成・同日03:56:10 UTC merge、closed。PR本文はlegacyを`56ba9c25552605eec89de8ed3dc6394b625c1993`で保存し、mainからserver実装・tests等を除いて入口へ変更したと説明。調査したmain treeも少数の案内・legal等のfileのみで、runtime codeがないことを確認。

**増分**: D15/D17/D33/D41/D44、F1/F4、R6。保存されている過去実装と、現在の製品を比較対象にした評価を区別する必要がある。repository名・star数・検索順位を現在の実装の同定に使わず、current sourceとlegacy sourceを別の候補構成として固定する。旧archive codeの機能評価はしていない。

## 9. MCP Registry: 不変publicationと可変status/latestを分離しても、整合性の修復は残る

- [versioning文書](https://github.com/modelcontextprotocol/registry/blob/bf4e88cbe8d1a635c06144ccea1d24cb52fa6186/docs/modelcontextprotocol-io/versioning.mdx): publicationごとにunique version、公開metadataは不変。任意version stringを許容し、SemVerとそれ以外、published timestamp、`latest`の選定規則を説明。文書はRegistryをpreviewとし、GA前のbreaking change/data reset可能性を留保。
- [FAQ](https://github.com/modelcontextprotocol/registry/blob/bf4e88cbe8d1a635c06144ccea1d24cb52fa6186/docs/modelcontextprotocol-io/faq.mdx): statusのdeletedは標準listingから隠すが、`include_deleted=true`で取得でき、activeへ復帰可能。metadataは恒久削除しないと説明。
- [versioning.go](https://github.com/modelcontextprotocol/registry/blob/bf4e88cbe8d1a635c06144ccea1d24cb52fa6186/internal/service/versioning.go): version比較関数を確認。両方SemVerならSemVer、両方非SemVerならtimestamp、混在ならSemVerを上位にする。これだけでpublication時の`is_latest`全挙動は確定しない。
- [migration 013](https://github.com/modelcontextprotocol/registry/blob/bf4e88cbe8d1a635c06144ccea1d24cb52fa6186/internal/database/migrations/013_add_status_fields.sql): status_changed_at/message追加、published_at以前のstatus時刻を拒否。
- [migration 014](https://github.com/modelcontextprotocol/registry/blob/bf4e88cbe8d1a635c06144ccea1d24cb52fa6186/internal/database/migrations/014_heal_is_latest.sql): deleted版へ`is_latest`が残る、またはlatestがない集合を修復。非deferrableな一意partial indexのため、旧latest clearと新latest setを二つのUPDATEへ分ける。frameworkのtransactionで包むとの注記がある。SQLを読んだが運用DBへの適用・結果は未確認。

**増分**: D15/D20/D21/D26/D31/D34/D44/D47、F2/F7、R1/R5/R6。immutable contentだけで現在pointerの健全性は保証されない。状態更新後の「利用可能な最新版が何か」を、制約付きmaterialized stateとして修復する実例。release selectionとsemantic compatibilityを区別するbaselineを補強し、latest/tombstoneの混在を試験対象へ追加する。

## 10. MCP Registry: 旧版とlocatorの一意制約が、namespace migrationを塞ぐ

- [issue #1106](https://github.com/modelcontextprotocol/registry/issues/1106): 2026-04-01作成、2026-04-23更新、調査時open。GitHub由来namespaceからdomain由来namespaceへ移ろうとした利用者が、旧不変versionに同じremote URLが残るため、新namespaceのpublishが拒否されると報告。最新の旧namespace版だけURLを変えても旧version参照は残る。
- [#1106 comments](https://api.github.com/repos/modelcontextprotocol/registry/issues/1106/comments): 2026-04-23コメントが#1193を対応対象として案内。
- [issue #1193](https://github.com/modelcontextprotocol/registry/issues/1193): 2026-04-23作成・更新、open。publish時URL検証でdeleted/deprecated serverを除外すべきとする問題。code修正や実際の解消は未確認。
- [issue #1623](https://github.com/modelcontextprotocol/registry/issues/1623): 2026-09-06作成・更新、open。org変更後の旧新identityが両方active/latestとして下流registryへ出て、古い情報が残るとの利用者報告。下流サービスはこの調査で直接確認していない。

**増分**: D04/D05/D15/D24/D25/D33/D44、F2/F4/F7、R4/R5/R6。baselineはidentityとaddressingを区別していたが、保持した全履歴へlocator一意制約を掛けるとidentity移管を妨げる、という具体的反例が増えた。名前の移管、同じresourceの後継、権限移転、旧locator解放を別操作として設計する必要がある。旧履歴削除を移行の必須条件にしない案を試験する。

## 11. 統合用の短いdelta候補

既存baselineから設計次元やfamilyを増やす根拠は、今回の担当調査だけでは示していない。既存D/F/Rへ具体的な実装・反例・確認項目を追加する材料である。

1. **追加を推奨する失敗試験**: stale writeだけでなくclose中のmutation、payload成功/history失敗、delete→reopen→次抽出、scopeの部分指定と特殊文字、namespace移管中の旧locator占有、deleted版をlatestが指す状態、detach後の残存file再発見、古いrepair workerの遅延完了。
2. **強まった境界**: current viewとhistory、物理存在と採用、目的別toolとtransaction保証、publication versionと採用pointer、hybridという名称と候補発見能力。
3. **比較に使える既存部分実装**: LangMemのaction/schema/namespace付きtool生成、Lettaのrepair claim/leaseと再試行停止、Registryのstatus/versionとlatest修復。全体Architectureの採用推奨ではない。
4. **未確認のまま残すもの**: upstream bugfixの最終merge/release、hostedサービスの実際の挙動、当方による再現、長期運用の費用と発生率、各方式のAKRへの意味適合性。

## 12. 除外した情報・調査上の制限

- issue投稿中の第三者製品紹介・benchmark数値を独立検証済みの根拠として採用していない。
- LangMem #11は検索本文でasync反映遅延・cancel競合の報告を見たが、状態・修正・現行実装を追っていないためfindingsから除外。
- Letta conflict repair関連testsは存在確認のみ。動作を試験済みと表現しない。
- Registryの不変metadataに対するadmin変更要求#1496、GitHub namespace大小文字#689は検索結果のみ読んだ。状態と修正未確認のためfindingsから除外。
- 新しいOpenAI発表、CAC/分業評価、workflow/Temporal/MLflow/buildの横断比較は担当外。最終Assumption Delta Auditはrootが統合する。
