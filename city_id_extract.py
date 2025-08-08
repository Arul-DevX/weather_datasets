import requests

API_KEY = "1a323e5e4e424388f7deb6f1ae9a1342"  # Replace with your OpenWeatherMap API key
cities = [
    # India
    "Bangalore", "Delhi", "Chennai", "Kolkata", "Mumbai",
    "Pune", "Hyderabad", "Jaipur", "Kochi", "Goa",
    # World
    "Paris", "London", "New York", "Tokyo", "Dubai",
    "Sydney", "Singapore", "Cape Town", "Rome", "Bali"
]

city_ids = []

for city in cities:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()
    
    if "id" in response:
        city_id = response["id"]
        city_ids.append(str(city_id))
        print(f"{city} → {city_id}")
    else:
        print(f"❌ Could not get ID for {city}: {response}")

print("\n✅ Final CITY_IDS string:")
print(",".join(city_ids))
