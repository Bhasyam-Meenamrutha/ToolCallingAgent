import requests


def get_weather(city: str):
    """
    Get current weather for a city.
    """

    # 1. Convert city name to coordinates
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    geo_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    geo_response = requests.get(
        geo_url,
        params=geo_params,
        timeout=10
    )

    geo_response.raise_for_status()

    geo_data = geo_response.json()

    if "results" not in geo_data:
        return {
            "success": False,
            "message": f"Could not find city: {city}"
        }

    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # 2. Get weather
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "timezone": "Asia/Kolkata"
    }

    weather_response = requests.get(
        weather_url,
        params=weather_params,
        timeout=10
    )

    weather_response.raise_for_status()

    weather_data = weather_response.json()

    current = weather_data["current"]

    return {
        "success": True,
        "city": location["name"],
        "country": location.get("country"),
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "precipitation": current["precipitation"],
        "wind_speed": current["wind_speed_10m"],
        "time": current["time"]
    }