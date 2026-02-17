"""
AI-Based Food & Restaurant Recommendation System
FastAPI Backend — FINAL (South Indian in famous foods + area + full ranking)
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

app = FastAPI(title="AI Food Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
client = pymongo.MongoClient(MONGODB_URI)
db = client["food_recommendation"]
restaurants_col = db["restaurants"]

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")


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
# ENDPOINT 1 — CITY SEARCH + FAMOUS FOODS
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
            raise HTTPException(status_code=404, detail=f"City '{city}' not found. Try: Hyderabad")

    famous_foods = get_famous_foods(city)
    total = restaurants_col.count_documents({"city": city})
    return {"city": city, "famous_foods": famous_foods, "total_restaurants": total}


def get_famous_foods(city: str) -> List[dict]:
    """
    Always guarantees South Indian, Biryani, Haleem, Andhra, Cafe
    appear in the famous foods list — the iconic Hyderabadi cuisines.
    """
    # Fetch top 20 by popularity
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

    # Build lookup map
    cuisine_map = {r["_id"]: r for r in all_results}

    # ── Cuisines that MUST always appear for Hyderabad ──
    MUST_SHOW = ["Biryani", "South Indian", "Haleem", "Andhra", "Cafe"]

    final = []
    seen  = set()

    # Add must-show first (exact → partial fallback)
    for must in MUST_SHOW:
        if must in cuisine_map and must not in seen:
            final.append(cuisine_map[must])
            seen.add(must)
        else:
            # Partial match — e.g. "South Indian, Veg" contains "South Indian"
            for key, val in cuisine_map.items():
                if must.lower() in key.lower() and key not in seen:
                    final.append(val)
                    seen.add(key)
                    break

    # Fill remaining slots with highest-popularity cuisines
    for r in all_results:
        if r["_id"] not in seen and len(final) < 7:
            final.append(r)
            seen.add(r["_id"])

    return [
        {
            "name":             item["_id"],
            "cuisine_type":     item["_id"],
            "popularity_score": round(item.get("popularity_score", 0), 2),
        }
        for item in final[:7]
    ]


# ─────────────────────────────────────────────
# ENDPOINT 2 — AI RECOMMENDATIONS
# ─────────────────────────────────────────────

@app.post("/api/restaurants/recommend")
async def recommend_restaurants(request: RecommendationRequest):

    print(f"\n{'='*50}")
    print(f"CITY={request.city} | AREA={request.area!r} | TASTE={request.taste_preference}")
    print(f"BUDGET=Rs{request.budget_min}-Rs{request.budget_max} | GPS={request.latitude},{request.longitude}")

    # STEP 1: All in city
    all_in_city = list(restaurants_col.find({"city": request.city}))
    if not all_in_city:
        all_in_city = list(restaurants_col.find(
            {"city": {"$regex": f"^{request.city}$", "$options": "i"}}
        ))
    if not all_in_city:
        raise HTTPException(status_code=404, detail=f"No restaurants found for '{request.city}'")
    print(f"Step 1 City: {len(all_in_city)}")

    # STEP 2: Area filter (exact match — dropdown guarantees correct value)
    if request.area and request.area.strip():
        area_text = request.area.strip()
        area_filtered = [
            r for r in all_in_city
            if str(r.get("locality", "")).strip().lower() == area_text.lower()
        ]
        print(f"Step 2 Area exact '{area_text}': {len(area_filtered)}")

        if not area_filtered:
            area_filtered = [
                r for r in all_in_city
                if area_text.lower() in str(r.get("locality", "")).lower()
            ]
            print(f"Step 2 Area partial: {len(area_filtered)}")

        if not area_filtered:
            print("Step 2 Area fallback → full city")
            area_filtered = all_in_city
    else:
        area_filtered = all_in_city
        print("Step 2 No area → full city")

    # STEP 3: Budget filter
    if request.budget_max >= 99999:
        budget_filtered = area_filtered
    else:
        budget_filtered = [
            r for r in area_filtered
            if request.budget_min <= r.get("cost_for_two", 500) <= request.budget_max
        ]
        if len(budget_filtered) < 3:
            budget_filtered = [
                r for r in area_filtered
                if r.get("cost_for_two", 500) <= request.budget_max + 500
            ]
        if not budget_filtered:
            budget_filtered = area_filtered
    print(f"Step 3 Budget: {len(budget_filtered)}")

    # STEP 4: Taste filter
    taste_filtered = filter_by_taste(budget_filtered, request.taste_preference)
    print(f"Step 4 Taste: {len(taste_filtered)}")

    # STEP 5: Distance
    has_gps = request.latitude != 0.0 and request.longitude != 0.0
    if has_gps:
        for r in taste_filtered:
            r["distance_km"] = calculate_distance(
                request.latitude, request.longitude,
                r.get("latitude") or 17.3850,
                r.get("longitude") or 78.4867,
            )
        within_10 = [r for r in taste_filtered if r["distance_km"] <= 10]
        if len(within_10) >= 3:
            final_list = within_10
        else:
            within_20 = [r for r in taste_filtered if r["distance_km"] <= 20]
            final_list = within_20 if within_20 else taste_filtered
        print(f"Step 5 GPS: {len(final_list)}")
    else:
        for r in taste_filtered:
            r["distance_km"] = 0.0
        final_list = taste_filtered
        print("Step 5 No GPS → skip distance")

    if not final_list:
        raise HTTPException(
            status_code=404,
            detail="No restaurants found. Try a wider budget or different area."
        )

    # STEP 6: AI Rank — return up to 20 so frontend shows hero + scroll row
    for r in final_list:
        r["ai_score"] = calculate_ai_score(r, request)
    final_list.sort(key=lambda x: x["ai_score"], reverse=True)
    top_results = final_list[:20]
    print(f"Step 6 Returning {len(top_results)}")

    # STEP 7: Build response
    result = []
    for r in top_results:
        google   = get_google_places_data(r.get("name", ""), r.get("address", ""))
        dist     = r.get("distance_km", 0)
        dist_lbl = f"{round(dist,1)} km" if has_gps and dist > 0 else "Nearby"

        result.append({
            "name":         r.get("name", ""),
            "address":      r.get("address", r.get("locality", "Hyderabad")),
            "distance_km":  dist_lbl,
            "cuisine":      ", ".join(r.get("cuisines", [])) if isinstance(r.get("cuisines"), list) else str(r.get("cuisines", "")),
            "best_dish":    r.get("best_dish", ""),
            "famous_for":   r.get("famous_for", ""),
            "spicy_level":  r.get("spicy_level", "Medium"),
            "food_type":    r.get("food_type", "Mixed"),
            "price_range":  r.get("price_category", get_price_symbol(r.get("cost_for_two", 500))),
            "cost_for_two": r.get("cost_for_two", 0),
            "rating":       r.get("rating", 0),
            "votes":        r.get("votes", 0),
            "opening_time": r.get("opening_time", ""),
            "closing_time": r.get("closing_time", ""),
            "is_open":      google.get("is_open", r.get("open_now", "Yes") == "Yes"),
            "map_link":     google.get("map_link", ""),
            "ai_score":     round(r["ai_score"], 2),
        })

    return result


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def filter_by_taste(restaurants: list, preference: str) -> list:
    pref = preference.lower()
    if pref == "spicy":
        filtered = [r for r in restaurants if r.get("spicy_level") == "High"]
    else:
        filtered = [r for r in restaurants if r.get("spicy_level") in ["Low", "Medium"]]
    if not filtered:
        spicy_kw = ["biryani","andhra","chettinad","kebab","mughlai","schezwan"]
        mild_kw  = ["cafe","continental","south indian","italian","dessert","bakery"]
        kws = spicy_kw if pref == "spicy" else mild_kw
        filtered = [r for r in restaurants
                    if any(k in " ".join(r.get("cuisines",[])).lower() for k in kws)]
    return filtered if filtered else restaurants


def calculate_distance(lat1, lon1, lat2, lon2) -> float:
    try:
        return geodesic((lat1,lon1),(lat2,lon2)).kilometers if lat2 and lon2 else 5.0
    except Exception:
        return 5.0


def calculate_ai_score(r: dict, req: RecommendationRequest) -> float:
    rating_score   = r.get("rating", 0) / 5.0
    dist           = r.get("distance_km", 5.0)
    if isinstance(dist, str): dist = 5.0
    distance_score = max(0.0, 1.0 - dist / 20.0)
    cost           = r.get("cost_for_two", 500)
    if req.budget_max < 99999:
        mid  = (req.budget_min + req.budget_max) / 2
        diff = abs(cost - mid)
        budget_score = 1.0 if diff < 200 else (0.7 if diff < 500 else 0.4)
    else:
        budget_score = 0.8
    return 0.35*rating_score + 0.30*distance_score + 0.20*budget_score + 0.15*1.0


def get_google_places_data(name: str, address: str) -> dict:
    fallback = "https://www.google.com/maps/search/?api=1&query=" + (name+" Hyderabad").replace(" ","+")
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
            det = requests.get(
                "https://maps.googleapis.com/maps/api/place/details/json",
                params={"place_id":pid,"fields":"opening_hours,url","key":GOOGLE_API_KEY},
                timeout=5,
            ).json().get("result",{})
            return {"is_open":det.get("opening_hours",{}).get("open_now",True),"map_link":det.get("url",fallback)}
    except Exception as e:
        print(f"Google error: {e}")
    return {"is_open": True, "map_link": fallback}


def get_price_symbol(cost: int) -> str:
    if cost < 300:  return "₹"
    if cost < 800:  return "₹₹"
    if cost < 1500: return "₹₹₹"
    return "₹₹₹₹"


@app.get("/")
async def root():
    return {"status":"running ✅","total_restaurants":restaurants_col.count_documents({})}

@app.get("/health")
async def health():
    try: client.admin.command("ping"); db_ok=True
    except: db_ok=False
    return {"api":"healthy","database":"connected" if db_ok else "disconnected",
            "google_api":"set" if GOOGLE_API_KEY else "fallback","total_restaurants":restaurants_col.count_documents({})}

@app.get("/api/cities")
async def list_cities():
    return {"cities": sorted(restaurants_col.distinct("city"))}

@app.get("/api/areas")
async def list_areas(city: str = "Hyderabad"):
    areas = restaurants_col.distinct("locality", {"city": city})
    return {"city": city, "areas": sorted([a for a in areas if a and a != "Unknown"])}
