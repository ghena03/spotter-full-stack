import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_location(location):
    response = requests.get(
        NOMINATIM_URL,
        params={
            "q": location,
            "format": "json",
            "limit": 1,
        },
        headers={
            "User-Agent": "Spotter-Trip-Planner/1.0"
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        raise ValueError(f"Could not find location: {location}")

    return {
        "latitude": float(data[0]["lat"]),
        "longitude": float(data[0]["lon"]),
        "display_name": data[0]["display_name"],
    }