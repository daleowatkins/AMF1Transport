import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import re
import base64
import os

# 1. Page Config
st.set_page_config(page_title="AMF1 Transport", page_icon="🏎️", layout="centered")

# --- MEMORY INITIALIZATION ---
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
if 'booking_code' not in st.session_state:
    st.session_state.booking_code = ""
if 'navigate_to_route' not in st.session_state:
    st.session_state.navigate_to_route = False
if 'view_route_num' not in st.session_state:
    st.session_state.view_route_num = None

# --- NAVIGATION LOGIC (Must be Top Level) ---
if st.session_state.navigate_to_route:
    st.session_state.navigate_to_route = False 
    st.switch_page("pages/Routes.py")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stSidebar"] {display: none;}

    /* Professional Banner Style */
    .banner-container {
        width: 100%;
        height: 200px; 
        overflow: hidden;
        margin-bottom: 20px;
        border-radius: 10px;
    }
    
    .banner-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
    }
    
    /* Typography */
    h1 {
        text-align: center !important;
        color: white !important;
        margin-top: 1rem;
    }
    
    h2, h3, p, div {
        color: white !important;
    }
    
    /* Link Style */
    .route-link {
        color: #229971 !important;
        font-weight: bold;
        text-decoration: none !important;
    }
    .route-link:hover {
        color: #2DFFBC !important;
        text-decoration: none !important;
    }
    
    /* Expander & Button */
    .streamlit-expanderHeader {
        background-color: #1F1F1F;
        color: white;
    }
    
    div.stButton > button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Load Data
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("bookings.csv", dtype=str)
        data.columns = data.columns.str.strip()
        data['Code'] = data['Code'].ffill().str.strip().str.upper()
        
        if 'Direction' not in data.columns: data['Direction'] = "Both"
        if 'PickupTime' not in data.columns: data['PickupTime'] = "TBC"

        if 'Lat' in data.columns and 'Lon' in data.columns:
            data['Lat'] = pd.to_numeric(data['Lat'], errors='coerce')
            data['Lon'] = pd.to_numeric(data['Lon'], errors='coerce')
            
        return data
    except FileNotFoundError:
        return None

df = load_data()

# --- 3. HERO BANNER ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

banner_b64 = get_base64_image("banner.jpg")
if banner_b64:
    st.markdown(f'<div class="banner-container"><img src="data:image/jpg;base64,{banner_b64}"></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="banner-container"><img src="
