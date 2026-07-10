import { useNavigate } from 'react-router-dom';
import { Bot, Shield, Brain, Zap, Users, FileText, ChevronRight, Sparkles } from 'lucide-react';
import { DEMO_USERS } from '../types';
import { useAuth } from '../context/AuthContext';

export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    navigate('/dashboard');
    return null;
  }

  const features = [
    {
      icon: <Brain size={28} />,
      title: 'AI-Powered Profiling',
      description: 'Our intelligent agent builds your profile through natural conversation, understanding your needs without complex forms.',
      gradient: 'linear-gradient(135deg, #FF6B35, #E55A2B)',
    },
    {
      icon: <Shield size={28} />,
      title: 'Smart Eligibility Engine',
      description: 'Advanced rule-based + AI reasoning to match you with schemes you truly qualify for, with transparent explanations.',
      gradient: 'linear-gradient(135deg, #138808, #1DA80D)',
    },
    {
      icon: <FileText size={28} />,
      title: 'RAG-Powered Knowledge',
      description: 'Retrieval-Augmented Generation over official government documents ensures accurate, up-to-date scheme information.',
      gradient: 'linear-gradient(135deg, #3B82F6, #2563EB)',
    },
    {
      icon: <Zap size={28} />,
      title: 'Instant Checklists',
      description: 'Get personalized document checklists and step-by-step application guides tailored to your specific situation.',
      gradient: 'linear-gradient(135deg, #8B5CF6, #7C3AED)',
    },
  ];

  return (
    <div style={{ minHeight: '100vh' }}>
      {/* Hero Section */}
      <section className="landing-hero">
        <div className="landing-hero-content">
          <div style={{ 
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.5rem 1rem', borderRadius: '999px',
            background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)', marginBottom: '1.5rem',
            fontSize: '0.875rem', color: 'rgba(255,255,255,0.9)'
          }}>
            <Sparkles size={16} color="#FFD700" />
            Powered by AI Agents + RAG Pipeline
          </div>
          
          <h1>Your AI Guide to<br />Government Welfare Schemes</h1>
          
          <p>
            Discover government schemes you're eligible for through intelligent conversation. 
            GOVs-AI uses autonomous AI agents to analyze your profile, search official documents, 
            and provide personalized recommendations with full transparency.
          </p>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button className="btn btn-primary btn-lg" onClick={() => navigate('/login')}
              style={{ fontSize: '1rem', padding: '0.875rem 2rem' }}>
              <Bot size={20} /> Get Started Free
            </button>
            <button className="btn btn-secondary btn-lg" onClick={() => navigate('/login')}
              style={{ 
                fontSize: '1rem', padding: '0.875rem 2rem',
                background: 'rgba(255,255,255,0.1)', color: 'white',
                border: '1px solid rgba(255,255,255,0.3)',
              }}>
              Try Demo <ChevronRight size={18} />
            </button>
          </div>

          {/* Stats */}
          <div style={{ 
            display: 'flex', gap: '2rem', justifyContent: 'center', marginTop: '3rem',
            flexWrap: 'wrap',
          }}>
            {[
              { value: '15+', label: 'Government Schemes' },
              { value: '5', label: 'Demo Personas' },
              { value: '100%', label: 'Free & Open Source' },
            ].map((stat) => (
              <div key={stat.label} style={{ textAlign: 'center' }}>
                <div style={{ 
                  fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-heading)',
                  background: 'linear-gradient(135deg, #FFD700, #FF6B35)',
                  WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                }}>
                  {stat.value}
                </div>
                <div style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.6)' }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section style={{ 
        padding: 'var(--space-3xl) var(--space-xl)',
        background: 'var(--bg-primary)',
      }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <h2 style={{ 
            textAlign: 'center', marginBottom: '0.5rem',
            fontSize: 'var(--text-3xl)',
          }}>
            How GOVs-AI Works
          </h2>
          <p style={{ 
            textAlign: 'center', color: 'var(--text-secondary)',
            marginBottom: 'var(--space-2xl)', maxWidth: '600px', margin: '0 auto var(--space-2xl)',
          }}>
            Four AI Agent capabilities working together to bridge the gap between citizens and government welfare.
          </p>

          <div className="grid grid-2" style={{ gap: 'var(--space-lg)' }}>
            {features.map((feature, i) => (
              <div 
                key={feature.title}
                className="glass-card"
                style={{ 
                  padding: 'var(--space-xl)',
                  animationDelay: `${i * 100}ms`,
                  animation: 'slideUp 0.5s ease-out both',
                }}
              >
                <div style={{ 
                  width: '56px', height: '56px', borderRadius: 'var(--radius-lg)',
                  background: feature.gradient, display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  color: 'white', marginBottom: 'var(--space-md)',
                }}>
                  {feature.icon}
                </div>
                <h3 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-sm)' }}>
                  {feature.title}
                </h3>
                <p style={{ color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)' }}>
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Users Section */}
      <section style={{ 
        padding: 'var(--space-3xl) var(--space-xl)',
        background: 'var(--bg-tertiary)',
      }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <h2 style={{ textAlign: 'center', marginBottom: 'var(--space-sm)' }}>
            Try Demo Personas
          </h2>
          <p style={{ 
            textAlign: 'center', color: 'var(--text-secondary)',
            marginBottom: 'var(--space-2xl)',
          }}>
            Experience GOVs-AI through pre-built citizen profiles representing diverse demographics.
          </p>

          <div style={{ 
            display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: 'var(--space-md)',
          }}>
            {DEMO_USERS.map((demo) => (
              <div
                key={demo.email}
                className="glass-card"
                onClick={() => navigate('/login')}
                style={{ 
                  padding: 'var(--space-lg)', textAlign: 'center', cursor: 'pointer',
                }}
              >
                <div style={{ fontSize: '2.5rem', marginBottom: 'var(--space-sm)' }}>
                  {demo.avatar}
                </div>
                <h4 style={{ marginBottom: '0.25rem' }}>{demo.name}</h4>
                <div className={`badge badge-${demo.role === 'Farmer' ? 'agriculture' : demo.role === 'Student' ? 'education' : 'business'}`}>
                  {demo.role}
                </div>
                <p style={{ 
                  fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)',
                  marginTop: 'var(--space-sm)',
                }}>
                  {demo.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Agent Capabilities */}
      <section style={{ 
        padding: 'var(--space-3xl) var(--space-xl)',
        background: 'var(--bg-primary)',
      }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ marginBottom: 'var(--space-2xl)' }}>
            AI Agent Characteristics
          </h2>
          <div className="grid grid-2" style={{ gap: 'var(--space-lg)', textAlign: 'left' }}>
            {[
              { icon: '🧠', title: 'Planning & Decision Making', desc: 'LangGraph workflow classifies intent, identifies missing info, and decides the optimal path to help each citizen.' },
              { icon: '🔧', title: 'Tool Usage', desc: 'The agent uses FAISS semantic search, eligibility engine, checklist generator, and scheme comparison tools autonomously.' },
              { icon: '💾', title: 'Memory Management', desc: 'Persists user context across sessions — remembers previous conversations, extracted profile data, and scheme interests.' },
              { icon: '⚡', title: 'Autonomous Execution', desc: 'Runs a complete 10-node workflow without human intervention — from understanding to recommendation to checklist generation.' },
            ].map((cap) => (
              <div key={cap.title} className="glass-card" style={{ padding: 'var(--space-lg)' }}>
                <div style={{ fontSize: '1.5rem', marginBottom: 'var(--space-sm)' }}>{cap.icon}</div>
                <h4 style={{ marginBottom: 'var(--space-xs)' }}>{cap.title}</h4>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>{cap.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ 
        padding: 'var(--space-xl)', textAlign: 'center',
        borderTop: '1px solid var(--border-color)',
        background: 'var(--bg-secondary)',
        color: 'var(--text-tertiary)', fontSize: 'var(--text-sm)',
      }}>
        <p>🇮🇳 GOVs-AI — Built for India, Powered by AI</p>
        <p style={{ marginTop: '0.25rem' }}>Hackathon 2026 • LangGraph + FastAPI + React</p>
      </footer>
    </div>
  );
}
