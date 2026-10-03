import { useEffect } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMap,
} from "react-leaflet";

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./TripMap.css";


const createMarkerIcon = (color) =>
  L.divIcon({
    className: "custom-map-marker",
    html: `
      <div class="map-marker-pin" style="--marker-color:${color}">
        <div class="map-marker-dot"></div>
      </div>
    `,
    iconSize: [28, 38],
    iconAnchor: [14, 38],
    popupAnchor: [0, -38],
  });


const currentIcon = createMarkerIcon("#202b3f");
const pickupIcon = createMarkerIcon("#28c7b7");
const dropoffIcon = createMarkerIcon("#ff4f9a");
const fuelIcon = createMarkerIcon("#f59e0b");
const restIcon = createMarkerIcon("#8b5cf6");


function FitRoute({ positions }) {
  const map = useMap();

  useEffect(() => {
    if (!positions || positions.length === 0) return;

    map.fitBounds(positions, {
      padding: [40, 40],
    });
  }, [map, positions]);

  return null;
}


/*
 * Distance between two latitude/longitude points.
 * Returns miles.
 */
function distanceMiles(pointA, pointB) {
  const [lat1, lon1] = pointA;
  const [lat2, lon2] = pointB;

  const earthRadiusMiles = 3958.7613;

  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;

  const c =
    2 * Math.atan2(
      Math.sqrt(a),
      Math.sqrt(1 - a)
    );

  return earthRadiusMiles * c;
}


/*
 * Build cumulative route distances.
 */
function buildRouteDistanceIndex(positions) {
  const cumulative = [0];

  for (let i = 1; i < positions.length; i += 1) {
    cumulative.push(
      cumulative[i - 1] +
        distanceMiles(
          positions[i - 1],
          positions[i]
        )
    );
  }

  return cumulative;
}


/*
 * Find the exact point on the route at a target
 * distance from the beginning.
 */
function positionAtDistance(
  positions,
  cumulativeDistances,
  targetMiles
) {
  if (!positions.length) return null;

  if (targetMiles <= 0) {
    return positions[0];
  }

  const totalMiles =
    cumulativeDistances[
      cumulativeDistances.length - 1
    ];

  if (targetMiles >= totalMiles) {
    return positions[positions.length - 1];
  }

  for (
    let i = 1;
    i < cumulativeDistances.length;
    i += 1
  ) {
    const previousDistance =
      cumulativeDistances[i - 1];

    const currentDistance =
      cumulativeDistances[i];

    if (targetMiles <= currentDistance) {
      const segmentMiles =
        currentDistance - previousDistance;

      if (segmentMiles <= 0) {
        return positions[i];
      }

      const ratio =
        (targetMiles - previousDistance) /
        segmentMiles;

      const [lat1, lon1] =
        positions[i - 1];

      const [lat2, lon2] =
        positions[i];

      return [
        lat1 + (lat2 - lat1) * ratio,
        lon1 + (lon2 - lon1) * ratio,
      ];
    }
  }

  return positions[positions.length - 1];
}


/*
 * Convert an HOS event time into a distance along
 * the route.
 *
 * Only DRIVING time moves the truck forward.
 */
function distanceAtEventTime(
  events,
  targetTime,
  totalDistanceMiles,
  totalDrivingHours
) {
  if (
    !events ||
    !Number.isFinite(totalDistanceMiles) ||
    !Number.isFinite(totalDrivingHours) ||
    totalDrivingHours <= 0
  ) {
    return 0;
  }

  let drivingBefore = 0;

  for (const event of events) {
    const start = Number(
      event?.start ?? 0
    );

    const end = Number(
      event?.end ?? start
    );

    const type = String(
      event?.type || ""
    ).toUpperCase();

    if (start >= targetTime) {
      break;
    }

    const effectiveEnd = Math.min(
      end,
      targetTime
    );

    if (
      effectiveEnd > start &&
      type === "DRIVING"
    ) {
      drivingBefore +=
        effectiveEnd - start;
    }
  }

  const ratio = Math.max(
    0,
    Math.min(
      1,
      drivingBefore / totalDrivingHours
    )
  );

  return totalDistanceMiles * ratio;
}


