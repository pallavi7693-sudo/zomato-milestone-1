"use client";
import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import AIAssistant from '../components/AIAssistant';
import FilterSearch from '../components/FilterSearch';
import LoadingOverlay from '../components/LoadingOverlay';
import RestaurantCard from '../components/RestaurantCard';

export default function Home() {
  const [mode, setMode] = useState('ai');
  const [isLoading, setIsLoading] = useState(false);

  const [favorites, setFavorites] = useState([]);
  const [history, setHistory] = useState([]);
  const [filterResults, setFilterResults] = useState(null);

  const handleToggleFavorite = (rec) => {
    setFavorites(prev => {
      const isFav = prev.find(f => f.restaurant_name === rec.restaurant_name);
      if (isFav) return prev.filter(f => f.restaurant_name !== rec.restaurant_name);
      return [...prev, rec];
    });
  };

  const handleAddToHistory = (query, results) => {
    setHistory(prev => [{ query, results, timestamp: new Date() }, ...prev]);
  };

  return (
    <>
      <header className="top-app-bar">
        <div className="top-app-bar__left">
          <button className="top-app-bar__menu-btn" title="Menu">
            <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>menu</span>
          </button>
          <div className="top-app-bar__brand">
            <span className="material-symbols-outlined top-app-bar__brand-icon">lunch_dining</span>
            <span className="top-app-bar__brand-name">GastroAI</span>
          </div>
        </div>

        <div className="top-app-bar__center">
          <button 
            className={`mode-toggle-btn ${mode === 'ai' ? 'mode-toggle-btn--active' : 'mode-toggle-btn--inactive'}`}
            onClick={() => setMode('ai')}
          >
            AI Assistant
          </button>
          <button 
            className={`mode-toggle-btn ${mode === 'filter' ? 'mode-toggle-btn--active' : 'mode-toggle-btn--inactive'}`}
            onClick={() => setMode('filter')}
          >
            Filter Search
          </button>
        </div>

        <div className="top-app-bar__right">
          <button className="notification-btn" title="Notifications">
            <span className="material-symbols-outlined" style={{ fontSize: '28px' }}>notifications</span>
          </button>
          <div className="user-profile">
            <div className="user-profile__avatar">G</div>
            <div className="user-profile__info">
              <p className="user-profile__name">Gastronome Elite</p>
              <p className="user-profile__tag">Premium Member</p>
            </div>
          </div>
        </div>
      </header>

      <div className="main-layout">
        <Sidebar 
          mode={mode} 
          setMode={setMode} 
          onFilterSearch={(results) => { setFilterResults(results); setMode('filter'); }} 
          setIsLoading={setIsLoading}
          onAddToHistory={handleAddToHistory}
        />
        <main className="main-content">
          <header className="mobile-header" style={{ display: 'none' }}>
            <div className="logo">
              <span className="material-symbols-outlined logo__icon">restaurant_menu</span>
              <span className="logo__text">GastroAI</span>
            </div>
          </header>
          
          {mode === 'ai' && (
            <AIAssistant 
              setIsLoading={setIsLoading} 
              onAddToHistory={handleAddToHistory}
              favorites={favorites}
              onToggleFavorite={handleToggleFavorite}
            />
          )}
          {mode === 'filter' && (
            <FilterSearch 
              results={filterResults}
              favorites={favorites}
              onToggleFavorite={handleToggleFavorite}
            />
          )}
          {mode === 'favorites' && (
            <div className="view-section">
              <div className="results-header">
                <div>
                  <h2 className="text-headline-md results-header__title">Your Favorites</h2>
                  <p className="results-header__subtitle">Restaurants you've loved</p>
                </div>
              </div>
              {favorites.length === 0 ? (
                <div style={{ height: '50vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: 'var(--on-surface-variant)' }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 64, color: 'var(--primary-container)', marginBottom: 16 }}>favorite</span>
                  <p className="text-body-md">You haven't saved any restaurants yet. Heart some restaurants to see them here.</p>
                </div>
              ) : (
                <div className="results-grid">
                  {favorites.map((rec, i) => (
                    <RestaurantCard key={i} rec={rec} index={i} isFavorite={true} onToggleFavorite={() => handleToggleFavorite(rec)} />
                  ))}
                </div>
              )}
            </div>
          )}
          {mode === 'history' && (
            <div className="view-section">
              <div className="results-header">
                <div>
                  <h2 className="text-headline-md results-header__title">Search History</h2>
                  <p className="results-header__subtitle">Your past requests</p>
                </div>
              </div>
              {history.length === 0 ? (
                <div style={{ height: '50vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: 'var(--on-surface-variant)' }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 64, color: 'var(--primary-container)', marginBottom: 16 }}>history</span>
                  <p className="text-body-md">Your past recommendations and searches will appear here.</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
                  {history.map((hItem, idx) => (
                    <div key={idx} style={{ padding: 16, backgroundColor: 'var(--surface-container-high)', borderRadius: 16 }}>
                      <h4 className="text-body-lg" style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span className="material-symbols-outlined">search</span> {hItem.query}
                      </h4>
                      <div className="results-grid">
                        {hItem.results.slice(0, 3).map((rec, i) => {
                           const isFav = favorites.some(f => f.restaurant_name === rec.restaurant_name);
                           return <RestaurantCard key={i} rec={rec} index={i} isFavorite={isFav} onToggleFavorite={() => handleToggleFavorite(rec)} />;
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      <nav className="bottom-nav">
        <a href="#" className={`bottom-nav__link ${mode === 'ai' ? 'bottom-nav__link--active' : ''}`} onClick={(e) => {e.preventDefault(); setMode('ai');}}>
          <span className="material-symbols-outlined">smart_toy</span>
          <span className="bottom-nav__label">AI</span>
        </a>
        <a href="#" className={`bottom-nav__link ${mode === 'filter' ? 'bottom-nav__link--active' : ''}`} onClick={(e) => {e.preventDefault(); setMode('filter');}}>
          <span className="material-symbols-outlined">tune</span>
          <span className="bottom-nav__label">Filter</span>
        </a>
      </nav>

      <LoadingOverlay isLoading={isLoading} />
    </>
  );
}
