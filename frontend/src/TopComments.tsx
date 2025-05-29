import React, { useState, useEffect } from 'react';

interface TopComment {
  id: string;
  comment: string;
  category: string;
  sentiment: string;
  importance: string;
  commonality: string;
  score: number;
}

interface TopCommentsData {
  max_count: number;
  overall_top_comments: TopComment[];
  category_top_comments: { [key: string]: TopComment[] };
}

interface TopCommentsProps {
  apiUrl: string;
  analyzed: boolean;
}

const TopComments: React.FC<TopCommentsProps> = ({ apiUrl, analyzed }) => {
  const [topComments, setTopComments] = useState<TopCommentsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [maxCount, setMaxCount] = useState(5);
  const [selectedCategory, setSelectedCategory] = useState<string>('全体');

  const fetchTopComments = async (count: number) => {
    if (!analyzed) return;
    
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/csv/top-comments?max_count=${count}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch top comments');
      }

      const data = await response.json();
      setTopComments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch top comments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopComments(maxCount);
  }, [analyzed, maxCount]);

  const handleMaxCountChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newCount = parseInt(event.target.value);
    setMaxCount(newCount);
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'ポジティブ': return '#4caf50';
      case '中立': return '#ff9800';
      case 'ネガティブ': return '#f44336';
      default: return '#666';
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'ポジティブ': return '😊';
      case '中立': return '😐';
      case 'ネガティブ': return '😞';
      default: return '❓';
    }
  };

  const renderCommentCard = (comment: TopComment, rank: number) => {
    return (
      <div key={comment.id} className="comment-card">
        <div className="comment-header">
          <div className="comment-rank">#{rank}</div>
          <div className="comment-score">スコア: {comment.score}</div>
          <div className="comment-id">ID: {comment.id}</div>
        </div>
        <div className="comment-content">
          <p className="comment-text">{comment.comment}</p>
        </div>
        <div className="comment-metadata">
          <div className="metadata-item">
            <span className="metadata-label">カテゴリ:</span>
            <span className="metadata-value category">{comment.category}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">感情:</span>
            <span 
              className="metadata-value sentiment" 
              style={{ color: getSentimentColor(comment.sentiment) }}
            >
              {getSentimentIcon(comment.sentiment)} {comment.sentiment}
            </span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">重要性:</span>
            <span className="metadata-value importance">{comment.importance}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">共通性:</span>
            <span className="metadata-value commonality">{comment.commonality}</span>
          </div>
        </div>
      </div>
    );
  };

  if (!analyzed) {
    return (
      <div className="top-comments">
        <p>解析を実行するとトップコメントが表示されます。</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="top-comments">
        <div className="loading">トップコメントを読み込み中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="top-comments">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!topComments) {
    return (
      <div className="top-comments">
        <p>トップコメントデータがありません。</p>
      </div>
    );
  }

  const categories = ['全体', ...Object.keys(topComments.category_top_comments).sort((a, b) => {
    if (a === 'その他') return 1;
    if (b === 'その他') return -1;
    return a.localeCompare(b);
  })];

  const currentComments = selectedCategory === '全体' 
    ? topComments.overall_top_comments 
    : topComments.category_top_comments[selectedCategory] || [];

  return (
    <div className="top-comments">
      <h3>トップコメント</h3>
      
      <div className="top-comments-controls">
        <div className="control-group">
          <label htmlFor="max-count">表示件数:</label>
          <select
            id="max-count"
            value={maxCount}
            onChange={handleMaxCountChange}
          >
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
              <option key={num} value={num}>{num}件</option>
            ))}
          </select>
        </div>
        
        <div className="control-group">
          <label htmlFor="category-select">カテゴリ:</label>
          <select
            id="category-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="comments-section">
        <h4>{selectedCategory}のトップコメント</h4>
        <p className="section-description">
          重要性と共通性のスコア（高=3, 中=2, 低=1）の掛け算で算出されたランキングです。
        </p>
        
        {currentComments.length === 0 ? (
          <p className="no-comments">該当するコメントがありません。</p>
        ) : (
          <div className="comments-list">
            {currentComments.map((comment, index) => 
              renderCommentCard(comment, index + 1)
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TopComments;
