import React, { useState, useEffect } from 'react';
import './App.css';
import CSVUploader from './CSVUploader';
import CSVViewer from './CSVViewer';

interface ApiResponse {
  message: string;
}

const App: React.FC = () => {
  const [message, setMessage] = useState<string>('Loading...');
  const [error, setError] = useState<string | null>(null);
  const [uploadInfo, setUploadInfo] = useState<any>(null);
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('API URL:', apiUrl);
        console.log('Environment variables:', process.env);
        
        const response = await fetch(`${apiUrl}/`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data: ApiResponse = await response.json();
        setMessage(data.message);
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        setMessage('Failed to fetch data from backend');
      }
    };

    fetchData();
  }, []);

  const handleUploadSuccess = (data: any) => {
    setUploadInfo(data);
    console.log('Upload successful:', data);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Comment Picker</h1>
        
        <div className="connection-status">
          <h2>Backend Connection:</h2>
          {error ? (
            <div className="error">
              <p>Error: {error}</p>
              <p>Message: {message}</p>
            </div>
          ) : (
            <p className="success">{message}</p>
          )}
        </div>

        <div className="csv-section">
          <CSVUploader 
            onUploadSuccess={handleUploadSuccess}
            apiUrl={apiUrl}
          />
          
          <CSVViewer 
            apiUrl={apiUrl}
            uploadInfo={uploadInfo}
          />
        </div>
      </header>
    </div>
  );
};

export default App;
