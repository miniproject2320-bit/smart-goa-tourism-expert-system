
import math
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
        "Affordable attractions prioritised."
    )

    rule(
        "B2",
        budget == "High",
        "Higher-cost experiences allowed."
    )

    rule(
        "T1",
        transport == "No vehicle",
        "Fewer daily stops without personal transport."
    )

    rule(
        "T2",
        transport == "Own scooter or car",
        "More daily stops allowed."
    )

    df = places.copy()

    selected_categories = {
        cat
        for vibe in vibes
        for cat in VIBE_CATEGORIES.get(vibe, [])
    }

    if selected_categories:

        matching = df[
            df["Category"].isin(selected_categories)
        ].copy()

        if not matching.empty:
            df = matching

        else:
            fired.append(
                "V6 — No exact category match; using full dataset."
            )

    score_col = "Composite score (0-5)"

    if score_col in df.columns:

        df["_score"] = pd.to_numeric(
            df[score_col],
            errors="coerce"
        ).fillna(3.0)

    else:
        df["_score"] = 3.0

    df["_cost"] = df["Cost"].map(COST_SCORE).fillna(3)

    if budget == "Low":

        df["_score"] += df["_cost"] * 0.20

        affordable = df[
            df["Cost"].isin([
                "Free / very low",
                "Budget",
                "Moderate"
            ])
        ]

        if len(affordable) >= days * 2:
            df = affordable.copy()

    elif budget == "Mid":

        df["_score"] -= (
            df["_cost"] - 3
        ).abs() * 0.06

    else:

        df["_score"] += (
            6 - df["_cost"]
        ) * 0.08

    if season.startswith("Monsoon"):

        status_col = "Monsoon (Jun-Sep) status"

        if status_col in df.columns:

            risk = df[status_col].fillna("").astype(str).str.contains(
                "unsafe|closed|restricted|limited|suspended|slippery|waterlogged",
                case=False,
                regex=True
            )

            df["_score"] -= risk.astype(float) * 0.75

            if risk.any():

                fired.append(
                    "M1 — Monsoon-sensitive places down-ranked."
                )

    if group == "Family" and "Crowd level" in df.columns:

        df["_score"] += (
            df["Crowd level"]
            .astype(str)
            .str.lower()
            .map({
                "low": .12,
                "medium": .04,
                "high": -.10
            })
            .fillna(0)
        )

    if group == "Couple" and "Type" in df.columns:

        df["_score"] += (
            df["Type"]
            .astype(str)
            .str.lower()
            .map({
                "viewpoint": .18,
                "island": .12,
                "beach": .08
            })
            .fillna(0)
        )

    if group == "Friends" and "Type" in df.columns:

        df["_score"] += (
            df["Type"]
            .astype(str)
            .str.lower()
            .map({
                "nightlife": .18,
                "market": .10,
                "cruise": .08
            })
            .fillna(0)
        )

    # Starting region preference for short trips
    if not segments:

        df["_score"] += (
            df["Region"] == start_region
        ).astype(float) * (
            0.70 if days <= 2 else 0.40
        )

        if transport == "No vehicle":

            df["_score"] += (
                df["Region"] == start_region
            ).astype(float) * 0.25

    sort_cols = ["_score"]

    if "Review score (5=best)" in df.columns:
        sort_cols.append("Review score (5=best)")

    df = df.sort_values(
        sort_cols,
        ascending=False,
        na_position="last"
    )

    df = df.drop_duplicates("Place")

    if df.empty:

        df = places.copy()
        df["_score"] = 3.0

        fired.append(
            "K1 — Full dataset restored as fallback."
        )

    fired.append(
        "K2 — Places ranked using interest, budget, group, "
        "region and season preferences."
    )

    return df, fired, facts


# ============================================================
# 9. ROUTING FUNCTIONS
# ============================================================

