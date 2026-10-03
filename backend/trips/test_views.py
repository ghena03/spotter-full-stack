from unittest.mock import patch

from rest_framework.test import APITestCase
from rest_framework import status


class PlanTripAPITests(APITestCase):

    @patch("trips.views.get_trip_route")
    def test_plan_trip_returns_schedule(self, mock_get_trip_route):
        mock_get_trip_route.return_value = {
            "current": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "display_name": "New York, NY",
            },
            "pickup": {
                "latitude": 39.9526,
                "longitude": -75.1652,
                "display_name": "Philadelphia, PA",
            },
            "dropoff": {
                "latitude": 38.9072,
                "longitude": -77.0369,
                "display_name": "Washington, DC",
            },
            "legs": {
                "current_to_pickup": {
                    "distance_miles": 94.6,
                    "duration_hours": 2.0,
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [],
                    },
                },
                "pickup_to_dropoff": {
                    "distance_miles": 137.1,
                    "duration_hours": 3.0,
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [],
                    },
                },
            },
            "total_distance_miles": 231.7,
            "total_duration_hours": 5.0,
        }

        response = self.client.post(
            "/api/trips/plan/",
            {
                "current_location": "New York, NY",
                "pickup_location": "Philadelphia, PA",
                "dropoff_location": "Washington, DC",
                "cycle_used_hours": 20,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("events", data)
        self.assertIn("route", data)
        self.assertIn("distance_miles", data)
        self.assertIn("driving_hours", data)
        self.assertIn("cycle_remaining_hours", data)
        self.assertIn("total_duration_hours", data)

        self.assertEqual(data["distance_miles"], 231.7)
        self.assertEqual(data["driving_hours"], 5.0)
        self.assertEqual(data["route"]["total_distance_miles"], 231.7)

        mock_get_trip_route.assert_called_once_with(
            current_location="New York, NY",
            pickup_location="Philadelphia, PA",
            dropoff_location="Washington, DC",
        )