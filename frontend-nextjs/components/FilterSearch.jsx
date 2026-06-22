"use client";
import RestaurantCard from './RestaurantCard';

export default function FilterSearch({ results, favorites = [], onToggleFavorite }) {
  if (results && results.recommendations) {
    const { relaxation_applied, location_relaxed, searched_locations } = results;

    return (
      <div className="view-section">
        <div className="results-header">
          <div>
            <h2 className="text-headline-md results-header__title">Search Results</h2>
            <p className="results-header__subtitle">
              <span className="material-symbols-outlined">tune</span>
              {results.recommendations.length} matches found.
            </p>
          </div>
        </div>

        {(relaxation_applied || location_relaxed) && (
          <div style={{ backgroundColor: '#332b00', color: '#ffcc00', padding: '16px', borderRadius: '12px', marginBottom: '24px', display: 'flex', gap: '12px', alignItems: 'center' }}>
            <span className="material-symbols-outlined">info</span>
            <div style={{ margin: 0, fontSize: '14px', lineHeight: '1.5' }}>
              <p style={{ margin: 0, fontWeight: '500' }}>We dynamically relaxed some constraints to find the best alternatives:</p>
              <ul style={{ margin: '8px 0 0 20px', padding: 0 }}>
                {results.original_constraints?.min_rating > results.final_constraints?.min_rating && (
                  <li><strong>Rating</strong>: Relaxed from {results.original_constraints.min_rating}+ to {results.final_constraints.min_rating}+</li>
                )}
                {results.original_constraints?.max_budget < results.final_constraints?.max_budget && (
                  <li><strong>Budget</strong>: Expanded maximum from ₹{results.original_constraints.max_budget} to ₹{results.final_constraints.max_budget}</li>
                )}
                {location_relaxed && searched_locations?.length > 1 && (
                  <li><strong>Location</strong>: Expanded search from {results.original_constraints?.location || 'your area'} to nearby areas ({searched_locations.slice(1).join(', ')})</li>
                )}
              </ul>
            </div>
          </div>
        )}

        <div className="results-grid">
          {results.recommendations.length > 0 ? (
            results.recommendations.map((rec, i) => {
              const isFav = favorites.some(f => f.restaurant_name === rec.restaurant_name);
              return <RestaurantCard key={i} rec={rec} index={i} isFavorite={isFav} onToggleFavorite={() => onToggleFavorite(rec)} />;
            })
          ) : (
            <div style={{ gridColumn: '1 / -1', padding: '32px', textAlign: 'center', color: 'var(--on-surface-variant)' }}>
              No restaurants found even after constraint relaxation. Try broadening your criteria.
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="filter-search-view" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div className="filter-initial-state">
        <div className="empty-state" style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <span className="material-symbols-outlined" style={{ fontSize: '64px', color: 'var(--primary)', marginBottom: '16px' }}>tune</span>
          <h3 className="empty-state__title text-headline-md" style={{ color: 'var(--on-surface)', marginBottom: '8px' }}>Configure your filters</h3>
          <p className="empty-state__subtitle text-body-lg" style={{ color: 'var(--on-surface-variant)' }}>Use the filter panel on the left to set your preferences, then click "Search".</p>
        </div>
      </div>
    </div>
  );
}
