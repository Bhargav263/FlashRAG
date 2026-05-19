import { Bot, User, Search, Zap } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

export default function ChatMessage({ role, text, retrievalTime, generationTime }) {
  const isUser = role === 'user';

  return (
    <div className={`chat-msg ${isUser ? 'chat-msg-user' : 'chat-msg-bot'}`}>
      {/* Avatar */}
      <div className={`chat-avatar ${isUser ? 'avatar-user' : 'avatar-bot'}`}>
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      {/* Bubble */}
      <div className="chat-bubble-wrapper">
        <div className={`chat-bubble ${isUser ? 'bubble-user' : 'bubble-bot'} markdown-body ${!isUser && text === '' ? 'typing-indicator' : ''}`}>
          {isUser ? (
            text
          ) : text === '' ? (
            <>
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                }
              }}
            >
              {text}
            </ReactMarkdown>
          )}
        </div>

        {/* Timing badges (bot only) */}
        {!isUser && (retrievalTime != null || generationTime != null) && (
          <div className="chat-timing">
            {retrievalTime != null && (
              <span className="timing-badge">
                <Search size={11} />
                {retrievalTime?.toFixed(2)}s
              </span>
            )}
            {generationTime != null && (
              <span className="timing-badge">
                <Zap size={11} />
                {generationTime?.toFixed(2)}s
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
