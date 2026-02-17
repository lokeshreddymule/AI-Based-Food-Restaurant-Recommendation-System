import React, { useState, useEffect } from 'react';
import './PreferenceForm.css';

const API_URL = 'http://localhost:8000';

function PreferenceForm({ onSubmit, city }) {
  const [preferences, setPreferences] = useState({
    area: '',
    latitude: 0,
    longitude: 0,
    taste_preference: 'spicy',
    budget_min: 200,
    budget_max: 2000,
  });

  const [areas, setAreas]                   = useState([]);
  const [loadingAreas, setLoadingAreas]     = useState(false);
  const [locationCaptured, setLocationCaptured] = useState(false);
  const [areaError, setAreaError]           = useState('');

  // ── Fetch areas for selected city ──────────────────────────────────────
  useEffect(() => {
    const fetchAreas = async () => {
      setLoadingAreas(true);
      try {
        const cityName = city || 'Hyderabad';
        const res  = await fetch(`${API_URL}/api/areas?city=${encodeURIComponent(cityName)}`);
        const data = await res.json();
        setAreas(data.areas || []);
      } catch (err) {
        console.error('Failed to load areas:', err);
        // Fallback — hardcoded Hyderabad areas
        setAreas([
          'Banjara Hills',
          'Jubilee Hills',
          'Gachibowli',
          'Hitech City',
          'Madhapur',
          'Charminar',
          'Secunderabad',
          'Kukatpally',
          'Begumpet',
        ]);
      } finally {
        setLoadingAreas(false);
      }
    };

    fetchAreas();
  }, [city]);

  // ── GPS location ────────────────────────────────────────────────────────
  const handleGetLocation = () => {
    if (!navigator.geolocation) {
      alert('❌ Geolocation not supported by your browser');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setPreferences((prev) => ({
          ...prev,
          latitude:  pos.coords.latitude,
          longitude: pos.coords.longitude,
        }));
        setLocationCaptured(true);
      },
      () => {
        alert('❌ Could not get location. Please select your area from the dropdown.');
      }
    );
  };

  // ── Submit ───────────────────────────────────────────────────────────────
  const handleSubmit = (e) => {
    e.preventDefault();

    if (!preferences.area) {
      setAreaError('Please select your area from the dropdown.');
      return;
    }
    setAreaError('');
    onSubmit(preferences);
  };

  return (
    <div className="preference-form">
      <h2>📍 Set Your Preferences</h2>

      <form onSubmit={handleSubmit}>

        {/* ── Area Dropdown ──────────────────────────────────────────── */}
        <div className="form-section">
          <label>📍 Select Your Area:</label>

          <div className="location-group">
            {/* DROPDOWN — always exact match with DB */}
            <select
              className="area-select"
              value={preferences.area}
              onChange={(e) => {
                setPreferences({ ...preferences, area: e.target.value });
                setAreaError('');
              }}
            >
              <option value="">
                {loadingAreas ? 'Loading areas...' : '-- Select Area --'}
              </option>
              {areas.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>

            {/* Optional GPS button */}
            <button
              type="button"
              onClick={handleGetLocation}
              className={`location-btn ${locationCaptured ? 'captured' : ''}`}
            >
              {locationCaptured ? '✅ GPS On' : '📍 Use GPS'}
            </button>
          </div>

          {areaError && (
            <p style={{ color: '#ff6b6b', fontSize: '0.9rem', marginTop: '0.5rem' }}>
              ⚠️ {areaError}
            </p>
          )}

          {locationCaptured && (
            <small style={{ color: 'rgba(255,255,255,0.9)' }}>
              ✅ GPS location captured — distances will be calculated
            </small>
          )}

          {!locationCaptured && preferences.area && (
            <small>
              Showing restaurants in <strong>{preferences.area}</strong>
              {' '}— enable GPS for accurate distances
            </small>
          )}
        </div>

        {/* ── Taste Preference ──────────────────────────────────────── */}
        <div className="form-section">
          <label>🌶️ Taste Preference:</label>
          <div className="radio-group">

            <label className={`radio-card ${preferences.taste_preference === 'spicy' ? 'selected' : ''}`}>
              <input
                type="radio"
                value="spicy"
                checked={preferences.taste_preference === 'spicy'}
                onChange={(e) => setPreferences({ ...preferences, taste_preference: e.target.value })}
              />
              <span className="radio-icon">🌶️</span>
              <div className="radio-text">
                <strong>Spicy</strong>
                <small>Biryani, Kebabs, Andhra, Chinese</small>
              </div>
            </label>

            <label className={`radio-card ${preferences.taste_preference === 'normal' ? 'selected' : ''}`}>
              <input
                type="radio"
                value="normal"
                checked={preferences.taste_preference === 'normal'}
                onChange={(e) => setPreferences({ ...preferences, taste_preference: e.target.value })}
              />
              <span className="radio-icon">🥘</span>
              <div className="radio-text">
                <strong>Normal / Mild</strong>
                <small>South Indian, Continental, Cafe</small>
              </div>
            </label>

          </div>
        </div>

        {/* ── Budget ────────────────────────────────────────────────── */}
        <div className="form-section">
          <label>💰 Budget (Cost for Two):</label>

          <div className="budget-display">
            <span className="budget-value">₹{preferences.budget_min}</span>
            <span className="budget-separator">to</span>
            <span className="budget-value">₹{preferences.budget_max}</span>
          </div>

          <div className="slider-group">
            <div className="slider-container">
              <label>Min: ₹{preferences.budget_min}</label>
              <input
                type="range"
                min="100"
                max="2000"
                step="100"
                value={preferences.budget_min}
                onChange={(e) =>
                  setPreferences({ ...preferences, budget_min: parseInt(e.target.value) })
                }
              />
            </div>
            <div className="slider-container">
              <label>Max: ₹{preferences.budget_max}</label>
              <input
                type="range"
                min="200"
                max="5000"
                step="100"
                value={preferences.budget_max}
                onChange={(e) =>
                  setPreferences({ ...preferences, budget_max: parseInt(e.target.value) })
                }
              />
            </div>
          </div>
          <small>Average cost for two people including taxes</small>
        </div>

        <button type="submit" className="submit-btn">
          🔍 Find Best Restaurants
        </button>
      </form>
    </div>
  );
}

export default PreferenceForm;
