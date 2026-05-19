import { useState, useEffect, useRef, useCallback } from 'react';
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import ProgressBar from './components/ProgressBar';
import ChatWindow from './components/ChatWindow';
import { uploadDocuments, getMetrics } from './api';
import './App.css';

function generateSessionId() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
}

export default function App() {
  const [sessionId] = useState(() => generateSessionId());
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Ingestion state
  const [isProcessing, setIsProcessing] = useState(false);
  const [ingestStatus, setIngestStatus] = useState('idle'); // idle | processing | done | failed
  const [progress, setProgress] = useState(0);
  const [progressMsg, setProgressMsg] = useState('Processing…');
  const [metrics, setMetrics] = useState(null);

  const pollRef = useRef(null);

  // Poll backend metrics while processing
  const startPolling = useCallback(() => {
    if (pollRef.current) return;
    pollRef.current = setInterval(async () => {
      try {
        const data = await getMetrics();
        const status = data.status;

        if (status === 'processing') {
          setProgress(data.progress || 0);
          setProgressMsg(data.message || 'Processing…');
          setMetrics(data.metrics || {});
          setIngestStatus('processing');
        } else if (status === 'done') {
          setIngestStatus('done');
          setMetrics(data.metrics || {});
          setIsProcessing(false);
          clearInterval(pollRef.current);
          pollRef.current = null;
        } else if (status === 'failed') {
          setIngestStatus('failed');
          setMetrics(data.metrics || {});
          setIsProcessing(false);
          clearInterval(pollRef.current);
          pollRef.current = null;
        }
      } catch {
        // Keep polling if backend is temporarily unreachable
      }
    }, 1000);
  }, []);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const handleUpload = async (files, opts) => {
    try {
      setIsProcessing(true);
      setIngestStatus('processing');
      setProgress(0);
      setProgressMsg('Uploading files…');
      setMetrics(null);

      await uploadDocuments(files, opts);
      startPolling();
    } catch (err) {
      setIsProcessing(false);
      setIngestStatus('failed');
      setMetrics({ error: err.response?.data?.detail || err.message });
    }
  };

  return (
    <div className="app-container">
      <Header />

      <main className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        {/* Left panel — Upload & Progress */}
        <aside className={`panel panel-left animate-fade-in-up ${sidebarCollapsed ? 'collapsed' : ''}`}>
          <div className="sidebar-topbar">
            <button
              className="sidebar-toggle"
              onClick={() => setSidebarCollapsed(prev => !prev)}
              title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              id="sidebar-toggle-btn"
            >
              {sidebarCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
            </button>
            {!sidebarCollapsed && <span className="sidebar-label">Pipeline</span>}
          </div>
          <div className="sidebar-content">
            <FileUpload onUpload={handleUpload} isProcessing={isProcessing} />
            <ProgressBar
              status={ingestStatus}
              progress={progress}
              message={progressMsg}
              metrics={metrics}
            />
          </div>
        </aside>

        {/* Right panel — Chat */}
        <section className="panel panel-right animate-fade-in-up" style={{ animationDelay: '.1s' }}>
          <ChatWindow sessionId={sessionId} />
        </section>
      </main>
    </div>
  );
}
