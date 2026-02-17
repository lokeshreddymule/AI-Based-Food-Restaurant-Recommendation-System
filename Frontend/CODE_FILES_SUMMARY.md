# 📝 ALL CODE FILES - Quick Reference

This document shows you exactly where each file goes and what it contains.

---

## 📁 **PROJECT STRUCTURE**

```
food-recommendation-system/
│
├── backend/                          ← Python/FastAPI Backend
│   ├── main.py                       ← 500+ lines - Main API with AI ranking
│   ├── import_data.py                ← 150+ lines - Database import script
│   ├── requirements.txt              ← Python dependencies
│   └── .env.example                  ← Environment variables template
│
├── frontend/                         ← React Frontend
│   ├── package.json                  ← Node.js dependencies
│   │
│   ├── public/
│   │   └── index.html                ← HTML template
│   │
│   └── src/
│       ├── index.js                  ← React entry point
│       ├── index.css                 ← Global styles
│       ├── App.js                    ← Main React app (200+ lines)
│       ├── App.css                   ← Main app styles
│       │
│       └── components/
│           ├── CitySearch.js         ← City search component
│           ├── CitySearch.css        ← City search styles
│           ├── FamousFoods.js        ← Famous foods component
│           ├── FamousFoods.css       ← Famous foods styles
│           ├── PreferenceForm.js     ← User preferences component
│           ├── PreferenceForm.css    ← Preferences styles
│           ├── RestaurantList.js     ← Results component
│           └── RestaurantList.css    ← Results styles
│
├── README.md                         ← Full documentation
├── SETUP_CHECKLIST.md                ← Step-by-step setup
├── WHAT_YOU_NEED_TO_DO.md            ← Quick start guide
└── .gitignore                        ← Git ignore file
```

---

## 🐍 **BACKEND FILES**

### 1. `backend/main.py` (500+ lines)

**What it does:**
- FastAPI web server
- 2 main API endpoints
- AI ranking algorithm
- Google Places integration
- Database queries

**Key Functions:**
```python
def get_famous_foods()          # AI: Find popular foods per city
def filter_by_taste()            # AI: Map preferences to cuisines
def calculate_ai_score()         # AI: Multi-factor ranking
def get_google_places_data()    # Fetch live data from Google
```

**Endpoints:**
- `POST /api/city/search` - Returns famous foods
- `POST /api/restaurants/recommend` - Returns AI-ranked restaurants

---

### 2. `backend/import_data.py` (150+ lines)

**What it does:**
- Reads Zomato CSV file
- Cleans and transforms data
- Imports into MongoDB
- Creates database indexes

**Usage:**
```bash
python import_data.py
# Then enter path to zomato.csv
```

---

### 3. `backend/requirements.txt`

**Python packages needed:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pymongo==4.6.0
geopy==2.4.0
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.0
python-multipart==0.0.6
```

**Install with:**
```bash
pip install -r requirements.txt
```

---

### 4. `backend/.env.example`

**Environment variables template:**
```
MONGODB_URI=mongodb://localhost:27017/
GOOGLE_API_KEY=your_google_api_key_here
```

**Setup:**
```bash
cp .env.example .env
# Edit .env and add your actual Google API key
```

---

## ⚛️ **FRONTEND FILES**

### 5. `frontend/package.json`

**Node.js dependencies:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0"
  }
}
```

**Install with:**
```bash
npm install
```

---

### 6. `frontend/public/index.html`

**HTML template:**
- Minimal HTML structure
- React root div
- Meta tags for SEO

---

### 7. `frontend/src/index.js`

**React entry point:**
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

---

### 8. `frontend/src/App.js` (200+ lines)

**Main React application:**

**What it does:**
- Manages 3 steps of user flow
- Handles API calls to backend
- State management
- Component orchestration

**Components used:**
- CitySearch
- FamousFoods
- PreferenceForm
- RestaurantList

**State:**
```javascript
- step (1, 2, or 3)
- cityData (famous foods)
- restaurants (AI-ranked results)
- loading, error
```

---

### 9. `frontend/src/components/CitySearch.js` (50+ lines)

**City search component:**
- Input field for city name
- Popular cities quick select
- Search button
- Calls `/api/city/search`

---

### 10. `frontend/src/components/FamousFoods.js` (50+ lines)

**Famous foods display component:**
- Shows popular cuisines
- Displays popularity scores
- Visual food cards with emojis
- Responsive grid layout

---

### 11. `frontend/src/components/PreferenceForm.js` (150+ lines)

**User preferences component:**
- Location input (manual or GPS)
- Taste preference (Spicy/Normal)
- Budget range sliders
- Form validation
- Calls `/api/restaurants/recommend`

