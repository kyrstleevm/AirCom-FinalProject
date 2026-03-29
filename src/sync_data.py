import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Setup MongoDB database
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Trigger a quick connection check
    client.server_info() 
    db = client.aircom_db
    collection = db.live_measurements
    print("Successfully connected to MongoDB Atlas -- Syncing Script")
except Exception as e:
    print(f"Connection Error: {e}")

# Location IDs of cities for obtaining in OpenAQ API
CITY_IDS = {
    "Dubai": 5531836,
    "Yerevan": 3089094,
    "Styria": 4549,
    "Sydney": 2392564,
    "Aali": 3408765,
    "Rio de Janeiro": 6152593,
    "Beijing": 2836346,
    "California": 3163445,
    "Berlin": 2162178,
    "Black Forest": 3058,
    "Hanau": 4458,
    "Narva": 10634,
    "Helsinki": 4588,
    "Jyvaskyla": 2162538,
    "Kallio": 4593,
    "London": 148,
    "Cambridge": 4019582,
    "Brighton": 2675271,
    "Scotland": 2847307,
    "Athens": 7832,
    "Alberta": 8910,
    "Hong Kong": 7733,
    "Kowloon": 7735,
    "Tel Aviv": 6129326,
    "Nagpur": 6112064,
    "Mumbai": 3409482,
    "Chiba": 1215422,
    "Osaka": 1216006,
    "Tokyo": 1214515,
    "Busan": 2623148,
    "Incheon": 2622770,
    "Seoul": 2622837,
    "Almaty": 6175495,
    "Luang Prabang": 3510965,
    "Hetauda": 5710078,
    "Kathmandu": 6176215,
    "Manila": 4797646,
    "Karachi": 4712030,
    "Santarem": 7910,
    "Siberia": 5578266,
    "Alkhobar": 4421507,
    "Riyadh": 3185012,
    "Baghdad": 5104909,
    "Singapore": 3040714,
    "Las Vegas": 344,
    "Los Angeles": 3903452,
    "Miami": 5943758,
    "Montana": 542,
    "New York": 616696,
    "South Carolina": 1650,
    "South Dakota": 1037,
    "Paris": 2162591,
    "Hanoi": 4946811,
    "Ho Chi Minh": 3276359,
}

def sync_openaq():
    for city, loc_id in CITY_IDS.items():
        url = f"https://api.openaq.org/v3/locations/{loc_id}/sensors"
        try:
            # Took API Key from OpenAQ
            response = requests.get(url, headers={"X-API-Key": OPENAQ_API_KEY}, timeout=15)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if not results:
                    continue

                # Returns None if the value is not present in the live database
                def get_measurement(param_name):
                    for m in results:
                        # Checking both 'name' and 'displayName'
                        info = m.get('parameter', {})
                        if info.get('name') == param_name or info.get('displayName') == param_name:
                            latest = m.get('latest')
                            return latest.get('value') if latest else None
                    return None
                
                # Gets the particles measurement values
                pm25 = get_measurement('pm25')
                pm1 = get_measurement('pm1')
                um003 = get_measurement('um003')

                # Safety Net for PM2.5 getting a negative value
                if pm25 is None or pm25 < 0:
                    pm25 = 0

                # It uses values from API if it exixts, else it will use regional averages
                # Ensuring that the model won't crash because of the required number of values the model expects
                humidity = get_measurement('relativehumidity') or get_measurement('humidity') or 60
                temperature = get_measurement('temperature') or 28
                
                # Scanning sesnsors to find the sensor with a valid timestamp
                update_time = None
                for s in results:
                    latest = s.get('latest')
                    if latest and 'datetime' in latest:
                        update_time = latest['datetime'].get('utc')
                        break

                # Save to MongoDB
                collection.update_one(
                    {"_id": loc_id},
                    {"$set": {
                        "city": city,
                        "pm25": pm25,
                        "um003": um003,
                        "pm1": pm1,
                        "humidity": humidity,
                        "temperature": temperature,
                        "lastUpdated": update_time
                    }}, upsert = True
                )
                print(f"Synced {city}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("--- Starting Sync Process ---")
    sync_openaq()