import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import re

# 1. Page Config
st.set_page_config(page_title="AMF1 Transport", page_icon="🏎️", layout="centered")

# --- CUSTOM CSS (For that "Premium" Aston Look) ---
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
    
    /* Force specific text colors if needed */
    h1, h2, h3 {
        color: white !important;
    }
    
    /* Custom Link Style for Routes */
    /* This removes the underline and sets the color */
    .route-link {
        color: #229971 !important;
        font-weight: bold;
        text-decoration: none !important; /* Removes underline */
    }
    .route-link:hover {
        color: #2DFFBC !important;
        text-decoration: none !important; /* Ensures underline stays gone on hover */
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
# This displays your banner image at the very top
try:
    st.image("banner.jpg", use_container_width=True) 
except:
    pass

# Sidebar Logo
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
        # The primary button will now use the "Aston Green" from config.toml
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
                    # --- NEW ROUTE LINK LOGIC ---
                    route_name = str(row['Route'])
                    
                    # 1. Extract the number from string (e.g. "1 - Banbury" -> "1")
                    match = re.search(r'\d+', route_name)
                    
                    route_display = f"**Route:** {route_name}" # Default fallback

                    if match:
                        route_num = match.group()
                        # 2. Check if we have a URL for this number
                        if route_num in ROUTE_URLS:
                            link = ROUTE_URLS[route_num]
                            # Render clean clickable link (No Emoji, No Underline via CSS class)
                            route_display = f"**Route:** <a href='{link}' target='_blank' class='route-link'>{route_name}</a>"
                    
                    st.markdown(route_display, unsafe_allow_html=True)

                    st.write(f"**{label_text}** {row['Pickup']}")
                    
                    if show_time:
                        p_time = row.get('PickupTime')
                        if pd.isna(p_time): p_time = "TBC"
                        st.write(f"**⏱️ Time:** {p_time}")
                        
                        # Departure Warning
                        st.info("⚠️ Please ensure you are at your pickup point 5 mins before your time. The coach will unfortunately only be able to wait 2 minutes for any missing passengers.")

                    if show_return_msg:
                        st.info("ℹ️ **Return:** All coaches depart Silverstone at 01:00 AM.")

                    if pd.notna(row['MapLink']):
                        st.link_button("/// What 3 Words Link", row['MapLink'])
                        
                with c2:
                    # --- MAP ---
                    lat, lon = row.get('Lat'), row.get('Lon')
                    if pd.notna(lat) and pd.notna(lon):
                        m = folium.Map(location=[lat, lon], zoom_start=16)
                        folium.Marker(
                            [lat, lon], 
                            popup=row['Pickup'], 
                            icon=folium.Icon(color=pin_color, icon="bus", prefix="fa")
                        ).add_to(m)
                        
                        st_folium(m, height=200, use_container_width=True, returned_objects=[], key=f"map_{index}")
                    else:
                        st.info("🗺️ Map not available")

        # Footer
        st.divider()
        main_contact = bookings.iloc[0]['Name']
        subject = f"Change Request: {user_code}"
        body = f"Hello Transport Team,%0D%0A%0D%0AI need to request a change for booking {user_code} (Contact: {main_contact})."
        
        st.markdown(
            f'<div style="text-align: center;"><a href="mailto:transport@yourteam.com?subject={subject}&body={body}" '
            f'style="text-decoration:none; background-color:#229971; color:white; padding:10px 20px; border-radius:5px;">'
            f'✉️ Request Amendment / Cancellation</a></div>', 
            unsafe_allow_html=True
        )

    else:
        st.error("❌ Code not found. Please check your reference.")
        if st.button("Reset Search"):
            st.session_state.search_performed = False
            st.rerun()
