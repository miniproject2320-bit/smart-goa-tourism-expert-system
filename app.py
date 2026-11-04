from pathlib import Path
from urllib.parse import quote
import math

import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(
    page_title="Explore Goa | Smart Tourism Guide",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