def greedy_route(day_df):

    valid = day_df.dropna(
        subset=["Latitude", "Longitude"]
    ).copy()

    if len(valid) <= 1:
        return valid, 0.0

    rows = {
        str(r["Place"]): r
        for _, r in valid.iterrows()
    }

    current = str(valid.iloc[0]["Place"])

    remaining = set(rows) - {current}

    ordered = [current]
    distance = 0.0

    while remaining:

        here = rows[current]

        nxt = min(
            remaining,
            key=lambda name: haversine(
                here["Latitude"],
                here["Longitude"],
                rows[name]["Latitude"],
                rows[name]["Longitude"]
            )
        )

        there = rows[nxt]

        distance += haversine(
            here["Latitude"],
            here["Longitude"],
            there["Latitude"],
            there["Longitude"]
        )

        ordered.append(nxt)

        remaining.remove(nxt)

        current = nxt

    return pd.DataFrame(
        [rows[name] for name in ordered]
    ), distance


def pick_stop(candidates, used, region, category=None):

    pool = candidates[
        ~candidates["Place"].isin(used)
    ]

    # Never silently cross into another region.
    pool = pool[
        pool["Region"].astype(str) == region
    ]

    if category:

        matching = pool[
            pool["Category"] == category
        ]

        if not matching.empty:
            pool = matching

    if pool.empty:
        return None

    return pool.iloc[0]


# ============================================================
# 10. BUILD LONG TRIP ITINERARY
# ============================================================

def build_flow_itinerary(
    candidates,
    day_regions,
    transport,
    all_vibes
):

    max_stops = (
        2 if transport == "No vehicle" else 3
    )

    cats = sorted(
        candidates["Category"]
        .dropna()
        .unique()
        .tolist()
    ) if all_vibes else []

    result = {}
    used = set()
    slot = 0

    for day, region in enumerate(day_regions, 1):

        rows = []

        for _ in range(max_stops):

            category = (
                cats[slot % len(cats)]
                if cats else None
            )

            slot += 1

            row = pick_stop(
                candidates,
                used,
                region,
                category
            )

            if row is None:
                break

            rows.append(row)
            used.add(row["Place"])

        if not rows:
            continue

        picked, _ = greedy_route(
            pd.DataFrame(rows)
        )

        result[day] = picked

    return result


# ============================================================
# 11. BUILD SHORT TRIP ITINERARY
# ============================================================

def build_itinerary(
    candidates,
    days,
    transport,
    start_region,
    day_regions=None,
    all_vibes=False
):

    # Long trips use regional flow.
    if day_regions:

        return build_flow_itinerary(
            candidates,
            day_regions,
            transport,
            all_vibes
        )

    max_stops = (
        2 if transport == "No vehicle" else 3
    )

    region_order = [start_region]

    for region in REGIONS:

        if region not in region_order:
            region_order.append(region)

    result = {}
    used = set()

    for day in range(1, days + 1):

        if days <= 2:
            preferred = start_region

        else:
            preferred = region_order[
                (day - 1) % min(3, len(region_order))
            ]

        pool = candidates[
            (candidates["Region"] == preferred)
            & (~candidates["Place"].isin(used))
        ]

        if pool.empty:

            pool = candidates[
                ~candidates["Place"].isin(used)
            ]

        picked = pool.head(max_stops).copy()

        if picked.empty:
            break

        picked, _ = greedy_route(picked)

        result[day] = picked

        used.update(
            picked["Place"].tolist()
        )

    return result


# ============================================================
# 12. NEARBY ATTRACTIONS
# ============================================================

