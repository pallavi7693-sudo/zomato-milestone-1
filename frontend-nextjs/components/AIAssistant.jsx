"use client";
import { useState } from 'react';
import { fetchAIRecommendations } from '../utils/api';
import RestaurantCard from './RestaurantCard';

export default function AIAssistant({ setIsLoading }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setIsLoading(true);
    const data = await fetchAIRecommendations(query);
    setResults(data);
    setIsLoading(false);
  };

  if (results) {
    return (
      <div className="view-section">
        <button className="chip" style={{marginBottom: 24}} onClick={() => setResults(null)}>
          <span className="material-symbols-outlined" style={{fontSize: 16}}>arrow_back</span> New Search
        </button>
        {results.summary && (
          <div className="summary-box">
            <span className="material-symbols-outlined">auto_awesome</span>
            <span>{results.summary}</span>
          </div>
        )}
        <div className="results-header">
          <div>
            <h2 className="text-headline-md results-header__title">AI Recommendations</h2>
            <p className="results-header__subtitle">
              <span className="material-symbols-outlined">auto_awesome</span>
              {results.recommendations?.length || 0} matches found.
            </p>
          </div>
        </div>
        <div className="results-grid">
          {results.recommendations?.map((rec, i) => (
            <RestaurantCard key={i} rec={rec} index={i} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="view-section">
      <div className="hero-section">
        <h1 className="hero-title">Discover the perfect restaurant</h1>
        <p className="hero-subtitle">Describe what you're craving. Our AI understands taste, budget, vibe, and location to find exactly what you need.</p>
        <div className="search-bar">
          <span className="material-symbols-outlined search-bar__icon">search</span>
          <input 
            type="text" 
            className="search-bar__input" 
            placeholder="e.g. 'Cozy cafe in Indiranagar under Rs. 1000'" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button className="btn-primary search-bar__btn" onClick={handleSearch}>Ask AI</button>
        </div>
      </div>
    </div>
  );
}
