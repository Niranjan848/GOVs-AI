import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Plus, ArrowLeft, Bot, User as UserIcon, Moon, Sun, Copy, Check } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useChat } from '../hooks/useChat';
import type { Message, SchemePreview } from '../types';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const { theme, toggleTheme } = useTheme();
  const { messages, chatId, isLoading, history, sendMessage, loadChat, loadHistory, startNewChat } = useChat();
  const navigate = useNavigate();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { loadHistory(); }, []);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    sendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestions = [
    "🌾 What schemes can a farmer with 2 acres land get?",
    "📚 Show me scholarships for SC category students",
    "💼 Compare Mudra Loan and Stand-Up India",
    "🏥 Am I eligible for Ayushman Bharat?",
  ];

  return (
    <div style={{ display: 'flex', height: '100vh', background: 'var(--bg-primary)' }}>
      {/* Chat Sidebar */}
      <div style={{
        width: '280px', borderRight: '1px solid var(--border-color)',
        background: 'var(--bg-secondary)', display: 'flex', flexDirection: 'column',
        padding: 'var(--space-md)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', marginBottom: 'var(--space-lg)' }}>
          <button className="btn btn-icon btn-ghost" onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={20} />
          </button>
          <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: 'var(--text-lg)' }}>
            🏛️ GOVs-AI
          </span>
        </div>

        <button className="btn btn-primary" onClick={startNewChat} style={{ width: '100%', marginBottom: 'var(--space-lg)' }}>
          <Plus size={18} /> New Chat
        </button>

        <div style={{ flex: 1, overflowY: 'auto' }}>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 'var(--space-sm)', letterSpacing: '0.5px' }}>
            History
          </p>
          {history.map((chat) => (
            <button
              key={chat.id}
              className="btn btn-ghost"
              onClick={() => loadChat(chat.id)}
              style={{
                width: '100%', justifyContent: 'flex-start', padding: '0.5rem 0.75rem',
                fontSize: 'var(--text-sm)', marginBottom: '2px', borderRadius: 'var(--radius-sm)',
                background: chatId === chat.id ? 'rgba(255,107,53,0.1)' : undefined,
                color: chatId === chat.id ? 'var(--color-saffron)' : undefined,
              }}
            >
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {chat.title}
              </span>
            </button>
          ))}
        </div>

        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: 'var(--space-sm)' }}>
          <button className="btn btn-ghost btn-sm" onClick={toggleTheme} style={{ width: '100%', justifyContent: 'flex-start' }}>
            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
            <span>{theme === 'light' ? 'Dark' : 'Light'} Mode</span>
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="chat-container" style={{ flex: 1 }}>
        {/* Messages */}
        <div className="chat-messages">
          {messages.length === 0 && (
            <div style={{
              flex: 1, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
            }}>
              <div style={{ fontSize: '3rem', marginBottom: 'var(--space-lg)' }}>🤖</div>
              <h2 style={{ fontSize: 'var(--text-2xl)', marginBottom: 'var(--space-sm)' }}>
                GOVs-AI Assistant
              </h2>
              <p style={{
                color: 'var(--text-secondary)', textAlign: 'center',
                maxWidth: '500px', marginBottom: 'var(--space-2xl)',
                lineHeight: 'var(--leading-relaxed)',
              }}>
                I can help you discover government schemes, check eligibility, 
                compare programs, and generate application checklists. What would you like to know?
              </p>
              <div style={{
                display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-sm)',
                width: '100%', maxWidth: '600px',
              }}>
                {suggestions.map((s) => (
                  <button
                    key={s}
                    className="btn btn-secondary"
                    onClick={() => { setInput(s.substring(2).trim()); }}
                    style={{
                      padding: '0.75rem 1rem', fontSize: 'var(--text-sm)',
                      textAlign: 'left', lineHeight: '1.4',
                    }}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <ChatBubble key={msg.id} message={msg} />
          ))}

          {isLoading && (
            <div className="typing-indicator" style={{
              background: 'var(--bg-glass)', borderRadius: 'var(--radius-xl)',
              border: '1px solid var(--border-color)', display: 'inline-flex',
              alignSelf: 'flex-start',
            }}>
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <textarea
              ref={inputRef}
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about government schemes..."
              rows={1}
              style={{
                height: 'auto',
                minHeight: '44px',
                maxHeight: '120px',
              }}
            />
            <button
              className="btn btn-primary btn-icon"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              style={{
                width: '44px', height: '44px', borderRadius: 'var(--radius-full)',
                flexShrink: 0,
              }}
            >
              <Send size={18} />
            </button>
          </div>
          <p style={{
            textAlign: 'center', fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)',
            marginTop: 'var(--space-sm)',
          }}>
            GOVs-AI provides AI-generated suggestions. Always verify with official sources.
          </p>
        </div>
      </div>
    </div>
  );
}

