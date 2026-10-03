# 🚛 Spotter Truck Trip Planner

A full-stack truck trip planning application built as part of the **Spotter Full Stack Developer Assessment**.

The application plans a truck trip based on **FMCSA Hours-of-Service (HOS) rules**, calculates the driving route and duration, schedules required breaks and rest periods, plans fuel stops, tracks the driver's cycle hours, and generates **ELD Daily Log Sheets** for the resulting trip schedule.

### 🌐 Live Demo

**Frontend:** [Spotter Trip Planner](https://spotter-full-stack-three.vercel.app)

**Backend API:** [Spotter Backend](https://spotter-full-stack-9bzx.onrender.com)

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

- Fuel interval: **1,000 miles**
- Fuel duration: **30 minutes**

The system calculates the appropriate mileage markers and integrates the fuel stops into the trip schedule.

---

## 💤 Rest & Off-Duty Scheduling

The HOS engine automatically schedules required off-duty periods when the driver's available driving or duty time is exhausted.

The scheduling engine accounts for:

- Maximum driving time
- Duty window
- Required breaks
- Off-duty resets
- Cycle limitations

---

## ☕ 30-Minute Breaks

The system tracks cumulative driving time and schedules a 30-minute break when the required threshold is reached.

The current rule implemented is:

- Break required after **8 cumulative driving hours**
- Break duration: **30 minutes**

---

## 🔄 34-Hour Restart

The scheduling engine supports a 34-hour restart when required by the driver's cycle limitations.

- Restart duration: **34 hours**

This allows the planner to restore the available cycle hours when appropriate.

---

## 📊 70/8 Cycle Tracking

The application tracks the driver's available cycle hours.

The current cycle rule is:

**70 hours / 8 consecutive days**

The user provides the number of hours already used in the current cycle.

The planner then calculates the remaining available cycle hours.

---

## 📋 ELD Daily Logs

The generated trip timeline is converted into daily ELD logs.

Each day is represented as a 24-hour timeline showing the driver's status throughout the day.

Supported statuses include:

- Off Duty
- Sleeper Berth
- Driving
- On Duty / Not Driving

The UI provides:

- Daily summary
- Driving hours
- On-duty hours
- Off-duty hours
- 24-hour timeline
- Individual trip events

---

# 🧠 HOS Rules Implemented

The application implements the following HOS assumptions and constraints for property-carrying drivers.

## Maximum Driving Time

**11 hours**

The driver cannot exceed 11 hours of driving before the applicable rest period.

---

## 14-Hour Duty Window

**14 consecutive hours**

The driver has a 14-hour duty window after starting the work period.

Off-duty time does not extend the 14-hour window.

---

## 30-Minute Break

**After 8 cumulative driving hours**

A 30-minute break is scheduled when the driver reaches the required cumulative driving threshold.

---

## 10-Hour Off-Duty Reset

**10 consecutive hours off duty**

A full new driving window requires the driver to complete the required off-duty period.

---

## 70/8 Cycle

**70 on-duty hours / 8 consecutive days**

The system tracks the driver's current cycle usage and calculates remaining cycle availability.

---

## 34-Hour Restart

**34 consecutive hours**

A 34-hour restart can be scheduled when necessary to reset the driver's cycle availability.

---

## Fueling

- Every **1,000 miles**
- **30 minutes** per fuel stop

---

## Pickup

**1 hour**

---

## Drop-off

**1 hour**

---

# 🏗️ System Architecture

The application follows a frontend/backend architecture.

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   React Frontend    │
                         │                     │
                         │  Trip Planner UI    │
                         │  Interactive Map    │
                         │  ELD Daily Logs     │
                         └──────────┬──────────┘
                                    │
                         POST /api/trips/plan/
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Django REST      │
                         │        API          │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
             ┌────────────┐  ┌────────────┐  ┌──────────────┐
             │ Geocoding  │  │  Routing   │  │  HOS Engine  │
             │ Nominatim  │  │    OSRM    │  │              │
             └────────────┘  └────────────┘  └──────┬───────┘
                                                    │
                                                    ▼
                                           ┌────────────────┐
                                           │ Trip Schedule  │
                                           └───────┬────────┘
                                                   │
                                  ┌────────────────┴────────────────┐
                                  ▼                                 ▼
                         ┌─────────────────┐               ┌─────────────────┐
                         │  Route / Stops  │               │    ELD Logs     │
                         │                 │               │                 │
                         │ Fuel            │               │ Day 1           │
                         │ Rest            │               │ Day 2           │
                         │ Pickup          │               │ Day 3 ...       │
                         │ Drop-off        │               └─────────────────┘
                         └─────────────────┘
```

---

# 🔄 Trip Planning Flow

```text
User Input
    │
    ▼
Validate Input
    │
    ▼
Geocode Locations
    │
    ▼
Calculate Route
    │
    ▼
Calculate Distance & Driving Time
    │
    ▼
Apply HOS Constraints
    │
    ├── Driving Limit
    ├── 14-Hour Window
    ├── 30-Minute Break
    ├── 10-Hour Reset
    ├── 70/8 Cycle
    └── 34-Hour Restart
    │
    ▼
Add Fuel Stops
    │
    ▼
Add Pickup / Drop-off Time
    │
    ▼
Generate Trip Events
    │
    ▼
Generate Daily ELD Logs
    │
    ▼
Return JSON Response
    │
    ▼
React UI
```

---

# 🛠️ Tech Stack

## Frontend

- React
- Vite
- React Router
- React Leaflet
- Leaflet
- CSS

## Backend

- Python
- Django
- Django REST Framework
- Requests

## Routing & Geocoding

- OpenStreetMap
- Nominatim
- OSRM

## Deployment

- Vercel
- Render

---

# 📁 Project Structure

```text
spotter-full-stack/
│
├── backend/
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── trips/
│   │   ├── geocoding.py
│   │   ├── hos_engine.py
│   │   ├── routing.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── ...
│   │
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   │
│   ├── src/
│   │   │
│   │   ├── components/
│   │   │   ├── ELDLog.jsx
│   │   │   ├── ELDLog.css
│   │   │   ├── TripMap.jsx
│   │   │   └── TripMap.css
│   │   │
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── LandingPage.css
│   │   │   ├── PlannerPage.jsx
│   │   │   ├── PlannerPage.css
│   │   │   └── ...
│   │   │
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

# 🌐 External Services

## OpenStreetMap / Nominatim

Nominatim is used to convert human-readable locations into geographic coordinates.

Example:

```text
Los Angeles, CA
        ↓
Latitude / Longitude
```

---

## OSRM

OSRM is used to calculate the driving route between geographic coordinates.

The application retrieves:

- Route distance
- Route duration
- Route geometry

The geometry is then rendered on the frontend using Leaflet.

---

# 🔌 API

## Plan Trip

```http
POST /api/trips/plan/
```

---

## Request

```json
{
  "current_location": "Los Angeles, CA",
  "pickup_location": "Las Vegas, NV",
  "dropoff_location": "Phoenix, AZ",
  "cycle_used_hours": 10
}
```

---

## Response Structure

The API returns the following main sections:

```json
{
  "success": true,
  "input": {},
  "route": {},
  "trip": {}
}
```

The `route` object contains:

- Current location
- Pickup location
- Drop-off location
- Route legs
- Total distance
- Total duration

The `trip` object contains:

- Distance
- Driving hours
- Remaining driving hours
- Remaining cycle hours
- Total trip duration
- Fuel stops
- Rest stops
- Breaks
- Cycle restarts
- Trip events
- Status
- Warnings
- Daily ELD logs

---

# 🧪 Testing

The HOS engine includes an automated test suite covering the trip planning logic and edge cases.

Run the backend tests with:

```bash
cd backend
python manage.py test trips
```

The current test suite contains:

**75 tests**

The tests cover areas including:

- Driving limits
- Duty windows
- Required breaks
- Off-duty resets
- Fuel stop calculations
- Cycle-hour calculations
- Cycle restarts
- Trip scheduling
- Edge cases
- ELD-related scheduling behavior

---

# 🖥️ Running the Project Locally

## Prerequisites

Make sure the following are installed:

- Python 3
- Node.js
- npm
- Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/ghena03/spotter-full-stack.git
cd spotter-full-stack
```

---

# Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

### Windows

Activate the virtual environment:

```powershell
..\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

Backend:

```text
http://127.0.0.1:8000
```

---

# Frontend Setup

Open a second terminal.

Navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🔗 Connecting Frontend and Backend

The frontend sends requests to:

```text
http://127.0.0.1:8000/api/trips/plan/
```

During local development, Django is configured to allow requests from the Vite development server.

The frontend and backend can therefore run independently:

```text
React / Vite
localhost:5173
       │
       ▼
Django API
127.0.0.1:8000
```

---

# 🗺️ Supported Locations

The current UI provides a predefined list of major US locations including:

- Los Angeles, CA
- Las Vegas, NV
- Phoenix, AZ
- Denver, CO
- Dallas, TX
- Houston, TX
- Chicago, IL
- New York, NY
- Atlanta, GA
- Miami, FL
- Seattle, WA
- San Francisco, CA
- Salt Lake City, UT
- Portland, OR
- Kansas City, MO

The backend itself accepts location strings and geocodes them using Nominatim.

---

# 📋 ELD Log Generation

The HOS engine first generates a chronological list of trip events.

Example event types include:

```text
Pickup
Driving
Break
Fuel
Off Duty
Restart
Drop-off
```

These events are then transformed into daily ELD logs.

Each event contains timing information that allows the frontend to render the driver's duty status across a 24-hour period.

---

# 📊 Trip Status

The generated trip contains a planning status.

For example:

```text
PLANNED
```

Warnings can also be returned when the planner encounters a scheduling constraint or other relevant condition.

---

# 🎨 Frontend UI

The frontend consists of two primary pages.

## Landing Page

The landing page introduces the Spotter Trip Planner and provides an entry point to the planner.

## Planner Page

The planner contains:

### Trip Input

Users select:

- Current location
- Pickup location
- Drop-off location
- Cycle hours already used

### Trip Summary

The system displays:

- Total distance
- Driving time
- HOS status
- Fuel stops
- Rest stops

### Route Map

The map visualizes:

- Current position
- Pickup
- Drop-off
- Fuel stops
- Rest stops
- Driving route

### ELD Daily Logs

The final section displays the generated daily driver logs.

---

# ⚙️ Design Decisions

## Separate HOS Engine

The HOS scheduling logic is implemented separately from the API view layer.

This makes the core scheduling logic easier to:

- Test
- Maintain
- Extend
- Reuse

---

## External Routing Service

Routing is delegated to OSRM instead of implementing route calculation inside the application.

This allows the application to focus on:

- Trip planning
- HOS compliance logic
- Scheduling
- ELD generation

---

## Frontend Map Rendering

Route geometry is returned by the backend and rendered by the React frontend using Leaflet.

This keeps routing calculations on the backend while allowing the frontend to provide an interactive visualization.

---

## Event-Based Scheduling

The trip is represented as a sequence of events.

This makes it possible to transform the same schedule into:

- Trip summaries
- Map markers
- Daily ELD logs
- Status calculations
- Future reporting features

---

# ⚠️ Assumptions & Limitations

This assessment implementation uses simplified assumptions.

Current assumptions include:

- Property-carrying driver
- 70/8 cycle
- No adverse driving conditions
- Pickup duration of 1 hour
- Drop-off duration of 1 hour
- Fuel stop every 1,000 miles
- Fueling duration of 30 minutes

The application is designed as a technical assessment implementation and should not be considered a replacement for:

- Certified ELD software
- Commercial dispatch systems
- Carrier-specific HOS policies
- Professional compliance systems

Actual operational use should always verify the applicable regulations and carrier requirements.

---

# 🚀 Deployment

The intended production architecture is:

```text
                 Internet
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
       Vercel               Render
          │                   │
          ▼                   ▼
     React Frontend      Django API
                              │
                   ┌──────────┴──────────┐
                   ▼                     ▼
               Nominatim                OSRM
```

### Frontend

The React/Vite application can be deployed to:

**Vercel**

### Backend

The Django application can be deployed to:

**Render**

The production frontend should point its API requests to the deployed Django backend URL rather than:

```text
http://127.0.0.1:8000
```

---

# 🔐 Environment & Security

Sensitive configuration should not be committed to Git.

The project ignores environment files such as:

```text
.env
.env.*
```

Production environment variables should be configured through the hosting provider.

---

# 📈 Future Improvements

Possible future improvements include:

- 🚦 Live traffic-aware routing
- 🌦️ Weather-aware trip planning
- 🚛 Truck-specific route restrictions
- ⛽ Real fuel station locations
- 👤 Driver profiles
- 🧑‍🤝‍🧑 Multiple-driver trips
- 📚 Trip history
- 🔐 User authentication
- 🗄️ PostgreSQL persistence
- 📊 Analytics dashboard
- 🔔 Trip alerts
- 📱 Improved mobile experience
- 🧾 Exportable ELD logs
- 🔄 More advanced schedule optimization
- 🧪 Expanded integration testing

---

# 📚 Regulatory Reference

The HOS rules implemented in this project are based on the FMCSA Hours-of-Service requirements for property-carrying drivers.

Official FMCSA information:

https://www.fmcsa.dot.gov/regulations/hours-service

---

# 👩‍💻 Author

**Ghena Ali**

Computer Engineering Graduate

GitHub:

https://github.com/ghena03

---

# 📄 Project Purpose

This project was developed as part of the **Spotter Full Stack Developer Technical Assessment**.

The primary goal was to demonstrate the ability to build a complete application covering:

- Frontend development
- Backend API development
- Business-rule implementation
- External API integration
- Route calculation
- Scheduling algorithms
- Automated testing
- Data visualization
- ELD log generation
- Full-stack application architecture
- Production deployment