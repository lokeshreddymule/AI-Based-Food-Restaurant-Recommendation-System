import React, { useRef } from 'react';
import './RestaurantList.css';

function RestaurantList({ restaurants, area }) {
  const scrollRef = useRef(null);

  if (!restaurants || restaurants.length === 0) {
    return (
      <div className="restaurant-list">
        <div className="no-results">
          <span className="no-results-emoji">😔</span>
          <p>No restaurants found matching your criteria.</p>
          <p>Try adjusting your budget or area.</p>
        </div>
      </div>
    );
  }

  const topPick    = restaurants[0];
  const remaining  = restaurants.slice(1);

  const scroll = (dir) => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: dir * 340, behavior: 'smooth' });
    }
  };

  const getSpicyBadge = (level) => {
    const map = {
      High:   { label: '🌶️🌶️🌶️ Very Spicy', cls: 'spicy-high' },
      Medium: { label: '🌶️🌶️ Medium',        cls: 'spicy-med'  },
      Low:    { label: '🌿 Mild',             cls: 'spicy-low'  },
    };
    return map[level] || map['Medium'];
  };

  const getFoodIcon = (type) => {
    if (type === 'Veg')     return '🥗';
    if (type === 'Non-Veg') return '🍗';
    return '🍽️';
  };

  const getScoreColor = (score) => {
    if (score >= 0.80) return '#22c55e';
    if (score >= 0.65) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="restaurant-list">

      {/* ── Page Title ─────────────────────────────────────────────── */}
      <div className="results-header">
        <h2>🏆 AI-Ranked Restaurants</h2>
        <p className="results-subtitle">
          {area
            ? <>Found <strong>{restaurants.length}</strong> restaurants in <strong>{area}</strong></>
            : <>Found <strong>{restaurants.length}</strong> restaurants matching your preferences</>
          }
        </p>
      </div>

      {/* ══════════════════════════════════════════════════════════════
          TOP PICK — Full-width hero card
      ══════════════════════════════════════════════════════════════ */}
      <div className="top-pick-section">
        <div className="top-pick-label">
          <span className="crown">👑</span> AI Top Pick
        </div>

        <div className="hero-card">
          {/* Left: main info */}
          <div className="hero-left">
            <div className="hero-rank-badge">#1 Best Match</div>

            <h3 className="hero-name">{topPick.name}</h3>
            <p className="hero-address">📍 {topPick.address}</p>

            {topPick.famous_for && (
              <p className="hero-famous">⭐ {topPick.famous_for}</p>
            )}

            {topPick.best_dish && (
              <div className="hero-dish">
                🍴 Best Dish: <strong>{topPick.best_dish}</strong>
              </div>
            )}

            <p className="hero-cuisine">{topPick.cuisine}</p>

            {/* Tags */}
            <div className="hero-tags">
              <span className={`spicy-tag ${getSpicyBadge(topPick.spicy_level).cls}`}>
                {getSpicyBadge(topPick.spicy_level).label}
              </span>
              <span className="food-type-tag">
                {getFoodIcon(topPick.food_type)} {topPick.food_type}
              </span>
              <span className={`open-tag ${topPick.is_open ? 'open' : 'closed'}`}>
                {topPick.is_open ? '🟢 Open Now' : '🔴 Closed'}
              </span>
            </div>

            {/* Timing */}
            {topPick.opening_time && (
              <p className="hero-timing">
                🕐 {topPick.opening_time} – {topPick.closing_time}
              </p>
            )}
          </div>

          {/* Right: stats + CTA */}
          <div className="hero-right">
            <div
              className="hero-score-ring"
              style={{ '--score-color': getScoreColor(topPick.ai_score) }}
            >
              <span className="score-number">{topPick.ai_score}</span>
              <span className="score-label">AI Score</span>
            </div>

            <div className="hero-stats">
              <div className="stat-box">
                <span className="stat-icon">⭐</span>
                <span className="stat-value">{topPick.rating}</span>
                <span className="stat-name">Rating</span>
              </div>
              <div className="stat-box">
                <span className="stat-icon">📏</span>
                <span className="stat-value">{topPick.distance_km}</span>
                <span className="stat-name">Distance</span>
              </div>
              <div className="stat-box">
                <span className="stat-icon">💰</span>
                <span className="stat-value">{topPick.price_range}</span>
                <span className="stat-name">Price</span>
              </div>
              <div className="stat-box">
                <span className="stat-icon">👥</span>
                <span className="stat-value">{topPick.votes?.toLocaleString()}</span>
                <span className="stat-name">Reviews</span>
              </div>
            </div>

            <a
              href={topPick.map_link || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(topPick.name + ' Hyderabad')}`}
              target="_blank"
              rel="noreferrer"
              className="hero-map-btn"
            >
              📱 View on Google Maps
            </a>
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════════
          REMAINING — Horizontal scroll row
      ══════════════════════════════════════════════════════════════ */}
      {remaining.length > 0 && (
        <div className="more-section">
          <div className="more-header">
            <div className="more-title-group">
              <h3 className="more-title">
                More Restaurants in {area || 'This Area'}
              </h3>
              <p className="more-subtitle">
                {remaining.length} more option{remaining.length !== 1 ? 's' : ''} — scroll to explore →
              </p>
            </div>
            <div className="scroll-arrows">
              <button className="arrow-btn" onClick={() => scroll(-1)} aria-label="Scroll left">‹</button>
              <button className="arrow-btn" onClick={() => scroll(1)}  aria-label="Scroll right">›</button>
            </div>
          </div>

          <div className="scroll-track" ref={scrollRef}>
            {remaining.map((r, i) => {
              const spicy = getSpicyBadge(r.spicy_level);
              return (
                <div key={i} className="mini-card">
                  {/* Rank badge */}
                  <div className="mini-rank">#{i + 2}</div>

                  {/* Score pill */}
                  <div
                    className="mini-score"
                    style={{ background: getScoreColor(r.ai_score) }}
                  >
                    {r.ai_score}
                  </div>

                  <h4 className="mini-name">{r.name}</h4>
                  <p className="mini-address">📍 {r.address}</p>

                  {r.best_dish && (
                    <p className="mini-dish">🍴 {r.best_dish}</p>
                  )}

                  {/* Mini stats */}
                  <div className="mini-stats">
                    <span>⭐ {r.rating}</span>
                    <span>💰 {r.price_range}</span>
                    <span>📏 {r.distance_km}</span>
                  </div>

                  {/* Tags */}
                  <div className="mini-tags">
                    <span className={`spicy-tag ${spicy.cls}`}>{spicy.label}</span>
                    <span className={`open-tag ${r.is_open ? 'open' : 'closed'}`}>
                      {r.is_open ? '🟢 Open' : '🔴 Closed'}
                    </span>
                  </div>

                  {/* Timing */}
                  {r.opening_time && (
                    <p className="mini-timing">
                      🕐 {r.opening_time} – {r.closing_time}
                    </p>
                  )}

                  <a
                    href={r.map_link || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(r.name + ' Hyderabad')}`}
                    target="_blank"
                    rel="noreferrer"
                    className="mini-map-btn"
                  >
                    📱 View on Maps
                  </a>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default RestaurantList;
