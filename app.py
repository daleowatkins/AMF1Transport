import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import re

# 1. Page Config
st.set_page_config(page_title="AMF1 Transport", page_icon="🏎️", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* Rounded corners for the banner */
    img {
        border-radius: 5px;
    }
    
    /* Center Title */
    h1 {
        text-align: center !important;
        color: white !important;
    }
    
    h2, h3 {
        color: white !important;
    }
    
    /* Custom Link Style for Routes */
    .route-link {
        color: #229971 !important;
        font-weight: bold;
        text-decoration: none !important;
    }
    .route-link:hover {
        color: #2DFFBC !important;
        text-decoration: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORY INITIALIZATION ---
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
if 'booking_code' not in st.session_state:
    st.session_state.booking_code = ""

# --- ROUTE MAPPING CONFIGURATION ---
# This maps the Route Name (from CSV) to your specific GitHub URL
# Note: This dictionary is kept for reference, but the app now uses internal page switching
ROUTE_URLS = {
    "1": "https://daleowatkins.github.io/AMF1Transport/route1.html",
    "2": "https://daleowatkins.github.io/AMF1Transport/route2.html",
    "3": "https://daleowatkins.github.io/AMF1Transport/route3.html",
    "4": "https://daleowatkins.github.io/AMF1Transport/route4.html",
    "5": "https://daleowatkins.github.io/AMF1Transport/route5.html",
    "6": "https://daleowatkins.github.io/AMF1Transport/route6.html",
    "7": "https://daleowatkins.github.io/AMF1Transport/route7.html"
}

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

# --- 3. BRANDING HEADER ---
try:
    st.image("banner.jpg", use_container_width=True) 
except:
    pass

try:
    st.logo("logo.png")
except:
    pass

st.title("Aston Martin F1 End of Season Party Transport")

if df is None:
    st.error("⚠️ System Error: 'bookings.csv' not found.")
    st.stop()

# 4. Login Form
with st.container(border=True):
    st.write("Please enter your booking reference.")
    
    def update_search():
        st.session_state.search_performed = True
        st.session_state.booking_code = st.session_state.widget_input.upper().strip()

    with st.form(key='login_form'):
        st.text_input("Booking Code", key="widget_input")
        st.form_submit_button(label='Find My Booking', type="primary", on_click=update_search)

# 5. Results Logic
if st.session_state.search_performed:
    user_code = st.session_state.booking_code
    bookings = df[df['Code'] == user_code]

    if not bookings.empty:
        st.success(f"✅ Found {len(bookings)} passengers")
        
        for index, row in bookings.iterrows():
            with st.expander(f"🎫 Passenger: {row['Name']}", expanded=True):
                
                # --- TRAVEL BADGE ---
                direction = str(row['Direction']).title()
                label_text = "Pickup:"
                show_time, show_return_msg = False, False
                badge_color, icon, pin_color = "blue", "🚌", "blue"

                if "Both" in direction:
                    label_text, show_time, show_return_msg = "Pickup & Dropoff:", True, True
                    badge_color, icon, pin_color = "green", "🔄", "green"
                elif "To" in direction:
                    label_text, show_time, show_return_msg = "Pickup:", True, False
                    badge_color, icon, pin_color = "orange", "➡️", "green"
                else:
                    label_text, show_time, show_return_msg = "Dropoff:", False, True
                    badge_color, icon, pin_color = "blue", "⬅️", "blue"

                st.markdown(f":{badge_color}[**{icon} Travel Direction: {direction}**]")
                st.divider()

                # --- DETAILS ---
                c1, c2 = st.columns([1.5, 2])
                with c1:
                    # Route Link Logic
                    route_name = str(row['Route'])
                    match = re.search(r'\d+', route_name)
                    
                    # Just display the name
                    st.write(f"**Route:** {route_name}")
                    
                    # Create a specific button for this route
                    if match:
                        r_num = match.group()
                        # Unique key for every button (important!)
                        if st.button(f"👉 View Route {r_num} Map", key=f"btn_route_{index}"):
                            st.session_state.view_route_num = r_num  # SAVE to memory
                            st.switch_page("pages/Routes.py")        # SWITCH page
                    
                    st.write(f"**{label_text}** {row['Pickup']}")
                    
                    if show_time:
                        p_time = row.get('PickupTime')
                        if pd.isna(p_time): p_time = "TBC"
                        st.write(f"**⏱️ Time:** {p_time}")
                        
                        st.info("⚠️ Please ensure you are at your pickup point 5 mins before your time. The coach will unfortunately only be able to wait 2 minutes for any missing passengers.")

                    if show_return_msg:
                        st.info("ℹ️ **Return:** All coaches depart Silverstone at 01:00 AM.")

                    if pd.notna(row['MapLink']):
                        st.link_button("/// What 3 Words Link", row['MapLink'])
                        
                with c2:
                    # --- STATIC MAP (STOPS SPINNING) ---
                    lat, lon = row.get('Lat'), row.get('Lon')
                    if pd.notna(lat) and pd.notna(lon):
                        m = folium.Map(location=[lat, lon], zoom_start=16, control_scale=False, zoom_control=False)
                        folium.Marker(
                            [lat, lon], 
                            popup=row['Pickup'], 
                            icon=folium.Icon(color=pin_color, icon="bus", prefix="fa")
                        ).add_to(m)
                        
                        # Use folium_static instead of st_folium
                        folium_static(m, height=200, width=350)
                    else:
                        st.info("🗺️ Map not available")

        # Footer
        st.divider()
        main_contact = bookings.iloc[0]['Name']
        subject = f"Change Request: {user_code}"
        body = f"Hello Transport Team,%0D%0A%0D%0AI need to request a change for booking {user_code} (Contact: {main_contact})."
        
        st.markdown(
            f'<div style="text-align: center;"><a href="mailto:sambrough@countrylion.co.uk?subject={subject}&body={body}" '
            f'style="text-decoration:none; background-color:#229971; color:white; padding:10px 20px; border-radius:5px;">'
            f'✉️ Request Amendment / Cancellation</a></div>', 
            unsafe_allow_html=True
        )

    else:
        st.error("❌ Code not found. Please check your reference.")
        if st.button("Reset Search"):
            st.session_state.search_performed = False
            st.rerun()
