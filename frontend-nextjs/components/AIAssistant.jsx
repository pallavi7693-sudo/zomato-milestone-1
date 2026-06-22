"use client";
import { useState } from 'react';
import { fetchAIRecommendations } from '../utils/api';
import RestaurantCard from './RestaurantCard';

export default function AIAssistant({ setIsLoading, onAddToHistory, favorites = [], onToggleFavorite }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setIsLoading(true);
    try {
      const data = await fetchAIRecommendations(query);
      if (data.error) {
        setResults({ recommendations: [], summary: `Error: ${data.error}` });
      } else {
        setResults(data);
        if (onAddToHistory && data.recommendations?.length > 0) {
          onAddToHistory(query, data.recommendations);
        }
      }
    } catch (e) {
      console.error(e);
      setResults({ recommendations: [], summary: "Failed to connect to the server. Please try again." });
    } finally {
      setIsLoading(false);
    }
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
        {(results.relaxation_applied || results.location_relaxed) && (
          <div className="alert-box alert-warning" style={{marginBottom: 16, padding: 16, backgroundColor: '#332b00', color: '#ffcc00', borderRadius: 12, display: 'flex', gap: 12, alignItems: 'center'}}>
            <span className="material-symbols-outlined">warning</span>
            <div style={{ margin: 0, fontSize: '14px', lineHeight: '1.5' }}>
              <p style={{ margin: 0, fontWeight: '500' }}>We dynamically relaxed some constraints to find the best alternatives:</p>
              <ul style={{ margin: '8px 0 0 20px', padding: 0 }}>
                {results.original_constraints?.min_rating > results.final_constraints?.min_rating && (
                  <li><strong>Rating</strong>: Relaxed from {results.original_constraints.min_rating}+ to {results.final_constraints.min_rating}+</li>
                )}
                {results.original_constraints?.max_budget < results.final_constraints?.max_budget && (
                  <li><strong>Budget</strong>: Expanded maximum from ₹{results.original_constraints.max_budget} to ₹{results.final_constraints.max_budget}</li>
                )}
                {results.location_relaxed && results.searched_locations?.length > 1 && (
                  <li><strong>Location</strong>: Expanded search from {results.original_constraints?.location || 'your area'} to nearby areas ({results.searched_locations.slice(1).join(', ')})</li>
                )}
              </ul>
            </div>
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
          {results.recommendations?.map((rec, i) => {
            const isFav = favorites.some(f => f.restaurant_name === rec.restaurant_name);
            return <RestaurantCard key={i} rec={rec} index={i} isFavorite={isFav} onToggleFavorite={() => onToggleFavorite(rec)} />;
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="ai-assistant-view">
      <div className="ai-hero">
        <span className="material-symbols-outlined ai-hero__icon">restaurant</span>
        <h1 className="text-display-lg ai-hero__title">Discover the perfect restaurant</h1>
        <p className="text-body-lg ai-hero__subtitle">Describe what you're craving. Our AI understands taste, budget, vibe, and location to find exactly what you need.</p>
      </div>

      <div className="ai-input-container">
        <div className="ai-input-box">
          <textarea 
            placeholder="e.g., I want a romantic Italian place in Koramangala with a great ambiance..." 
            rows="3"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSearch();
              }
            }}
          ></textarea>
          <div className="ai-input-box__actions">
            <div className="ai-input-box__tools">
              <button className="ai-tool-btn" title="Use Voice">
                <span className="material-symbols-outlined">mic</span>
              </button>
              <button className="ai-tool-btn" title="Upload Image">
                <span className="material-symbols-outlined">image</span>
              </button>
            </div>
            <button className="btn-primary" onClick={handleSearch}>
              <span className="material-symbols-outlined">auto_awesome</span>
              Ask AI
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
