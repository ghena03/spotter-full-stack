# Spotter Truck Trip Planner

A full-stack truck trip planning application built as part of the Spotter Full Stack Developer assessment.

The application plans a truck trip based on **FMCSA Hours-of-Service (HOS) regulations**, calculates the route and driving time, identifies required fuel/rest stops, and generates **ELD Daily Log Sheets** for the planned trip.

---

## Features

- 🚛 Truck trip planning
- 📍 Current location, pickup, and drop-off locations
- 🗺️ Route calculation using OpenStreetMap-based services
- 📏 Total route distance
- ⏱️ Estimated driving duration
- ⛽ Automatic fuel-stop planning
- 💤 HOS-compliant rest/off-duty periods
- ☕ 30-minute HOS break handling
- 🔄 34-hour cycle restart handling
- 📊 70/8 cycle-hour tracking
- 📋 ELD Daily Log generation
- 🗺️ Interactive route map
- 📱 Responsive React frontend
- ⚡ Django REST API backend

---

## Tech Stack

### Frontend

- React
- Vite
- React Router
- React Leaflet
- Leaflet
- CSS

### Backend

- Python
- Django
- Django REST Framework
- Requests

### Routing & Geocoding

- OpenStreetMap
- Nominatim
- OSRM

### Deployment

- Frontend: Vercel
- Backend: Render

---

## Project Structure

```text
spotter-full-stack/
│
├── backend/
│   ├── config/
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
│   ├── src/
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
│   │   │   └── PlannerPage.css
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
└── README.md