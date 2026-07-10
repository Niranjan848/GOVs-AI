import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, BookOpen, Bookmark, TrendingUp, User, ChevronRight, Bot, Sun, Moon, LogOut, Menu } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useProfile } from '../hooks/useProfile';
import { useSchemes } from '../hooks/useSchemes';
import { useChat } from '../hooks/useChat';
import type { Scheme } from '../types';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { profile, completion, fetchProfile, fetchCompletion } = useProfile();
  const { schemes, bookmarks, fetchSchemes, fetchBookmarks } = useSchemes();
  const { history, loadHistory } = useChat();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    fetchProfile();
    fetchCompletion();
    fetchSchemes();
    fetchBookmarks();
    loadHistory();
  }, []);

  const completionPct = completion?.completion ?? profile?.completion_percentage ?? 0;

  const navItems = [
    { icon: <TrendingUp size={20} />, label: 'Dashboard', path: '/dashboard', active: true },
    { icon: <MessageSquare size={20} />, label: 'AI Chat', path: '/chat' },
    { icon: <BookOpen size={20} />, label: 'Schemes', path: '/schemes' },
    { icon: <User size={20} />, label: 'Profile', path: '/profile' },
    { icon: <Bookmark size={20} />, label: 'Bookmarks', path: '/schemes' },
  ];

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className={`app-sidebar glass-sidebar ${sidebarOpen ? '' : 'collapsed'}`} style={{
        display: 'flex', flexDirection: 'column', padding: 'var(--space-md)',
        background: 'var(--bg-secondary)',
      }}>
        {/* Logo */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 'var(--space-sm)',
          padding: 'var(--space-md)', marginBottom: 'var(--space-lg)',
        }}>
          <span style={{ fontSize: '1.5rem' }}>🏛️</span>
          {sidebarOpen && (
            <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, fontSize: 'var(--text-lg)' }}>
              GOVs-AI
            </span>
          )}
        </div>

        {/* Nav Items */}
        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
          {navItems.map((item) => (
            <button
              key={item.label}
              className="btn btn-ghost"
              onClick={() => navigate(item.path)}
              style={{
                justifyContent: 'flex-start', padding: '0.625rem 0.875rem',
                borderRadius: 'var(--radius-md)',
                background: item.active ? 'rgba(255,107,53,0.1)' : 'transparent',
                color: item.active ? 'var(--color-saffron)' : 'var(--text-secondary)',
                fontWeight: item.active ? 600 : 400,
              }}
            >
              {item.icon}
              {sidebarOpen && <span>{item.label}</span>}
            </button>
          ))}
        </nav>

        {/* Bottom */}
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: 'var(--space-md)', display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
          <button className="btn btn-ghost" onClick={toggleTheme} style={{ justifyContent: 'flex-start', padding: '0.5rem 0.875rem' }}>
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            {sidebarOpen && <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>}
          </button>
          <button className="btn btn-ghost" onClick={() => { logout(); navigate('/'); }} style={{ justifyContent: 'flex-start', padding: '0.5rem 0.875rem', color: 'var(--error)' }}>
            <LogOut size={18} />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="app-main">
        {/* Header */}
        <header className="app-header">
          <button className="btn btn-icon btn-ghost" onClick={() => setSidebarOpen(!sidebarOpen)}>
            <Menu size={20} />
          </button>
          <div style={{ flex: 1, marginLeft: 'var(--space-md)' }}>
            <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: 700 }}>
              Welcome back, {profile?.name || user?.email?.split('@')[0] || 'User'} 👋
            </h2>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
              Here's your personalized scheme dashboard
            </p>
          </div>
          <button className="btn btn-primary" onClick={() => navigate('/chat')}>
            <Bot size={18} /> Ask AI
          </button>
        </header>

        {/* Content */}
        <div className="app-content">
          {/* Stats Row */}
          <div className="grid grid-4" style={{ marginBottom: 'var(--space-xl)' }}>
            {[
              { icon: '📊', label: 'Profile Complete', value: `${completionPct}%`, color: '#3B82F6', bg: 'rgba(59,130,246,0.1)' },
              { icon: '📋', label: 'Available Schemes', value: `${schemes.length}`, color: '#10B981', bg: 'rgba(16,185,129,0.1)' },
              { icon: '🔖', label: 'Bookmarks', value: `${bookmarks.length}`, color: '#F59E0B', bg: 'rgba(245,158,11,0.1)' },
              { icon: '💬', label: 'Conversations', value: `${history.length}`, color: '#8B5CF6', bg: 'rgba(139,92,246,0.1)' },
            ].map((stat) => (
              <div key={stat.label} className="stats-card animate-slide-up">
                <div className="stats-icon" style={{ background: stat.bg }}>
                  <span style={{ fontSize: '1.5rem' }}>{stat.icon}</span>
                </div>
                <div>
                  <div className="stats-value" style={{ color: stat.color }}>{stat.value}</div>
                  <div className="stats-label">{stat.label}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-3">
            {/* Profile Completion Card */}
            <div className="glass-card" style={{ padding: 'var(--space-xl)', gridColumn: 'span 1' }}>
              <h3 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-lg)' }}>
                Profile Completion
              </h3>
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 'var(--space-lg)' }}>
                <div className="progress-ring" style={{ width: '120px', height: '120px' }}>
                  <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle className="progress-ring-track" cx="60" cy="60" r="50" strokeWidth="10" />
                    <circle
                      className="progress-ring-fill"
                      cx="60" cy="60" r="50" strokeWidth="10"
                      stroke={completionPct >= 80 ? 'var(--success)' : completionPct >= 50 ? 'var(--warning)' : 'var(--color-saffron)'}
                      strokeDasharray={`${2 * Math.PI * 50}`}
                      strokeDashoffset={`${2 * Math.PI * 50 * (1 - completionPct / 100)}`}
                    />
                  </svg>
                  <span className="progress-ring-text" style={{ fontSize: 'var(--text-2xl)' }}>
                    {completionPct}%
                  </span>
                </div>
              </div>
              {completion?.missing_fields && completion.missing_fields.length > 0 && (
                <div>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginBottom: 'var(--space-sm)' }}>
                    Missing: {completion.missing_fields.slice(0, 3).join(', ')}
                  </p>
                  <button className="btn btn-secondary btn-sm" onClick={() => navigate('/profile')} style={{ width: '100%' }}>
                    Complete Profile
                  </button>
                </div>
              )}
            </div>

            {/* Recent Chats */}
            <div className="glass-card" style={{ padding: 'var(--space-xl)', gridColumn: 'span 2' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
                <h3 style={{ fontSize: 'var(--text-lg)' }}>Recent Conversations</h3>
                <button className="btn btn-ghost btn-sm" onClick={() => navigate('/chat')}>
                  View All <ChevronRight size={14} />
                </button>
              </div>
              {history.length === 0 ? (
                <div className="empty-state" style={{ padding: 'var(--space-xl)' }}>
                  <div className="empty-state-icon">💬</div>
                  <p>No conversations yet</p>
                  <button className="btn btn-primary btn-sm" onClick={() => navigate('/chat')} style={{ marginTop: 'var(--space-md)' }}>
                    <Bot size={16} /> Start Chatting
                  </button>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                  {history.slice(0, 4).map((chat) => (
                    <div
                      key={chat.id}
                      onClick={() => navigate('/chat')}
                      style={{
                        padding: 'var(--space-md)', borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--border-color)', cursor: 'pointer',
                        transition: 'background var(--transition-fast)',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-glass)')}
                      onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 500, fontSize: 'var(--text-sm)' }}>{chat.title}</span>
                        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>
                          {new Date(chat.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                        {chat.last_message_preview || `${chat.message_count} messages`}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Schemes Row */}
          <div style={{ marginTop: 'var(--space-xl)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
              <h3 style={{ fontSize: 'var(--text-lg)' }}>Available Schemes</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => navigate('/schemes')}>
                Browse All <ChevronRight size={14} />
              </button>
            </div>
            <div className="grid grid-3">
              {schemes.slice(0, 6).map((scheme) => (
                <SchemeSmallCard key={scheme.id} scheme={scheme} onClick={() => navigate('/schemes')} />
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function SchemeSmallCard({ scheme, onClick }: { scheme: Scheme; onClick: () => void }) {
  return (
    <div className="scheme-card" onClick={onClick}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-sm)' }}>
        <span className={`badge badge-${scheme.category}`}>{scheme.category}</span>
        {scheme.benefits_amount && (
          <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--success)' }}>
            {scheme.benefits_amount}
          </span>
        )}
      </div>
      <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 600, marginBottom: 'var(--space-xs)' }}>
        {scheme.name}
      </h4>
      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)' }}>
        {scheme.description.substring(0, 100)}...
      </p>
    </div>
  );
}
