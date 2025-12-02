import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Page Config
st.set_page_config(page_title="Route Maps", page_icon="🗺️", layout="centered")

# Custom CSS (Matches main app)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    h1, h2, h3 { color: white !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# Logo
try:
    st.logo("logo.png")
except:
    pass

st.title("🚌 Route Timetables & Maps")

# Route Selector
route_id = st.selectbox(
    "Select a Route to view details:",
    ["1 - Banbury", "2 - Leamington", "3 - Northampton", "4 - Milton Keynes", 
     "5 - Oxford", "6 - Rugby", "7 - London"]
)

# Extract just the number (e.g., "1")
r_num = route_id.split(" - ")[0]
filename = f"route{r_num}.csv"

# Load Route Data
try:
    df = pd.read_csv(filename)
    
    # 1. Display Timetable
    st.subheader(f"⏱️ Timetable: {route_id}")
    st.dataframe(
        df[['Stop Name', 'Time']], 
        hide_index=True, 
        use_container_width=True
    )

    # 2. Display Map
    st.subheader("🗺️ Route Map")
    
    # Center map on the first stop
    start_lat = df.iloc[0]['Lat']
    start_lon = df.iloc[0]['Lon']
    m = folium.Map(location=[start_lat, start_lon], zoom_start=10)

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
    st.error(f"Data for {route_id} not found. Please upload '{filename}'.")
except Exception as e:
    st.error(f"An error occurred: {e}")

# Back Button
if st.button("⬅️ Back to Ticket Search"):
    st.switch_page("app.py")
```

### Step 4: Update `app.py` to Link to this Internal Page
Instead of linking to `github.io`, we will link to the internal Streamlit page.

**Update the `ROUTE_URLS` section in `app.py` to this:**
*(Note: Streamlit doesn't support direct URL parameters easily yet, so simply directing them to the "Routes" page is the cleanest way. They can then select their route from the dropdown).*

**Wait!** To make it truly seamless ("Click Ticket -> See Specific Route"), we can use **Query Parameters**.

**Revised `app.py` Link Logic (Replace the loop section):**
Change the link generation in `app.py` to:
`link_url = f"/Routes?route={route_num}"`

And update the top of `pages/Routes.py` to read that parameter:
```python
# Check for URL parameter ?route=1
query_params = st.query_params
default_index = 0

if "route" in query_params:
    r_param = query_params["route"]
    # Logic to find which list item matches "1" -> Index 0
    # (I can write this logic if you want this advanced flow)
