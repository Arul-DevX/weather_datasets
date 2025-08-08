import requests
import mysql.connector
from datetime import datetime, timezone
import time

# --------- CONFIGURATION ---------
API_KEY = "1a323e5e4e424388f7deb6f1ae9a1342".strip()
CITY_IDS = [
    1277333, 1273294, 1264527, 1275004, 1275339,
    1259229, 1269843, 1269515, 1273874, 1271157,
    2988507, 2643743, 5128581, 1850144, 292223,
    2147714, 1880252, 3369157, 4219762, 1650535
]
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "tiger",
    "database": "weather_database"
}
LOOP_COUNT = 50
SLEEP_SECONDS = 5
# ---------------------------------

# Connect to MySQL
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor(buffered=True)


def insert_city(city_id, name, country, lat, lon):
    cursor.execute("""
        INSERT IGNORE INTO cities (city_id, city_name, country, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s)
    """, (city_id, name, country, lat, lon))

def insert_condition(main, description, icon):
    cursor.execute("""
        INSERT IGNORE INTO weather_conditions (main, description, icon)
        VALUES (%s, %s, %s)
    """, (main, description, icon))
    conn.commit()
    cursor.execute("""
        SELECT condition_id FROM weather_conditions
        WHERE main=%s AND description=%s AND icon=%s
    """, (main, description, icon))
    return cursor.fetchone()[0]

def insert_weather_record(city_id, condition_id, temp, feels_like, temp_min, temp_max, pressure, humidity, visibility, recorded_at):
    cursor.execute("""
        INSERT INTO weather_records (city_id, condition_id, temperature, feels_like, temp_min, temp_max, pressure, humidity, visibility, recorded_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (city_id, condition_id, temp, feels_like, temp_min, temp_max, pressure, humidity, visibility, recorded_at))
    conn.commit()
    return cursor.lastrowid

def insert_wind(record_id, wind_speed, wind_deg):
    cursor.execute("""
        INSERT INTO wind_data (record_id, wind_speed, wind_deg)
        VALUES (%s, %s, %s)
    """, (record_id, wind_speed, wind_deg))
    conn.commit()

# Main loop
for _ in range(LOOP_COUNT):
    for city_id in CITY_IDS:
        url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"❌ Failed for {city_id}: {response.status_code} - {response.text}")
            continue

        city = response.json()

        # Insert city
        insert_city(city["id"], city["name"], city["sys"]["country"], city["coord"]["lat"], city["coord"]["lon"])

        # Insert weather condition
        weather = city["weather"][0]
        condition_id = insert_condition(weather["main"], weather["description"], weather["icon"])

        # Insert weather record
        record_id = insert_weather_record(
            city["id"], condition_id,
            city["main"]["temp"], city["main"]["feels_like"],
            city["main"]["temp_min"], city["main"]["temp_max"],
            city["main"]["pressure"], city["main"]["humidity"],
            city.get("visibility", None),
            datetime.fromtimestamp(city["dt"], timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        )

        # Insert wind
        wind = city.get("wind", {})
        insert_wind(record_id, wind.get("speed"), wind.get("deg"))

        print(f"✅ Inserted data for {city['name']} at {datetime.now()}")

    time.sleep(SLEEP_SECONDS)

cursor.close()
conn.close()
