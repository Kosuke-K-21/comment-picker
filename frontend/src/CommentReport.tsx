import React, { useState, useEffect } from 'react';

interface CommentReportProps {
  apiUrl: string;
  analyzed: boolean;
}

interface ReportData {
  positive_summary: string;
  negative_summary: string;
  overall_insights: string;
  cost_display: string;
  total_comments_analyzed: number;
}

const CommentReport: React.FC<CommentReportProps> = ({ apiUrl, analyzed }) => {
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);

  const generateReport = async () => {
    setGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/csv/generate-report`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'レポート生成に失敗しました');
      }

      const data = await response.json();
      setReportData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'レポート生成に失敗しました');
    } finally {
      setGenerating(false);
    }
  };

  if (!analyzed) {
    return (
      <div className="comment-report">
        <div className="report-placeholder">
          <h3>📋 コメントレポート</h3>
          <p>レポートを生成するには、まずコメントの解析を完了してください。</p>
        </div>
      </div>
    );
  }

  return (
    <div className="comment-report">
      <div className="report-header">
        <h3>📋 コメントレポート</h3>
        <p className="report-description">
          トップコメント50件を分析して、ポジティブとネガティブな意見をまとめたレポートを生成します。
        </p>
        
        {!reportData && (
          <button
            onClick={generateReport}
            disabled={generating}
            className="generate-report-btn"
          >
            {generating ? '🔄 レポート生成中...' : '📊 レポート生成'}
          </button>
        )}
      </div>

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}

      {generating && (
        <div className="generating-status">
          <div className="loading-spinner"></div>
          <p>Nova Proを使用してレポートを生成しています...</p>
          <p className="loading-note">この処理には数分かかる場合があります。</p>
        </div>
      )}

      {reportData && (
        <div className="report-content">
          <div className="report-meta">
            <div className="meta-item">
              <span className="meta-label">解析コメント数:</span>
              <span className="meta-value">{reportData.total_comments_analyzed}件</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">生成コスト:</span>
              <span className="meta-value cost">{reportData.cost_display}</span>
            </div>
          </div>

          <div className="report-sections">
            <div className="report-section positive">
              <div className="section-header">
                <h4>😊 ポジティブな意見まとめ</h4>
              </div>
              <div className="section-content">
                <p>{reportData.positive_summary}</p>
              </div>
            </div>

            <div className="report-section negative">
              <div className="section-header">
                <h4>😔 ネガティブな意見まとめ</h4>
              </div>
              <div className="section-content">
                <p>{reportData.negative_summary}</p>
              </div>
            </div>

            <div className="report-section insights">
              <div className="section-header">
                <h4>💡 総合的な洞察</h4>
              </div>
              <div className="section-content">
                <p>{reportData.overall_insights}</p>
              </div>
            </div>
          </div>

          <div className="report-actions">
            <button
              onClick={generateReport}
              className="regenerate-btn"
            >
              🔄 レポート再生成
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CommentReport;
