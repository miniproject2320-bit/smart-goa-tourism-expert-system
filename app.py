from pathlib import Path
from urllib.parse import quote
import math

import pandas as pd
import pydeck as pdk
import streamlit as st

st.markdown("""
<style>

/* ===== MAIN BACKGROUND ===== */
.stApp {
    background: linear-gradient(
        135deg,
        #EAF6F5 0%,
        #F5FAF8 55%,
        #FFF5E9 100%
    );
    color: #294B55;
}

/* ===== PAGE SPACING ===== */
.main .block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* ===== HEADINGS ===== */
h1, h2, h3 {
    color: #174B60 !important;
    font-weight: 750;
    letter-spacing: -0.4px;
}

/* ===== PARAGRAPHS ===== */
p, label, .stMarkdown {
    color: #42636C;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #DFF1EF,
        #EEF7F3
    );
    border-right: 1px solid #D4E9E5;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(
        135deg,
        #168C88,
        #28A69B
    );
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    transition: all 0.25s ease;
    box-shadow: 0 3px 10px rgba(22,140,136,0.15);
}

.stButton > button:hover {
    background: #11736F;
    color: white;
    transform: translateY(-2px);
}

/* ===== INPUTS ===== */
.stTextInput input,
.stNumberInput input {
    background-color: white;
    border: 1px solid #D5E7E4;
    border-radius: 10px;
}

/* ===== SELECT BOX ===== */
.stSelectbox div[data-baseweb="select"] {
    background-color: white;
    border-radius: 10px;
}

/* ===== CONTAINERS / CARDS ===== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(255,255,255,0.94);
    border: 1px solid #E0ECE8;
    border-radius: 16px;
    box-shadow: 0 5px 18px rgba(36,85,79,0.06);
}

/* ===== TABS ===== */
button[data-baseweb="tab"] {
    color: #42636C;
    font-weight: 600;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #168C88;
    border-bottom-color: #168C88;
}

/* ===== IMAGES ===== */
.stImage img {
    border-radius: 14px;
}

/* ===== ALERTS ===== */
div[data-testid="stAlert"] {
    border-radius: 12px;
}

/* ===== DATAFRAMES ===== */
.stDataFrame {
    background-color: white;
    border-radius: 12px;
}

/* ===== DIVIDERS ===== */
hr {
    border-color: #DCEAE6;
}

/* ===== LINKS ===== */
a {
    color: #168C88 !important;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Goa Smart Tourism - friendly travel-discovery interface
# Inspired by common travel-site patterns, not a copy of Tripadvisor.
# ------------------------------------------------------------
st.set_page_config(
    page_title="Explore Goa | Smart Tourism Guide",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
PLACES_FILE = BASE_DIR / "Goa_Places_Merged (2).csv"
STAYS_FILE = BASE_DIR / "output.csv"

CATEGORY_IMAGES = {
    "Beaches": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1000&q=85",
    "Heritage & Religious": "https://images.unsplash.com/photo-1606293926075-69a00db_d6a3?auto=format&fit=crop&w=1000&q=85",
    "Nature & Adventure": "https://images.unsplash.com/photo-1472396961693-142e6e269027?auto=format&fit=crop&w=1000&q=85",
    "Culture, Markets & Nightlife": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1000&q=85",
}
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1000&q=85"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
:root { --green:#00aa6c; --dark:#17332c; --muted:#66756f; --line:#e5ebe7; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.block-container { max-width:1320px; padding-top:1.1rem; padding-bottom:3rem; }
header[data-testid="stHeader"] { background:transparent; }
.brand {font-family:Manrope,sans-serif;font-weight:800;font-size:1.35rem;color:#17332c;letter-spacing:-.04em;}
.brand span {color:#00a86b;}
.hero { margin-top:.8rem; border-radius:28px; min-height:360px; padding:2.7rem; display:flex; flex-direction:column; justify-content:center; color:white;
 background:linear-gradient(90deg,rgba(5,35,28,.82),rgba(5,35,28,.18)),url('https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1900&q=90') center 48%/cover; }
.hero .eyebrow {font-size:.78rem;letter-spacing:.13em;text-transform:uppercase;font-weight:800;color:#d5fff0;}
.hero h1 {font-family:Manrope,sans-serif;font-size:clamp(2.4rem,5vw,4.6rem);line-height:1.03;max-width:720px;color:white;margin:.7rem 0;letter-spacing:-.055em;}
.hero p {font-size:1.08rem;max-width:650px;color:#f0fff9;margin:0;}
.section-title {font-family:Manrope,sans-serif;font-weight:800;letter-spacing:-.035em;color:#17332c;font-size:1.75rem;margin:.2rem 0 .3rem;}
.section-sub {color:#687871;margin-bottom:1rem;}
div[data-testid="stMetric"] {background:#f5faf7;border:1px solid #e3eee7;padding:1rem;border-radius:16px;}
.stButton>button,.stLinkButton>a,.stDownloadButton>button {border-radius:999px;font-weight:700;min-height:2.7rem;}
.stButton>button[kind="primary"] {background:#00a86b;border:1px solid #00a86b;color:white;}
[data-testid="stTabs"] button {font-weight:700;}
[data-testid="stSidebar"] {background:#f5faf7;}
div[data-testid="stVerticalBlock"] div[data-testid="stExpander"] {border-radius:14px;border-color:#e3eae5;}
.small-note {color:#718079;font-size:.86rem;}
@media(max-width:700px){.block-container{padding:.6rem .7rem 2rem}.hero{min-height:280px;padding:1.4rem;border-radius:20px}.hero p{font-size:.95rem}}
</style>
<div class="brand">🌴 goa<span>guide</span></div>
<div class="hero">
  <div class="eyebrow">Discover · Explore · Experience</div>
  <h1>Find your kind of Goa.</h1>
  <p>Beaches, hidden corners, heritage, food and memorable experiences. Explore places and plan an easier trip around Goa.</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    if not PLACES_FILE.exists():
        raise FileNotFoundError(f"Could not find {PLACES_FILE.name}. Keep it in the same folder as app.py.")
    places = pd.read_csv(PLACES_FILE)
    places.columns = [str(c).strip() for c in places.columns]
    required = ["Place", "Region", "Category", "Cost", "Latitude", "Longitude"]
    missing = [c for c in required if c not in places.columns]
    if missing:
        raise ValueError("Places CSV is missing columns: " + ", ".join(missing))
    for col in ["Latitude", "Longitude", "Composite score (0-5)", "Review score (5=best)", "Popularity score (5=most)"]:
        if col in places.columns:
            places[col] = pd.to_numeric(places[col], errors="coerce")
    if STAYS_FILE.exists():
        stays = pd.read_csv(STAYS_FILE)
        stays.columns = [str(c).strip() for c in stays.columns]
    else:
        stays = pd.DataFrame()
    return places, stays

try:
    places, stays = load_data()
except Exception as exc:
    st.error(f"Unable to load project data: {exc}")
    st.stop()

# Small helpers
def image_for(category):
    return CATEGORY_IMAGES.get(str(category), DEFAULT_IMAGE)

def safe_text(value, fallback="Details coming soon"):
    if pd.isna(value) or str(value).strip().lower() in {"", "nan", "none"}:
        return fallback
    return str(value)

def haversine(lat1, lon1, lat2, lon2):
    radius = 6371.0
    p1, p2 = math.radians(float(lat1)), math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(max(0, min(1, a))))

def maps_url(origin, destinations, mode="driving"):
    if not destinations:
        return f"https://www.google.com/maps/search/?api=1&query={quote(str(origin) + ', Goa, India')}"
    url = ("https://www.google.com/maps/dir/?api=1"
           f"&origin={quote(str(origin) + ', Goa, India')}"
           f"&destination={quote(str(destinations[-1]) + ', Goa, India')}"
           f"&travelmode={quote(mode)}")
    if len(destinations) > 1:
        url += "&waypoints=" + quote("|".join(f"{n}, Goa, India" for n in destinations[:-1]), safe="")
    return url

def place_card(row, key_suffix):
    name = safe_text(row.get("Place"), "Goa attraction")
    region = safe_text(row.get("Region"), "Goa")
    category = safe_text(row.get("Category"), "Experience")
    cost = safe_text(row.get("Cost"), "Check locally")
    note = safe_text(row.get("Notes"), "Discover this place in Goa.")
    with st.container(border=True):
        st.image(image_for(category), use_container_width=True)
        st.markdown(f"**{name}**")
        st.caption(f"📍 {region}  ·  {category}")
        st.write(note[:145] + ("…" if len(note) > 145 else ""))
        st.markdown(f"**Typical cost:** {cost}")
        if st.button("View directions", key=f"directions_{key_suffix}", use_container_width=True):
            st.link_button("Open in Google Maps", maps_url(name, [], "driving"), use_container_width=True)

# Top-level navigation
tabs = st.tabs(["🏝️ Discover", "📍 Attractions", "🧭 Plan a trip", "🏨 Places to stay", "ℹ️ Travel tips"])

with tabs[0]:
    st.markdown('<div class="section-title">Start exploring</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Search for a place or choose what you feel like doing.</div>', unsafe_allow_html=True)
    search_col, region_col = st.columns([3, 1])
    with search_col:
        search_text = st.text_input("Search Goa", placeholder="Try Baga Beach, Fort Aguada, waterfall...", label_visibility="collapsed", key="home_search")
    with region_col:
        region_choice = st.selectbox("Area", ["All Goa", "North Goa", "Central Goa", "South Goa"], label_visibility="collapsed", key="home_region")

    categories = ["All experiences"] + sorted(places["Category"].dropna().astype(str).unique().tolist())
    selected_category = st.selectbox("What would you like to explore?", categories, label_visibility="collapsed")
    featured = places.copy()
    if region_choice != "All Goa":
        featured = featured[featured["Region"].astype(str).str.casefold() == region_choice.casefold()]
    if selected_category != "All experiences":
        featured = featured[featured["Category"].astype(str) == selected_category]
    if search_text.strip():
        mask = featured.astype(str).apply(lambda col: col.str.contains(search_text, case=False, na=False)).any(axis=1)
        featured = featured[mask]
    score_col = "Composite score (0-5)" if "Composite score (0-5)" in featured.columns else None
    if score_col:
        featured = featured.sort_values(score_col, ascending=False, na_position="last")

    m1, m2, m3 = st.columns(3)
    m1.metric("Places to explore", len(places))
    m2.metric("Goa regions", places["Region"].nunique())
    m3.metric("Experience types", places["Category"].nunique())
    st.markdown("### Popular ways to experience Goa")
    quick = st.columns(4)
    quick_items = [("🏖️", "Beaches", "Coast & sunsets"), ("🏰", "Heritage & Religious", "History & culture"), ("🌿", "Nature & Adventure", "Outdoors & nature"), ("🎶", "Culture, Markets & Nightlife", "Food & local life")]
    for col, (emoji, cat, desc) in zip(quick, quick_items):
        with col:
            with st.container(border=True):
                st.markdown(f"## {emoji}")
                st.markdown(f"**{cat}**")
                st.caption(desc)
                if st.button("Explore", key=f"quick_{cat}", use_container_width=True):
                    st.session_state["browse_category"] = cat
                    st.toast(f"Choose the Attractions tab to browse {cat}.")
    st.markdown("### Places you might love")
    if featured.empty:
        st.info("No places match your search. Try another name, category or region.")
    else:
        card_cols = st.columns(3)
        for i, (_, row) in enumerate(featured.head(6).iterrows()):
            with card_cols[i % 3]:
                place_card(row, f"home_{i}")

with tabs[1]:
    st.markdown('<div class="section-title">Explore attractions</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Find beaches, heritage sites, nature spots and local experiences.</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        filter_region = st.selectbox("Region", ["All Goa"] + sorted(places["Region"].dropna().astype(str).unique()), key="at_region")
    with f2:
        filter_cat = st.selectbox("Category", ["All categories"] + sorted(places["Category"].dropna().astype(str).unique()), key="at_cat")
    with f3:
        filter_cost = st.selectbox("Budget", ["Any budget"] + sorted(places["Cost"].dropna().astype(str).unique()), key="at_cost")
    filtered = places.copy()
    if filter_region != "All Goa": filtered = filtered[filtered["Region"].astype(str) == filter_region]
    if filter_cat != "All categories": filtered = filtered[filtered["Category"].astype(str) == filter_cat]
    if filter_cost != "Any budget": filtered = filtered[filtered["Cost"].astype(str) == filter_cost]
    st.caption(f"Showing {len(filtered)} matching attractions")
    for start in range(0, min(len(filtered), 30), 3):
        cols = st.columns(3)
        for start in range(0, min(len(filtered), 30), 3):
            cols = st.columns(3)

        for i, (col, (_, row)) in enumerate(
            zip(cols, filtered.iloc[start:start + 3].iterrows())
        ):
            with col:
                place_card(
                    row,
                    f"browse_{start}_{i}_{str(row['Place'])[:12]}"
                )

    if len(filtered) > 30:
        st.info("Showing the first 30 matches. Narrow your filters to find a particular place.")
        st.info("Showing the first 30 matches. Narrow your filters to find a particular place.")

with tabs[2]:
    st.markdown('<div class="section-title">Build your Goa route</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Choose a starting attraction and discover nearby stops. Google Maps opens the road directions.</div>', unsafe_allow_html=True)
    route_data = places.dropna(subset=["Latitude", "Longitude"]).copy()
    route_data["Latitude"] = pd.to_numeric(route_data["Latitude"], errors="coerce")
    route_data["Longitude"] = pd.to_numeric(route_data["Longitude"], errors="coerce")
    route_data = route_data.dropna(subset=["Latitude", "Longitude"])
    if route_data.empty:
        st.warning("No usable coordinates are available in the places dataset.")
    else:
        r1, r2, r3 = st.columns([2, 1, 1])
        with r1: start_name = st.selectbox("Where will you start?", route_data["Place"].astype(str).tolist())
        with r2: radius = st.slider("Search radius (km)", 2, 80, 20, 2)
        with r3: travel_mode_label = st.selectbox("Travel by", ["Car / taxi", "Walking", "Bicycle", "Scooter"])
        start_row = route_data[route_data["Place"].astype(str) == start_name].iloc[0]
        nearby = route_data[route_data["Place"].astype(str) != start_name].copy()
        nearby["Approx. straight-line km"] = nearby.apply(lambda r: haversine(start_row["Latitude"], start_row["Longitude"], r["Latitude"], r["Longitude"]), axis=1)
        nearby = nearby[nearby["Approx. straight-line km"] <= radius].sort_values("Approx. straight-line km").head(8)
        mode = {"Car / taxi": "driving", "Walking": "walking", "Bicycle": "bicycling", "Scooter": "driving"}[travel_mode_label]
        if nearby.empty:
            st.info("No attractions found in this radius. Increase the search radius.")
        else:
            st.markdown("#### Nearby places, closest first")
            for _, row in nearby.iterrows(): 
                c1, c2 = st.columns([4, 1])
                with c1:
                  st.markdown(f"**{row['Place']}** · {row['Region']} · {row['Category']}")
                  st.caption(f"About {row['Approx. straight-line km']:.1f} km in a straight line · {safe_text(row.get('Cost'), 'Check locally')}")
                with c2:
                    st.link_button("Directions", maps_url(start_name, [row['Place']], mode), use_container_width=True)
            chosen_stops = st.multiselect("Choose stops for a multi-stop route", nearby["Place"].astype(str).tolist(), default=nearby["Place"].astype(str).head(min(3, len(nearby))).tolist())
            if chosen_stops:
                st.link_button("🗺️ Open route in Google Maps", maps_url(start_name, chosen_stops, mode), use_container_width=True)
            st.caption("Distances shown are approximate straight-line distances from your dataset coordinates, not road kilometres. Google Maps calculates road directions and may reorder or adjust travel based on its routing data.")
            map_df = nearby[["Place", "Latitude", "Longitude", "Region", "Category"]].rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
            start_pin = pd.DataFrame([{"Place": f"START: {start_name}", "latitude": start_row["Latitude"], "longitude": start_row["Longitude"], "Region": start_row["Region"], "Category": "Starting point"}])
            map_df = pd.concat([start_pin, map_df], ignore_index=True)
            st.map(map_df[["latitude", "longitude"]], use_container_width=True)

with tabs[3]: 
    st.markdown('<div class="section-title">Find a place to stay</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Browse accommodation ideas from the supplied project dataset. Confirm prices and availability directly.</div>', unsafe_allow_html=True)
    if stays.empty:
        st.info("No accommodation dataset was found. Add output.csv beside app.py to show stays.")
    else:
        s1, s2 = st.columns(2)
        with s1: stay_region = st.selectbox("Area", ["All areas"] + sorted(stays["region"].dropna().astype(str).unique()), key="stay_region") if "region" in stays else "All areas"
        with s2: stay_budget = st.selectbox("Budget", ["Any budget"] + sorted(stays["budget_level"].dropna().astype(str).unique()), key="stay_budget") if "budget_level" in stays else "Any budget"
        stay_view = stays.copy()
        if stay_region != "All areas" and "region" in stay_view: stay_view = stay_view[stay_view["region"].astype(str) == stay_region]
        if stay_budget != "Any budget" and "budget_level" in stay_view: stay_view = stay_view[stay_view["budget_level"].astype(str) == stay_budget]
        show = [c for c in ["name", "type", "region", "area", "budget_level", "price_range_inr", "nearest_airport", "nearest_station", "beach_access", "family_friendly", "wifi", "notes"] if c in stay_view.columns]
        st.dataframe(stay_view[show], use_container_width=True, hide_index=True)

with tabs[4]:
    st.markdown('<div class="section-title">A few helpful travel tips</div>', unsafe_allow_html=True)
    tips = [
        ("🌤️ Check the season", "Goa's monsoon season can affect beach access, water activities and outdoor travel. Check local advisories before you go."),
        ("🛵 Choose transport carefully", "A scooter can be flexible for confident riders. Taxis or a hired car may be easier for families, groups and longer trips."),
        ("🗺️ Check the road route", "Distances in this project are approximate. Open Google Maps for road directions and check traffic before departure."),
        ("💳 Confirm prices", "Entry fees, accommodation rates, transport fares and activity availability can change. Confirm with the provider."),
        ("🤝 Travel responsibly", "Respect local communities, keep beaches clean, follow safety signs and avoid swimming when conditions are unsafe."),
    ]
    for title, body in tips:
        with st.expander(title, expanded=True): st.write(body)
    st.divider()
    st.caption(f"Goa Smart Tourism Expert System · {len(places)} attractions loaded · Student project prototype. Not affiliated with Tripadvisor.")
