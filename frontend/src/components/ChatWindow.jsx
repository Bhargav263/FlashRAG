import { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, Loader2, FileText } from 'lucide-react';
import ChatMessage from './ChatMessage';
import { streamChat } from '../api';

export default function ChatWindow({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    // Add user message
    setMessages((prev) => [...prev, { role: 'user', text }]);
    setInput('');
    setLoading(true);

    try {
      // Create an empty bot message
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text: '',
        },
      ]);

      await streamChat(text, sessionId, (event) => {
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastIndex = newMessages.length - 1;
          
          if (event.type === 'chunk') {
            newMessages[lastIndex] = {
              ...newMessages[lastIndex],
              text: newMessages[lastIndex].text + event.content
            };
          } else if (event.type === 'metrics') {
            newMessages[lastIndex] = {
              ...newMessages[lastIndex],
              retrievalTime: event.retrieval_time,
              generationTime: event.generation_time
            };
          }
          return newMessages;
        });
      });
    } catch (err) {
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        // If the last message is from bot and is empty, replace it. Otherwise append.
        if (newMessages[lastIndex].role === 'bot' && newMessages[lastIndex].text === '') {
          newMessages[lastIndex].text = `⚠️ Error: ${err.response?.data?.detail || err.message}`;
          return newMessages;
        } else {
          return [
            ...prev,
            { role: 'bot', text: `⚠️ Error: ${err.response?.data?.detail || err.message}` },
          ];
        }
      });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-section">
      <div className="section-header">
        <div className="section-title-group">
          <MessageSquare size={20} className="section-icon" />
          <h2 className="section-title">Chat with Sales Bot</h2>
        </div>
        {messages.length > 0 && (
          <button className="btn-clear" onClick={() => setMessages([])}>
            Clear Chat
          </button>
        )}
      </div>

      {/* Messages area */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">
              <MessageSquare size={40} />
            </div>
            <h3>Start a Conversation</h3>
            <p>Upload documents first, then ask questions about them.</p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <ChatMessage
              key={i}
              role={msg.role}
              text={msg.text}
              retrievalTime={msg.retrievalTime}
              generationTime={msg.generationTime}
            />
          ))
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="chat-input-bar">
        <input
          ref={inputRef}
          className="chat-input"
          type="text"
          placeholder="Ask something about your documents…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          id="chat-input"
        />
        <button
          className="btn-send"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          id="btn-send"
        >
          {loading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
        </button>
      </div>
    </div>
  );
}