function TripMap({
  route,
  fuelStops = [],
  restStops = [],
  events = [],
  distanceMiles: totalDistanceMiles = 0,
  drivingHours: totalDrivingHours = 0,
}) {
  if (!route) return null;


  /*
   * Backend route structure:
   *
   * route
   * ├── current
   * ├── pickup
   * ├── dropoff
   * └── legs
   *     ├── current_to_pickup
   *     └── pickup_to_dropoff
   */

  const firstLeg =
    route?.legs?.current_to_pickup;

  const secondLeg =
    route?.legs?.pickup_to_dropoff;


  /*
   * Build the complete route polyline.
   */

  const positions = [];

  const legs = [
    firstLeg,
    secondLeg,
  ].filter(Boolean);

  legs.forEach((leg) => {
    const coordinates =
      leg?.geometry?.coordinates || [];

    coordinates.forEach(
      ([longitude, latitude]) => {
        positions.push([
          latitude,
          longitude,
        ]);
      }
    );
  });


  if (positions.length === 0) {
    return (
      <div className="trip-map-empty">
        Route map is unavailable.
      </div>
    );
  }


  /*
   * Current location.
   */
  const currentLocation =
    route?.current?.latitude != null &&
    route?.current?.longitude != null
      ? [
          Number(route.current.latitude),
          Number(route.current.longitude),
        ]
      : positions[0];


  /*
   * Dropoff location.
   */
  const dropoffLocation =
    route?.dropoff?.latitude != null &&
    route?.dropoff?.longitude != null
      ? [
          Number(route.dropoff.latitude),
          Number(route.dropoff.longitude),
        ]
      : positions[positions.length - 1];


  /*
   * Pickup location.
   *
   * IMPORTANT:
   * Take it directly from the backend geocoding
   * result instead of calculating it from the
   * route geometry.
   */
  const pickupLocation =
    route?.pickup?.latitude != null &&
    route?.pickup?.longitude != null
      ? [
          Number(route.pickup.latitude),
          Number(route.pickup.longitude),
        ]
      : firstLeg?.geometry?.coordinates?.length
        ? (() => {
            const coordinates =
              firstLeg.geometry.coordinates;

            const [
              longitude,
              latitude,
            ] =
              coordinates[
                coordinates.length - 1
              ];

            return [
              latitude,
              longitude,
            ];
          })()
        : null;


  /*
   * Calculate cumulative physical distance
   * along the actual road geometry.
   */
  const cumulativeDistances =
    buildRouteDistanceIndex(
      positions
    );

  const geometryDistanceMiles =
    cumulativeDistances[
      cumulativeDistances.length - 1
    ];


  /*
   * Prefer backend distance when available.
   */
  const routeDistance =
    Number(totalDistanceMiles) > 0
      ? Number(totalDistanceMiles)
      : geometryDistanceMiles;


  /*
   * =========================
   * FUEL STOPS
   * =========================
   */

  const validFuelStops = fuelStops
    .map((stop, index) => {
      const start = Number(
        stop?.start ?? 0
      );

      const end = Number(
        stop?.end ?? start
      );

      if (!Number.isFinite(start)) {
        return null;
      }

      const distanceAtFuel =
        distanceAtEventTime(
          events,
          start,
          routeDistance,
          Number(totalDrivingHours)
        );

      const geometryTargetMiles =
        routeDistance > 0
          ? (distanceAtFuel / routeDistance) *
            geometryDistanceMiles
          : 0;

      const position =
        positionAtDistance(
          positions,
          cumulativeDistances,
          geometryTargetMiles
        );

      return {
        index,
        start,
        end,
        duration: end - start,
        distanceAtFuel,
        position,
      };
    })
    .filter(Boolean);


  /*
   * =========================
   * REST STOPS
   * =========================
   */

  const validRestStops = restStops
    .map((stop, index) => {
      const start = Number(
        stop?.start ?? 0
      );

      const end = Number(
        stop?.end ?? start
      );

      const duration = Number(
        stop?.duration ??
          end - start
      );

      const distanceAtRest =
        distanceAtEventTime(
          events,
          start,
          routeDistance,
          Number(totalDrivingHours)
        );

      const geometryTargetMiles =
        routeDistance > 0
          ? (distanceAtRest / routeDistance) *
            geometryDistanceMiles
          : 0;

      const position =
        positionAtDistance(
          positions,
          cumulativeDistances,
          geometryTargetMiles
        );

      return {
        index,
        start,
        end,
        duration,
        distanceAtRest,
        position,
      };
    })
    .filter(Boolean);


  return (
    <section className="trip-map-section">

      <div className="trip-map-header">

        <div>
          <span className="trip-map-label">
            ROUTE MAP
          </span>

          <h2>
            Trip Route
          </h2>

          <p>
            Planned route with pickup,
            dropoff, fuel and rest stops.
          </p>
        </div>


        <div className="trip-map-legend">

          <div>
            <span className="legend-dot current" />
            Current
          </div>

          <div>
            <span className="legend-dot pickup" />
            Pickup
          </div>

          <div>
            <span className="legend-dot dropoff" />
            Dropoff
          </div>

          <div>
            <span className="legend-dot fuel" />
            Fuel
          </div>

          <div>
            <span className="legend-dot rest" />
            Rest
          </div>

        </div>

      </div>


      <div className="trip-map-container">

        <MapContainer
          center={currentLocation}
          zoom={5}
          scrollWheelZoom={true}
          className="trip-map"
        >

          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />


          <FitRoute
            positions={positions}
          />


          {/* Main route */}

          <Polyline
            positions={positions}
            pathOptions={{
              color: "#ff4f9a",
              weight: 5,
              opacity: 0.85,
            }}
          />


          {/* =========================
              FUEL STOPS
              ========================= */}

          {validFuelStops.map((stop) => (
            <Marker
              key={`fuel-${stop.index}`}
              position={stop.position}
              icon={fuelIcon}
            >
              <Popup>

                <strong>
                  Fuel Stop #{stop.index + 1}
                </strong>

                <br />

                Approx.{" "}
                {stop.distanceAtFuel.toFixed(0)}
                {" "}mi

              </Popup>
            </Marker>
          ))}


          {/* =========================
              REST STOPS
              ========================= */}

          {validRestStops.map((stop) => (
            <Marker
              key={`rest-${stop.index}`}
              position={stop.position}
              icon={restIcon}
            >
              <Popup>

                <strong>
                  Rest Stop #{stop.index + 1}
                </strong>

                <br />

                Rest{" "}
                {stop.duration.toFixed(1)}
                {" "}hrs

                <br />

                Approx.{" "}
                {stop.distanceAtRest.toFixed(0)}
                {" "}mi

              </Popup>
            </Marker>
          ))}


          {/* =========================
              CURRENT LOCATION
              ========================= */}

          <Marker
            position={currentLocation}
            icon={currentIcon}
            zIndexOffset={3000}
          >
            <Popup>

              <strong>
                Current Location
              </strong>

            </Popup>

          </Marker>


          {/* =========================
              PICKUP
              ========================= */}

          {pickupLocation && (
            <Marker
              position={pickupLocation}
              icon={pickupIcon}
              zIndexOffset={10000}
            >
              <Popup>

                <strong>
                  Pickup
                </strong>

                <br />

                {route?.pickup?.display_name ||
                  "Pickup Location"}

              </Popup>

            </Marker>
          )}


          {/* =========================
              DROPOFF
              ========================= */}

          <Marker
            position={dropoffLocation}
            icon={dropoffIcon}
            zIndexOffset={10000}
          >
            <Popup>

              <strong>
                Dropoff
              </strong>

              <br />

              {route?.dropoff?.display_name ||
                "Dropoff Location"}

            </Popup>

          </Marker>


        </MapContainer>

      </div>

    </section>
  );
}


export default TripMap;