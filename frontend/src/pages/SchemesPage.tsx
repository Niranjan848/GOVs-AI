import { useEffect, useState } from 'react';
import { Search, Bookmark, ArrowLeft, ExternalLink, TrendingUp } from 'lucide-react';
import { useSchemes } from '../hooks/useSchemes';
import { SCHEME_CATEGORIES } from '../types';
import type { Scheme } from '../types';
import { useNavigate } from 'react-router-dom';

export default function SchemesPage() {
  const { schemes, isLoading, fetchSchemes, fetchBookmarks, toggleBookmark, isBookmarked } = useSchemes();
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedScheme, setSelectedScheme] = useState<Scheme | null>(null);

  useEffect(() => {
    fetchSchemes();
    fetchBookmarks();
  }, []);

  const handleFilter = (category: string) => {
    setSelectedCategory(category);
    fetchSchemes({
      category: category === 'all' ? undefined : category,
      search: searchQuery || undefined,
    });
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchSchemes({
      category: selectedCategory === 'all' ? undefined : selectedCategory,
      search: searchQuery || undefined,
    });
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Sidebar navigation placeholder or simple header navigation */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <header className="app-header">
          <button className="btn btn-icon btn-ghost" onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={20} />
          </button>
          <div style={{ flex: 1, marginLeft: 'var(--space-md)' }}>
            <h2 style={{ fontSize: 'var(--text-xl)' }}>Government Welfare Schemes</h2>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
              Browse and search official welfare programs across India
            </p>
          </div>
        </header>

        <div className="app-content">
          {/* Search bar & Filters */}
          <div style={{ marginBottom: 'var(--space-xl)' }}>
            <form onSubmit={handleSearch} style={{ display: 'flex', gap: 'var(--space-sm)', marginBottom: 'var(--space-md)' }}>
              <div style={{ position: 'relative', flex: 1 }}>
                <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
                <input
                  className="input-field"
                  type="text"
                  placeholder="Search schemes by name, keyword, or description..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ paddingLeft: '40px', width: '100%' }}
                />
              </div>
              <button type="submit" className="btn btn-primary">Search</button>
            </form>

            {/* Category tabs */}
            <div style={{ display: 'flex', gap: 'var(--space-xs)', overflowX: 'auto', paddingBottom: 'var(--space-xs)' }}>
              {SCHEME_CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  className="btn btn-secondary btn-sm"
                  onClick={() => handleFilter(cat.id)}
                  style={{
                    background: selectedCategory === cat.id ? 'var(--color-saffron)' : undefined,
                    color: selectedCategory === cat.id ? 'white' : undefined,
                    borderColor: selectedCategory === cat.id ? 'var(--color-saffron)' : undefined,
                  }}
                >
                  <span style={{ marginRight: '0.25rem' }}>{cat.icon}</span>
                  {cat.label}
                </button>
              ))}
            </div>
          </div>

          {/* Catalog Grid */}
          {isLoading ? (
            <div className="grid grid-3">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="glass-card" style={{ padding: 'var(--space-lg)', height: '160px' }}>
                  <div className="skeleton" style={{ height: '20px', width: '40%', marginBottom: 'var(--space-sm)' }} />
                  <div className="skeleton" style={{ height: '24px', width: '80%', marginBottom: 'var(--space-md)' }} />
                  <div className="skeleton" style={{ height: '16px', width: '100%', marginBottom: 'var(--space-xs)' }} />
                  <div className="skeleton" style={{ height: '16px', width: '90%' }} />
                </div>
              ))}
            </div>
          ) : schemes.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📋</div>
              <h3>No Schemes Found</h3>
              <p>Try resetting filters or adjusting your search keywords.</p>
            </div>
          ) : (
            <div className="grid grid-3">
              {schemes.map((scheme) => (
                <div key={scheme.id} className="scheme-card animate-slide-up" onClick={() => setSelectedScheme(scheme)}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-sm)' }}>
                    <span className={`badge badge-${scheme.category}`}>{scheme.category}</span>
                    <button
                      className="btn btn-icon btn-ghost btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleBookmark(scheme.id);
                      }}
                      style={{ color: isBookmarked(scheme.id) ? 'var(--color-saffron)' : 'var(--text-tertiary)' }}
                    >
                      <Bookmark size={16} fill={isBookmarked(scheme.id) ? 'var(--color-saffron)' : 'none'} />
                    </button>
                  </div>
                  <h4 style={{ fontSize: 'var(--text-sm)', fontWeight: 600, marginBottom: 'var(--space-xs)' }}>
                    {scheme.name}
                  </h4>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', marginBottom: 'var(--space-md)' }}>
                    {scheme.description.substring(0, 120)}...
                  </p>
                  {scheme.benefits_amount && (
                    <div style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--success)' }}>
                      Benefit: {scheme.benefits_amount}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Scheme Detail Modal */}
      {selectedScheme && (
        <div className="modal-overlay" onClick={() => setSelectedScheme(null)}>
          <div className="modal-content animate-scale-in" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px', padding: 'var(--space-2xl)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-md)' }}>
              <span className={`badge badge-${selectedScheme.category}`}>{selectedScheme.category}</span>
              <button
                className="btn btn-icon btn-ghost"
                onClick={() => toggleBookmark(selectedScheme.id)}
                style={{ color: isBookmarked(selectedScheme.id) ? 'var(--color-saffron)' : 'var(--text-tertiary)' }}
              >
                <Bookmark size={20} fill={isBookmarked(selectedScheme.id) ? 'var(--color-saffron)' : 'none'} />
              </button>
            </div>

            <h3 style={{ fontSize: 'var(--text-2xl)', marginBottom: 'var(--space-md)', fontFamily: 'var(--font-heading)' }}>
              {selectedScheme.name}
            </h3>

            {selectedScheme.ministry && (
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)', marginBottom: 'var(--space-md)' }}>
                🏛️ {selectedScheme.ministry}
              </p>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)', marginBottom: 'var(--space-lg)' }}>
              <div>
                <h5 style={{ fontSize: 'var(--text-sm)', fontWeight: 600, marginBottom: '0.25rem' }}>Description</h5>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)' }}>
                  {selectedScheme.description}
                </p>
              </div>

              {selectedScheme.benefits_amount && (
                <div style={{ display: 'flex', gap: 'var(--space-sm)', alignItems: 'center', padding: 'var(--space-md)', background: 'var(--success-light)', borderRadius: 'var(--radius-md)', color: '#065F46' }}>
                  <TrendingUp size={20} />
                  <div>
                    <h5 style={{ fontSize: 'var(--text-xs)', fontWeight: 600 }}>Financial Benefit</h5>
                    <p style={{ fontSize: 'var(--text-sm)', fontWeight: 700 }}>{selectedScheme.benefits_amount}</p>
                  </div>
                </div>
              )}

              <div>
                <h5 style={{ fontSize: 'var(--text-sm)', fontWeight: 600, marginBottom: '0.25rem' }}>Documents Required</h5>
                <ul style={{ paddingLeft: '1.25rem', fontSize: 'var(--text-xs)', color: 'var(--text-secondary)' }}>
                  {selectedScheme.documents_required && (selectedScheme.documents_required as string[]).map((doc, idx) => (
                    <li key={idx} style={{ padding: '2px 0' }}>{doc}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
              {selectedScheme.website_url && (
                <a
                  href={selectedScheme.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary"
                  style={{ flex: 1 }}
                >
                  Apply Online <ExternalLink size={14} style={{ marginLeft: '4px' }} />
                </a>
              )}
              <button className="btn btn-secondary" onClick={() => setSelectedScheme(null)} style={{ flex: 1 }}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
