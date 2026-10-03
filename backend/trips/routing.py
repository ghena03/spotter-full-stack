import requests


OSRM_BASE_URL = "https://router.project-osrm.org"


def get_route(start_lon, start_lat, end_lon, end_lat):
    """
    Get driving route information from OSRM.

    Returns:
        distance_miles: route distance in miles
        duration_hours: estimated driving duration
        geometry: GeoJSON route geometry
    """

    url = (
        f"{OSRM_BASE_URL}/route/v1/driving/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
    )

    params = {
        "overview": "full",
        "geometries": "geojson",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        raise ValueError("OSRM could not calculate the route")

    route = data["routes"][0]

    distance_miles = route["distance"] / 1609.344
    duration_hours = route["duration"] / 3600

    return {
        "distance_miles": distance_miles,
        "duration_hours": duration_hours,
        "geometry": route["geometry"],
    }

from .geocoding import geocode_location


def get_route_between_locations(start_location, end_location):
    start = geocode_location(start_location)
    end = geocode_location(end_location)

    route = get_route(
        start_lon=start["longitude"],
        start_lat=start["latitude"],
        end_lon=end["longitude"],
        end_lat=end["latitude"],
    )

    return {
        "start": start,
        "end": end,
        "route": route,
    }

def get_trip_route(current_location, pickup_location, dropoff_location):
    current = geocode_location(current_location)
    pickup = geocode_location(pickup_location)
    dropoff = geocode_location(dropoff_location)

    route_to_pickup = get_route(
        start_lon=current["longitude"],
        start_lat=current["latitude"],
        end_lon=pickup["longitude"],
        end_lat=pickup["latitude"],
    )

    route_to_dropoff = get_route(
        start_lon=pickup["longitude"],
        start_lat=pickup["latitude"],
        end_lon=dropoff["longitude"],
        end_lat=dropoff["latitude"],
    )

    total_distance_miles = (
        route_to_pickup["distance_miles"]
        + route_to_dropoff["distance_miles"]
    )

    total_duration_hours = (
        route_to_pickup["duration_hours"]
        + route_to_dropoff["duration_hours"]
    )

    return {
        "current": current,
        "pickup": pickup,
        "dropoff": dropoff,
        "legs": {
            "current_to_pickup": route_to_pickup,
            "pickup_to_dropoff": route_to_dropoff,
        },
        "total_distance_miles": total_distance_miles,
        "total_duration_hours": total_duration_hours,
    }