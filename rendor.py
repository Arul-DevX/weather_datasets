import requests
import time
from datetime import datetime, timezone
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()  # this loads variables from .env into os.environ

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_KEY = os.getenv("OPENWEATHER_API_KEY")



API_KEY = "1a323e5e4e424388f7deb6f1ae9a1342".strip()
CITY_IDS = [
    1277333, 1273294, 1264527, 1275004, 1275339,
    1259229, 1269843, 1269515, 1273874, 1271157,
    2988507, 2643743, 5128581, 1850144, 292223,
    2147714, 1880252, 3369157, 4219762, 1650535
]
INTERVAL = 15 * 60  # 15 mins


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_condition_id(main, description, icon):
    # Check if condition exists
    res = supabase.table("weather_conditions").select("condition_id") \
        .eq("main", main).eq("description", description).eq("icon", icon).execute()
    if res.data:
        return res.data[0]["condition_id"]

    # Insert new condition
    insert_res = supabase.table("weather_conditions").insert({
        "main": main,
        "description": description,
        "icon": icon
    }).execute()

    return insert_res.data[0]["condition_id"]

def insert_city(city_id, name, country, lat, lon):
    # Upsert city (insert or update if exists)
    supabase.table("cities").upsert({
        "city_id": city_id,
        "city_name": name,
        "country": country,
        "latitude": lat,
        "longitude": lon
    }).execute()

def insert_weather_record(city_id, condition_id, temp, feels_like, temp_min, temp_max, pressure, humidity, visibility, recorded_at):
    res = supabase.table("weather_records").insert({
        "city_id": city_id,
        "condition_id": condition_id,
        "temperature": temp,
        "feels_like": feels_like,
        "temp_min": temp_min,
        "temp_max": temp_max,
        "pressure": pressure,
        "humidity": humidity,
        "visibility": visibility,
        "recorded_at": recorded_at
    }).execute()
    return res.data[0]["record_id"]

def insert_wind(record_id, wind_speed, wind_deg):
    supabase.table("wind_data").insert({
        "record_id": record_id,
        "wind_speed": wind_speed,
        "wind_deg": wind_deg
    }).execute()

def fetch_and_store():
    for city_id in CITY_IDS:
        url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Failed for {city_id}: {response.status_code} - {response.text}")
            continue
        city = response.json()

        # Insert city info
        insert_city(city["id"], city["name"], city["sys"]["country"], city["coord"]["lat"], city["coord"]["lon"])

        # Weather condition
        weather = city["weather"][0]
        condition_id = get_condition_id(weather["main"], weather["description"], weather["icon"])

        # Weather record
        record_id = insert_weather_record(
            city["id"], condition_id,
            city["main"]["temp"], city["main"]["feels_like"],
            city["main"]["temp_min"], city["main"]["temp_max"],
            city["main"]["pressure"], city["main"]["humidity"],
            city.get("visibility", None),
            datetime.fromtimestamp(city["dt"], timezone.utc).isoformat()
        )

        # Wind
        wind = city.get("wind", {})
        insert_wind(record_id, wind.get("speed"), wind.get("deg"))

        print(f"✅ Inserted data for {city['name']}")

def main_loop():
    while True:
        fetch_and_store()
        print(f"⏳ Waiting {INTERVAL} seconds till next fetch...")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main_loop()