function ChatBubble({ message }: { message: Message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';
  const meta = message.metadata_json;

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-end' : 'flex-start' }}>
      {/* Role indicator */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '0.375rem',
        marginBottom: '0.25rem', fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)',
      }}>
        {isUser ? <UserIcon size={12} /> : <Bot size={12} />}
        {isUser ? 'You' : 'GOVs-AI'}
      </div>

      {/* Bubble */}
      <div className={`chat-bubble ${isUser ? 'chat-bubble-user' : 'chat-bubble-ai'}`}>
        {/* Render content with basic markdown-like formatting */}
        <div style={{ whiteSpace: 'pre-wrap' }}>
          {message.content.split('\n').map((line, i) => {
            if (line.startsWith('**') && line.endsWith('**')) {
              return <div key={i} style={{ fontWeight: 700, marginTop: i > 0 ? '0.5rem' : 0 }}>{line.replace(/\*\*/g, '')}</div>;
            }
            if (line.startsWith('- ') || line.startsWith('• ')) {
              return <div key={i} style={{ paddingLeft: '1rem' }}>{line}</div>;
            }
            return <div key={i}>{line}</div>;
          })}
        </div>

        {/* Scheme cards */}
        {meta?.schemes && meta.schemes.length > 0 && (
          <div style={{ marginTop: 'var(--space-md)', display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
            {meta.schemes.map((scheme: SchemePreview, i: number) => (
              <div key={i} style={{
                padding: 'var(--space-md)', borderRadius: 'var(--radius-md)',
                background: 'rgba(255,107,53,0.05)', border: '1px solid rgba(255,107,53,0.15)',
              }}>
                <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>{scheme.name}</div>
                {scheme.benefits_amount && (
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--success)', fontWeight: 600 }}>
                    {scheme.benefits_amount}
                  </div>
                )}
                <div style={{
                  fontSize: 'var(--text-xs)', marginTop: '0.25rem',
                  display: 'flex', alignItems: 'center', gap: '0.5rem',
                }}>
                  <span style={{
                    padding: '0.125rem 0.5rem', borderRadius: 'var(--radius-full)',
                    background: scheme.score >= 0.8 ? 'var(--success-light)' : 'var(--warning-light)',
                    color: scheme.score >= 0.8 ? '#065F46' : '#92400E',
                    fontWeight: 600,
                  }}>
                    {Math.round(scheme.score * 100)}% match
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Checklist */}
        {meta?.checklist && (
          <div style={{ marginTop: 'var(--space-md)', padding: 'var(--space-md)', borderRadius: 'var(--radius-md)', background: 'rgba(16,185,129,0.05)', border: '1px solid rgba(16,185,129,0.15)' }}>
            <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)', marginBottom: 'var(--space-sm)' }}>
              📋 Document Checklist — {meta.checklist.scheme_name}
            </div>
            {meta.checklist.items.map((item, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: 'var(--text-xs)', padding: '0.25rem 0' }}>
                <span>{item.user_likely_has ? '✅' : '⬜'}</span>
                <span>{item.document}</span>
                {item.mandatory && <span style={{ color: 'var(--error)', fontWeight: 600 }}>*</span>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action buttons for AI messages */}
      {!isUser && (
        <div style={{ display: 'flex', gap: '0.25rem', marginTop: '0.25rem' }}>
          <button className="btn btn-ghost btn-sm" onClick={handleCopy} style={{ fontSize: 'var(--text-xs)', padding: '0.25rem 0.5rem' }}>
            {copied ? <Check size={12} /> : <Copy size={12} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
      )}
    </div>
  );
}
