import math
import heapq
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="Goa Smart Tourism | Trip Planner", page_icon="🌴", layout="wide", initial_sidebar_state="expanded")
BASE_DIR = Path(__file__).resolve().parent
PLACES_FILE = BASE_DIR / "Goa_Places_Merged (2).csv"
STAYS_FILE = BASE_DIR / "output.csv"

VIBE_CATEGORIES = {
    "Beach & chill": ["Beaches"],
    "Heritage": ["Heritage & Religious"],
    "Adventure": ["Nature & Adventure"],
    "Nature": ["Nature & Adventure"],
    "Food & markets": ["Culture, Markets & Nightlife"],
    "Nightlife": ["Culture, Markets & Nightlife"],
    "Spiritual": ["Heritage & Religious"],
}
GROUPS = ["Solo", "Couple", "Family", "Friends"]
SEASONS = ["Winter (Nov-Feb)", "Summer (Mar-May)", "Monsoon (Jun-Sep)"]
BUDGETS = ["Low", "Mid", "High"]
TRANSPORTS = ["Own scooter or car", "No vehicle"]
REGIONS = ["North Goa", "Central Goa", "South Goa"]
COST_SCORE = {"Free / very low": 5, "Budget": 4, "Moderate": 3, "Expensive": 2, "Very expensive": 1}

