import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, Mail, Lock, User, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function SignupPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await signup(email, password, name);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg-hero)', padding: 'var(--space-xl)',
      position: 'relative',
    }}>
      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(circle at 60% 40%, rgba(255,107,53,0.12), transparent 50%)',
      }} />

      <div className="animate-scale-in" style={{ width: '100%', maxWidth: '480px', zIndex: 1 }}>
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-2xl)' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: 'var(--space-sm)' }}>🏛️</div>
          <h1 style={{ color: 'white', fontSize: 'var(--text-2xl)', fontWeight: 800, fontFamily: 'var(--font-heading)' }}>
            Create Account
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: 'var(--text-sm)' }}>
            Start discovering government schemes you're eligible for
          </p>
        </div>

        <div className="glass-panel" style={{ padding: 'var(--space-2xl)', borderRadius: 'var(--radius-2xl)', background: 'var(--bg-glass-strong)' }}>
          <form onSubmit={handleSubmit}>
            {error && (
              <div style={{
                display: 'flex', alignItems: 'center', gap: 'var(--space-sm)',
                padding: 'var(--space-md)', marginBottom: 'var(--space-lg)',
                background: 'var(--error-light)', borderRadius: 'var(--radius-md)',
                color: 'var(--error)', fontSize: 'var(--text-sm)',
              }}>
                <AlertCircle size={16} /> {error}
              </div>
            )}

            <div className="input-group" style={{ marginBottom: 'var(--space-md)' }}>
              <label className="input-label">Full Name</label>
              <div style={{ position: 'relative' }}>
                <User size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
                <input className="input-field" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your full name" style={{ paddingLeft: '38px', width: '100%' }} />
              </div>
            </div>

            <div className="input-group" style={{ marginBottom: 'var(--space-md)' }}>
              <label className="input-label">Email</label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
                <input className="input-field" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="your@email.com" required style={{ paddingLeft: '38px', width: '100%' }} />
              </div>
            </div>

            <div className="input-group" style={{ marginBottom: 'var(--space-lg)' }}>
              <label className="input-label">Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
                <input className="input-field" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Min 6 characters" required minLength={6} style={{ paddingLeft: '38px', width: '100%' }} />
              </div>
            </div>

            <button type="submit" className={`btn btn-primary ${isLoading ? 'btn-loading' : ''}`} style={{ width: '100%', padding: '0.75rem', fontSize: 'var(--text-base)' }} disabled={isLoading}>
              {isLoading ? <span className="animate-spin" style={{ display: 'inline-block' }}>⏳</span> : <><UserPlus size={18} /> Create Account</>}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 'var(--space-lg)', color: 'var(--text-tertiary)', fontSize: 'var(--text-sm)' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--color-saffron)', fontWeight: 600 }}>Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
