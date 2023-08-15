from fastapi import Depends, HTTPException, status, Response
from typing import Any, Optional
from pydantic import Field

from app.utils import AppModel

from ..service import Service, get_service
from . import router
from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data
import datetime
from datetime import date, datetime, timedelta


import math
import requests
import json


class PrayerTimeRequest(AppModel):
    latitude: str = Field(..., alias="lat")
    longitude: str = Field(..., alias="lon")
    date: Optional[str] = Field(None, alias="date")


@router.post("/get_time")
def prayer_time(input: PrayerTimeRequest):
    latitude = float(input.latitude)
    longitude = float(input.longitude)

    if input.date is not None:
        try:
            day, month, year = map(int, input.date.split("-"))
            current_date = date(year, month, day)
        except ValueError:
            return {
                "status": "failure",
                "message": "Invalid date format, it should be dd-mm-yyyy",
            }
    else:
        current_date = datetime.now().date()

    # Load prayer times data from JSON file
    prayer_times_data = load_json_data("app/imam/router/prayer_times.json")

    # Calculate the distance between the input coordinates and each city
    distances = []
    for city, data in prayer_times_data.items():
        city_latitude = data["latitude"]
        city_longitude = data["longitude"]
        distance = calculate_distance(
            latitude, longitude, city_latitude, city_longitude
        )
        distances.append((distance, city))

    # Find the city with the smallest distance
    _, closest_city = min(distances, key=lambda item: item[0])

    print("Closest city", closest_city)

    # Get the prayer times for the closest city
    prayer_times = prayer_times_data[closest_city]["prayer_times"]

    if prayer_times is not None:
        # Extract today's date and calculate the date for the next 7 days
        prayer_times_for_week = []

        for i in range(7):
            target_date = current_date + timedelta(days=i)
            target_date_str = target_date.strftime("%d-%m-%Y")

            # Find the prayer times for the target date
            target_date_prayer_times = next(
                (
                    result
                    for result in prayer_times["result"]
                    if result["date"] == target_date_str
                ),
                None,
            )

            if target_date_prayer_times is not None:
                # Extract the required information
                prayer_times_dict = {
                    "date": target_date_str,
                    "city_name": closest_city,
                    "asr_time": target_date_prayer_times["Asr"].strip(),
                    "isha_time": target_date_prayer_times["Isha"].strip(),
                    "sunrise_time": target_date_prayer_times["Sunrise"].strip(),
                    "maghrib_time": target_date_prayer_times["Maghrib"].strip(),
                    "dhuhr_time": target_date_prayer_times["Dhuhr"].strip(),
                    "fajr_time": target_date_prayer_times["Fajr"].strip(),
                }

                prayer_times_for_week.append(prayer_times_dict)
            else:
                print(f"No prayer times available for {target_date_str}.")

        # Return the prayer times for the week in JSON format
        return prayer_times_for_week
    else:
        print("Failed to fetch prayer times.")

    return {"status": "failure"}


def load_json_data(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data


def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert coordinates to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = 6371 * c  # Radius of the Earth in kilometers
    return distance
