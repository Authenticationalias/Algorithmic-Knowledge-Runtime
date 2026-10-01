# AKR bounded research pilot

実行日: 2026-10-01 JST。研究fixture。Production runtime、Canonical形式、algorithm改修、Family順位を提案する実装ではない。

## 入力と判定基準

- repository: `Authenticationalias/Algorithmic-Knowledge-Runtime`
- source ref: `0f22fec375af8001afa4a2cd948ba205c409ad3d`
- [source-snapshot.json](./source-snapshot.json): 固定commitのregistryとalgorithm 3件/policy 2件。元本文とGit blob SHAを保存。研究input copyであり、別の編集authorityではない。
- [oracle.json](./oracle.json): 実行前に手確認したID/version/path/requires/blob、3seedの期待closure、共通mutation/recovery条件。closure関数から期待値を生成していない。
- [run_pilot.py](./run_pilot.py): Python standard libraryのみ。一時Git repositoryと取得bundleを `/private/tmp` に作成し、自身の一時領域は終了時にcleanupする。
- [results.json](./results.json): 観測値。意図した反例はoracle不成立として保存し、隠したり成功へ読み替えたりしない。

## 再実行

このfolder内で `python3 run_pilot.py` を実行する。必要なものはPython 3とGit。記録した環境はPython 3.9.6、Git 2.54.0 (Apple Git-157)。network、package install、認証情報、外部serviceへの書込みは使用しない。再実行はこのfolderのresults.jsonを更新する。

実行する条件:

1. 実Gitによるmutation 4条件: 古いparent、最新parentと古い全文、3-way merge、refのold-value条件。共通oracleは受理時の両marker保持、または公開拒否と既受理Aの本文・commit保持。
2. 実Git clean merge後のID参照欠落1条件。改名側と旧ID caller追加側を同baseから分岐する。
3. 3seed × seed本文のみ/宣言closure/全登録assetの9比較。期待集合はoracleの手確認値。
4. 完了/途中/manifestなし/違うversion/同header違う本文/上流欠落の6復元条件。新child processは保存fileからのみ復元する。

## 解釈の限界

- 人工故障、一つのhost、決定的schedule。20行の条件は独立した20研究sampleではない。
- mutationのmarkerは独立text変更の残存を検査するだけ。clean mergeの反例も構造的参照破壊であり、一般的な意味checkerではない。
- header readerは固定入力のfrontmatterに限定。一般的なYAML、未知schema、悪意あるinputの処理は対象外。
- payload_bytesはUTF-8本文bytes、registryは別計上。model token数・回答品質・scale性能ではない。
- extra_to_declared_closureは宣言集合との差であり、実taskに意味上不要と判定したものではない。
- repair_source_entries_checkedは修復のため存在する上流entryを検査した件数。manifestがあればsource cache file全体を毎回読むため、0でも実source I/Oはある。MCP/network呼出し回数やI/O bytesではない。
- manifestと固定sourceをこのfixtureでは信頼する。hashはauthority、許可、意味同一性を保証しない。
- 部分状態を人工的に作った。process kill、電源断、fsync、並行worker、外部作用、event delivery、model/harness交換は未実験。
- COMPLETEはこのoracleのscope・ID/version/byte・宣言closureの完了。意味上の正しさやalgorithmの採用状態ではない。

統合判断は[分析本文](../2026-10-01-semantic-evaluation-and-bounded-pilot.md)を参照。

## 独立レビューの反映

期待blob、closure、本文bytes、欠落/追加集合を別担当が独立計算し、保存観測と一致した。レビューで、修復entry計数と実I/Oの区別、拒否時の既受理状態保持を明示・実装し、修正後に再実行した。意味・評価のレビューでは、結果対応写像の非可逆性、再実行不能と旧結果の比較可能性、scoreと採否規則の分離を分析本文へ反映した。独立レビューは自然言語の意味checkerや長期保守費の検証ではない。