def nearby_places(
    places,
    start_row,
    max_km=15,
    limit=10,
    categories=None
):

    df = places.copy()

    df["Latitude"] = pd.to_numeric(
        df["Latitude"],
        errors="coerce"
    )

    df["Longitude"] = pd.to_numeric(
        df["Longitude"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Latitude", "Longitude"]
    )

    start_name = str(start_row["Place"])

    start_lat = float(start_row["Latitude"])
    start_lon = float(start_row["Longitude"])

    df = df[
        df["Place"].astype(str) != start_name
    ].copy()

    if categories:

        matching = df[
            df["Category"].isin(categories)
        ]

        if not matching.empty:
            df = matching

    df["Approx. straight-line km"] = df.apply(
        lambda row: haversine(
            start_lat,
            start_lon,
            row["Latitude"],
            row["Longitude"]
        ),
        axis=1
    )

    df = df[
        df["Approx. straight-line km"] <= max_km
    ]

    return (
        df.sort_values("Approx. straight-line km")
        .head(limit)
        .reset_index(drop=True)
    )


# ============================================================
# 13. ACCOMMODATION RECOMMENDATIONS
# ============================================================

def recommend_stays(stays, budget, regions):

    if stays.empty:
        return stays

    if "budget_level" not in stays.columns:
        return stays.head(0)

    budget_map = {
        "Low": "Low",
        "Mid": "Medium",
        "High": "High"
    }

    result = stays[
        stays["budget_level"]
        .astype(str)
        .str.lower()
        == budget_map[budget].lower()
    ].copy()

    if regions and "region" in result:

        mapped = [
            r.replace(" Goa", "")
            for r in regions
        ]

        regional = result[
            result["region"].astype(str).isin(mapped)
        ]

        if not regional.empty:
            result = regional

    return result.head(8)


# ============================================================
# 14. MAIN NAVIGATION
# ============================================================

tabs = st.tabs([
    "🏝️ Discover",
    "📍 Attractions",
    "🧭 Plan a trip",
    "🏨 Places to stay",
    "ℹ️ Travel tips"
])


# ============================================================
# TAB 1: DISCOVER
# ============================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">Start exploring</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'Search for a place or choose what you feel like doing.'
        '</div>',
        unsafe_allow_html=True
    )

    search_col, region_col = st.columns([3, 1])

    with search_col:

        search_text = st.text_input(
            "Search Goa",
            placeholder="Try Baga Beach, Fort Aguada, waterfall...",
            label_visibility="collapsed",
            key="home_search"
        )

    with region_col:

        region_choice = st.selectbox(
            "Area",
            ["All Goa"] + REGIONS,
            label_visibility="collapsed",
            key="home_region"
        )

    categories = [
        "All experiences"
    ] + sorted(
        places["Category"].dropna().astype(str).unique()
    )

    selected_category = st.selectbox(
        "What would you like to explore?",
        categories,
        label_visibility="collapsed",
        key="home_category"
    )

    featured = places.copy()

    if region_choice != "All Goa":

        featured = featured[
            featured["Region"] == region_choice
        ]

    if selected_category != "All experiences":

        featured = featured[
            featured["Category"] == selected_category
        ]

    if search_text.strip():

        mask = featured.astype(str).apply(
            lambda col: col.str.contains(
                search_text,
                case=False,
                na=False
            )
        ).any(axis=1)

        featured = featured[mask]

    if "Composite score (0-5)" in featured.columns:

        featured = featured.sort_values(
            "Composite score (0-5)",
            ascending=False,
            na_position="last"
        )

    m1, m2, m3 = st.columns(3)

    m1.metric("Places to explore", len(places))
    m2.metric("Goa regions", places["Region"].nunique())
    m3.metric("Experience types", places["Category"].nunique())

    st.markdown("### Popular ways to experience Goa")

    quick_items = [
        ("🏖️", "Beaches", "Coast & sunsets"),
        ("🏰", "Heritage & Religious", "History & culture"),
        ("🌿", "Nature & Adventure", "Outdoors & nature"),
        ("🎶", "Culture, Markets & Nightlife", "Food & local life")
    ]

    quick_cols = st.columns(4)

    for col, (emoji, cat, desc) in zip(
        quick_cols,
        quick_items
    ):

        with col:

            with st.container(border=True):

                st.markdown(f"## {emoji}")
                st.markdown(f"**{cat}**")
                st.caption(desc)

                if st.button(
                    "Explore",
                    key=f"quick_{cat}",
                    use_container_width=True
                ):

                    st.session_state["browse_category"] = cat

                    st.toast(
                        "Open the Attractions tab to browse this category."
                    )

    st.markdown("### Places you might love")

    if featured.empty:

        st.info(
            "No places match your search. Try another name, category or region."
        )

    else:

        card_cols = st.columns(3)

        for i, (_, row) in enumerate(
            featured.head(6).iterrows()
        ):

            with card_cols[i % 3]:

                place_card(
                    row,
                    f"home_{i}"
                )


