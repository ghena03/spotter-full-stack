from unittest.mock import patch, Mock

from django.test import SimpleTestCase

from .routing import get_route


class RoutingTests(SimpleTestCase):

    @patch("trips.routing.requests.get")
    def test_get_route_returns_route_data(self, mock_get):
        mock_response = Mock()

        mock_response.json.return_value = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 16093.44,
                    "duration": 3600,
                    "geometry": {
                        "coordinates": [
                            [-74.0060, 40.7128],
                            [-73.9855, 40.7580],
                        ],
                        "type": "LineString",
                    },
                }
            ],
        }

        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_route(
            -74.0060,
            40.7128,
            -73.9855,
            40.7580,
        )

        self.assertAlmostEqual(result["distance_miles"], 10.0)
        self.assertAlmostEqual(result["duration_hours"], 1.0)

        self.assertEqual(
            result["geometry"]["type"],
            "LineString",
        )

        mock_get.assert_called_once()