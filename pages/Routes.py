import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title="Route Maps", page_icon="🗺️", layout="centered")

# --- CUSTOM CSS (Matches Main App) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    h1, h2, h3 { color: white !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

try:
    st.logo("logo.png")
except:
    pass

st.title("🚌 Route Timetables")

# Route Selector
route_options = ["1 - Banbury", "2 - Leamington", "3 - Northampton", "4 - Milton Keynes", "5 - Oxford", "6 - Rugby", "7 - London"]
selected_route = st.selectbox("Select a Route:", route_options)

# Load the correct CSV based on selection
route_num = selected_route.split(" - ")[0]
filename = f"route{route_num}.csv"

try:
    df = pd.read_csv(filename)
    
    # 1. TIMETABLE
    st.subheader(f"⏱️ Timetable: Route {route_num}")
    st.dataframe(
        df[['Stop Name', 'Time']], 
        hide_index=True, 
        use_container_width=True
    )

    # 2. MAP
    st.subheader("🗺️ Route Map")
    
    # Center map on the first stop
    start_lat = df.iloc[0]['Lat']
    start_lon = df.iloc[0]['Lon']
    m = folium.Map(location=[start_lat, start_lon], zoom_start=11)

    # Add Points and Line
    points = []
    for index, row in df.iterrows():
        coords = [row['Lat'], row['Lon']]
        points.append(coords)
        
        # Add Marker
        folium.Marker(
            coords,
            popup=f"{row['Stop Name']} ({row['Time']})",
            tooltip=row['Stop Name'],
            icon=folium.Icon(color="green", icon="bus", prefix="fa")
        ).add_to(m)

    # Draw the line connecting stops
    folium.PolyLine(points, color="#229971", weight=5, opacity=0.8).add_to(m)

    folium_static(m, height=400, width=700)

except FileNotFoundError:
    st.info(f"Route data for {selected_route} is coming soon.")

# Back Button
if st.button("⬅️ Back to Ticket Search"):
    st.switch_page("app.py")
