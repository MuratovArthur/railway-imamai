import requests
import json
import datetime


def fetch_cities_data():
    cities_data = []
    page = 1
    while True:
        url = f"https://api.muftyat.kz/cities/?page={page}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cities_data += data["results"]
            if data["next"] is not None:
                page += 1
            else:
                break
        else:
            print("Failed to fetch cities data.")
            break
    return cities_data


def get_prayer_times(year, latitude, longitude):
    url = f"http://namaz.muftyat.kz/api/times/{year}/{latitude}/{longitude}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch prayer times.")
        return None


current_year = datetime.datetime.now().year

all_cities_data = fetch_cities_data()
prayer_times_data = {}

for city in all_cities_data:
    city_latitude = float(city["lat"])
    city_longitude = float(city["lng"])
    prayer_times = get_prayer_times(current_year, city_latitude, city_longitude)
    if prayer_times is not None:
        prayer_times_data[city["title"]] = {
            "latitude": city_latitude,
            "longitude": city_longitude,
            "prayer_times": prayer_times,
        }

# Save the data to a JSON file
with open("prayer_times.json", "w") as file:
    json.dump(prayer_times_data, file)
