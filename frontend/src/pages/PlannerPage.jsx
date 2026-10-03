import { useState } from "react";

import {
  MapPin,
  Route,
  Clock3,
  Fuel,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";

import spotterLogo from "../assets/spotter.png";

import "./PlannerPage.css";

import ELDLog from "../components/ELDLog";
import TripMap from "../components/TripMap";

const LOCATIONS = [
  "Los Angeles, CA",
  "Las Vegas, NV",
  "Phoenix, AZ",
  "Denver, CO",
  "Dallas, TX",
  "Houston, TX",
  "Chicago, IL",
  "New York, NY",
  "Atlanta, GA",
  "Miami, FL",
  "Seattle, WA",
  "San Francisco, CA",
  "Salt Lake City, UT",
  "Portland, OR",
  "Kansas City, MO",
];

function PlannerPage() {
  const [formData, setFormData] = useState({
    current_location: "",
    pickup_location: "",
    dropoff_location: "",
    cycle_used_hours: "",
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const apiResponse = await fetch(
        "http://127.0.0.1:8000/api/trips/plan/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            current_location: formData.current_location,
            pickup_location: formData.pickup_location,
            dropoff_location: formData.dropoff_location,
            cycle_used_hours: Number(formData.cycle_used_hours),
          }),
        }
      );

      const data = await apiResponse.json();

      if (!apiResponse.ok) {
        throw new Error(
          data.error || "Unable to generate the trip plan."
        );
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const trip = result?.trip || result;

  return (
    <main className="planner-page">
      {/* HEADER */}
      <header className="planner-header">
        <div className="planner-logo">
          <div className="planner-logo-box">
            <img
              src={spotterLogo}
              alt="Spotter"
              className="planner-logo-image"
            />
          </div>

          <strong>SPOTTER</strong>
        </div>

        <div className="planner-status">
          <span></span>
          TRIP PLANNER
        </div>
      </header>

      {/* CONTENT */}
      <section className="planner-content">
        <div className="planner-intro">
          <div className="planner-label">
            TRIP PLANNER
          </div>

          <h1>
            Plan your trip.
            <br />
            <span>Drive smarter.</span>
          </h1>

          <p>
            Enter your route details and Spotter will calculate
            the distance, driving time, breaks, rest stops and
            HOS-compliant trip schedule.
          </p>
        </div>

        {/* MAIN GRID */}
        <div className="planner-grid">
          {/* FORM */}
          <section className="planner-card form-card">
            <div className="card-heading">
              <div className="card-heading-top">
                <div className="card-number">
                  01
                </div>

                <div>
                  <h2>Trip details</h2>
                  <p>Tell us where you're going.</p>
                </div>
              </div>
            </div>

            <form
              className="planner-form"
              onSubmit={handleSubmit}
            >
              {/* CURRENT */}
              <div className="form-field">
                <label htmlFor="current_location">
                  Current location
                </label>

                <div className="select-wrapper">
                  <MapPin size={17} />

                  <select
                    id="current_location"
                    name="current_location"
                    value={formData.current_location}
                    onChange={handleChange}
                    required
                  >
                    <option value="">
                      Select current location
                    </option>

                    {LOCATIONS.map((location) => (
                      <option
                        key={`current-${location}`}
                        value={location}
                      >
                        {location}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* PICKUP */}
              <div className="form-field">
                <label htmlFor="pickup_location">
                  Pickup location
                </label>

                <div className="select-wrapper">
                  <Route size={17} />

                  <select
                    id="pickup_location"
                    name="pickup_location"
                    value={formData.pickup_location}
                    onChange={handleChange}
                    required
                  >
                    <option value="">
                      Select pickup location
                    </option>

                    {LOCATIONS.map((location) => (
                      <option
                        key={`pickup-${location}`}
                        value={location}
                      >
                        {location}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* DROPOFF */}
              <div className="form-field">
                <label htmlFor="dropoff_location">
                  Dropoff location
                </label>

                <div className="select-wrapper">
                  <MapPin size={17} />

                  <select
                    id="dropoff_location"
                    name="dropoff_location"
                    value={formData.dropoff_location}
                    onChange={handleChange}
                    required
                  >
                    <option value="">
                      Select dropoff location
                    </option>

                    {LOCATIONS.map((location) => (
                      <option
                        key={`dropoff-${location}`}
                        value={location}
                      >
                        {location}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* CYCLE HOURS */}
              <div className="form-field">
                <label htmlFor="cycle_used_hours">
                  Cycle hours already used
                </label>

                <div className="input-with-unit">
                  <Clock3 size={17} />

                  <input
                    id="cycle_used_hours"
                    name="cycle_used_hours"
                    type="number"
                    min="0"
                    max="70"
                    step="0.1"
                    placeholder="e.g. 20"
                    value={formData.cycle_used_hours}
                    onChange={handleChange}
                    required
                  />

                  <span>HRS</span>
                </div>
              </div>

              {/* ERROR */}
              {error && (
                <div className="planner-error">
                  {error}
                </div>
              )}

              {/* BUTTON */}
              <button
                className="plan-button"
                type="submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    Calculating route...
                  </>
                ) : (
                  <>
                    Generate trip plan
                    <ArrowRight size={18} />
                  </>
                )}
              </button>
            </form>
          </section>
        </div>

        {/* RESULTS */}
        {result && (
          <>
            <section className="trip-results">
              {/* DISTANCE */}
              <div className="result-card">
                <Route size={19} />

                <span>DISTANCE</span>

                <strong>
                  {Number(
                    trip?.distance_miles || 0
                  ).toFixed(1)}{" "}
                  mi
                </strong>
              </div>

              {/* DRIVING TIME */}
              <div className="result-card">
                <Clock3 size={19} />

                <span>DRIVING TIME</span>

                <strong>
                  {Number(
                    trip?.driving_hours || 0
                  ).toFixed(1)}{" "}
                  hrs
                </strong>
              </div>

              {/* HOS STATUS */}
              <div className="result-card">
                <ShieldCheck size={19} />

                <span>HOS STATUS</span>

                <strong className="status-value">
                  {trip?.status || "PLANNED"}
                </strong>
              </div>

              {/* FUEL STOPS */}
              <div className="result-card">
                <Fuel size={19} />

                <span>FUEL STOPS</span>

                <strong>
                  {trip?.fuel_stops?.length || 0}
                </strong>
              </div>

              {/* REST STOPS */}
              <div className="result-card">
                <Clock3 size={19} />

                <span>REST STOPS</span>

                <strong>
                  {trip?.rest_stops?.length || 0}
                </strong>
              </div>
            </section>

            {/* REAL ROUTE MAP */}
            {result?.route && (
   <TripMap
  route={result.route}
  fuelStops={trip?.fuel_stops || []}
  restStops={trip?.rest_stops || []}
  events={trip?.events || []}
  distanceMiles={trip?.distance_miles || 0}
  drivingHours={trip?.driving_hours || 0}
/>
            )}

            {/* ELD DAILY LOGS */}
            {trip?.daily_logs?.length > 0 && (
              <ELDLog
                dailyLogs={trip.daily_logs}
              />
            )}
          </>
        )}
      </section>
    </main>
  );
}

export default PlannerPage;