import React, { useState, useEffect } from 'react';

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
}

const CSVViewer: React.FC<CSVViewerProps> = ({ apiUrl, uploadInfo }) => {
  const [csvData, setCsvData] = useState<CSVData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

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

  if (!uploadInfo) {
    return (
      <div className="csv-viewer">
        <p>Please upload a CSV file to view data.</p>
      </div>
    );
  }

  return (
    <div className="csv-viewer">
      <h3>CSV Data: {uploadInfo.filename}</h3>
      
      {loading && <div className="loading">Loading...</div>}
      {error && <div className="error">{error}</div>}
      
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