# ============================================================
# TAB 2: ATTRACTIONS
# ============================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">Explore attractions</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'Find beaches, heritage sites, nature spots and local experiences.'
        '</div>',
        unsafe_allow_html=True
    )

    f1, f2, f3 = st.columns(3)

    with f1:

        filter_region = st.selectbox(
            "Region",
            ["All Goa"] + REGIONS,
            key="at_region"
        )

    with f2:

        filter_cat = st.selectbox(
            "Category",
            ["All categories"] + sorted(
                places["Category"].dropna().astype(str).unique()
            ),
            key="at_cat"
        )

    with f3:

        filter_cost = st.selectbox(
            "Budget",
            ["Any budget"] + sorted(
                places["Cost"].dropna().astype(str).unique()
            ),
            key="at_cost"
        )

    filtered = places.copy()

    if filter_region != "All Goa":

        filtered = filtered[
            filtered["Region"] == filter_region
        ]

    if filter_cat != "All categories":

        filtered = filtered[
            filtered["Category"] == filter_cat
        ]

    if filter_cost != "Any budget":

        filtered = filtered[
            filtered["Cost"].astype(str) == filter_cost
        ]

    st.caption(
        f"Showing {len(filtered)} matching attractions"
    )

    for start in range(0, min(len(filtered), 30), 3):

        cols = st.columns(3)

        for i, (_, row) in enumerate(
            filtered.iloc[start:start + 3].iterrows()
        ):

            with cols[i]:

                place_card(
                    row,
                    f"browse_{start}_{i}"
                )

    if len(filtered) > 30:

        st.info(
            "Showing the first 30 matches. Narrow your filters to find a particular place."
        )


