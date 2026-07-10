import { useEffect, useState } from 'react';
import { ArrowLeft, Users, FileText, MessageSquare, Database } from 'lucide-react';
import { adminAPI } from '../lib/api';
import type { AdminStats } from '../types';
import { useNavigate } from 'react-router-dom';

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadData() {
      try {
        const statsRes = await adminAPI.getStats();
        const analyticsRes = await adminAPI.getAnalytics();
        setStats(statsRes.data as AdminStats);
        setAnalytics(analyticsRes.data);
      } catch (err) {
        console.error('Failed to load admin stats:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <header className="app-header">
        <button className="btn btn-icon btn-ghost" onClick={() => navigate('/dashboard')}>
          <ArrowLeft size={20} />
        </button>
        <div style={{ flex: 1, marginLeft: 'var(--space-md)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)' }}>Admin Console</h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
            System health, indexing stats, and usage metrics
          </p>
        </div>
      </header>

      <div className="app-content">
        {isLoading ? (
          <div className="skeleton" style={{ height: '300px', width: '100%' }} />
        ) : (
          <div>
            {/* KPI Metrics */}
            <div className="grid grid-4" style={{ marginBottom: 'var(--space-xl)' }}>
              <div className="stats-card">
                <div className="stats-icon" style={{ background: 'rgba(59,130,246,0.1)' }}><Users size={20} color="#3B82F6" /></div>
                <div>
                  <div className="stats-value">{stats?.total_users}</div>
                  <div className="stats-label">Registered Citizens</div>
                </div>
              </div>

              <div className="stats-card">
                <div className="stats-icon" style={{ background: 'rgba(16,185,129,0.1)' }}><MessageSquare size={20} color="#10B981" /></div>
                <div>
                  <div className="stats-value">{stats?.total_chats}</div>
                  <div className="stats-label">AI Dialogs</div>
                </div>
              </div>

              <div className="stats-card">
                <div className="stats-icon" style={{ background: 'rgba(139,92,246,0.1)' }}><FileText size={20} color="#8B5CF6" /></div>
                <div>
                  <div className="stats-value">{stats?.total_documents}</div>
                  <div className="stats-label">Indexed Documents</div>
                </div>
              </div>

              <div className="stats-card">
                <div className="stats-icon" style={{ background: 'rgba(245,158,11,0.1)' }}><Database size={20} color="#F59E0B" /></div>
                <div>
                  <div className="stats-value">{analytics?.vector_db?.total_vectors || 0}</div>
                  <div className="stats-label">Vector Database Status</div>
                </div>
              </div>
            </div>

            {/* Ingestion & Analytics Details */}
            <div className="grid grid-2">
              <div className="glass-card" style={{ padding: 'var(--space-xl)' }}>
                <h3 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-md)' }}>Popular States</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                  {stats?.popular_states.map((state, idx) => (
                    <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: 'var(--space-sm) 0', borderBottom: '1px solid var(--border-color)' }}>
                      <span style={{ fontSize: 'var(--text-sm)' }}>{state.state}</span>
                      <span style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>{state.count} users</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="glass-card" style={{ padding: 'var(--space-xl)' }}>
                <h3 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-md)' }}>Top Recommended Schemes</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
                  {stats?.popular_schemes.map((scheme, idx) => (
                    <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: 'var(--space-sm) 0', borderBottom: '1px solid var(--border-color)' }}>
                      <span style={{ fontSize: 'var(--text-sm)' }}>{scheme.name}</span>
                      <span style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>{scheme.count} times</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