# Illustrative category photos (not verified photographs of the exact venue).
PHOTO_BY_CATEGORY = {
    "Beaches": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=900&q=80",
    "Heritage & Religious": "https://images.unsplash.com/photo-1606293926075-69a00db_d6a3?auto=format&fit=crop&w=900&q=80",
    "Nature & Adventure": "https://images.unsplash.com/photo-1472396961693-142e6e269027?auto=format&fit=crop&w=900&q=80",
    "Culture, Markets & Nightlife": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80",
}
DEFAULT_PHOTO = "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=900&q=80"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --sea:#087f8c; --deep:#073b4c; --sand:#f5b971; --ink:#16343b; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container {padding-top: 1rem; padding-bottom: 3rem; max-width: 1440px;}
[data-testid="stSidebar"] {background: linear-gradient(180deg,#e8f7f5 0%,#f7fbfa 65%,#fff8ef 100%); border-right:1px solid #d8ebe8;}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {color:var(--deep);font-family:Manrope,sans-serif;}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {color:#16343b !important;}
[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="input"] *,
[data-testid="stSidebar"] [data-testid="stSlider"] *,
[data-testid="stSidebar"] [role="radiogroup"] label {color:#f8fafc;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#36565b !important;}
.hero {position:relative; overflow:hidden; min-height:270px; display:flex; flex-direction:column; justify-content:flex-end; padding:2rem; border-radius:26px; color:white; background:linear-gradient(90deg,rgba(4,42,54,.88),rgba(4,70,76,.45)),url('https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1800&q=85') center 48%/cover; box-shadow:0 16px 38px rgba(7,59,76,.16); margin-bottom:1.1rem;}
.hero h1 {color:white!important; margin:0; font-family:Manrope,sans-serif; font-size:clamp(2rem,4vw,3.25rem); font-weight:800; letter-spacing:-.04em;}
.hero p {margin:.65rem 0 0 0; color:#e7fffb; font-size:1.05rem; max-width:700px;}
.eyebrow {display:inline-block; width:fit-content; padding:.35rem .7rem; border:1px solid rgba(255,255,255,.4); border-radius:99px; color:#fff; font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; margin-bottom:.85rem; background:rgba(255,255,255,.12);}
.section-kicker {color:#087f8c;text-transform:uppercase;font-weight:700;letter-spacing:.09em;font-size:.75rem;}
.place-card {border:1px solid #e0ece9;border-radius:18px;overflow:hidden;background:var(--background-color);height:100%;box-shadow:0 5px 20px rgba(10,65,70,.06);margin-bottom:1rem;}
.place-card img {width:100%;height:150px;object-fit:cover;display:block;}
.place-card .body {padding:1rem;}
.place-card h3 {margin:0 0 .35rem 0;font-family:Manrope,sans-serif;font-size:1.05rem;color:var(--ink);}
.place-card p {font-size:.88rem;color:#62777b;margin:.35rem 0;}
div[data-testid="stMetric"] {background:linear-gradient(145deg,#f0faf8,#fff);padding:1rem;border:1px solid #deefeb;border-radius:16px;}
.stButton>button, .stDownloadButton>button, .stLinkButton>a {border-radius:12px;font-weight:700;min-height:2.7rem;}
.stButton>button[kind="primary"] {background:linear-gradient(100deg,#087f8c,#0b9a91);border:0;}
[data-testid="stTabs"] button {font-weight:700;}
[data-testid="stExpander"] {border:1px solid #e0ece9;border-radius:14px;overflow:hidden;}
@media (max-width: 700px) { .block-container {padding:.7rem .7rem 2rem .7rem;} .hero {min-height:230px;padding:1.25rem;border-radius:18px;} .hero p {font-size:.92rem;} [data-testid="stMetric"] {padding:.65rem;} [data-testid="stMetricValue"] {font-size:1.35rem;} }
</style>
<div class="hero"><span class="eyebrow">Discover · Explore · Experience</span><h1>Goa, your way.</h1><p>A smarter way to plan sunlit beaches, heritage trails, local culture and memorable days across Goa.</p></div>
""", unsafe_allow_html=True)
st.info("Travel smarter, explore thoughtfully. This academic prototype uses your supplied datasets; check live weather, opening hours, prices and local advisories before departure.", icon="🌊")

@st.cache_data
def load_data():
    places = pd.read_csv(PLACES_FILE)
    stays = pd.read_csv(STAYS_FILE)
    places.columns = [str(c).strip() for c in places.columns]
    stays.columns = [str(c).strip() for c in stays.columns]
    for c in ["Latitude", "Longitude", "Composite score (0-5)", "Average suitability", "Review score (5=best)", "Popularity score (5=most)"]:
        if c in places:
            places[c] = pd.to_numeric(places[c], errors="coerce")
    for c in ["latitude", "longitude"]:
        if c in stays:
            stays[c] = pd.to_numeric(stays[c], errors="coerce")
    required = ["Place", "Region", "Category", "Cost", "Latitude", "Longitude"]
    missing = [c for c in required if c not in places.columns]
    if missing:
        raise ValueError("Tourism CSV is missing columns: " + ", ".join(missing))
    return places, stays

def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(max(0, min(1, a))))

def infer_places(places, days, season, vibes, group, budget, transport, start_region):
    """Small explainable forward-chaining rule engine; filters are intentionally transparent."""
    facts = {"days": days, "season": season, "vibes": vibes, "group": group,
             "budget": budget, "transport": transport, "starting_region": start_region}
    fired = []
    def rule(code, condition, message):
        if condition: fired.append(f"{code} — {message}")
    rule("D1", days <= 2, "Short trip: favour a compact route and avoid over-scheduling.")
    rule("D2", 3 <= days <= 4, "Medium trip: use a main region plus a nearby region where possible.")
    rule("D3", days >= 5, "Long trip: spread sightseeing across Goa's three regions with a lighter day.")
    rule("S1", season.startswith("Winter"), "Winter preference: use the selected interests and scores; expect popular sites to be busy.")
    rule("S2", season.startswith("Summer"), "Summer preference: favour early/late outdoor visits and add breaks in the hottest hours.")
    rule("S3", season.startswith("Monsoon"), "Monsoon caution: swimming and water activities may be unsafe or suspended; verify local advisories.")
    rule("V1", "Beach & chill" in vibes, "Beach places are prioritised for a relaxed trip.")
    rule("V2", any(v in vibes for v in ["Heritage", "Spiritual"]), "Heritage and spiritual places are prioritised.")
    rule("V3", any(v in vibes for v in ["Adventure", "Nature"]), "Nature and adventure places are prioritised; check access before departure.")
    rule("V4", any(v in vibes for v in ["Food & markets", "Nightlife"]), "Culture, markets and nightlife places are prioritised.")
    rule("V5", len(vibes) > 1, "Multiple interests selected: ranking balances all selected categories.")
    rule("G1", group == "Family", "Family trip: apply a preference for calmer, broadly accessible visits.")
    rule("G2", group == "Couple", "Couple trip: slightly favour scenic and relaxed experiences.")
    rule("G3", group == "Friends", "Friends trip: slightly favour social, cultural and activity-oriented experiences.")
    rule("G4", group == "Solo", "Solo trip: slightly favour well-known places and practical daytime options.")
    rule("B1", budget == "Low", "Low budget: boost free and budget-cost places and remove very expensive options where possible.")
    rule("B2", budget == "High", "High budget: allow higher-cost experiences where the interest match is strong.")
    rule("T1", transport == "No vehicle", "No vehicle: favour a compact region plan and fewer stops per day.")
    rule("T2", transport == "Own scooter or car", "Own transport: allow a few more stops, while still grouping nearby places.")

    df = places.copy()
    selected_categories = {cat for vibe in vibes for cat in VIBE_CATEGORIES.get(vibe, [])}
    if selected_categories:
        matching = df[df["Category"].isin(selected_categories)].copy()
        if not matching.empty:
            # Respect the user's selected interests; only fall back if the dataset has no matches.
            df = matching
        else:
            fired.append("V6 — No exact category match was found in the dataset; showing the full list as a fallback.")
    score_col = "Composite score (0-5)"
    df["_score"] = pd.to_numeric(df.get(score_col, pd.Series(3, index=df.index)), errors="coerce").fillna(3.0)
    df["_cost"] = df["Cost"].map(COST_SCORE).fillna(3)
    if budget == "Low":
        df["_score"] += df["_cost"] * 0.20
        affordable = df[df["Cost"].isin(["Free / very low", "Budget", "Moderate"])]
        if len(affordable) >= min(3, days * 2): df = affordable.copy()
    elif budget == "Mid":
        df["_score"] += (df["_cost"] - 3).abs().mul(-0.06)
    else:
        df["_score"] += (6 - df["_cost"]) * 0.08
    if season.startswith("Monsoon"):
        status_col = "Monsoon (Jun-Sep) status"
        if status_col in df:
            risk = df[status_col].fillna("").str.contains("unsafe|closed|restricted|limited|suspended|slippery|waterlogged", case=False, regex=True)
            df["_score"] -= risk.astype(float) * 0.75
            if risk.any(): fired.append("M1 — Monsoon-sensitive places are down-ranked, not assumed closed; check current advisories.")
    if group == "Family" and "Crowd level" in df:
        df["_score"] += df["Crowd level"].astype(str).str.lower().map({"low": .12, "medium": .04, "high": -.10}).fillna(0)
    if group == "Couple" and "Type" in df:
        df["_score"] += df["Type"].astype(str).str.lower().map({"viewpoint": .18, "island": .12, "beach": .08, "heritage walk": .08}).fillna(0)
    if group == "Friends" and "Type" in df:
        df["_score"] += df["Type"].astype(str).str.lower().map({"nightlife": .18, "market": .10, "cruise": .08}).fillna(0)
    # Starting region is a soft preference, not a hard filter, so other regions remain available.
    df["_score"] += (df["Region"] == start_region).astype(float) * (0.70 if days <= 2 else 0.40)
    if transport == "No vehicle":
        df["_score"] += (df["Region"] == start_region).astype(float) * 0.25
    sort_cols = ["_score"]
    if "Review score (5=best)" in df: sort_cols.append("Review score (5=best)")
    df = df.sort_values(sort_cols, ascending=False).drop_duplicates("Place")
    if df.empty:
        df = places.copy(); df["_score"] = pd.to_numeric(df.get(score_col, 3), errors="coerce").fillna(3)
        fired.append("K1 — No preference-specific results; restored the full knowledge base as a fallback.")
    fired.append("K2 — Ranked places by composite score, budget fit, group preference, region and monsoon sensitivity.")
    fired.append("K3 — Each recommendation is traceable to the rules listed here; ratings and status come from the supplied dataset.")
    return df, fired, facts

def greedy_route(day_df):
    """Arrange stops by nearest next coordinate; distances are straight-line estimates."""
    valid = day_df.dropna(subset=["Latitude", "Longitude"]).copy()
    if len(valid) <= 1: return valid, 0.0
    rows = {str(r["Place"]): r for _, r in valid.iterrows()}
    current = str(valid.iloc[0]["Place"])
    remaining = set(rows) - {current}
    ordered = [current]
    distance = 0.0
    while remaining:
        here = rows[current]
        nxt = min(remaining, key=lambda name: haversine(float(here["Latitude"]), float(here["Longitude"]), float(rows[name]["Latitude"]), float(rows[name]["Longitude"])))
        there = rows[nxt]
        distance += haversine(float(here["Latitude"]), float(here["Longitude"]), float(there["Latitude"]), float(there["Longitude"]))
        ordered.append(nxt); remaining.remove(nxt); current = nxt
    ordered_df = pd.DataFrame([rows[n] for n in ordered])
    return ordered_df, distance

def build_itinerary(candidates, days, transport, start_region):
    max_stops = 2 if transport == "No vehicle" else 3
    # For short trips, keep the whole plan centred around the starting region.
    region_order = [start_region]
    for region in ["North Goa", "Central Goa", "South Goa"]:
        if region not in region_order: region_order.append(region)
    result, used = {}, set()
    for day in range(1, days + 1):
        preferred = region_order[(day - 1) % (1 if days <= 2 else min(3, len(region_order)))]
        pool = candidates[(candidates["Region"] == preferred) & (~candidates["Place"].isin(used))]
        if pool.empty: pool = candidates[~candidates["Place"].isin(used)]
        picked = pool.head(max_stops).copy()
        if picked.empty: break
        picked, _ = greedy_route(picked)
        result[day] = picked
        used.update(picked["Place"].tolist())
    return result

def maps_url(names):
    if not names: return ""
    destination = quote(str(names[-1])) + ", Goa, India"
    if len(names) == 1: return "https://www.google.com/maps/search/?api=1&query=" + destination
    origin = quote(str(names[0])) + ", Goa, India"
    waypoints = "|".join(quote(str(n)) + ", Goa, India" for n in names[1:-1])
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"
    if waypoints: url += "&waypoints=" + waypoints
    return url

def nearby_places(places, start_row, max_km=15, limit=10, categories=None):
    """Rank nearby dataset places by straight-line distance from the selected start."""
    df = places.copy()
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df = df.dropna(subset=["Latitude", "Longitude"])
    start_name = str(start_row["Place"])
    start_lat, start_lon = float(start_row["Latitude"]), float(start_row["Longitude"])
    df = df[df["Place"].astype(str) != start_name].copy()
    if categories:
        matching = df[df["Category"].isin(categories)]
        if not matching.empty:
            df = matching
    df["Approx. straight-line km"] = df.apply(
        lambda row: haversine(start_lat, start_lon, float(row["Latitude"]), float(row["Longitude"])), axis=1
    )
    df = df[df["Approx. straight-line km"] <= float(max_km)]
    return df.sort_values("Approx. straight-line km").head(int(limit)).reset_index(drop=True)


def maps_route_url(origin, destinations, travel_mode="driving"):
    """Build a Google Maps directions URL; Google Maps calculates the road route."""
    if not destinations:
        query = quote(f"{origin}, Goa, India")
        return f"https://www.google.com/maps/search/?api=1&query={query}"
    url = ("https://www.google.com/maps/dir/?api=1"
           f"&origin={quote(str(origin) + ', Goa, India')}"
           f"&destination={quote(str(destinations[-1]) + ', Goa, India')}"
           f"&travelmode={quote(travel_mode)}")
    if len(destinations) > 1:
        url += "&waypoints=" + quote("|".join(f"{name}, Goa, India" for name in destinations[:-1]), safe="")
    return url

def recommend_stays(stays, budget, regions):
    if "budget_level" not in stays: return stays.head(0)
    budget_map = {"Low": "Low", "Mid": "Medium", "High": "High"}
    result = stays[stays["budget_level"].astype(str).str.lower() == budget_map[budget].lower()].copy()
    if regions and "region" in result:
        mapped = [r.replace(" Goa", "") for r in regions]
        regional = result[result["region"].isin(mapped)]
        if not regional.empty: result = regional
    return result.head(8)

try:
    places, stays = load_data()
except Exception as e:
    st.error(f"Could not load the CSV files. Keep both CSVs in the same folder as app.py. Details: {e}")
    st.stop()

with st.sidebar:
    st.header("🧭 Build your trip")
    days_label = st.selectbox("Trip duration", ["1–2 days", "3–4 days", "5+ days"])
    days = {"1–2 days": 2, "3–4 days": 4, "5+ days": 5}[days_label]
    season = st.selectbox("Season", SEASONS)
    vibes = st.multiselect("What do you enjoy?", list(VIBE_CATEGORIES), default=["Beach & chill"],
                           help="Choose one or more interests. Recommendations will prioritize the selected categories.")
    if not vibes:
        st.caption("No interest selected — all categories will be considered.")
        vibes = list(VIBE_CATEGORIES)
    group = st.selectbox("Travelling with", GROUPS)
    budget = st.select_slider("Budget", options=BUDGETS, value="Mid")
    transport = st.radio("Transport", TRANSPORTS)
    start_region = st.selectbox("Starting region", REGIONS, index=0)
    st.caption("You can change any preference and regenerate the plan.")
    generate = st.button("✨ Generate my itinerary", type="primary", use_container_width=True)

if generate or "run_result" not in st.session_state:
    ranked, rules, facts = infer_places(places, days, season, vibes, group, budget, transport, start_region)
    itinerary = build_itinerary(ranked, days, transport, start_region)
    st.session_state["run_result"] = {"ranked": ranked, "rules": rules, "facts": facts, "itinerary": itinerary,
        "days": days, "season": season, "vibes": vibes, "group": group, "budget": budget,
        "transport": transport, "start_region": start_region}

res = st.session_state["run_result"]
ranked, itinerary = res["ranked"], res["itinerary"]
# Summary metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Places in knowledge base", f"{len(places)}")
m2.metric("Planned days", str(res["days"]))
m3.metric("Recommended stops", str(sum(len(x) for x in itinerary.values())))
m4.metric("Accommodation records", str(len(stays)))
st.caption(f"Current plan: {', '.join(res['vibes'])} · {res['season']} · {res['budget']} budget · {res['group']} · {res['transport']} · start in {res['start_region']}")
st.success("Your itinerary has been generated using the preferences shown above. Change any option in the sidebar and select **Generate my itinerary** to update it.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗓️ Your itinerary", "📍 Explore & map", "🏨 Places to stay", "🧠 How it works", "🛣️ Nearby & road route"])

with tab1:
    st.subheader(f"Your {res['days']}-day plan")
    if not itinerary:
        st.warning("No itinerary could be built. Try changing the preferences.")
    for day, day_df in itinerary.items():
        region = str(day_df.iloc[0]["Region"])
        with st.expander(f"Day {day} · {region} · {len(day_df)} stops", expanded=(day == 1)):
            for idx, (_, place) in enumerate(day_df.iterrows(), 1):
                name = str(place["Place"])
                typ = str(place.get("Type", place.get("Category", "Sightseeing")))
                cost = str(place.get("Cost", "Check locally"))
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(f"**{idx}. {name}**")
                    st.caption(f"{typ} · {place.get('Region', 'Goa')} · {cost}")
                    note = str(place.get("Notes", ""))
                    if note and note.lower() != "nan": st.write(note)
                with col_b:
                    st.markdown("🕒")
                    st.caption("Allow 1–2 h")
                if idx < len(day_df): st.divider()
            names = day_df["Place"].astype(str).tolist()
            _, km = greedy_route(day_df)
            st.info(f"Estimated straight-line distance between stops: **{km:.1f} km**. Road distance and travel time will differ.")
            st.link_button("Open this day's stops in Google Maps", maps_url(names), use_container_width=True)
    export_rows = []
    for day, day_df in itinerary.items():
        for order, (_, row) in enumerate(day_df.iterrows(), 1):
            export_rows.append({"Day": day, "Stop": order, "Place": row.get("Place"), "Region": row.get("Region"), "Category": row.get("Category"), "Cost": row.get("Cost"), "Latitude": row.get("Latitude"), "Longitude": row.get("Longitude")})
    if export_rows:
        export = pd.DataFrame(export_rows)
        st.download_button("⬇️ Download itinerary (CSV)", export.to_csv(index=False).encode("utf-8-sig"), "goa_smart_itinerary.csv", "text/csv")

with tab2:
    st.markdown('<div class="section-kicker">Handpicked for your preferences</div>', unsafe_allow_html=True)
    st.subheader("Places worth discovering")
    st.caption("Recommendations are ranked by your selected interests, budget, group, season and starting region. Photos are illustrative category images.")
    gallery = ranked.head(6)
    gallery_cols = st.columns(3)
    for i, (_, place) in enumerate(gallery.iterrows()):
        photo = PHOTO_BY_CATEGORY.get(str(place.get("Category", "")), DEFAULT_PHOTO)
        name = str(place.get("Place", "Goa highlight"))
        region = str(place.get("Region", "Goa"))
        category = str(place.get("Category", "Experience"))
        cost = str(place.get("Cost", "Check locally"))
        note = str(place.get("Notes", ""))
        if note.lower() == "nan": note = ""
        card_html = f'<div class="place-card"><img src="{photo}" alt="Illustrative Goa travel photo"><div class="body"><h3>{name}</h3><p>📍 {region} · {category}</p><p>💰 {cost}</p><p>{note[:150]}</p></div></div>'
        with gallery_cols[i % 3]:
            st.markdown(card_html, unsafe_allow_html=True)
    st.markdown("### All matching places")
    display_cols = [c for c in ["Place", "Region", "Taluka", "Category", "Type", "Cost", "Review score (5=best)", "Composite score (0-5)", "Monsoon (Jun-Sep) status"] if c in ranked.columns]
    st.dataframe(ranked[display_cols].head(30), use_container_width=True, hide_index=True)
    st.download_button("Download recommendations (CSV)", ranked[display_cols].to_csv(index=False).encode("utf-8-sig"), "goa_recommendations.csv", "text/csv")
    coords = ranked.dropna(subset=["Latitude", "Longitude"]).copy()
    coords = coords.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
    coords["latitude"] = pd.to_numeric(coords["latitude"], errors="coerce")
    coords["longitude"] = pd.to_numeric(coords["longitude"], errors="coerce")
    coords = coords.dropna(subset=["latitude", "longitude"]).head(40)
    if not coords.empty:
        st.markdown("#### Map preview")
        st.caption("Pins show dataset coordinates for recommended places. Verify coordinates and access before travelling.")
        st.pydeck_chart(pdk.Deck(initial_view_state=pdk.ViewState(latitude=float(coords["latitude"].mean()), longitude=float(coords["longitude"].mean()), zoom=8.5, pitch=0), layers=[pdk.Layer("ScatterplotLayer", data=coords, get_position="[longitude, latitude]", get_radius=100, get_fill_color=[8, 127, 140, 190], pickable=True)], tooltip={"text": "{Place}\n{Region}\n{Category}"}), use_container_width=True)

with tab3:
    st.subheader("Accommodation ideas")
    regions = list(dict.fromkeys([str(x) for x in ranked["Region"].head(12).tolist()]))
    stay_recs = recommend_stays(stays, res["budget"], regions)
    if stay_recs.empty:
        st.warning("No stays matched this budget in the supplied data. Try another budget.")
    else:
        cols = [c for c in ["name", "type", "region", "area", "budget_level", "price_range_inr", "nearest_airport", "nearest_station", "beach_access", "family_friendly", "wifi", "best_season", "notes"] if c in stay_recs.columns]
        st.dataframe(stay_recs[cols], use_container_width=True, hide_index=True)
        st.caption("Accommodation data comes from the supplied CSV; prices, facilities and availability should be confirmed with the property.")
        if all(c in stay_recs.columns for c in ["latitude", "longitude"]):
            stay_coords = stay_recs.copy()
            stay_coords["latitude"] = pd.to_numeric(stay_coords["latitude"], errors="coerce")
            stay_coords["longitude"] = pd.to_numeric(stay_coords["longitude"], errors="coerce")
            stay_coords = stay_coords.dropna(subset=["latitude", "longitude"])
            if not stay_coords.empty:
                st.markdown("#### Stay locations")
                st.pydeck_chart(pdk.Deck(initial_view_state=pdk.ViewState(latitude=float(stay_coords["latitude"].mean()), longitude=float(stay_coords["longitude"].mean()), zoom=8.5), layers=[pdk.Layer("ScatterplotLayer", data=stay_coords, get_position="[longitude, latitude]", get_radius=130, get_fill_color=[242, 166, 90, 210], pickable=True)], tooltip={"text":"{name}\n{area}\n{price_range_inr}"}), use_container_width=True)

with tab4:
    st.subheader("Working memory")
    st.json(res["facts"])
    st.subheader("Rules that fired")
    for item in res["rules"]: st.markdown(f"- {item}")
    if res["season"].startswith("Monsoon") and any(v in res["vibes"] for v in ["Beach & chill", "Adventure"]):
        st.warning("Monsoon conflict check: the system can still recommend beach/nature places, but it down-ranks known sensitive entries. Check weather, sea conditions, operator status and local advisories on the day.")
    st.subheader("How to interpret route distances")
    st.write("The in-app kilometre estimate is a straight-line distance between coordinates after arranging stops by a nearest-next heuristic. The Google Maps link opens a road route in your browser; its road distance and travel time may differ. This app does not claim live road-network routing.")
    st.subheader("Knowledge base")
    st.write(f"Loaded {len(places)} place records and {len(stays)} accommodation records from the supplied CSV files.")


with tab5:
    st.subheader("Find nearby attractions and plan an easier route")
    st.write("Choose a place as your starting point. The app ranks nearby attractions using the coordinates in your dataset, then opens Google Maps for road directions.")
    route_places = places.dropna(subset=["Latitude", "Longitude"]).copy()
    route_places["Latitude"] = pd.to_numeric(route_places["Latitude"], errors="coerce")
    route_places["Longitude"] = pd.to_numeric(route_places["Longitude"], errors="coerce")
    route_places = route_places.dropna(subset=["Latitude", "Longitude"])
    if route_places.empty:
        st.warning("No usable coordinates were found in the tourism dataset.")
    else:
        place_names = route_places["Place"].astype(str).tolist()
        start_name = st.selectbox("Where are you starting from?", place_names, key="nearby_start")
        c1, c2, c3 = st.columns(3)
        with c1:
            max_km = st.slider("Search radius (straight-line km)", min_value=2, max_value=80, value=20, step=2)
        with c2:
            max_places = st.slider("Maximum attractions", min_value=2, max_value=12, value=6)
        with c3:
            mode_label = st.selectbox("Travel mode for Google Maps", ["Driving", "Walking", "Bicycling"])
        start_rows = route_places[route_places["Place"].astype(str) == start_name]
        if not start_rows.empty:
            start_row = start_rows.iloc[0]
            category_options = sorted(places["Category"].dropna().astype(str).unique().tolist())
            selected_near_categories = st.multiselect("Optional: focus on attraction types", category_options, key="nearby_categories")
            near = nearby_places(route_places, start_row, max_km=max_km, limit=max_places, categories=selected_near_categories or None)
            if near.empty:
                st.info("No other attractions were found in this radius. Increase the search radius or clear the category filter.")
            else:
                show_cols = [c for c in ["Place", "Region", "Category", "Cost", "Approx. straight-line km", "Notes"] if c in near.columns]
                display = near[show_cols].copy()
                display["Approx. straight-line km"] = display["Approx. straight-line km"].round(1)
                st.markdown("#### Closest attractions first")
                st.dataframe(display, use_container_width=True, hide_index=True)
                st.caption("Distances above are straight-line estimates, not road kilometres. Road routes and travel times are calculated by Google Maps when opened; traffic and access can change.")
                selected_names = near["Place"].astype(str).tolist()
                mode = {"Driving": "driving", "Walking": "walking", "Bicycling": "bicycling"}[mode_label]
                st.link_button("🗺️ Open nearby route in Google Maps", maps_route_url(start_name, selected_names, mode), use_container_width=True)
                st.markdown("#### Individual directions")
                for _, row in near.iterrows():
                    name = str(row["Place"])
                    km = float(row["Approx. straight-line km"])
                    url = maps_route_url(start_name, [name], mode)
                    st.markdown(f"- **{name}** — approximately {km:.1f} km straight-line · [Get directions]({url})")
                # A coordinate preview shows the selected start and nearby candidates.
                map_df = near.copy()
                start_pin = pd.DataFrame([{"Place": start_name, "Region": start_row.get("Region", "Goa"), "Category": "Starting point", "Latitude": float(start_row["Latitude"]), "Longitude": float(start_row["Longitude"])}])
                map_df = pd.concat([start_pin, map_df], ignore_index=True, sort=False)
                map_df = map_df.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
                st.markdown("#### Attraction map preview")
                st.pydeck_chart(pdk.Deck(
                    initial_view_state=pdk.ViewState(latitude=float(map_df["latitude"].mean()), longitude=float(map_df["longitude"].mean()), zoom=10, pitch=0),
                    layers=[pdk.Layer("ScatterplotLayer", data=map_df, get_position="[longitude, latitude]", get_radius=150, get_fill_color=[8, 127, 140, 210], pickable=True)],
                    tooltip={"text": "{Place}\n{Region}\n{Category}"}), use_container_width=True)
                st.info("For a true shortest road route, use the Google Maps link. The in-app ranking uses your CSV coordinates because the supplied dataset does not contain a verified road network.")

st.divider()
st.caption("Goa Smart Tourism Expert System · educational prototype · verify live conditions, prices, opening hours and transport before travel.")
