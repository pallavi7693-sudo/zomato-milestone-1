"use client";
import { useState, useEffect } from 'react';
import { fetchLocations, fetchCuisines, fetchFilterRecommendations } from '../utils/api';
import RestaurantCard from './RestaurantCard';

export default function FilterSearch({ setIsLoading }) {
  const [locations, setLocations] = useState([]);
  const [cuisines, setCuisines] = useState([]);
  
  const [selectedLoc, setSelectedLoc] = useState('');
  const [selectedCuisines, setSelectedCuisines] = useState([]);
  const [rating, setRating] = useState(0);
  const [budget, setBudget] = useState(3000);
  const [people, setPeople] = useState(2);
  const [results, setResults] = useState(null);
  const [expandedCuisines, setExpandedCuisines] = useState(false);

  useEffect(() => {
    fetchLocations().then(l => { setLocations(l); if(l[0]) setSelectedLoc(l[0]); });
    fetchCuisines().then(c => setCuisines(c));
  }, []);

  const handleSearch = async () => {
    setIsLoading(true);
    const data = await fetchFilterRecommendations({
      location: selectedLoc,
      cuisines: selectedCuisines,
      min_rating: rating,
      max_budget: budget,
      num_people: people,
      limit: 9
    });
    setResults(data);
    setIsLoading(false);
  };

  const handleCuisineToggle = (c) => {
    setSelectedCuisines(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);
  };

  if (results) {
    return (
      <div className="view-section">
        <button className="chip" style={{marginBottom: 24}} onClick={() => setResults(null)}>
          <span className="material-symbols-outlined" style={{fontSize: 16}}>arrow_back</span> Edit Filters
        </button>
        <div className="results-grid">
          {results.recommendations?.map((rec, i) => (
            <RestaurantCard key={i} rec={rec} index={i} />
          ))}
        </div>
      </div>
    );
  }

  const visibleCuisines = expandedCuisines ? cuisines : cuisines.slice(0, 5);

  return (
    <div className="view-section">
      <div className="hero-section hero-section--compact">
        <h1 className="hero-title">Filter Search</h1>
        <p className="hero-subtitle">Precisely tune your requirements to find the perfect spot.</p>
      </div>
      <div className="filter-grid">
        <div className="filter-section">
          <h3 className="filter-section__title">Location</h3>
          <select className="gastro-input" value={selectedLoc} onChange={e => setSelectedLoc(e.target.value)}>
            {locations.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <div className="filter-section">
          <h3 className="filter-section__title">People</h3>
          <div className="people-stepper">
            <button className="people-stepper__btn" onClick={() => setPeople(Math.max(1, people - 1))}>-</button>
            <span className="people-stepper__value">{people}</span>
            <button className="people-stepper__btn" onClick={() => setPeople(Math.min(20, people + 1))}>+</button>
          </div>
        </div>
        <div className="filter-section">
          <h3 className="filter-section__title">Budget <span className="budget-value">₹0 - ₹{budget}</span></h3>
          <input type="range" className="gastro-slider" min="500" max="10000" step="500" value={budget} onChange={e => setBudget(Number(e.target.value))} />
        </div>
        <div className="filter-section">
          <h3 className="filter-section__title">Cuisines</h3>
          <div className="checkbox-grid">
            {visibleCuisines.map(c => (
              <label key={c} className="gastro-checkbox">
                <input type="checkbox" checked={selectedCuisines.includes(c)} onChange={() => handleCuisineToggle(c)} />
                <span className="gastro-checkbox__label">{c}</span>
              </label>
            ))}
          </div>
          {cuisines.length > 5 && (
            <button className="btn-link" onClick={() => setExpandedCuisines(!expandedCuisines)}>
              {expandedCuisines ? '- Show less' : `+ View ${cuisines.length - 5} more`}
            </button>
          )}
        </div>
      </div>
      <div className="filter-actions" style={{marginTop: 32}}>
        <button className="btn-primary" onClick={handleSearch}>Search Restaurants</button>
      </div>
    </div>
  );
}
