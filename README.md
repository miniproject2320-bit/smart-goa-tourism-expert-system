# Goa Smart Tourism Expert System

A Python + Streamlit mini-project built from the supplied project plan and CSV files.

## Features
- Six core preference inputs: trip duration, season, vibe(s), group, budget and transport
- Knowledge base from the supplied 79-place dataset
- Accommodation suggestions from the supplied 99-record stay dataset
- Forward-chaining-style rule log with explanations
- Ranked destinations and day-wise itinerary
- A* pathfinding demonstration using a coordinate-neighbour graph

## Run locally
1. Install Python 3.10 or later.
2. Extract this folder and open a terminal in it.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```

## Important accuracy note
The supplied place CSV contains coordinates but not a verified road-network edge list. The A* demo therefore uses a nearest-neighbour graph based on straight-line distances. This is an educational demonstration, not reliable road navigation. For the final project, replace `make_graph()` edges and weights with verified road links and travel-time/distance values, then compare A* against Dijkstra as specified in the project plan.

Opening hours, live closures, weather, festival dates and prices are not live-verified. The app warns users to verify current conditions.
