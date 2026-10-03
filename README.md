# 🚛 Spotter Truck Trip Planner

A full-stack truck trip planning application built as part of the **Spotter Full Stack Developer Assessment**.

The application plans a truck trip based on **FMCSA Hours-of-Service (HOS) rules**, calculates the driving route and duration, schedules required breaks and rest periods, plans fuel stops, tracks the driver's cycle hours, and generates **ELD Daily Log Sheets** for the resulting trip schedule.

---

## 📌 Overview

The Spotter Truck Trip Planner is designed to help a dispatcher or driver understand how a trip can be completed while respecting operational and Hours-of-Service constraints.

The user provides:

- Current driver location
- Pickup location
- Drop-off location
- Hours already used in the driver's current cycle

The system then:

1. Geocodes the provided locations.
2. Calculates the driving route.
3. Calculates total distance and estimated driving time.
4. Applies the HOS scheduling rules.
5. Adds pickup and drop-off service time.
6. Schedules required 30-minute breaks.
7. Schedules off-duty rest periods when necessary.
8. Tracks the 70/8 cycle limit.
9. Adds fuel stops based on mileage.
10. Generates a complete trip timeline.
11. Converts the timeline into daily ELD logs.
12. Displays the route and trip information in an interactive React interface.

---

# ✨ Features

## 🚛 Trip Planning

Users can select:

- Current location
- Pickup location
- Drop-off location
- Current cycle hours used

The planner generates a complete schedule from the driver's current position through pickup and finally to the drop-off location.

---

## 🗺️ Interactive Route Map

The application displays the calculated route using an interactive Leaflet map.

The map includes:

- Current location
- Pickup location
- Drop-off location
- Fuel stops
- Rest stops
- Route geometry

The route is calculated using OpenStreetMap-based routing services.

---

## 📏 Distance & Driving Time

The system calculates:

- Distance from current location to pickup
- Distance from pickup to drop-off
- Total trip distance
- Estimated driving duration

Distances are converted to miles and driving durations to hours for the HOS engine.

---

## ⛽ Fuel Stop Planning

Fuel stops are automatically scheduled based on mileage.

The current planning assumption is:

```text
Fuel interval: 1,000 miles
Fuel duration: 30 minutes