# ============================================================
# TAB 3: PLAN A TRIP
# ============================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">Build your Goa itinerary</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'Create a personalised trip using your interests, '
        'budget, season and regional route.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # PLANNER INPUTS
    # --------------------------------------------------------

    with st.expander(
        "🧭 Trip preferences",
        expanded=True
    ):

        c1, c2, c3 = st.columns(3)

        with c1:

            days_label = st.selectbox(
                "Trip duration",
                list(DURATIONS),
                key="planner_duration"
            )

            days = DURATIONS[days_label]

            season = st.selectbox(
                "Season",
                SEASONS,
                key="planner_season"
            )

            vibes = st.multiselect(
                "What do you enjoy?",
                list(VIBE_CATEGORIES),
                default=["Beach & chill"],
                key="planner_vibes"
            )

        with c2:

            group = st.selectbox(
                "Travelling with",
                GROUPS,
                key="planner_group"
            )

            budget = st.select_slider(
                "Budget",
                options=BUDGETS,
                value="Mid",
                key="planner_budget"
            )

            transport = st.radio(
                "Transport",
                TRANSPORTS,
                key="planner_transport"
            )

        with c3:

            start_region = st.selectbox(
                "Starting region",
                REGIONS,
                key="planner_start"
            )

            end_region = None

            if days >= 6:

                default_end = DEFAULT_END[start_region]

                end_region = st.selectbox(
                    "Where do you want to end your trip?",
                    REGIONS,
                    index=REGIONS.index(default_end),
                    key="planner_end"
                )

                st.caption(
                    "Choose the same region for a round trip."
                )

        if not vibes:

            st.warning(
                "No interests selected. All categories will be considered."
            )

            effective_vibes = list(VIBE_CATEGORIES)

        else:

            effective_vibes = vibes

        all_vibes = is_all_vibes(effective_vibes)

        if all_vibes:

            st.info(
                "All interests selected: daily stops will rotate through "
                "beaches, heritage, nature and culture."
            )

        generate = st.button(
            "✨ Generate my itinerary",
            type="primary",
            use_container_width=True,
            key="generate_itinerary"
        )

    # --------------------------------------------------------
    # GENERATE AND SAVE RESULTS
    # --------------------------------------------------------

    if generate:

        day_regions, segments = plan_regions(
            start_region,
            end_region,
            days
        )

        ranked, rules, facts = infer_places(
            places,
            days,
            season,
            effective_vibes,
            group,
            budget,
            transport,
            start_region,
            end_region,
            all_vibes,
            segments
        )

        itinerary = build_itinerary(
            ranked,
            days,
            transport,
            start_region,
            day_regions,
            all_vibes
        )

        st.session_state["run_result"] = {
            "ranked": ranked,
            "rules": rules,
            "facts": facts,
            "itinerary": itinerary,
            "days": days,
            "season": season,
            "vibes": effective_vibes,
            "group": group,
            "budget": budget,
            "transport": transport,
            "start_region": start_region,
            "end_region": end_region,
            "segments": segments,
            "all_vibes": all_vibes
        }

    if "run_result" not in st.session_state:

        st.info(
            "Choose your trip preferences above and generate your itinerary."
        )

    else:

        res = st.session_state["run_result"]

        ranked = res["ranked"]
        itinerary = res["itinerary"]

        # ----------------------------------------------------
        # SUMMARY METRICS
        # ----------------------------------------------------

        st.markdown("### Your trip overview")

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "Places in knowledge base",
            len(places)
        )

        m2.metric(
            "Planned days",
            res["days"]
        )

        m3.metric(
            "Recommended stops",
            sum(len(x) for x in itinerary.values())
        )

        m4.metric(
            "Accommodation records",
            len(stays)
        )

        st.caption(
            f"{', '.join(res['vibes'])} · "
            f"{res['season']} · {res['budget']} budget · "
            f"{res['group']} · {res['transport']}"
        )

        st.success(
            "Your personalised itinerary has been generated."
        )

        # ----------------------------------------------------
        # LONG TRIP ROUTE DISPLAY
        # ----------------------------------------------------

        if res.get("segments"):

            flow = " → ".join(
                f"**{r}** ({n} days)"
                for r, n in res["segments"]
            )

            st.info(
                "🛣️ Regional route: " + flow
            )

        # ----------------------------------------------------
        # INTERNAL PLANNER TABS
        # ----------------------------------------------------

        pt1, pt2, pt3, pt4 = st.tabs([
            "🗓️ Your itinerary",
            "📍 Explore & map",
            "🧠 How it works",
            "🛣️ Nearby route"
        ])

        # ====================================================
        # ITINERARY
        # ====================================================

        with pt1:

            st.subheader(
                f"Your {res['days']}-day plan"
            )

            if not itinerary:

                st.warning(
                    "No itinerary could be built. Try changing your preferences."
                )

            for day, day_df in itinerary.items():

                region = str(
                    day_df.iloc[0]["Region"]
                )

                with st.expander(
                    f"Day {day} · {region} · {len(day_df)} stops",
                    expanded=(day == 1)
                ):

                    for idx, (_, place) in enumerate(
                        day_df.iterrows(),
                        1
                    ):

                        name = str(place["Place"])

                        typ = safe_text(
                            place.get(
                                "Type",
                                place.get("Category", "Sightseeing")
                            )
                        )

                        cost = safe_text(
                            place.get("Cost"),
                            "Check locally"
                        )

                        col_a, col_b = st.columns([5, 1])

                        with col_a:

                            st.markdown(
                                f"**{idx}. {name}**"
                            )

                            st.caption(
                                f"{typ} · {place['Region']} · {cost}"
                            )

                            note = safe_text(
                                place.get("Notes"),
                                ""
                            )

                            if note:
                                st.write(note)

                        with col_b:

                            st.markdown("🕒")
                            st.caption("Allow 1–2 h")

                        if idx < len(day_df):
                            st.divider()

                    names = (
                        day_df["Place"]
                        .astype(str)
                        .tolist()
                    )

                    _, km = greedy_route(day_df)

                    st.info(
                        f"Estimated straight-line distance: **{km:.1f} km**. "
                        "Actual road distance may differ."
                    )

                    st.link_button(
                        "🗺️ Open this day's stops in Google Maps",
                        maps_url(names),
                        use_container_width=True
                    )

            # CSV EXPORT

            export_rows = []

            for day, day_df in itinerary.items():

                for order, (_, row) in enumerate(
                    day_df.iterrows(),
                    1
                ):

                    export_rows.append({
                        "Day": day,
                        "Stop": order,
                        "Place": row.get("Place"),
                        "Region": row.get("Region"),
                        "Category": row.get("Category"),
                        "Cost": row.get("Cost"),
                        "Latitude": row.get("Latitude"),
                        "Longitude": row.get("Longitude")
                    })

            if export_rows:

                export = pd.DataFrame(export_rows)

                st.download_button(
                    "⬇️ Download itinerary (CSV)",
                    export.to_csv(
                        index=False
                    ).encode("utf-8-sig"),
                    "goa_smart_itinerary.csv",
                    "text/csv"
                )

        # ====================================================
        # EXPLORE AND MAP
        # ====================================================

        with pt2:

            st.subheader(
                "Places worth discovering"
            )

            st.caption(
                "Recommendations are ranked using your preferences. "
                "Photos are illustrative category images."
            )

            gallery = ranked.head(6)

            gallery_cols = st.columns(3)

            for i, (_, place) in enumerate(
                gallery.iterrows()
            ):

                with gallery_cols[i % 3]:

                    place_card(
                        place,
                        f"planner_gallery_{i}"
                    )

            st.markdown("### All matching places")

            display_cols = [
                c for c in [
                    "Place",
                    "Region",
                    "Taluka",
                    "Category",
                    "Type",
                    "Cost",
                    "Review score (5=best)",
                    "Composite score (0-5)",
                    "Monsoon (Jun-Sep) status"
                ]
                if c in ranked.columns
            ]

            st.dataframe(
                ranked[display_cols].head(30),
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Download recommendations (CSV)",
                ranked[display_cols].to_csv(
                    index=False
                ).encode("utf-8-sig"),
                "goa_recommendations.csv",
                "text/csv"
            )

            coords = ranked.dropna(
                subset=["Latitude", "Longitude"]
            ).copy()

            coords["Latitude"] = pd.to_numeric(
                coords["Latitude"],
                errors="coerce"
            )

            coords["Longitude"] = pd.to_numeric(
                coords["Longitude"],
                errors="coerce"
            )

            coords = coords.dropna(
                subset=["Latitude", "Longitude"]
            ).head(40)

            if not coords.empty:

                st.markdown("### Map preview")

                st.pydeck_chart(
                    pdk.Deck(
                        initial_view_state=pdk.ViewState(
                            latitude=float(
                                coords["Latitude"].mean()
                            ),
                            longitude=float(
                                coords["Longitude"].mean()
                            ),
                            zoom=8.5,
                            pitch=0
                        ),
                        layers=[
                            pdk.Layer(
                                "ScatterplotLayer",
                                data=coords,
                                get_position="[Longitude, Latitude]",
                                get_radius=100,
                                get_fill_color=[8, 127, 140, 190],
                                pickable=True
                            )
                        ],
                        tooltip={
                            "text": "{Place}\n{Region}\n{Category}"
                        }
                    ),
                    use_container_width=True
                )

        # ====================================================
        # HOW IT WORKS
        # ====================================================

        with pt3:

            st.subheader("Working memory")

            st.json(res["facts"])

            st.subheader("Rules that fired")

            for item in res["rules"]:

                st.markdown(f"- {item}")

            if (
                res["season"].startswith("Monsoon")
                and any(
                    v in res["vibes"]
                    for v in ["Beach & chill", "Adventure"]
                )
            ):

                st.warning(
                    "Monsoon caution: check sea conditions, "
                    "weather and operator availability before travelling."
                )

            st.subheader("How route distances work")

            st.write(
                "The in-app kilometre estimate is a straight-line "
                "distance between coordinates. Stops are arranged "
                "using a nearest-next heuristic. Google Maps calculates "
                "the actual road route when opened."
            )

            st.subheader("Knowledge base")

            st.write(
                f"Loaded {len(places)} attraction records and "
                f"{len(stays)} accommodation records."
            )

        # ====================================================
        # NEARBY ROUTE
        # ====================================================

        with pt4:

            st.subheader(
                "Find nearby attractions"
            )

            route_places = places.dropna(
                subset=["Latitude", "Longitude"]
            ).copy()

            route_places["Latitude"] = pd.to_numeric(
                route_places["Latitude"],
                errors="coerce"
            )

            route_places["Longitude"] = pd.to_numeric(
                route_places["Longitude"],
                errors="coerce"
            )

            route_places = route_places.dropna(
                subset=["Latitude", "Longitude"]
            )

            if route_places.empty:

                st.warning(
                    "No usable coordinates were found."
                )

            else:

                place_names = (
                    route_places["Place"]
                    .astype(str)
                    .tolist()
                )

                start_name = st.selectbox(
                    "Where are you starting from?",
                    place_names,
                    key="nearby_start"
                )

                c1, c2, c3 = st.columns(3)

                with c1:

                    max_km = st.slider(
                        "Search radius (km)",
                        2,
                        80,
                        20,
                        step=2,
                        key="nearby_radius"
                    )

                with c2:

                    max_places = st.slider(
                        "Maximum attractions",
                        2,
                        12,
                        6,
                        key="nearby_limit"
                    )

                with c3:

                    mode_label = st.selectbox(
                        "Travel mode",
                        ["Driving", "Walking", "Bicycling"],
                        key="nearby_mode"
                    )

                start_rows = route_places[
                    route_places["Place"].astype(str)
                    == start_name
                ]

                start_row = start_rows.iloc[0]

                category_options = sorted(
                    places["Category"]
                    .dropna()
                    .astype(str)
                    .unique()
                )

                selected_near_categories = st.multiselect(
                    "Focus on attraction types",
                    category_options,
                    key="nearby_categories"
                )

                near = nearby_places(
                    route_places,
                    start_row,
                    max_km=max_km,
                    limit=max_places,
                    categories=selected_near_categories or None
                )

                if near.empty:

                    st.info(
                        "No nearby attractions found. "
                        "Increase the radius or clear the category filter."
                    )

                else:

                    show_cols = [
                        c for c in [
                            "Place",
                            "Region",
                            "Category",
                            "Cost",
                            "Approx. straight-line km",
                            "Notes"
                        ]
                        if c in near.columns
                    ]

                    display = near[show_cols].copy()

                    display["Approx. straight-line km"] = (
                        display["Approx. straight-line km"].round(1)
                    )

                    st.dataframe(
                        display,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.caption(
                        "Distances are straight-line estimates, not road kilometres."
                    )

                    selected_names = (
                        near["Place"].astype(str).tolist()
                    )

                    mode = {
                        "Driving": "driving",
                        "Walking": "walking",
                        "Bicycling": "bicycling"
                    }[mode_label]

                    st.link_button(
                        "🗺️ Open nearby route in Google Maps",
                        maps_url(
                            [start_name] + selected_names,
                            mode
                        ),
                        use_container_width=True
                    )

                    st.markdown("### Individual directions")

                    for _, row in near.iterrows():

                        name = str(row["Place"])

                        km = float(
                            row["Approx. straight-line km"]
                        )

                        url = maps_url(
                            [start_name, name],
                            mode
                        )

                        st.markdown(
                            f"- **{name}** — approximately "
                            f"{km:.1f} km straight-line · "
                            f"[Get directions]({url})"
                        )

                    map_df = near.copy()

                    start_pin = pd.DataFrame([{
                        "Place": start_name,
                        "Region": start_row["Region"],
                        "Category": "Starting point",
                        "Latitude": float(start_row["Latitude"]),
                        "Longitude": float(start_row["Longitude"])
                    }])

                    map_df = pd.concat(
                        [start_pin, map_df],
                        ignore_index=True
                    )

                    st.markdown("### Attraction map")

                    st.pydeck_chart(
                        pdk.Deck(
                            initial_view_state=pdk.ViewState(
                                latitude=float(
                                    map_df["Latitude"].mean()
                                ),
                                longitude=float(
                                    map_df["Longitude"].mean()
                                ),
                                zoom=10
                            ),
                            layers=[
                                pdk.Layer(
                                    "ScatterplotLayer",
                                    data=map_df,
                                    get_position="[Longitude, Latitude]",
                                    get_radius=150,
                                    get_fill_color=[8, 127, 140, 210],
                                    pickable=True
                                )
                            ],
                            tooltip={
                                "text": "{Place}\n{Region}\n{Category}"
                            }
                        ),
                        use_container_width=True
                    )


# ============================================================
# TAB 4: PLACES TO STAY
# ============================================================

with tabs[3]:

    st.markdown(
        '<div class="section-title">Find a place to stay</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'Accommodation recommendations based on your budget and route.'
        '</div>',
        unsafe_allow_html=True
    )

    if stays.empty:

        st.info(
            "No accommodation dataset found. "
            "Add output.csv beside app.py."
        )

    else:

        s1, s2 = st.columns(2)

        with s1:

            stay_region = (
                st.selectbox(
                    "Area",
                    ["All areas"] + sorted(
                        stays["region"]
                        .dropna()
                        .astype(str)
                        .unique()
                    ),
                    key="stay_region"
                )
                if "region" in stays.columns
                else "All areas"
            )

        with s2:

            stay_budget = (
                st.selectbox(
                    "Budget",
                    ["Any budget"] + sorted(
                        stays["budget_level"]
                        .dropna()
                        .astype(str)
                        .unique()
                    ),
                    key="stay_budget"
                )
                if "budget_level" in stays.columns
                else "Any budget"
            )

        stay_view = stays.copy()

        if (
            stay_region != "All areas"
            and "region" in stay_view.columns
        ):

            stay_view = stay_view[
                stay_view["region"].astype(str) == stay_region
            ]

        if (
            stay_budget != "Any budget"
            and "budget_level" in stay_view.columns
        ):

            stay_view = stay_view[
                stay_view["budget_level"].astype(str) == stay_budget
            ]

        show_cols = [
            c for c in [
                "name",
                "type",
                "region",
                "area",
                "budget_level",
                "price_range_inr",
                "nearest_airport",
                "nearest_station",
                "beach_access",
                "family_friendly",
                "wifi",
                "notes"
            ]
            if c in stay_view.columns
        ]

        st.dataframe(
            stay_view[show_cols],
            use_container_width=True,
            hide_index=True
        )

        # Use the generated itinerary to suggest regional stays.
        if "run_result" in st.session_state:

            res = st.session_state["run_result"]

            if res.get("segments"):

                route_regions = list(
                    dict.fromkeys([
                        r for r, _ in res["segments"]
                    ])
                )

                st.markdown("### Stays along your itinerary")

                st.caption(
                    "Suggested regions: "
                    + " → ".join(route_regions)
                )

                stay_recs = recommend_stays(
                    stays,
                    res["budget"],
                    route_regions
                )

                if stay_recs.empty:

                    st.info(
                        "No stays matched the itinerary budget and regions."
                    )

                else:

                    cols = [
                        c for c in [
                            "name",
                            "type",
                            "region",
                            "area",
                            "budget_level",
                            "price_range_inr",
                            "nearest_airport",
                            "nearest_station",
                            "beach_access",
                            "family_friendly",
                            "wifi",
                            "notes"
                        ]
                        if c in stay_recs.columns
                    ]

                    st.dataframe(
                        stay_recs[cols],
                        use_container_width=True,
                        hide_index=True
                    )


# ============================================================
# TAB 5: TRAVEL TIPS
# ============================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">Helpful Goa travel tips</div>',
        unsafe_allow_html=True
    )

    tips = [
        (
            "🌤️ Check the season",
            "Goa's monsoon season can affect beach access, "
            "water activities and outdoor travel. "
            "Check local advisories before travelling."
        ),

        (
            "🛵 Choose transport carefully",
            "A scooter can be flexible for confident riders. "
            "Taxis or a hired car may be easier for families "
            "and longer journeys."
        ),

        (
            "🗺️ Check road routes",
            "The distances in this project are approximate. "
            "Open Google Maps for road directions and check traffic."
        ),

        (
            "💳 Confirm prices",
            "Entry fees, accommodation rates and transport fares "
            "can change. Confirm directly with providers."
        ),

        (
            "🤝 Travel responsibly",
            "Respect local communities, keep beaches clean, "
            "follow safety signs and avoid swimming in unsafe conditions."
        )
    ]

    for title, body in tips:

        with st.expander(title, expanded=True):

            st.write(body)

    st.divider()

    st.markdown("### About this project")

    st.write(
        "Goa Smart Tourism Expert System is an educational "
        "prototype that uses a supplied tourism knowledge base "
        "and explainable rule-based recommendations to help "
        "visitors discover Goa and plan regional itineraries."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    f"🌴 Goa Smart Tourism Expert System · "
    f"{len(places)} attractions loaded · "
    f"Student project prototype. "
    f"Verify live conditions, prices, opening hours and transport "
    f"before travelling."
)
