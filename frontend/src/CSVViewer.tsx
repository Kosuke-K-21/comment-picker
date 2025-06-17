import React, { useState, useEffect } from 'react';
import AlertSettings, { AlertCondition } from './AlertSettings';
import AlertChecker from './AlertChecker';

interface CSVData {
  filename: string;
  data: any[];
  pagination: {
    current_page: number;
    page_size: number;
    total_rows: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
  columns: string[];
}

interface CSVViewerProps {
  apiUrl: string;
  uploadInfo: any;
  onAnalysisComplete?: () => void;
}

const CSVViewer: React.FC<CSVViewerProps> = ({ apiUrl, uploadInfo, onAnalysisComplete }) => {
  const [csvData, setCsvData] = useState<CSVData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [dangerousComments, setDangerousComments] = useState<any[]>([]);
  const [analysisCost, setAnalysisCost] = useState<string | null>(null);
  const [alertConditions, setAlertConditions] = useState<AlertCondition[]>([]);
  const [statistics, setStatistics] = useState<any>(null);

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${apiUrl}/csv/statistics`);
      if (response.ok) {
        const stats = await response.json();
        setStatistics(stats);
      }
    } catch (err) {
      console.error('Failed to fetch statistics:', err);
    }
  };

  const fetchData = async (page: number, size: number) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/csv/data?page=${page}&page_size=${size}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch data');
      }

      const data = await response.json();
      setCsvData(data);
      setCurrentPage(page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (uploadInfo) {
      fetchData(1, pageSize);
    }
  }, [uploadInfo, pageSize]);

  const handlePageChange = (newPage: number) => {
    fetchData(newPage, pageSize);
  };

  const handlePageSizeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newSize = parseInt(event.target.value);
    setPageSize(newSize);
    fetchData(1, newSize);
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/csv/analyze`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result = await response.json();
      console.log('Analysis completed:', result);
      setAnalyzed(true);
      
      // Set dangerous comments if any
      if (result.dangerous_comments && result.dangerous_comments.length > 0) {
        setDangerousComments(result.dangerous_comments);
      } else {
        setDangerousComments([]);
      }
      
      // Set analysis cost if available
      if (result.cost_display) {
        setAnalysisCost(result.cost_display);
      }
      
      // Notify parent component that analysis is complete
      if (onAnalysisComplete) {
        onAnalysisComplete();
      }
      
      // Refresh the data to show the new columns
      fetchData(currentPage, pageSize);
      
      // Fetch statistics for alerts
      fetchStatistics();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(`${apiUrl}/csv/download`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Download failed');
      }

      // Get the filename from the response headers
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'analyzed_data.csv';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=(.+)/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed');
    }
  };

  if (!uploadInfo) {
    return (
      <div className="csv-viewer">
        <p>Please upload a CSV file to view data.</p>
      </div>
    );
  }

  return (
    <div className="csv-viewer">
      <div className="csv-header">
        <h3>CSV Data: {uploadInfo.filename}</h3>
        <div className="header-buttons">
          <button
            onClick={handleAnalyze}
            disabled={analyzing || analyzed}
            className="analyze-btn"
          >
            {analyzing ? '解析中...' : analyzed ? '解析済み' : '解析開始'}
          </button>
          {analyzed && (
            <button
              onClick={handleDownload}
              className="download-btn"
            >
              📥 CSVダウンロード
            </button>
          )}
        </div>
      </div>
      
      {analysisCost && (
        <div className="analysis-cost-info">
          <span className="cost-label">解析コスト:</span>
          <span className="cost-value">{analysisCost}</span>
        </div>
      )}
      
      {loading && <div className="loading">Loading...</div>}
      {error && <div className="error">{error}</div>}
      {analyzing && <div className="loading">コメントを解析しています...</div>}
      
      {analyzed && (
        <>
          <AlertChecker conditions={alertConditions} statistics={statistics} />
          <AlertSettings 
            conditions={alertConditions} 
            onConditionsChange={setAlertConditions}
            statistics={statistics}
          />
        </>
      )}
      
      {dangerousComments.length > 0 && (
        <div className="danger-alert">
          <div className="alert-header">
            <span className="alert-icon">⚠️</span>
            <h4>危険度の高いコメントが検出されました</h4>
          </div>
          <div className="dangerous-comments-list">
            {dangerousComments.map((comment, index) => (
              <div key={index} className="dangerous-comment-item">
                <div className="comment-id">No. {comment.id}</div>
                <div className="comment-sections">
                  {(() => {
                    try {
                      const commentObj = JSON.parse(comment.comment);
                      return Object.entries(commentObj).map(([key, value], idx) => (
                        <div key={idx} className="comment-section">
                          <div className="section-title">{key}</div>
                          <div className="section-content">{String(value)}</div>
                        </div>
                      ));
                    } catch {
                      return <div className="comment-text">{comment.comment}</div>;
                    }
                  })()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {csvData && (
        <>
          <div className="controls">
            <div className="page-size-control">
              <label htmlFor="page-size">Rows per page: </label>
              <select
                id="page-size"
                value={pageSize}
                onChange={handlePageSizeChange}
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>
            
            <div className="pagination-info">
              Showing {((csvData.pagination.current_page - 1) * csvData.pagination.page_size) + 1} to{' '}
              {Math.min(csvData.pagination.current_page * csvData.pagination.page_size, csvData.pagination.total_rows)} of{' '}
              {csvData.pagination.total_rows} rows
            </div>
          </div>

          <div className="table-container">
            <table className="csv-table">
              <thead>
                <tr>
                  {csvData.columns.map((column, index) => (
                    <th key={index}>{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {csvData.data.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {csvData.columns.map((column, colIndex) => (
                      <td key={colIndex}>{row[column]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              onClick={() => handlePageChange(csvData.pagination.current_page - 1)}
              disabled={!csvData.pagination.has_previous}
              className="pagination-btn"
            >
              Previous
            </button>
            
            <span className="page-info">
              Page {csvData.pagination.current_page} of {csvData.pagination.total_pages}
            </span>
            
            <button
              onClick={() => handlePageChange(csvData.pagination.current_page + 1)}
              disabled={!csvData.pagination.has_next}
              className="pagination-btn"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default CSVViewer;
