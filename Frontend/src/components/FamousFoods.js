import React from 'react';
import './FamousFoods.css';

function FamousFoods({ city, foods }) {
  const foodEmojis = {
    'Biryani': '🍛',
    'Pizza': '🍕',
    'Burger': '🍔',
    'Chinese': '🥡',
    'North Indian': '🍲',
    'South Indian': '🥘',
    'Desserts': '🍰',
    'Cafe': '☕',
    'Italian': '🍝',
    'Thai': '🍜',
    'Continental': '🍽️',
    'default': '🍴'
  };

  const getEmoji = (cuisine) => {
    return foodEmojis[cuisine] || foodEmojis['default'];
  };

  return (
    <div className="famous-foods">
      <h2>🌟 Famous Foods in {city}</h2>
      <p className="subtitle">Popular cuisines based on ratings and frequency</p>
      
      <div className="food-grid">
        {foods.map((food, index) => (
          <div key={index} className="food-card">
            <div className="food-emoji">{getEmoji(food.name)}</div>
            <h3>{food.name}</h3>
            <div className="popularity">
              <span className="popularity-bar">
                <span 
                  className="popularity-fill"
                  style={{ width: `${Math.min(food.popularity_score / 10, 100)}%` }}
                ></span>
              </span>
              <span className="popularity-score">
                Score: {food.popularity_score.toFixed(0)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {foods.length === 0 && (
        <p className="no-data">No famous foods data available for this city</p>
      )}
    </div>
  );
}

export default FamousFoods;
