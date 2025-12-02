import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 1. Page Config
st.set_page_config(page_title="Route Map", page_icon="🗺️", layout="centered")

# --- CUSTOM CSS (Matches Main App) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    img { border-radius: 5px; }
    h1, h2, h3 { color: white !important; text-align: center !important; }
    
    /* Center the back button */
    div.stButton > button:first-child {
        display: block;
        margin: 0 auto;
    }
    
    /* Link style for table */
    a { color: #229971 !important; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; }
    
    /* Hide Sidebar Nav */
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- BRANDING HEADER ---
try:
    st.image("banner.jpg", use_container_width=True) 
except:
    pass

try:
    st.logo("logo.png")
except:
    pass

# --- LOGIC: GET ROUTE FROM SESSION STATE ---
# This effectively "locks" the page. If they didn't click a specific route, they get bounced back.
if "view_route_num" not in st.session_state:
    st.warning("⚠️ No route selected. Please go back to the ticket page.")
    if st.button("⬅️ Back to Ticket Search"):
        st.switch_page("app.py")
    st.stop()

# Get the number passed from the main app
route_num = st.session_state.view_route_num
filename = f"route{route_num}.csv"

st.title(f"🚌 Route {route_num} Details")

try:
    # Read the CSV
    df = pd.read_csv(filename)
    
    # --- 1. TIMETABLE ---
    st.subheader(f"⏱️ Timetable")
    
    # Create display dataframe
    display_df = df[['Stop Name', 'Time']].copy()
    
    # Make W3W links clickable if column exists
    if 'W3W' in df.columns:
        display_df['Location'] = df['W3W'].apply(
            lambda x: f"<a href='https://w3w.co/{x.replace('///', '')}' target='_blank'>{x}</a>"
        )
    
    # Display as HTML table to allow links
    st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # --- 2. MAP ---
    st.subheader("🗺️ Route Map")
    
    if 'Lat' in df.columns and 'Lon' in df.columns:
        # Center map on the first stop
        start_lat = df.iloc[0]['Lat']
        start_lon = df.iloc[0]['Lon']
        m = folium.Map(location=[start_lat, start_lon], zoom_start=11)

        # Add Points and Line
        points = []
        for index, row in df.iterrows():
            coords = [row['Lat'], row['Lon']]
            points.append(coords)
            
            # Popup with Stop Name & Time
            popup_text = f"{row['Stop Name']}<br>Time: {row['Time']}"
            
            # Add Marker
            folium.Marker(
                coords,
                popup=popup_text,
                tooltip=row['Stop Name'],
                # Green Bus Icon
                icon=folium.Icon(color="green", icon="bus", prefix="fa")
            ).add_to(m)

        # Draw the line connecting stops (only if more than 1 point)
        if len(points) > 1:
            folium.PolyLine(points, color="#229971", weight=5, opacity=0.8).add_to(m)

        # Display Static Map (Stable)
        folium_static(m, height=400, width=700)
    else:
        st.warning("Map coordinates missing for this route.")

except FileNotFoundError:
    st.info(f"Route data for Route {route_num} is coming soon.")

st.divider()

# Back Button
if st.button("⬅️ Back to Ticket Search"):
    st.switch_page("app.py")
