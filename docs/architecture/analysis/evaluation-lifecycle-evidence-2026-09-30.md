# Evaluation lifecycle — bounded evidence notes

開始2026-09-30、完了2026-10-01。対象は対照的な2例に限定。評価設定・根拠の有効性を調べ、製品採用や自然言語algorithmの意味評価能力は判断しない。外部書込み、導入、実験、GitHub編集なし。AKR実測なし。10-01の完成作業では09-30に取得・読取済みのMLflow根拠を保存し、外部状態の再確認はしていない。
証拠種別をcontract（公式記述）、code（固定版読解）、issue（利用者報告/議論）、PR（差分・merge状態）で区別する。Issueのopen状態だけで最新releaseの欠陥を判定しない。

## 1. EleutherAI/lm-evaluation-harness — benchmark設定と実際の評価入力

固定読取版: [`d6de81643928d653435c431bae19945d41d32520`](https://github.com/EleutherAI/lm-evaluation-harness/commit/d6de81643928d653435c431bae19945d41d32520)、commit時刻2026-09-14 10:51:05 UTC。release tagへ配布済みかは別途確認していない。

### L1. task名・task versionだけでは評価契約を固定しない
- **根拠 / 読取範囲:** [task guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/docs/task_guide.md) の設定説明・metric/filter・集約設定。contract。
- **claim:** guideはYAMLとcodebase commitを共有して設定を再現する意図を述べる。dataset path/name/kwargs、split、process_docs、prompt変換、生成kwargs、repeat、filter、metric引数・集約、任意metadata.versionが別々にある。versionはYAML設定のmetadataであり、外部datasetやmetric依存まで閉じた保証とは記されていない。
- **固定code:** [evaluator.py](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/lm_eval/evaluator.py#L394) L394–422でmodel/config、seeds、Git hash、環境/tokenizer情報を結果へ追加。[task.py](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/lm_eval/api/task.py#L855) L855–873でdataset kwargsをload_datasetへ渡す。
- **限界:** 各環境情報の網羅性や、すべてのtaskが外部dataset revisionを必ず固定することは確認していない。seed保存も完全決定性の証明ではない。
- **AKRの実験条件:** algorithm revisionを固定し、dataset/split・前処理・prompt・filter・metric/集約を一つずつ変更する。点数の変化をalgorithm改修の効果と誤認しないため、評価契約の変更として識別できるかを検査する。D15/17/32/37/45、F1/F5/F8、R4/R6/R7。

### L2. 記録した設定と、cacheから実際に使う評価入力がずれ得る
- **根拠 / 状態:** [Issue #4084](https://github.com/EleutherAI/lm-evaluation-harness/issues/4084)、2026-09-02作成、09-04更新、取得時open。本文と3コメントを読了。報告者はtask名を再利用してprompt/datasetを変更すると、request cacheが古い入力を返す一方、新しいconfigが記録されると述べる。こちらで再現していない。
- **固定code:** [task.py L288–300](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/lm_eval/api/task.py#L288) のcache keyはtask名、fewshot数、rank/world size、template flags、system prompt hash、tokenizer名を使用。読んだkey構築にはtask config digestがなく、報告の原因説明と整合する。
- **限定:** 同Issueの別件であるsample ID問題と、関連PR #4085/#4089の完成状態は調査対象に含めない。全cache経路や現在の配布versionに一般化しない。
- **AKRの実験条件:** 同じalgorithm/task名で、dataset・評価template・fewshot seedを変更しcacheを再利用する。要求した評価条件、記録された条件、実際に使った入力の一致を独立に確認する。D17/31/36/37/46、F1/F2/F7、R5/R6。

### L3. hashは何をまとめたものかを読む必要がある
- **根拠:** [evaluation_tracker.py L249–260](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/lm_eval/loggers/evaluation_tracker.py#L249) と [evaluator.py L655–664](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/lm_eval/evaluator.py#L655)。code。
- **claim:** task_hashesはsamplesがあるとき、各sampleのdoc_hash・prompt_hash・target_hashを連結して生成する。prompt_hashは当該箇所で `requests[0].arguments[0]`、target_hashはtarget文字列から作る。生成関数へmetric/filter実装や環境全体は直接含まれない。
- **限界:** hash一致から評価契約全体の一致を結論できない。log_samplesなしのrunや他の記録fieldを無視して、このhashだけがprovenance手段だとも扱わない。
- **AKRの実験条件:** 入力/期待値を固定したままmetric実装・rubric・集約を替え、結果の由来を区別できるか検査する。入力hash、評価器version、採点結果、比較可能性の判定を同じものにしない。D17/24/32/37、F5/F8、R4/R6。

### L4. 評価器の依存更新は、採点式以外の経路も壊し得る
- **根拠 / 状態:** [PR #4076](https://github.com/EleutherAI/lm-evaluation-harness/pull/4076) の本文・差分・レビューを読了。2026-09-14 merged、merge commitが上記固定版。旧`datasets.load_metric`のmodule-level importを関数内`evaluate.load`へ変更する差分。
- **claim:** PRはdatasets 3.0で消えたAPIにより、共有moduleを使う5つのtaskがload不能になり、F1 metricを使わないtaskまで影響したと説明する。PR作者はYAML load試験を報告する一方、network制約で`evaluate.load("f1")`自体は実行していないと明記する。
- **限界:** mergedだから採点値の同等性まで実測済みとは言えない。metricとcompute引数が不変という作者説明・差分と、metric依存の実行確認は別である。
- **AKRの実験条件:** evaluator packageの更新について、load可能性、採点値、旧結果の再採点を分ける。共有依存による波及範囲と、未検証の部分をreceiptに残せるかを比較する。D09/15/33/37/45、F1/F5/F8、R2/R6。

## 2. MLflow — dataset / scorer / runの結び付け

prompt registryの既往調査とは別に、評価datasetの履歴復元とscorerの版を確認した。
固定読取版: [`f130e764257080e33de1c5cdb263e98ca02c099d`](https://github.com/mlflow/mlflow/commit/f130e764257080e33de1c5cdb263e98ca02c099d)、commit時刻2026-09-30 10:12:03 UTC。headを固定したcode/同repo docsの読解であり、特定releaseやhosted環境での動作確認ではない。

### M1. 「digest」というfield名からcontent hashを推定できない
- **根拠 / 読取範囲:** 固定版 [Evaluation Dataset Concepts](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/docs/docs/genai/concepts/evaluation-datasets.mdx) 全文と、[SQL store `_compute_dataset_digest` L7740–7755](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/mlflow/store/tracking/sqlalchemy_store.py#L7740)。contract/code。
- **claim:** docsのobject schemaはdigestをcontent hashと説明するが、読んだSQL storeの関数は `name:last_update_time` をSHA-256に入力し先頭8文字を返す。直接の入力はdatasetのrecords/期待値ではない。したがって、この経路のdigestだけを内容同一性・改変検出の根拠にできない。
- **限界:** MLflowの全Dataset実装が同じ方式だという主張ではない。全mutation経路での更新条件、衝突の実測、同一millisecondの並行更新は未検証。ここで確かめたのは関数の入力とdocsの説明の差である。
- **AKRの実験条件:** dataset識別子、変更を識別する値、内容fingerprint、snapshotを取得する参照を別に観測する。期待値だけを変える/同じ内容を再登録する試験で、それぞれが何を検出するか確認する。D04/17/24/32/37、F2/F5/F7、R4/R6。

### M2. runにdatasetを記録しても、当時の内容へ戻れるとは限らない
- **固定code:** [EvaluationDatasetSource](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/mlflow/data/evaluation_dataset_source.py) 全文。sourceはdataset_idのみを保持し、loadは現在のtracking storeへIDを渡す。[GenAI wrapper L225–264](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/mlflow/genai/datasets/evaluation_dataset.py#L225) はOSS側のmerge/deleteを委譲する一方、list_versionsはDatabricks以外でNotImplementedErrorとなる。[run inputの記録 L446–457](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/mlflow/genai/evaluation/base.py#L446) も読んだ。
- **運用上の要求 / 状態:** [Issue #25313](https://github.com/mlflow/mlflow/issues/25313) 本文・2コメント・timelineを読了。2026-08-24作成、08-25更新、09-30取得時open/ready/has-closing-pr。dataset編集後も旧runに対応する不変版を取得したいというfeature requestで、maintainerが妥当と回答。timelineは [PR #25347](https://github.com/mlflow/mlflow/pull/25347) を関連付け、取得時open/merged_at=null。PR本文・差分・その後の状態は未読。
- **claim:** 読んだOSS経路では、同じdataset IDの履歴snapshotを指定して再loadする契約を確認できない。Issueはその不足を具体的な「期待値修正・case追加後の旧run再現」として示す。Databricks側のversion APIの存在とOSSの保証を混ぜない。
- **限界:** 全run artifactsに旧入力が一切残らないとは断定しない。記録内容を他の手段で保存する可能性は残る。Issueでdigestを内容識別として述べる部分はM1のcode確認により限定し、無条件には採用しない。
- **AKRの実験条件:** 同じalgorithm revisionに対しD@1で評価し、期待値/caseをD@2へ更新後、旧結果からD@1を取得して再採点できるか試す。「違いが分かる」と「元を取り戻せる」を分ける。D15/17/33/37/41、F2/F5/F7、R5/R6。

### M3. scorer定義のversionと、評価条件全体の固定は別である
- **公式契約:** [Registering and Versioning Scorers](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/docs/docs/genai/eval-monitor/scorers/versioning.mdx) 全文。experiment＋登録名ごとにversionを増やし、version省略時はlatest、指定時は特定版。regressionでは版の固定を推奨し、旧版は削除まで利用可能と説明する。登録はRun単位ではない。
- **固定code:** [InstructionsJudge.model_dump L914–945](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/mlflow/genai/judges/instructions_judge/__init__.py#L914) はinstructions、model、feedback型、指定されたinference params、集約、MLflow/serialization version等をserialize。[Scorer L318–321](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/mlflow/genai/scorers/base.py#L318) は合否判定に使う `_pass_if` をprocess内限定・非serializeと明記する。周辺のserialization定義・version fieldも読んだ。
- **claim:** judge名が同じでもlatestは変わり得る。固定版の定義を保持しても、外部modelサービスの実体、library環境、process内の合否規則まで自動的に固定されるとは確認できない。同じscoreからreleaseの採否を決める規則も、scorerの返値と区別して扱う必要がある。
- **限界:** 全scorer種別の保存契約・runへのscorer解決版の自動記録・評価器の依存閉包を網羅監査していない。`_pass_if` はローカルなassertion用途という明示的設計で、登録欠陥と呼ばない。
- **AKRの実験条件:** 出力を固定しjudge版/rubric/model/合否閾値だけを替える再採点と、judgeを固定してalgorithmだけを替える比較を分ける。登録名だけでなく実際に解決した定義、依存条件、採否規則を再取得できるか検査する。D15/17/32/37/45、F2/F5/F8、R4/R6/R7。

### M4. judge自体の評価は必要だが、共通誤りの自動検出保証は得られない
- **公式記述 / 読取範囲:** 固定版 [Judge Alignment](https://github.com/mlflow/mlflow/blob/f130e764257080e33de1c5cdb263e98ca02c099d/docs/docs/genai/eval-monitor/scorers/llm-judge/alignment.mdx) 全文。judge評価と同名のhuman feedbackを同じtraceへ対応付け、alignmentに使い、別のheld-out dataで元judgeと比較する流れを説明する。品質はfeedbackの質と量に依存すると述べる。
- **claim:** この流れは評価器を不変の正解機械とせず、評価器にも参照labelと別の検証集合を要するという部分問題を具体化する。判定のversion管理やjudge同士の一致だけで、生成器とcheckerが共有する誤りを見つける機構ではない。
- **限界:** docsの改善率や一貫性の説明を独立検証済みの成績として採用しない。alignmentの実装・独立した実験dataは未読。held-outは最適化への直接の使い回しを減らすが、共通rubricの欠落、誤った期待値、同じmodel系の偏りを単独では除かない。この限界は今回のAKR向け推論である。
- **AKRの実験条件:** 小さな対象領域で、既知の正誤・反例・境界例を生成器/調整用集合から分けて保持し、checker変更前後のfalse accept/rejectと未判定を比べる。独立したlabel/検査手段を得られないcaseは「意味を保証済み」に昇格させない。human feedbackをAKR全体の主要保守手段にするという採用提案ではない。D07/17/32/37、F5/F8、R4/R7。

## 3. この2例で更新する実験上の境界

| 取り違えやすいもの | 今回分離できたもの | 根拠 |
|---|---|---|
| 同じalgorithm/task名なら同じ評価 | dataset・前処理・prompt・scoring・集約・環境を含む評価条件 | L1/L4、M3 |
| configを記録すればその条件で実行した | 要求条件・実際の入力・記録内容の一致 | L2 |
| hash/digest一致が全条件の一致を表す | hashの入力範囲と、単なる変更識別値 | L3、M1 |
| datasetをrunに結べば過去を再現できる | 識別・履歴snapshot取得・再実行可能性 | M2 |
| version付きjudgeがあれば意味評価は確か | judgeの定義固定・judge自体の妥当性・採否規則 | M3/M4 |

今回の根拠は、自然言語algorithmの一般的な意味同等性を検証できることや、F5全体の優位性を示さない。追加したのは、評価対象の変更と評価基準の変更を区別する試験条件、hash/source/versionの射程、checkerにも検証が要るという限定である。
未確認: 現行releaseでのIssue再現、MLflow #25347のPR本文/merge/配布、全dataset/scorer backendの保証、記録からの完全な依存復元、共通誤りの発生率。固定codeとIssueの一致は独立したAKR試験件数には数えない。
