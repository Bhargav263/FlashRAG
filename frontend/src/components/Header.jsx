import { Bot, Sparkles } from 'lucide-react';

export default function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        {/* Logo */}
        <div className="header-logo">
          <div className="logo-icon">
            <Bot size={22} />
          </div>
          <div>
            <h1 className="logo-title">
              Sales Bot <span className="logo-ai">AI</span>
            </h1>
            <p className="logo-subtitle">Intelligent Document Assistant</p>
          </div>
        </div>

        {/* Status badge */}
        <div className="header-actions">
          <div className="status-badge">
            <span className="status-dot" />
            <span>Online</span>
          </div>
          <div className="header-sparkle">
            <Sparkles size={16} />
            <span>Powered by RAG</span>
          </div>
        </div>
      </div>
    </header>
  );
}
