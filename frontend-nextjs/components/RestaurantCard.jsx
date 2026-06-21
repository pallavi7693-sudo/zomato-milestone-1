export default function RestaurantCard({ rec, index }) {
  const rating = rec.rating || 0;
  const matchScore = rec.match_score || 0;
  const cuisines = rec.cuisines || '';
  const cost = rec.cost || 0;
  const reason = rec.reason || '';
  const name = rec.restaurant_name || 'Unknown';
  const restType = rec.restaurant_type || '';

  const cuisineArr = cuisines.split(',').map((c) => c.trim()).filter(Boolean).slice(0, 3);
  const typeArr = restType.split(',').map((t) => t.trim()).filter(Boolean).slice(0, 1);
  const allTags = [...cuisineArr, ...typeArr];
  if (cost > 0) allTags.push(`₹${cost} for two`);

  const gradientClass = `card-gradient-${(index % 5) + 1}`;

  return (
    <div className="restaurant-card">
      <div className="card-image">
        <div className={`card-image__gradient ${gradientClass}`}>
          <span className="material-symbols-outlined">restaurant</span>
        </div>
        <div className="card-image__overlay"></div>
        {rating > 0 && (
          <div className="card-rating-badge">
            <span className="card-rating-badge__value">{rating.toFixed(1)}</span>
            <span className="material-symbols-outlined">star</span>
          </div>
        )}
      </div>
      <div className="card-body">
        <div className="card-body__header">
          <h3 className="card-body__name">{name}</h3>
          <div className="match-score-pill">
            <span className="material-symbols-outlined">target</span>
            <span className="match-score-pill__value">{matchScore}% Match</span>
          </div>
        </div>
        <div className="card-tags">
          {allTags.map((t, i) => (
            <span key={i} className="card-tag">{t}</span>
          ))}
        </div>
        {reason && (
          <div className="card-reasoning">
            <span className="material-symbols-outlined">auto_awesome</span>
            <p className="card-reasoning__text">{reason}</p>
          </div>
        )}
      </div>
    </div>
  );
}