---

### 12. `frontend/src/components/RestaurantList.js` (100+ lines)

**AI-ranked results component:**
- Displays top 10 restaurants
- Shows AI score, rating, distance
- Open/Closed status
- Google Maps links
- Medal rankings (🥇🥈🥉)

---

## 🎨 **CSS FILES**

All CSS files provide:
- Professional styling
- Responsive design
- Gradient backgrounds
- Smooth animations
- Mobile-friendly layout

**Files:**
- `App.css` - Main app layout
- `CitySearch.css` - Search interface
- `FamousFoods.css` - Food cards
- `PreferenceForm.css` - Form styling
- `RestaurantList.css` - Results cards

---

## 📄 **DOCUMENTATION FILES**

### README.md
- Complete project overview
- Feature list
- Installation guide
- API documentation
- Troubleshooting

### SETUP_CHECKLIST.md
- Step-by-step setup instructions
- Command reference
- Error solutions

### WHAT_YOU_NEED_TO_DO.md
- Quick start guide
- Summary of required steps
- Time estimates

---

## 🔢 **CODE STATISTICS**

**Backend:**
- Lines of Python code: ~700
- API endpoints: 2
- AI functions: 4
- Database operations: Multiple

**Frontend:**
- Lines of JavaScript: ~600
- React components: 4
- CSS files: 6
- Total styling: ~800 lines

**Total Project:**
- ~2,100+ lines of code
- 19 files
- Full-stack application

---

## 🚀 **HOW TO USE THESE FILES**

### Method 1: Download All Files
1. Download the entire `food-recommendation-system` folder
2. Extract to your computer
3. Follow SETUP_CHECKLIST.md

### Method 2: Copy Files Manually
1. Create the folder structure shown above
2. Copy each file content to the correct location
3. Install dependencies
4. Run the app

### Method 3: Clone from Git (if using version control)
1. Initialize git in the folder
2. Commit all files
3. Push to your repository

---

## 🎯 **KEY CODE HIGHLIGHTS**

### AI Ranking Algorithm (backend/main.py)
```python
def calculate_ai_score(restaurant, user_request):
    rating_score = restaurant.rating / 5.0
    distance_score = 1 - (restaurant.distance_km / 10)
    budget_score = calculate_budget_match()
    taste_score = 1.0
    
    final_score = (
        0.35 * rating_score +
        0.30 * distance_score +
        0.20 * budget_score +
        0.15 * taste_score
    )
    return final_score
```

### Famous Foods Detection (backend/main.py)
```python
def get_famous_foods(city):
    # MongoDB aggregation pipeline
    # Groups by cuisine, counts frequency
    # Weights by average rating
    # Returns top 7 foods
```

### React State Flow (frontend/src/App.js)
```javascript
Step 1: City Search → cityData
Step 2: Preferences Form → restaurants
Step 3: Display Results
```

---

## ✅ **FILES CHECKLIST**

Use this to verify you have all files:

**Backend:**
- [ ] main.py
- [ ] import_data.py
- [ ] requirements.txt
- [ ] .env.example

**Frontend:**
- [ ] package.json
- [ ] public/index.html
- [ ] src/index.js
- [ ] src/index.css
- [ ] src/App.js
- [ ] src/App.css
- [ ] src/components/CitySearch.js
- [ ] src/components/CitySearch.css
- [ ] src/components/FamousFoods.js
- [ ] src/components/FamousFoods.css
- [ ] src/components/PreferenceForm.js
- [ ] src/components/PreferenceForm.css
- [ ] src/components/RestaurantList.js
- [ ] src/components/RestaurantList.css

**Documentation:**
- [ ] README.md
- [ ] SETUP_CHECKLIST.md
- [ ] WHAT_YOU_NEED_TO_DO.md
- [ ] .gitignore

**Total: 22 files** ✅

---

## 🎓 **UNDERSTANDING THE CODE**

### Backend Flow:
1. User enters city → `search_city()` endpoint
2. Query MongoDB → Find restaurants in city
3. Run aggregation → Get famous foods
4. Return results → Frontend displays

5. User sets preferences → `recommend_restaurants()` endpoint
6. Filter by budget, taste → Apply AI ranking
7. Calculate distances → Sort by score
8. Enrich with Google data → Return top 10

### Frontend Flow:
1. App.js manages state
2. CitySearch captures city
3. FamousFoods displays data
4. PreferenceForm collects inputs
5. RestaurantList shows results

---

**All code files are ready to use! Just download and follow the setup guide.** 🚀
