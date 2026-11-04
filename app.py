
import math
import heapq
import html
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import pydeck as pdk
import streamlit as st
# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Explore Goa | Smart Tourism Guide",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = Path(__file__).resolve().parent
PLACES_FILE = BASE_DIR / "Goa_Places_Merged (2).csv"
STAYS_FILE = BASE_DIR / "output.csv"


# ============================================================
# 2. ITINERARY RULE CONFIGURATION
# ============================================================

VIBE_CATEGORIES = {
    "Beach & chill": ["Beaches"],
    "Heritage": ["Heritage & Religious"],
    "Adventure": ["Nature & Adventure"],
    "Nature": ["Nature & Adventure"],
    "Food & markets": ["Culture, Markets & Nightlife"],
    "Nightlife": ["Culture, Markets & Nightlife"],
    "Spiritual": ["Heritage & Religious"],
}

ALL_CATEGORIES = {
    c for cats in VIBE_CATEGORIES.values() for c in cats
}

GROUPS = ["Solo", "Couple", "Family", "Friends"]

SEASONS = [
    "Winter (Nov-Feb)",
    "Summer (Mar-May)",
    "Monsoon (Jun-Sep)"
]

BUDGETS = ["Low", "Mid", "High"]

TRANSPORTS = [
    "Own scooter or car",
    "No vehicle"
]

REGIONS = [
    "North Goa",
    "Central Goa",
    "South Goa"
]

COST_SCORE = {
    "Free / very low": 5,
    "Budget": 4,
    "Moderate": 3,
    "Expensive": 2,
    "Very expensive": 1
}

DURATIONS = {
    "1–2 days": 2,
    "3–4 days": 4,
    "5 days": 5,
    "6 days": 6,
    "7 days": 7,
    "8 days": 8,
    "9 days": 9,
    "10 days": 10
}

DEFAULT_END = {
    "North Goa": "South Goa",
    "Central Goa": "South Goa",
    "South Goa": "North Goa"
}

# North -> Central -> South and reverse
THREE_REGION_SPLITS = {
    6: [2, 2, 2],
    7: [2, 3, 2],
    8: [3, 2, 3],
    9: [3, 3, 3],
    10: [3, 4, 3]
}

# Neighbouring regions
TWO_REGION_SPLITS = {
    6: [3, 3],
    7: [3, 4],
    8: [4, 4],
    9: [4, 5],
    10: [5, 5]
}

# Same starting and ending region
ROUND_TRIP_SPLITS = {
    6: [2, 2, 2],
    7: [3, 2, 2],
    8: [3, 2, 3],
    9: [3, 3, 3],
    10: [4, 3, 3]
}

LONG_TRIP_RULES = {
    6: "6-day trip: three 2-day regional blocks.",
    7: "7-day trip: extra time for a relaxed regional experience.",
    8: "8-day trip: balanced exploration across regions.",
    9: "9-day trip: three 3-day regional blocks.",
    10: "10-day trip: complete Goa exploration with extended regional stays."
}


# ============================================================
# 3. IMAGES
# ============================================================

CATEGORY_IMAGES = {
    "Beaches":
        "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1000&q=85",

    "Heritage & Religious":
        "https://images.unsplash.com/photo-1606293926075-69a00db_d6a3?auto=format&fit=crop&w=1000&q=85",

    "Nature & Adventure":
        "https://images.unsplash.com/photo-1472396961693-142e6e269027?auto=format&fit=crop&w=1000&q=85",

    "Culture, Markets & Nightlife":
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1000&q=85"
}

DEFAULT_IMAGE = (
    "https://images.unsplash.com/photo-1500375592092-40eb2168fd21"
    "?auto=format&fit=crop&w=1000&q=85"
)


# ============================================================
# 4. DESIGN
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --green: #00aa6c;
    --dark: #17332c;
    --muted: #66756f;
    --line: #e5ebe7;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: linear-gradient(
        135deg,
        #EAF6F5 0%,
        #F5FAF8 55%,
        #FFF5E9 100%
    );
    color: #294B55;
}

.block-container {
    max-width: 1320px;
    padding-top: 1.1rem;
    padding-bottom: 3rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.brand {
    font-family: Manrope, sans-serif;
    font-weight: 800;
    font-size: 1.4rem;
    color: #17332c;
    letter-spacing: -.04em;
    margin-bottom: 1rem;
}

.brand span {
    color: #00a86b;
}

.hero {
    margin-top: .5rem;
    border-radius: 26px;
    min-height: 340px;
    padding: 2.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    color: white;

    background:
        linear-gradient(
            90deg,
            rgba(5,35,28,.85),
            rgba(5,35,28,.20)
        ),
        url('https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1900&q=90')
        center 48% / cover;

    box-shadow: 0 12px 35px rgba(7,59,76,.12);
}

.hero .eyebrow {
    font-size: .78rem;
    letter-spacing: .13em;
    text-transform: uppercase;
    font-weight: 800;
    color: #d5fff0;
}

.hero h1 {
    font-family: Manrope, sans-serif;
    font-size: clamp(2.4rem,5vw,4.3rem);
    line-height: 1.05;
    max-width: 720px;
    color: white !important;
    margin: .7rem 0;
    letter-spacing: -.05em;
}

.hero p {
    font-size: 1.05rem;
    max-width: 650px;
    color: #f0fff9;
}

h1, h2, h3 {
    color: #174B60 !important;
    font-weight: 750;
}

.section-title {
    font-family: Manrope, sans-serif;
    font-weight: 800;
    color: #17332c;
    font-size: 1.75rem;
    margin: .5rem 0 .3rem;
}

.section-sub {
    color: #687871;
    margin-bottom: 1rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #DFF1EF,
        #EEF7F3
    );
    border-right: 1px solid #D4E9E5;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #16343b !important;
}

.stButton > button,
.stDownloadButton > button,
.stLinkButton > a {
    border-radius: 12px;
    font-weight: 700;
    min-height: 2.7rem;
}

.stButton > button {
    background: linear-gradient(
        135deg,
        #168C88,
        #28A69B
    );
    color: white;
    border: none;
}

.stButton > button:hover {
    background: #11736F;
    color: white;
}

.stButton > button[kind="primary"] {
    background: #00a86b;
    color: white;
    border: none;
}

div[data-testid="stMetric"] {
    background: #f5faf7;
    border: 1px solid #e3eee7;
    padding: 1rem;
    border-radius: 16px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,.94);
    border: 1px solid #E0ECE8;
    border-radius: 16px;
    box-shadow: 0 5px 18px rgba(36,85,79,.06);
}

[data-testid="stTabs"] button {
    font-weight: 700;
}

[data-testid="stExpander"] {
    border: 1px solid #e0ece9;
    border-radius: 14px;
}

.stImage img {
    border-radius: 14px;
}

.small-note {
    color: #718079;
    font-size: .86rem;
}

@media(max-width:700px) {
    .block-container {
        padding: .6rem .7rem 2rem;
    }

    .hero {
        min-height: 260px;
        padding: 1.4rem;
        border-radius: 20px;
    }

    .hero p {
        font-size: .95rem;
    }
}

</style>

<div class="brand">🌴 goa<span>guide</span></div>

<div class="hero">
    <div class="eyebrow">
        Discover · Explore · Experience
    </div>

 
    
""", unsafe_allow_html=True)

st.info(
    "Travel smarter, explore thoughtfully. "
    "This academic prototype uses supplied datasets. "
    "Check live weather, opening hours, prices and local advisories.",
    icon="🌊"
)


# ============================================================
# 5. LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    if not PLACES_FILE.exists():
        raise FileNotFoundError(
            f"Missing file: {PLACES_FILE.name}"
        )

    places = pd.read_csv(PLACES_FILE)

    places.columns = [
        str(c).strip() for c in places.columns
    ]

    required = [
        "Place",
        "Region",
        "Category",
        "Cost",
        "Latitude",
        "Longitude"
    ]

    missing = [
        c for c in required if c not in places.columns
    ]

    if missing:
        raise ValueError(
            "Missing columns: " + ", ".join(missing)
        )

    numeric_cols = [
        "Latitude",
        "Longitude",
        "Composite score (0-5)",
        "Average suitability",
        "Review score (5=best)",
        "Popularity score (5=most)"
    ]

    for col in numeric_cols:
        if col in places.columns:
            places[col] = pd.to_numeric(
                places[col],
                errors="coerce"
            )

    if STAYS_FILE.exists():

        stays = pd.read_csv(STAYS_FILE)

        stays.columns = [
            str(c).strip() for c in stays.columns
        ]

        for col in ["latitude", "longitude"]:
            if col in stays.columns:
                stays[col] = pd.to_numeric(
                    stays[col],
                    errors="coerce"
                )

    else:
        stays = pd.DataFrame()

    return places, stays


try:
    places, stays = load_data()

except Exception as exc:
    st.error(f"Unable to load project data: {exc}")
    st.stop()


# ============================================================
# 6. HELPER FUNCTIONS
# ============================================================

def safe_text(value, fallback="Details coming soon"):

    if pd.isna(value):
        return fallback

    value = str(value).strip()

    if value.lower() in ["", "nan", "none"]:
        return fallback

    return value


def image_for(category):
    return CATEGORY_IMAGES.get(str(category), DEFAULT_IMAGE)


def haversine(lat1, lon1, lat2, lon2):

    radius = 6371.0

    p1 = math.radians(float(lat1))
    p2 = math.radians(float(lat2))

    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return 2 * radius * math.asin(
        math.sqrt(max(0, min(1, a)))
    )


# ============================================================
# A* SEARCH ALGORITHM
# ============================================================

def astar_route(places, start_name, goal_name, k=5):
    """
    Find an approximate shortest path between two places.
    Uses a k-nearest-neighbour graph and Haversine distances.
    """

    df = places.dropna(
        subset=["Latitude", "Longitude"]
    ).copy()

    df["Latitude"] = pd.to_numeric(
        df["Latitude"], errors="coerce"
    )
    df["Longitude"] = pd.to_numeric(
        df["Longitude"], errors="coerce"
    )

    df = df.dropna(
        subset=["Latitude", "Longitude"]
    ).drop_duplicates(subset=["Place"]).reset_index(drop=True)

    if len(df) < 2:
        return None, 0.0

    # Map destination names to row indexes
    name_to_index = {
        str(row["Place"]): i
        for i, row in df.iterrows()
    }

    if start_name not in name_to_index:
        return None, 0

    if goal_name not in name_to_index:
        return None, 0

    start = name_to_index[start_name]
    goal = name_to_index[goal_name]

    if start == goal:
        return [start_name], 0.0

    # Build a graph connecting each place to its
    # k nearest neighbours.
    graph = {i: {} for i in range(len(df))}

    for i, row in df.iterrows():

        distances = []

        for j, other in df.iterrows():

            if i == j:
                continue

            distance = haversine(
                row["Latitude"],
                row["Longitude"],
                other["Latitude"],
                other["Longitude"]
            )

            distances.append((distance, j))

        for distance, j in sorted(distances)[:k]:

            graph[i][j] = distance
            graph[j][i] = distance

    # A* heuristic: straight-line distance to destination
    def heuristic(node):

        current = df.iloc[node]
        destination = df.iloc[goal]

        return haversine(
            current["Latitude"],
            current["Longitude"],
            destination["Latitude"],
            destination["Longitude"]
        )

    open_list = [(heuristic(start), 0.0, start)]

    came_from = {}
    g_score = {start: 0.0}

    visited = set()

    while open_list:

        _, current_cost, current = heapq.heappop(
            open_list
        )

        if current in visited:
            continue

        visited.add(current)

        if current == goal:

            path = [current]

            while current in came_from:
                current = came_from[current]
                path.append(current)

            path.reverse()

            route_names = [
                str(df.iloc[i]["Place"])
                for i in path
            ]

            return route_names, current_cost

        for neighbour, edge_cost in graph[current].items():

            new_cost = current_cost + edge_cost

            if new_cost < g_score.get(neighbour, float("inf")):

                g_score[neighbour] = new_cost
                came_from[neighbour] = current

                f_score = new_cost + heuristic(neighbour)

                heapq.heappush(
                    open_list,
                    (f_score, new_cost, neighbour)
                )

    return None, 0.0

def maps_url(names, mode="driving"):

    if not names:
        return ""

    if len(names) == 1:
        return (
            "https://www.google.com/maps/search/?api=1&query="
            + quote(f"{names[0]}, Goa, India")
        )

    origin = quote(f"{names[0]}, Goa, India")
    destination = quote(f"{names[-1]}, Goa, India")

    url = (
        "https://www.google.com/maps/dir/"
        f"?api=1&origin={origin}"
        f"&destination={destination}"
        f"&travelmode={mode}"
    )

    if len(names) > 2:

        waypoints = "|".join(
            f"{name}, Goa, India"
            for name in names[1:-1]
        )

        url += "&waypoints=" + quote(
            waypoints,
            safe=""
        )

    return url


def place_card(row, key_suffix):

    name = safe_text(row.get("Place"))
    region = safe_text(row.get("Region"), "Goa")
    category = safe_text(row.get("Category"), "Experience")
    cost = safe_text(row.get("Cost"), "Check locally")
    note = safe_text(row.get("Notes"), "Discover this place.")

    with st.container(border=True):

        st.image(
            image_for(category),
            use_container_width=True
        )

        st.markdown(f"**{name}**")

        st.caption(
            f"📍 {region} · {category}"
        )

        st.write(note[:145])

        st.markdown(f"**Typical cost:** {cost}")

        st.link_button(
            "View directions",
            maps_url([name]),
            use_container_width=True
        )


# ============================================================
# 7. ITINERARY REGION RULES
# ============================================================

def is_all_vibes(vibes):

    chosen = {
        cat
        for vibe in vibes
        for cat in VIBE_CATEGORIES.get(vibe, [])
    }

    return ALL_CATEGORIES.issubset(chosen)


def plan_regions(start, end, days):

    if days < 6 or not end:
        return None, None

    days = min(days, 10)

    if start == end:

        mid = (
            "Central Goa"
            if start != "Central Goa"
            else "North Goa"
        )

        a, b, c = ROUND_TRIP_SPLITS[days]

        segments = [
            (start, a),
            (mid, b),
            (start, c)
        ]

    elif abs(
        REGIONS.index(start) - REGIONS.index(end)
    ) == 2:

        a, b, c = THREE_REGION_SPLITS[days]

        segments = [
            (start, a),
            ("Central Goa", b),
            (end, c)
        ]

    else:

        a, b = TWO_REGION_SPLITS[days]

        segments = [
            (start, a),
            (end, b)
        ]

    day_regions = [
        region
        for region, count in segments
        for _ in range(count)
    ]

    return day_regions, segments


# ============================================================
# 8. RULE-BASED RECOMMENDATION ENGINE
# ============================================================

def infer_places(
    places,
    days,
    season,
    vibes,
    group,
    budget,
    transport,
    start_region,
    end_region=None,
    all_vibes=False,
    segments=None
):

    facts = {
        "days": days,
        "season": season,
        "vibes": vibes,
        "group": group,
        "budget": budget,
        "transport": transport,
        "starting_region": start_region
    }

    if days >= 6:

        facts["ending_region"] = end_region
        facts["all_vibes"] = all_vibes

        facts["route"] = (
            " → ".join(
                f"{r} ({n}d)"
                for r, n in segments
            )
            if segments else None
        )

    fired = []

    def rule(code, condition, message):

        if condition:
            fired.append(f"{code} — {message}")

    rule(
        "D1",
        days <= 2,
        "Short trip: favour a compact route."
    )

    rule(
        "D2",
        3 <= days <= 4,
        "Medium trip: explore a main region and nearby areas."
    )

    rule(
        "D3",
        days == 5,
        "5-day trip: explore all three regions."
    )

    for n, message in LONG_TRIP_RULES.items():

        rule(
            f"D{n}",
            days == n,
            message
        )

    rule(
        "S1",
        season.startswith("Winter"),
        "Winter preference applied."
    )

    rule(
        "S2",
        season.startswith("Summer"),
        "Prioritise early and late outdoor visits."
    )

    rule(
        "S3",
        season.startswith("Monsoon"),
        "Check weather and water activity advisories."
    )

    rule(
        "V1",
        "Beach & chill" in vibes,
        "Beach experiences prioritised."
    )

    rule(
        "V2",
        any(v in vibes for v in ["Heritage", "Spiritual"]),
        "Heritage and spiritual places prioritised."
    )

    rule(
        "V3",
        any(v in vibes for v in ["Adventure", "Nature"]),
        "Nature and adventure places prioritised."
    )

    rule(
        "V4",
        any(v in vibes for v in ["Food & markets", "Nightlife"]),
        "Culture and nightlife places prioritised."
    )

    rule(
        "V5",
        len(vibes) > 1,
        "Multiple interests balanced."
    )

    rule(
        "V7",
        days >= 6 and all_vibes,
        "All categories are rotated across the daily itinerary."
    )

    if segments:

        label = " → ".join(
            f"{r} ({n} days)"
            for r, n in segments
        )

        fired.append(
            f"R1 — Regional route: {label}."
        )

        if start_region == end_region:

            fired.append(
                "R2 — Round trip through a neighbouring region."
            )

        elif abs(
            REGIONS.index(start_region)
            - REGIONS.index(end_region)
        ) == 2:

            fired.append(
                "R3 — North and South Goa connected through Central Goa."
            )

        else:

            fired.append(
                "R4 — Two-region route."
            )

        fired.append(
            "R5 — Daily attractions are selected from the planned region."
        )

    rule(
        "G1",
        group == "Family",
        "Family-friendly preference applied."
    )

    rule(
        "G2",
        group == "Couple",
        "Scenic and relaxed experiences prioritised."
    )

    rule(
        "G3",
        group == "Friends",
        "Social and activity-oriented experiences prioritised."
    )

    rule(
        "G4",
        group == "Solo",
        "Practical and well-known places prioritised."
    )

    rule(
        "B1",
        budget == "Low",
        "Affordable attracti
