"""
AI-Based Food & Restaurant Recommendation System
FastAPI Backend — DEPLOYMENT READY
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pymongo
from geopy.distance import geodesic
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────────

app = FastAPI(title="AI Food Recommendation API")

# Allow local + deployed frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# DATABASE (ATLAS READY)
# ─────────────────────────────────────────────

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI not set")

client = pymongo.MongoClient(MONGODB_URI)
db = client["food_recommendation"]
restaurants_col = db["restaurants"]

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────

class CityRequest(BaseModel):
    city: str

class RecommendationRequest(BaseModel):
    city: str
    area: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    taste_preference: str = "spicy"
    budget_min: int = 0
    budget_max: int = 99999

# ─────────────────────────────────────────────
# CITY SEARCH
# ─────────────────────────────────────────────

@app.post("/api/city/search")
async def search_city(request: CityRequest):
    city = request.city.strip().title()

    city_exists = restaurants_col.find_one({"city": city})
    if not city_exists:
        city_exists = restaurants_col.find_one(
            {"city": {"$regex": f"^{request.city.strip()}$", "$options": "i"}}
        )
        if city_exists:
            city = city_exists["city"]
        else:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")

    famous_foods = get_famous_foods(city)
    total = restaurants_col.count_documents({"city": city})
    return {"city": city, "famous_foods": famous_foods, "total_restaurants": total}

def get_famous_foods(city: str) -> List[dict]:
    pipeline = [
        {"$match": {"city": city}},
        {"$unwind": "$cuisines"},
        {"$group": {
            "_id": "$cuisines",
            "count": {"$sum": 1},
            "avg_rating": {"$avg": "$rating"},
        }},
        {"$addFields": {"popularity_score": {"$multiply": ["$count", "$avg_rating"]}}},
        {"$sort": {"popularity_score": -1}},
        {"$limit": 20},
    ]
    all_results = list(restaurants_col.aggregate(pipeline))

    cuisine_map = {r["_id"]: r for r in all_results}

    MUST_SHOW = ["Biryani", "South Indian", "Haleem", "Andhra", "Cafe"]

    final = []
    seen = set()

    for must in MUST_SHOW:
        if must in cuisine_map and must not in seen:
            final.append(cuisine_map[must])
            seen.add(must)
        else:
            for key, val in cuisine_map.items():
                if must.lower() in key.lower() and key not in seen:
                    final.append(val)
                    seen.add(key)
                    break

    for r in all_results:
        if r["_id"] not in seen and len(final) < 7:
            final.append(r)
            seen.add(r["_id"])

    return [
        {
            "name": item["_id"],
            "cuisine_type": item["_id"],
            "popularity_score": round(item.get("popularity_score", 0), 2),
        }
        for item in final[:7]
    ]

# ─────────────────────────────────────────────
# RECOMMENDATION ENGINE
# ─────────────────────────────────────────────

@app.post("/api/restaurants/recommend")
async def recommend_restaurants(request: RecommendationRequest):

    all_in_city = list(restaurants_col.find({"city": request.city}))
    if not all_in_city:
        all_in_city = list(restaurants_col.find(
            {"city": {"$regex": f"^{request.city}$", "$options": "i"}}
        ))
    if not all_in_city:
        raise HTTPException(status_code=404, detail="No restaurants found")

    # Area
    if request.area:
        area_filtered = [
            r for r in all_in_city
            if str(r.get("locality","")).lower() == request.area.lower()
        ]
        if not area_filtered:
            area_filtered = all_in_city
    else:
        area_filtered = all_in_city

    # Budget
    if request.budget_max >= 99999:
        budget_filtered = area_filtered
    else:
        budget_filtered = [
            r for r in area_filtered
            if request.budget_min <= r.get("cost_for_two",500) <= request.budget_max
        ] or area_filtered

    # Taste
    taste_filtered = filter_by_taste(budget_filtered, request.taste_preference)

    # Distance
    has_gps = request.latitude and request.longitude
    for r in taste_filtered:
        r["distance_km"] = calculate_distance(
            request.latitude, request.longitude,
            r.get("latitude") or 17.3850,
            r.get("longitude") or 78.4867,
        ) if has_gps else 0.0

    final_list = taste_filtered

    for r in final_list:
        r["ai_score"] = calculate_ai_score(r, request)

    final_list.sort(key=lambda x: x["ai_score"], reverse=True)
    top_results = final_list[:20]

    result = []
    for r in top_results:
        google = get_google_places_data(r.get("name",""), r.get("address",""))
        result.append({
            "name": r.get("name",""),
            "address": r.get("address",""),
            "distance_km": f"{round(r['distance_km'],1)} km" if has_gps else "Nearby",
            "cuisine": ", ".join(r.get("cuisines",[])),
            "best_dish": r.get("best_dish",""),
            "famous_for": r.get("famous_for",""),
            "spicy_level": r.get("spicy_level","Medium"),
            "food_type": r.get("food_type","Mixed"),
            "cost_for_two": r.get("cost_for_two",0),
            "rating": r.get("rating",0),
            "is_open": google.get("is_open",True),
            "map_link": google.get("map_link",""),
            "ai_score": round(r["ai_score"],2),
        })

    return result

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def filter_by_taste(restaurants: list, preference: str) -> list:
    if preference.lower() == "spicy":
        return [r for r in restaurants if r.get("spicy_level") == "High"] or restaurants
    else:
        return [r for r in restaurants if r.get("spicy_level") in ["Low","Medium"]] or restaurants

def calculate_distance(lat1, lon1, lat2, lon2) -> float:
    try:
        return geodesic((lat1,lon1),(lat2,lon2)).km
    except:
        return 5.0

def calculate_ai_score(r: dict, req: RecommendationRequest) -> float:
    rating_score = r.get("rating",0)/5.0
    dist = r.get("distance_km",5.0)
    distance_score = max(0.0, 1.0 - dist/20.0)

    cost = r.get("cost_for_two",500)
    if req.budget_max < 99999:
        mid = (req.budget_min + req.budget_max)/2
        diff = abs(cost-mid)
        budget_score = 1.0 if diff<200 else (0.7 if diff<500 else 0.4)
    else:
        budget_score = 0.8

    return 0.35*rating_score + 0.30*distance_score + 0.20*budget_score + 0.15

def get_google_places_data(name: str, address: str) -> dict:
    fallback = f"https://www.google.com/maps/search/?api=1&query={name}+Hyderabad"
    if not GOOGLE_API_KEY:
        return {"is_open": True, "map_link": fallback}
    try:
        r = requests.get(
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
            params={"input":f"{name} {address} Hyderabad","inputtype":"textquery","fields":"place_id","key":GOOGLE_API_KEY},
            timeout=5,
        ).json()
        if r.get("status")=="OK" and r.get("candidates"):
            pid = r["candidates"][0]["place_id"]
            return {"is_open": True, "map_link": f"https://www.google.com/maps/place/?q=place_id:{pid}"}
    except:
        pass
    return {"is_open": True, "map_link": fallback}

# ─────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status":"running"}

@app.get("/health")
async def health():
    try:
        client.admin.command("ping")
        db_ok = True
    except:
        db_ok = False
    return {
        "api":"healthy",
        "database":"connected" if db_ok else "disconnected",
        "total_restaurants":restaurants_col.count_documents({})
    }
