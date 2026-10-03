import requests

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .hos_engine import build_trip_schedule
from .routing import get_trip_route



@api_view(["POST"])
def plan_trip(request):
    """
    Plan a truck trip according to HOS rules.
    """

    current_location = request.data.get("current_location")
    pickup_location = request.data.get("pickup_location")
    dropoff_location = request.data.get("dropoff_location")
    cycle_used_hours = request.data.get("cycle_used_hours")

    # Validate required fields
    if not current_location:
        return Response(
            {"error": "current_location is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not pickup_location:
        return Response(
            {"error": "pickup_location is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not dropoff_location:
        return Response(
            {"error": "dropoff_location is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if cycle_used_hours is None:
        return Response(
            {"error": "cycle_used_hours is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        cycle_used_hours = float(cycle_used_hours)
    except (TypeError, ValueError):
        return Response(
            {"error": "cycle_used_hours must be a number."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Get real route between current location, pickup, and dropoff.
        trip_route = get_trip_route(
            current_location=current_location,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
        )

        distance_miles = trip_route["total_distance_miles"]
        driving_hours = trip_route["total_duration_hours"]

        # Run the HOS engine using the real route distance and duration.
        schedule = build_trip_schedule(
            distance_miles=distance_miles,
            driving_hours=driving_hours,
            cycle_used_hours=cycle_used_hours,
        )

        return Response(
    {
        "success": True,
        "input": {
            "current_location": current_location,
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "cycle_used_hours": cycle_used_hours,
        },
        "route": trip_route,
        **schedule,
    },
    status=status.HTTP_200_OK,
)

  

    except ValueError as exc:
        return Response(
            {"error": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except requests.RequestException as exc:
        return Response(
            {
                "error": "External routing service error.",
                "details": str(exc),
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    except Exception as exc:
        return Response(
            {
                "error": "Internal server error.",
                "details": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )