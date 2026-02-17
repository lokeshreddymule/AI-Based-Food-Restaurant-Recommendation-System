import React, { useState } from 'react';
import './CitySearch.css';

function CitySearch({ onSearch }) {
  const [city, setCity] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (city.trim()) {
      onSearch(city.trim());
    }
  };

  const popularCities = [
    'Hyderabad', 'Mumbai', 'Delhi', 'Bangalore',
    'Chennai', 'Kolkata', 'Pune', 'Ahmedabad'
  ];

  return (
    <section className="city-search">
      <div className="search-card">
        
        {/* Title */}
        <h2>Enter Your City</h2>
        <p>Find the best food and restaurants near you</p>

        {/* Search */}
        <form onSubmit={handleSubmit}>
          <div className="search-input-group">
            <input
              type="text"
              placeholder="e.g. Hyderabad, Mumbai, Delhi..."
              value={city}
              onChange={(e) => setCity(e.target.value)}
              required
            />
            <button type="submit" className="search-btn">
              Search
            </button>
          </div>
        </form>

        {/* Popular */}
        <div className="popular-cities">
          <p>POPULAR CITIES</p>
          <div className="city-tags">
            {popularCities.map((cityName) => (
              <span
                key={cityName}
                className="city-tag"
                onClick={() => setCity(cityName)}
              >
                {cityName}
              </span>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
}

export default CitySearch;
