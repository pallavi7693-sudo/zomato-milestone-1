"use client";
import { useState, useEffect } from 'react';
import { fetchLocations, fetchCuisines, fetchFilterRecommendations } from '../utils/api';

export default function Sidebar({ mode, setMode, onFilterSearch, setIsLoading, onAddToHistory }) {
  const [locations, setLocations] = useState([]);
  const [cuisines, setCuisines] = useState([]);
  
  const [selectedLoc, setSelectedLoc] = useState('');
  const [selectedCuisines, setSelectedCuisines] = useState([]);
  const [budget, setBudget] = useState(3000);
  const [people, setPeople] = useState(2);
  const [expandedCuisines, setExpandedCuisines] = useState(false);

  const [onlineOrder, setOnlineOrder] = useState(false);
  const [bookTable, setBookTable] = useState(false);

  useEffect(() => {
    fetchLocations().then(l => { setLocations(l); if(l[0]) setSelectedLoc(l[0]); });
    fetchCuisines().then(c => setCuisines(c));
  }, []);

  const handleSearch = async () => {
    setIsLoading(true);
    const data = await fetchFilterRecommendations({
      location: selectedLoc,
      cuisines: selectedCuisines,
      min_rating: 0,
      max_budget: budget,
      num_people: people,
      online_order: onlineOrder,
      book_table: bookTable,
      limit: 9
    });
    onFilterSearch(data);

    if (onAddToHistory && data.recommendations?.length > 0) {
       const queryDesc = `Filter: ${selectedLoc}${selectedCuisines.length ? ' · ' + selectedCuisines.join(', ') : ''} · ₹${budget}`;
       onAddToHistory(queryDesc, data.recommendations);
    }

    setIsLoading(false);
  };

  const handleCuisineToggle = (c) => {
    setSelectedCuisines(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);
  };

  const visibleCuisines = expandedCuisines ? cuisines : cuisines.slice(0, 5);

  return (
    <nav className="sidebar" style={{ overflowY: 'auto' }}>
      {mode === 'filter' ? (
        <div className="filter-panel" style={{ padding: '24px 16px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--on-surface)', margin: 0, fontSize: '20px' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--primary)' }}>tune</span> Filters
            </h2>
            <button className="chip" onClick={() => setMode('ai')} style={{ padding: '4px 8px', fontSize: '12px' }}>Close</button>
          </div>

          <div className="filter-section">
            <h3 className="filter-section__title">Location</h3>
            <div className="gastro-select-wrapper" style={{ marginTop: '8px' }}>
              <span className="material-symbols-outlined icon-left">location_on</span>
              <select className="gastro-select" value={selectedLoc} onChange={e => setSelectedLoc(e.target.value)}>
                {locations.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
              <span className="material-symbols-outlined icon-right">expand_more</span>
            </div>
          </div>

          <div className="filter-section">
            <h3 className="filter-section__title">Options</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
              <label className="gastro-checkbox">
                <input type="checkbox" checked={bookTable} onChange={e => setBookTable(e.target.checked)} />
                <span className="gastro-checkbox__label">Dine-in / Book Table</span>
              </label>
              <label className="gastro-checkbox">
                <input type="checkbox" checked={onlineOrder} onChange={e => setOnlineOrder(e.target.checked)} />
                <span className="gastro-checkbox__label">Online Ordering</span>
              </label>
            </div>
          </div>

          <div className="filter-section">
            <h3 className="filter-section__title">People</h3>
            <div className="people-stepper" style={{ marginTop: '8px' }}>
              <button className="people-stepper__btn" onClick={() => setPeople(Math.max(1, people - 1))}>
                 <span className="material-symbols-outlined">remove</span>
              </button>
              <div className="people-stepper__display">
                  <span className="people-stepper__value">{people}</span>
                  <span className="people-stepper__label">people</span>
              </div>
              <button className="people-stepper__btn" onClick={() => setPeople(Math.min(20, people + 1))}>
                 <span className="material-symbols-outlined">add</span>
              </button>
            </div>
          </div>

          <div className="filter-section">
            <h3 className="filter-section__title" style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Budget (For 2)</span> <span className="budget-value">₹{budget}</span>
            </h3>
            <input type="range" className="gastro-range" min="500" max="10000" step="500" value={budget} onChange={e => setBudget(Number(e.target.value))} />
          </div>

          <div className="filter-section">
            <h3 className="filter-section__title">Cuisines</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
              {visibleCuisines.map(c => (
                <label key={c} className="gastro-checkbox">
                  <input type="checkbox" checked={selectedCuisines.includes(c)} onChange={() => handleCuisineToggle(c)} />
                  <span className="gastro-checkbox__label">{c}</span>
                </label>
              ))}
            </div>
            {cuisines.length > 5 && (
              <button className="show-more-btn" style={{ marginTop: '12px' }} onClick={() => setExpandedCuisines(!expandedCuisines)}>
                {expandedCuisines ? '- Show less' : `+ View ${cuisines.length - 5} more`}
              </button>
            )}
          </div>

          <div className="filter-actions" style={{ marginTop: '16px' }}>
            <button className="filter-search-btn" style={{ width: '100%', padding: '12px', display: 'flex', justifyContent: 'center', gap: '8px', borderRadius: '12px', backgroundColor: 'var(--primary-container)', color: 'var(--on-primary-container)', fontWeight: 'bold' }} onClick={handleSearch}>
              <span className="material-symbols-outlined">search</span> Search
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="sidebar-nav">
            <a 
              href="#" 
              className={`sidebar-nav__link ${mode === 'ai' ? 'sidebar-nav__link--active' : ''}`}
              onClick={(e) => { e.preventDefault(); setMode('ai'); }}
            >
              <span className="material-symbols-outlined">magic_button</span>
              <span>AI Assistant</span>
            </a>
            <a 
              href="#" 
              className={`sidebar-nav__link ${mode === 'filter' ? 'sidebar-nav__link--active' : ''}`}
              onClick={(e) => { e.preventDefault(); setMode('filter'); }}
            >
              <span className="material-symbols-outlined">tune</span>
              <span>Filter Search</span>
            </a>
            <a 
              href="#" 
              className={`sidebar-nav__link ${mode === 'favorites' ? 'sidebar-nav__link--active' : ''}`}
              onClick={(e) => { e.preventDefault(); setMode('favorites'); }}
            >
              <span className="material-symbols-outlined">favorite</span>
              <span>Favorites</span>
            </a>
            <a 
              href="#" 
              className={`sidebar-nav__link ${mode === 'history' ? 'sidebar-nav__link--active' : ''}`}
              onClick={(e) => { e.preventDefault(); setMode('history'); }}
            >
              <span className="material-symbols-outlined">history</span>
              <span>History</span>
            </a>
          </div>
          <div className="sidebar-footer">
            <a href="#" className="sidebar-nav__link" onClick={(e) => e.preventDefault()}>
              <span className="material-symbols-outlined">settings</span>
              <span>Settings</span>
            </a>
          </div>
        </>
      )}
    </nav>
  );
}
