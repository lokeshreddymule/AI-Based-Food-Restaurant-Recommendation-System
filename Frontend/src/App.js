import React, { useState } from 'react';
import CitySearch from './components/CitySearch';
import FamousFoods from './components/FamousFoods';
import PreferenceForm from './components/PreferenceForm';
import RestaurantList from './components/RestaurantList';
import './App.css';

const API_URL = 'https://ai-based-food-restaurant-recommendation.onrender.com';

function App() {
  const [step, setStep]             = useState(1);
  const [cityData, setCityData]     = useState(null);
  const [restaurants, setRestaurants] = useState([]);
  const [selectedArea, setSelectedArea] = useState('');
  const [loading, setLoading]       = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('Loading...');

  /* ── toast ── */
  const showToast = (message, type = 'success') => {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
      position:fixed; top:24px; right:24px; z-index:9999;
      padding:1rem 1.8rem; border-radius:16px; font-weight:600;
      font-family:'Poppins',sans-serif; font-size:1rem; color:#fff;
      backdrop-filter:blur(20px);
      background:${type === 'success' ? 'rgba(34,197,94,0.35)' : 'rgba(239,68,68,0.35)'};
      border:1px solid ${type === 'success' ? 'rgba(34,197,94,0.5)' : 'rgba(239,68,68,0.5)'};
      box-shadow:0 8px 32px rgba(0,0,0,0.2);
      animation:toastIn 0.4s ease-out;
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'toastOut 0.4s ease-in forwards';
      setTimeout(() => document.body.removeChild(toast), 400);
    }, 3500);
  };

  /* ── Step 1: city search ── */
  const handleCitySearch = async (cityName) => {
    setLoadingMsg('Searching city & detecting famous foods...');
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/city/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city: cityName }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'City not found');
      }
      const data = await res.json();
      setCityData(data);
      setStep(2);
      showToast(`🌟 Found ${data.total_restaurants} restaurants in ${data.city}!`);
    } catch (err) {
      showToast('❌ ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  /* ── Step 2: get recommendations ── */
  const handleGetRecommendations = async (preferences) => {
    setLoadingMsg('AI is ranking the best restaurants for you...');
    setLoading(true);
    setSelectedArea(preferences.area || '');
    try {
      const res = await fetch(`${API_URL}/api/restaurants/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city: cityData.city, ...preferences }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Error fetching recommendations');
      }
      const data = await res.json();
      setRestaurants(data);
      setStep(3);
      showToast(`🎉 Found ${data.length} restaurants${preferences.area ? ' in ' + preferences.area : ''}!`);
    } catch (err) {
      showToast('❌ ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  /* ── Reset ── */
  const handleReset = () => {
    setStep(1);
    setCityData(null);
    setRestaurants([]);
    setSelectedArea('');
  };

  return (
    <div className="App">
      <style>{`
        @keyframes toastIn  { from{opacity:0;transform:translateX(80px)} to{opacity:1;transform:translateX(0)} }
        @keyframes toastOut { from{opacity:1;transform:translateX(0)} to{opacity:0;transform:translateX(80px)} }
      `}</style>

      <header className="app-header">
        <h1>🍽️ AI Food Finder</h1>
        <p>Discover the best restaurants in your city</p>
      </header>

      <div className="app-container">

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>{loadingMsg}</p>
          </div>
        )}

        {step === 1 && !loading && (
          <CitySearch onSearch={handleCitySearch} />
        )}

        {step === 2 && !loading && cityData && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <FamousFoods city={cityData.city} foods={cityData.famous_foods} />
            <PreferenceForm
              city={cityData.city}
              onSubmit={handleGetRecommendations}
            />
          </div>
        )}

        {step === 3 && !loading && restaurants.length > 0 && (
          <div>
            {/* Pass area so RestaurantList can show "More in Banjara Hills" */}
            <RestaurantList
              restaurants={restaurants}
              area={selectedArea}
            />
            <div style={{ textAlign: 'center' }}>
              <button className="reset-btn" onClick={handleReset}>
                🔄 Search Another City
              </button>
            </div>
          </div>
        )}

      </div>

      <footer className="app-footer">
        <p> Created by MLR • Google Places </p>
      </footer>
    </div>
  );
}

export default App;
