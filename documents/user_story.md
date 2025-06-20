# ユーザーストーリーマッピング

## 1. コメントデータの準備
- **ユーザーとして**  
  受講者コメントをCSVファイルでアップロードしたい。  
  _なぜなら_ 自動で分析・分類したいから。

## 2. コメント分析の実行
- **ユーザーとして**  
  アップロードしたコメントをLLMでポジティブ／ネガティブに分類したい。  
  _なぜなら_ コメントの傾向を把握したいから。

- **ユーザーとして**  
  講義内容・講義資料・運営・その他のカテゴリに自動分類したい。  
  _なぜなら_ フィードバックをカテゴリ別に整理したいから。

- **ユーザーとして**  
  危険度の高いコメントを自動でピックアップしたい。  
  _なぜなら_ 早急に対応が必要な問題を見逃したくないから。

- **ユーザーとして**  
  一度に数千件のコメント処理でも耐えられる性能を利用したい。  
  _なぜなら_ 大規模講座でも快適に処理したいから。

- **開発者として**  
  LLM/API利用コストを最適化したい。  
  _なぜなら_ コスト効率良く運用したいから。

## 3. 結果の可視化・出力
- **ユーザーとして**  
  重要コメント（緊急度・共通性を考慮したスコア順）のランキング表示を確認したい。  
  _なぜなら_ 優先度の高いフィードバックを把握したいから。

- **ユーザーとして**  
  カテゴリ別の件数・割合を確認したい。  
  _なぜなら_ フィードバック全体の傾向を可視化したいから。

- **ユーザーとして**  
  「○件以上」「○%以上」の条件でフラグを出したい。  
  _なぜなら_ 閾値を超えた場合にアラートを設定したいから。

- **ユーザーとして**  
  分析結果をCSVに出力したい。  
  _なぜなら_ 他システムで活用したいから。

## 4. 発展的な自動通知・連携
- (今回は省略)**ユーザーとして**  
  危険度の高いコメントをSlack通知やメール通知で受け取りたい。  
  _なぜなら_ 迅速に運営チームに知らせたいから。

- **ユーザーとして**  
  改善レポートの自動生成機能まで拡張したい。  
  _なぜなら_ 効率的にレポートを作成したいから。

- **ユーザーとして**  
  (今回は省略)Omnicampusと連携してアンケートデータを自動取得したい。  
  _なぜなら_ 手動でのデータ取り込みを省力化したいから。

- **ユーザーとして**  
  (今回は省略)複数回アンケート結果を時系列で分析したい。  
  _なぜなら_ 施策の効果を追跡したいから。