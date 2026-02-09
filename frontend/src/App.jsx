import React, { useState } from 'react';
import axios from 'axios';
import { Link, FileText, Loader, Copy, Check } from 'lucide-react';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [url, setUrl] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSummary('');

    try {
      const response = await axios.post(`${API_BASE_URL}/summarize`, { url });
      
      if (response.data.success) {
        setSummary(response.data.summary);
      } else {
        setError(response.data.error || 'Failed to generate summary');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const resetForm = () => {
    setUrl('');
    setSummary('');
    setError('');
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <FileText className="logo" size={32} />
          <h1>LinkedIn Post Summarizer</h1>
          <p>Get AI-powered summaries of any LinkedIn post in seconds</p>
        </header>

        <main className="main">
          <form onSubmit={handleSubmit} className="form">
            <div className="input-group">
              <Link className="input-icon" size={20} />
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste LinkedIn post URL here..."
                required
                className="url-input"
                disabled={loading}
              />
            </div>
            
            <button 
              type="submit" 
              disabled={loading || !url}
              className="submit-btn"
            >
              {loading ? (
                <>
                  <Loader className="spinner" size={20} />
                  Generating Summary...
                </>
              ) : (
                'Summarize Post'
              )}
            </button>
          </form>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {summary && (
            <div className="result-section">
              <div className="result-header">
                <h3>Summary</h3>
                <button onClick={copyToClipboard} className="copy-btn">
                  {copied ? <Check size={16} /> : <Copy size={16} />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <div className="summary-text">
                {summary}
              </div>
              <button onClick={resetForm} className="new-summary-btn">
                Summarize Another Post
              </button>
            </div>
          )}

          {!summary && !loading && (
            <div className="features">
              <h3>How it works:</h3>
              <div className="feature-list">
                <div className="feature">
                  <span>1</span>
                  <p>Copy any LinkedIn post URL</p>
                </div>
                <div className="feature">
                  <span>2</span>
                  <p>Paste it in the input above</p>
                </div>
                <div className="feature">
                  <span>3</span>
                  <p>Get an AI-generated summary instantly</p>
                </div>
              </div>
            </div>
          )}
        </main>

        <footer className="footer">
          <p>Powered by OpenAI GPT • Built with FastAPI & React</p>
        </footer>
      </div>
    </div>
  );
}

export default App;