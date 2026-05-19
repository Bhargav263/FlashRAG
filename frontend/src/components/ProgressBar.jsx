import { CheckCircle2, AlertCircle, Clock, FileText, Scissors, Database, Timer } from 'lucide-react';

export default function ProgressBar({ status, progress, message, metrics }) {
  if (status === 'idle') return null;

  /* ── Processing state ────────────────────────────────────────── */
  if (status === 'processing') {
    return (
      <div className="progress-card animate-fade-in-up">
        <div className="progress-header">
          <Clock size={16} className="progress-icon spin" />
          <span className="progress-label">{message || 'Processing…'}</span>
          <span className="progress-pct">{progress}%</span>
        </div>
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
        {metrics && Object.keys(metrics).length > 0 && (
          <div className="metrics-grid" style={{ marginTop: '4px' }}>
            <MetricCard icon={<FileText size={18} />} label="Docs Loaded" value={metrics.loading} />
            <MetricCard icon={<Scissors size={18} />} label="Text Chunked" value={metrics.chunking} />
            <MetricCard icon={<Database size={18} />} label="Embeddings" value={metrics.embedding} />
            <MetricCard icon={<Timer size={18} />}    label="Total Time" value={metrics.total} accent />
          </div>
        )}
      </div>
    );
  }

  /* ── Done state ──────────────────────────────────────────────── */
  if (status === 'done') {
    return (
      <div className="progress-card progress-done animate-fade-in-up">
        <div className="progress-header">
          <CheckCircle2 size={16} className="icon-success" />
          <span className="progress-label" style={{ color: 'var(--color-success)' }}>
            Documents ingested successfully!
          </span>
        </div>
        {metrics && Object.keys(metrics).length > 0 && (
          <div className="metrics-grid">
            <MetricCard icon={<FileText size={18} />} label="Docs Loaded" value={metrics.loading} />
            <MetricCard icon={<Scissors size={18} />} label="Text Chunked" value={metrics.chunking} />
            <MetricCard icon={<Database size={18} />} label="Embeddings" value={metrics.embedding} />
            <MetricCard icon={<Timer size={18} />}    label="Total Time" value={metrics.total} accent />
          </div>
        )}
      </div>
    );
  }

  /* ── Failed state ────────────────────────────────────────────── */
  if (status === 'failed') {
    return (
      <div className="progress-card progress-error animate-fade-in-up">
        <div className="progress-header">
          <AlertCircle size={16} className="icon-error" />
          <span className="progress-label" style={{ color: 'var(--color-error)' }}>
            Processing failed: {metrics?.error || 'Unknown error'}
          </span>
        </div>
      </div>
    );
  }

  return null;
}

function MetricCard({ icon, label, value, accent }) {
  if (!value) return null;
  
  return (
    <div className={`metric-card ${accent ? 'metric-accent' : ''}`}>
      <div className="metric-icon">{icon}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-label">{label}</div>
    </div>
  );
}
