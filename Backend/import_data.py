"""
Data Import Script
Loads Hyderabad Restaurant Dataset (.xlsx) into MongoDB
Updated for new dataset columns
"""

import pandas as pd
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGODB_URI)
db = client["food_recommendation"]
collection = db["restaurants"]


def clean_cuisines(cuisine_str):
    if pd.isna(cuisine_str):
        return []
    return [c.strip() for c in str(cuisine_str).split(',')]


def import_dataset(file_path):
    print("📁 Reading file...")

    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)

    print(f"✅ Found {len(df)} records")
    print("🧹 Cleaning data...")

    # Fill missing values
    df['Restaurant_Name'].fillna('Unknown', inplace=True)
    df['City'].fillna('Hyderabad', inplace=True)
    df['Area_Locality'].fillna('Unknown', inplace=True)
    df['Cuisine'].fillna('Not specified', inplace=True)
    df['Average_Cost_for_Two_INR'].fillna(500, inplace=True)
    df['Rating'].fillna(0, inplace=True)
    df['Latitude'].fillna(17.3850, inplace=True)
    df['Longitude'].fillna(78.4867, inplace=True)
    df['Number_of_Reviews'].fillna(0, inplace=True)
    df['Best_Dish'].fillna('', inplace=True)
    df['Taste_Profile_Spicy_Level'].fillna('Medium', inplace=True)
    df['Price_Category'].fillna('₹₹', inplace=True)
    df['Opening_Time'].fillna('11:00 AM', inplace=True)
    df['Closing_Time'].fillna('11:00 PM', inplace=True)
    df['Open_Now'].fillna('Yes', inplace=True)
    df['Famous_For'].fillna('', inplace=True)
    df['Food_Type'].fillna('Mixed', inplace=True)

    # Handle optional Reviews_Text column
    if 'Reviews_Text' not in df.columns:
        df['Reviews_Text'] = ''
    df['Reviews_Text'].fillna('', inplace=True)

    # Type conversions
    df['Average_Cost_for_Two_INR'] = pd.to_numeric(df['Average_Cost_for_Two_INR'], errors='coerce').fillna(500)
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(0)
    df['Number_of_Reviews'] = pd.to_numeric(df['Number_of_Reviews'], errors='coerce').fillna(0)
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce').fillna(17.3850)
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce').fillna(78.4867)

    print("🔄 Transforming data...")

    restaurants = []
    for _, row in df.iterrows():
        restaurant = {
            "name":             str(row['Restaurant_Name']),
            "city":             str(row['City']),
            "address":          str(row['Area_Locality']),
            "locality":         str(row['Area_Locality']),
            "cuisines":         clean_cuisines(row['Cuisine']),
            "cost_for_two":     int(row['Average_Cost_for_Two_INR']),
            "rating":           float(row['Rating']),
            "latitude":         float(row['Latitude']),
            "longitude":        float(row['Longitude']),
            "votes":            int(row['Number_of_Reviews']),
            "best_dish":        str(row['Best_Dish']),
            "spicy_level":      str(row['Taste_Profile_Spicy_Level']),
            "price_category":   str(row['Price_Category']),
            "opening_time":     str(row['Opening_Time']),
            "closing_time":     str(row['Closing_Time']),
            "open_now":         str(row['Open_Now']),
            "famous_for":       str(row['Famous_For']),
            "food_type":        str(row['Food_Type']),
            "reviews_text":     str(row['Reviews_Text']),
        }
        restaurants.append(restaurant)

    print("⚠️  Clearing existing data...")
    collection.delete_many({})

    print("📤 Inserting into MongoDB...")
    if restaurants:
        result = collection.insert_many(restaurants)
        print(f"✅ Inserted {len(result.inserted_ids)} restaurants")

    print("🔍 Creating indexes...")
    collection.create_index([("city", pymongo.ASCENDING)])
    collection.create_index([("locality", pymongo.ASCENDING)])
    collection.create_index([("cuisines", pymongo.ASCENDING)])
    collection.create_index([("cost_for_two", pymongo.ASCENDING)])
    collection.create_index([("rating", pymongo.DESCENDING)])
    collection.create_index([("spicy_level", pymongo.ASCENDING)])
    collection.create_index([("food_type", pymongo.ASCENDING)])

    print("\n✅ Data import complete!")
    print("\n📊 Database Statistics:")
    print(f"   Total Restaurants : {collection.count_documents({})}")
    print(f"   Total Cities      : {len(collection.distinct('city'))}")
    print(f"   Total Areas       : {len(collection.distinct('locality'))}")
    print("\n   Restaurants per Area:")
    for area in collection.distinct('locality'):
        count = collection.count_documents({"locality": area})
        print(f"   - {area}: {count} restaurants")


if __name__ == "__main__":
    file_path = input("Enter path to dataset file (.xlsx or .csv): ").strip()

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print("\n💡 Make sure you downloaded: hyderabad_restaurants_full.xlsx")
    else:
        import_dataset(file_path)
