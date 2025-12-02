import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import base64
import requests
import polyline

# 1. Page Config
st.set_page_config(page_title="Route Details", page_icon="🗺️", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stSidebar"] {display: none;}

    /* Full Width Banner Hack */
    .block-container {
        padding-top: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100%;
    }
    
    .banner-container {
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        margin-top: -6rem;
        height: 250px; 
        overflow: hidden;
        margin-bottom: 20px;
    }
    
    .banner-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
    }
    
    /* Typography - CENTER ALIGNMENT */
    h1, h2, h3, p, div {
        text-align: center !important;
        color: white !important;
    }
    
    h1 { margin-top: 1rem; }
    
    /* Main Content Wrapper */
    .main-content {
        padding: 0rem 1rem;
        max-width: 800px;
        margin: 0 auto;
        text-align: center; /* Force center alignment for all content */
    }

    /* Table Links */
    a { color: #229971 !important; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; }
    
    /* Back Button Centering */
    div.stButton > button {
        display: block;
        margin: 0 auto;
        background-color: #229971 !important;
        color: white !important;
        width: 100%;
    }
    
    /* Force Center for Map and Table */
    iframe { 
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    /* Target the dataframe container */
    div[data-testid="stDataFrame"] {
        width: fit-content !important;
        margin: 0 auto !important;
    }
    
    /* Ensure the map container is centered */
    div[data-testid="stFolium"] {
        display: flex;
        justify_content: center;
        align-items: center;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

# --- OSRM ROUTING FUNCTION ---
@st.cache_data
def get_osrm_route(coordinates):
    """
    Fetch route geometry from OSRM public API.
    coordinates: List of [lat, lon] pairs.
    """
    # OSRM expects [lon, lat]
    locs = [f"{lon},{lat}" for lat, lon in coordinates]
    loc_string = ";".join(locs)
    url = f"http://router.project-osrm.org/route/v1/driving/{loc_string}?overview=full&geometries=polyline"
    
    try:
        r = requests.get(url)
        if r.status_code == 200:
            res = r.json()
            # Decode polyline
            route_coords = polyline.decode(res['routes'][0]['geometry'])
            return route_coords
    except Exception: # Fixed Syntax Error here (added space)
        return None
    return None

# --- HERO BANNER ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# Look for banner in parent folder since we are in pages/
banner_b64 = get_base64_image("banner.jpg") 
if not banner_b64:
    banner_b64 = get_base64_image("../banner.jpg")

if banner_b64:
    banner_html = f'<img src="data:image/jpg;base64,{banner_b64}">'
else:
    banner_html = '<img src="https://media.formula1.com/image/upload/f_auto,c_limit,w_1440,q_auto/f_auto/q_auto/content/dam/fom-website/2018-redesign-assets/team%20logos/aston%20martin%202024.png">'

st.markdown(f"""<div class="banner-container">{banner_html}</div>""", unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

try:
    st.image("logo.png", width=150)
except:
    try:
        st.image("../logo.png", width=150)
    except:
        pass

# --- LOGIC: GET ROUTE ---
if "view_route_num" not in st.session_state:
    st.warning("⚠️ No route selected.")
    if st.button("⬅️ Back"):
        st.switch_page("app.py")
    st.stop()

route_num = st.session_state.view_route_num
filename = f"route{route_num}.csv"

# Removed Emoji from Title
st.title(f"Route {route_num} Details")

try:
    # Read CSV
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.read_csv(f"../{filename}")
    
    # --- 1. MAP (Full Route with OSRM) ---
    st.subheader("Route Map") # Removed Emoji
    
    if 'Lat' in df.columns and 'Lon' in df.columns:
        avg_lat = df['Lat'].mean()
        avg_lon = df['Lon'].mean()
        
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10)
        
        points = []
        for index, row in df.iterrows():
            coords = [row['Lat'], row['Lon']]
            points.append(coords)
            
            folium.Marker(
                coords,
                popup=f"{row['Stop Name']}<br>{row['Time']}",
                tooltip=row['Stop Name'],
                # Removed specific bus icon to be cleaner, just default pin or simple dot
                icon=folium.Icon(color="green", icon="info-sign") 
            ).add_to(m)
        
        # Draw Route Line (OSRM)
        if len(points) > 1:
            route_path = get_osrm_route(points)
            if route_path:
                folium.PolyLine(
                    route_path, 
                    color="#229971", 
                    weight=5, 
                    opacity=0.8
                ).add_to(m)
            else:
                # Fallback to straight lines if OSRM fails
                folium.PolyLine(
                    points, 
                    color="#229971", 
                    weight=5, 
                    opacity=0.8,
                    dash_array='5'
                ).add_to(m)

            m.fit_bounds(points)

        # FIX: Use st_folium with specific width/height to avoid warning
        # returned_objects=[] prevents the loop/crash
        # WRAPPED in columns to ensure centering
        c1, c2, c3 = st.columns([1, 10, 1])
        with c2:
             st_folium(m, height=400, width=700, returned_objects=[])
        
    else:
        st.warning("Map coordinates missing.")

    # --- 2. TIMETABLE ---
    st.divider()
    st.subheader(f"Timetable") # Removed Emoji
    
    display_df = df[['Stop Name', 'Time']].copy()
    if 'W3W' in df.columns:
        display_df['Location'] = df['W3W'].apply(
            lambda x: f"<a href='https://w3w.co/{str(x).replace('///', '')}' target='_blank'>{x}</a>"
        )
    
    # Use HTML table to support centering and links
    # Added 'margin: auto' style directly to the table HTML to force centering
    table_html = display_df.to_html(escape=False, index=False, classes="table-centered")
    table_html = table_html.replace('<table', '<table style="margin-left: auto; margin-right: auto;"')
    st.write(table_html, unsafe_allow_html=True)

except FileNotFoundError:
    st.info(f"Route data for Route {route_num} is coming soon.")

st.divider()

if st.button("⬅️ Back to Ticket Search"):
    st.switch_page("app.py")

st.markdown('</div>', unsafe_allow_html=True)
