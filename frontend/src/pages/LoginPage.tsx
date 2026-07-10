import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { LogIn, Mail, Lock, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { DEMO_USERS } from '../types';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Is the backend running?');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async (demoEmail: string, demoPassword: string) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError('');
    setIsLoading(true);
    try {
      await login(demoEmail, demoPassword);
      navigate('/dashboard');
    } catch (err: any) {
      setError('Demo login failed. Please start the backend server first.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg-hero)', padding: 'var(--space-xl)',
      position: 'relative', overflow: 'hidden',
    }}>
      {/* Background decoration */}
      <div style={{
        position: 'absolute', inset: 0,
        background: `
          radial-gradient(circle at 30% 70%, rgba(255,107,53,0.12), transparent 50%),
          radial-gradient(circle at 70% 30%, rgba(19,136,8,0.08), transparent 50%)
        `,
      }} />

      <div className="animate-scale-in" style={{
        width: '100%', maxWidth: '480px', zIndex: 1,
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-2xl)' }}>
          <div style={{
            fontSize: '2.5rem', marginBottom: 'var(--space-sm)',
          }}>🏛️</div>
          <h1 style={{
            color: 'white', fontSize: 'var(--text-2xl)', fontWeight: 800,
            fontFamily: 'var(--font-heading)',
          }}>
            GOVs-AI
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: 'var(--text-sm)' }}>
            Sign in to access your personalized scheme dashboard
          </p>
        </div>

        {/* Login Card */}
        <div className="glass-panel" style={{
          padding: 'var(--space-2xl)', borderRadius: 'var(--radius-2xl)',
          background: 'var(--bg-glass-strong)',
        }}>
          <form onSubmit={handleSubmit}>
            {error && (
              <div style={{
                display: 'flex', alignItems: 'center', gap: 'var(--space-sm)',
                padding: 'var(--space-md)', marginBottom: 'var(--space-lg)',
                background: 'var(--error-light)', borderRadius: 'var(--radius-md)',
                color: 'var(--error)', fontSize: 'var(--text-sm)',
              }}>
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <div className="input-group" style={{ marginBottom: 'var(--space-md)' }}>
              <label className="input-label">Email</label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{
                  position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)',
                  color: 'var(--text-tertiary)',
                }} />
                <input
                  className="input-field"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  required
                  style={{ paddingLeft: '38px', width: '100%' }}
                />
              </div>
            </div>

            <div className="input-group" style={{ marginBottom: 'var(--space-lg)' }}>
              <label className="input-label">Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{
                  position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)',
                  color: 'var(--text-tertiary)',
                }} />
                <input
                  className="input-field"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••"
                  required
                  style={{ paddingLeft: '38px', paddingRight: '38px', width: '100%' }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', color: 'var(--text-tertiary)',
                    cursor: 'pointer', padding: 0,
                  }}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className={`btn btn-primary ${isLoading ? 'btn-loading' : ''}`}
              style={{ width: '100%', padding: '0.75rem', fontSize: 'var(--text-base)' }}
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="animate-spin" style={{ display: 'inline-block' }}>⏳</span>
              ) : (
                <><LogIn size={18} /> Sign In</>
              )}
            </button>
          </form>

          <div style={{
            textAlign: 'center', margin: 'var(--space-lg) 0',
            color: 'var(--text-tertiary)', fontSize: 'var(--text-sm)',
          }}>
            Don't have an account?{' '}
            <Link to="/signup" style={{ color: 'var(--color-saffron)', fontWeight: 600 }}>
              Sign up
            </Link>
          </div>

          {/* Demo Users */}
          <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: 'var(--space-lg)' }}>
            <p style={{
              fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)',
              textAlign: 'center', marginBottom: 'var(--space-md)',
              textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600,
            }}>
              Quick Demo Login
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
              {DEMO_USERS.map((demo) => (
                <button
                  key={demo.email}
                  className="btn btn-ghost"
                  onClick={() => handleDemoLogin(demo.email, demo.password)}
                  style={{
                    justifyContent: 'flex-start', padding: '0.5rem 0.75rem',
                    fontSize: 'var(--text-sm)', borderRadius: 'var(--radius-md)',
                  }}
                >
                  <span style={{ fontSize: '1.2rem' }}>{demo.avatar}</span>
                  <span style={{ flex: 1, textAlign: 'left' }}>
                    <strong>{demo.name}</strong>
                    <span style={{ color: 'var(--text-tertiary)', marginLeft: '0.5rem' }}>
                      ({demo.role})
                    </span>
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
