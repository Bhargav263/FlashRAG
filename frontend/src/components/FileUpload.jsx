import { useState, useRef } from 'react';
import { Upload, FileText, X, Settings2, ChevronDown, ChevronUp } from 'lucide-react';

const STRATEGIES = ['Recursive', 'Sentence', 'Token', 'Semantic', 'Fixed'];

export default function FileUpload({ onUpload, isProcessing }) {
  const [files, setFiles] = useState([]);
  const [strategy, setStrategy] = useState('Recursive');
  const [chunkSize, setChunkSize] = useState(512);
  const [chunkOverlap, setChunkOverlap] = useState(64);
  const [showSettings, setShowSettings] = useState(true);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleFiles = (newFiles) => {
    const allowed = ['application/pdf', 'text/plain',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const ext = ['.pdf', '.txt', '.docx'];
    const valid = Array.from(newFiles).filter(
      (f) => allowed.includes(f.type) || ext.some((e) => f.name.toLowerCase().endsWith(e))
    );
    setFiles((prev) => [...prev, ...valid]);
  };

  const removeFile = (idx) => setFiles((prev) => prev.filter((_, i) => i !== idx));

  const handleSubmit = () => {
    if (files.length === 0 || isProcessing) return;
    onUpload(files, { strategy, chunk_size: chunkSize, chunk_overlap: chunkOverlap });
    setFiles([]);
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  };

  return (
    <div className="upload-section">
      <div className="section-header">
        <div className="section-title-group">
          <Upload size={20} className="section-icon" />
          <h2 className="section-title">Upload Documents</h2>
        </div>
        <button
          className={`settings-toggle ${showSettings ? 'active' : ''}`}
          onClick={() => setShowSettings(!showSettings)}
          title="Chunking settings"
        >
          <Settings2 size={16} />
          <span>Settings</span>
          {showSettings ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {/* Settings panel */}
      {showSettings && (
        <div className="settings-panel animate-fade-in-up">
          <div className="settings-grid">
            <div className="setting-field">
              <label>Chunking Strategy</label>
              <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
                {STRATEGIES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div className="setting-field">
              <label>Chunk Size</label>
              <input
                type="number"
                value={chunkSize}
                onChange={(e) => setChunkSize(Number(e.target.value))}
                min={64}
                step={64}
              />
            </div>
            <div className="setting-field">
              <label>Chunk Overlap</label>
              <input
                type="number"
                value={chunkOverlap}
                onChange={(e) => setChunkOverlap(Number(e.target.value))}
                min={0}
                step={16}
              />
            </div>
          </div>
        </div>
      )}

      {/* Drop zone */}
      <div
        className={`dropzone ${dragOver ? 'dropzone-active' : ''} ${files.length > 0 ? 'dropzone-has-files' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files); }}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          multiple
          hidden
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div className="dropzone-icon">
          <Upload size={28} />
        </div>
        <p className="dropzone-text">
          Drag & drop your files here, or <span className="dropzone-link">browse</span>
        </p>
        <p className="dropzone-hint">PDF, DOCX, TXT — up to 50 MB each</p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="file-list">
          {files.map((f, i) => (
            <div key={`${f.name}-${i}`} className="file-chip animate-fade-in-up" style={{ animationDelay: `${i * 60}ms` }}>
              <FileText size={14} className="file-chip-icon" />
              <span className="file-chip-name">{f.name}</span>
              <span className="file-chip-size">{formatSize(f.size)}</span>
              <button className="file-chip-remove" onClick={(e) => { e.stopPropagation(); removeFile(i); }}>
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload button */}
      <button
        className="btn-upload"
        disabled={files.length === 0 || isProcessing}
        onClick={handleSubmit}
      >
        {isProcessing ? (
          <>
            <span className="spinner" />
            <span>Processing…</span>
          </>
        ) : (
          <>
            <Upload size={16} />
            <span>Upload & Ingest ({files.length} file{files.length !== 1 ? 's' : ''})</span>
          </>
        )}
      </button>
    </div>
  );
}
