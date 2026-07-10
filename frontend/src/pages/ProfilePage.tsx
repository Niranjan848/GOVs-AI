import { useEffect, useState } from 'react';
import { ArrowLeft, Save, CheckCircle } from 'lucide-react';
import { useProfile } from '../hooks/useProfile';
import { INDIAN_STATES } from '../types';
import { useNavigate } from 'react-router-dom';

export default function ProfilePage() {
  const { profile, fetchProfile, updateProfile, fetchCompletion } = useProfile();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [age, setAge] = useState<number | ''>('');
  const [gender, setGender] = useState('');
  const [state, setState] = useState('');
  const [occupation, setOccupation] = useState('');
  const [annualIncome, setAnnualIncome] = useState<number | ''>('');
  const [category, setCategory] = useState('');
  const [education, setEducation] = useState('');
  const [landArea, setLandArea] = useState<number | ''>('');
  const [hasDisability, setHasDisability] = useState(false);
  const [familySize, setFamilySize] = useState<number | ''>('');
  const [bplCard, setBplCard] = useState(false);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchProfile();
    fetchCompletion();
  }, []);

  useEffect(() => {
    if (profile) {
      setName(profile.name || '');
      setAge(profile.age ?? '');
      setGender(profile.gender || '');
      setState(profile.state || '');
      setOccupation(profile.occupation || '');
      setAnnualIncome(profile.annual_income ?? '');
      setCategory(profile.category || '');
      setEducation(profile.education || '');
      setLandArea(profile.land_area_acres ?? '');
      setHasDisability(profile.has_disability || false);
      setFamilySize(profile.family_size ?? '');
      setBplCard(profile.bpl_card || false);
    }
  }, [profile]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(false);

    const successVal = await updateProfile({
      name,
      age: age === '' ? null : Number(age),
      gender: gender || null,
      state: state || null,
      occupation: occupation || null,
      annual_income: annualIncome === '' ? null : Number(annualIncome),
      category: category || null,
      education: education || null,
      land_area_acres: landArea === '' ? null : Number(landArea),
      has_disability: hasDisability,
      family_size: familySize === '' ? null : Number(familySize),
      bpl_card: bplCard,
    });

    if (successVal) {
      setSuccess(true);
      fetchCompletion();
      setTimeout(() => setSuccess(false), 3000);
    }
    setSaving(false);
  };

  const occupationsList = ['Farmer', 'Student', 'Artisan', 'Entrepreneur', 'Self-Employed', 'Unemployed', 'Retired', 'Private Sector', 'Government Sector'];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <header className="app-header">
        <button className="btn btn-icon btn-ghost" onClick={() => navigate('/dashboard')}>
          <ArrowLeft size={20} />
        </button>
        <div style={{ flex: 1, marginLeft: 'var(--space-md)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)' }}>Socioeconomic Profile</h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
            Provide details to calculate eligibility matches automatically
          </p>
        </div>
      </header>

      <div className="app-content" style={{ maxWidth: '800px' }}>
        <form onSubmit={handleSave} className="glass-card" style={{ padding: 'var(--space-2xl)' }}>
          {success && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: 'var(--space-sm)',
              padding: 'var(--space-md)', marginBottom: 'var(--space-lg)',
              background: 'var(--success-light)', borderRadius: 'var(--radius-md)',
              color: '#065F46', fontSize: 'var(--text-sm)', fontWeight: 600,
            }}>
              <CheckCircle size={18} /> Profile updated successfully!
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-lg)', marginBottom: 'var(--space-lg)' }}>
            <div className="input-group">
              <label className="input-label">Full Name</label>
              <input className="input-field" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Full Name" />
            </div>

            <div className="input-group">
              <label className="input-label">Age</label>
              <input className="input-field" type="number" value={age} onChange={(e) => setAge(e.target.value === '' ? '' : Number(e.target.value))} placeholder="Age" min={1} max={120} />
            </div>

            <div className="input-group">
              <label className="input-label">Gender</label>
              <select className="input-field" value={gender} onChange={(e) => setGender(e.target.value)}>
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="input-group">
              <label className="input-label">State</label>
              <select className="input-field" value={state} onChange={(e) => setState(e.target.value)}>
                <option value="">Select State</option>
                {INDIAN_STATES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <div className="input-group">
              <label className="input-label">Occupation</label>
              <select className="input-field" value={occupation} onChange={(e) => setOccupation(e.target.value)}>
                <option value="">Select Occupation</option>
                {occupationsList.map((o) => (
                  <option key={o} value={o.toLowerCase()}>{o}</option>
                ))}
              </select>
            </div>

            <div className="input-group">
              <label className="input-label">Annual Income (₹)</label>
              <input className="input-field" type="number" value={annualIncome} onChange={(e) => setAnnualIncome(e.target.value === '' ? '' : Number(e.target.value))} placeholder="Annual Income" min={0} />
            </div>

            <div className="input-group">
              <label className="input-label">Social Category</label>
              <select className="input-field" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="">Select Category</option>
                <option value="general">General</option>
                <option value="obc">OBC</option>
                <option value="sc">SC</option>
                <option value="st">ST</option>
                <option value="ews">EWS</option>
              </select>
            </div>

            <div className="input-group">
              <label className="input-label">Education level</label>
              <input className="input-field" type="text" value={education} onChange={(e) => setEducation(e.target.value)} placeholder="E.g., Matric, Undergraduate" />
            </div>

            <div className="input-group">
              <label className="input-label">Land Area (Acres)</label>
              <input className="input-field" type="number" step="0.01" value={landArea} onChange={(e) => setLandArea(e.target.value === '' ? '' : Number(e.target.value))} placeholder="Land Area in acres" />
            </div>

            <div className="input-group">
              <label className="input-label">Family Size</label>
              <input className="input-field" type="number" value={familySize} onChange={(e) => setFamilySize(e.target.value === '' ? '' : Number(e.target.value))} placeholder="Family Size" min={1} />
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)', marginBottom: 'var(--space-xl)' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', fontSize: 'var(--text-sm)', cursor: 'pointer' }}>
              <input type="checkbox" checked={hasDisability} onChange={(e) => setHasDisability(e.target.checked)} style={{ width: '18px', height: '18px' }} />
              <span>Person with Disability (PwD)</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', fontSize: 'var(--text-sm)', cursor: 'pointer' }}>
              <input type="checkbox" checked={bplCard} onChange={(e) => setBplCard(e.target.checked)} style={{ width: '18px', height: '18px' }} />
              <span>Below Poverty Line (BPL) Card Holder</span>
            </label>
          </div>

          <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
            <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={saving}>
              <Save size={18} /> {saving ? 'Saving...' : 'Save Profile'}
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/dashboard')} style={{ flex: 1 }}>
              Back to Dashboard
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
