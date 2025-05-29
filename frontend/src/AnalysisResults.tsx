import React, { useState, useEffect } from 'react';

interface CategoryStat {
  category: string;
  count: number;
  percentage: number;
}

interface SentimentStat {
  positive: number;
  neutral: number;
  negative: number;
  positive_percentage: number;
  neutral_percentage: number;
  negative_percentage: number;
}

interface CategorySentimentStat {
  category: string;
  positive: number;
  neutral: number;
  negative: number;
  positive_percentage: number;
  neutral_percentage: number;
  negative_percentage: number;
  total: number;
}

interface StatisticsData {
  total_comments: number;
  category_statistics: CategoryStat[];
  overall_sentiment: SentimentStat;
  category_sentiment_statistics: CategorySentimentStat[];
}

interface AnalysisResultsProps {
  apiUrl: string;
  analyzed: boolean;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ apiUrl, analyzed }) => {
  const [statistics, setStatistics] = useState<StatisticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatistics = async () => {
    if (!analyzed) return;
    
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/csv/statistics`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch statistics');
      }

      const data = await response.json();
      setStatistics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatistics();
  }, [analyzed]);

  const renderPieChart = (data: CategoryStat[]) => {
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
    let currentAngle = 0;
    
    return (
      <div className="pie-chart-container">
        <svg width="300" height="300" viewBox="0 0 300 300">
          <g transform="translate(150,150)">
            {data.map((item, index) => {
              const angle = (item.percentage / 100) * 360;
              const startAngle = currentAngle;
              const endAngle = currentAngle + angle;
              
              const x1 = Math.cos((startAngle * Math.PI) / 180) * 100;
              const y1 = Math.sin((startAngle * Math.PI) / 180) * 100;
              const x2 = Math.cos((endAngle * Math.PI) / 180) * 100;
              const y2 = Math.sin((endAngle * Math.PI) / 180) * 100;
              
              const largeArcFlag = angle > 180 ? 1 : 0;
              
              const pathData = [
                `M 0 0`,
                `L ${x1} ${y1}`,
                `A 100 100 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                'Z'
              ].join(' ');
              
              currentAngle += angle;
              
              return (
                <path
                  key={index}
                  d={pathData}
                  fill={colors[index % colors.length]}
                  stroke="#fff"
                  strokeWidth="2"
                />
              );
            })}
          </g>
        </svg>
        <div className="pie-chart-legend">
          {data.map((item, index) => (
            <div key={index} className="legend-item">
              <div 
                className="legend-color" 
                style={{ backgroundColor: colors[index % colors.length] }}
              ></div>
              <span>{item.category}: {item.count}件 ({item.percentage}%)</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderSentimentBar = (sentiment: SentimentStat | CategorySentimentStat, title: string) => {
    const total = sentiment.positive + sentiment.neutral + sentiment.negative;
    
    return (
      <div className="sentiment-bar-container">
        <h4>{title}</h4>
        <div className="sentiment-bar">
          <div 
            className="sentiment-positive" 
            style={{ width: `${sentiment.positive_percentage}%` }}
            title={`ポジティブ: ${sentiment.positive}件 (${sentiment.positive_percentage}%)`}
          ></div>
          <div 
            className="sentiment-neutral" 
            style={{ width: `${sentiment.neutral_percentage}%` }}
            title={`中立: ${sentiment.neutral}件 (${sentiment.neutral_percentage}%)`}
          ></div>
          <div 
            className="sentiment-negative" 
            style={{ width: `${sentiment.negative_percentage}%` }}
            title={`ネガティブ: ${sentiment.negative}件 (${sentiment.negative_percentage}%)`}
          ></div>
        </div>
        <div className="sentiment-labels">
          <span className="positive-label">ポジティブ: {sentiment.positive}件</span>
          <span className="neutral-label">中立: {sentiment.neutral}件</span>
          <span className="negative-label">ネガティブ: {sentiment.negative}件</span>
        </div>
      </div>
    );
  };

  if (!analyzed) {
    return (
      <div className="analysis-results">
        <p>解析を実行すると結果が表示されます。</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="analysis-results">
        <div className="loading">統計データを読み込み中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-results">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!statistics) {
    return (
      <div className="analysis-results">
        <p>統計データがありません。</p>
      </div>
    );
  }

  return (
    <div className="analysis-results">
      <h3>解析結果</h3>
      
      <div className="results-summary">
        <p>総コメント数: {statistics.total_comments}件</p>
      </div>

      <div className="results-section">
        <h4>カテゴリ別分布</h4>
        {renderPieChart(statistics.category_statistics)}
      </div>

      <div className="results-section">
        <h4>感情分析結果</h4>
        {renderSentimentBar(statistics.overall_sentiment, '全体')}
        
        <div className="category-sentiment-section">
          <h5>カテゴリ別感情分析</h5>
          {statistics.category_sentiment_statistics
            .sort((a, b) => {
              // 「その他」を最後に配置
              if (a.category === 'その他') return 1;
              if (b.category === 'その他') return -1;
              return a.category.localeCompare(b.category);
            })
            .map((categoryStat, index) => (
              <div key={index}>
                {renderSentimentBar(categoryStat, categoryStat.category)}
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default AnalysisResults;
