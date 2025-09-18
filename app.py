import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from io import BytesIO
import base64

# --- Initialize Session State ---
if "coffee_shops" not in st.session_state:
    st.session_state.coffee_shops = pd.DataFrame(columns=[
        "name", "lat", "lon", "status", "review", "pics"
    ])

st.title("☕ Coffee Shop Tracker")

# --- Add a new coffee shop ---
with st.expander("➕ Add a Coffee Shop"):
    name = st.text_input("Coffee Shop Name")
    
    # Option to search for location by address
    address = st.text_input("Search by address / place (optional)")
    lat, lon = None, None
    if address:
        if st.button("🔍 Lookup Address"):
            geolocator = Nominatim(user_agent="coffee_app")
            location = geolocator.geocode(address)
            if location:
                lat, lon = location.latitude, location.longitude
                st.success(f"Found: {location.address} (Lat: {lat:.5f}, Lon: {lon:.5f})")
            else:
                st.error("Address not found. Please try again.")
    
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", value=lat if lat else 43.65, format="%.6f")
    with col2:
        lon = st.number_input("Longitude", value=lon if lon else -79.38, format="%.6f")
    
    status = st.selectbox("Status", ["wishlist", "sipped"])
    review = st.text_area("Review (optional)")
    pics = st.file_uploader("Upload photos", type=["jpg", "png"], accept_multiple_files=True)
    
    if st.button("Add Coffee Shop"):
        # Save uploaded pics as base64 strings
        pic_data = []
        for file in pics:
            pic_data.append(base64.b64encode(file.read()).decode("utf-8"))
        
        new_entry = pd.DataFrame([{
            "name": name,
            "lat": lat,
            "lon": lon,
            "status": status,
            "review": review,
            "pics": pic_data
        }])
        st.session_state.coffee_shops = pd.concat(
            [st.session_state.coffee_shops, new_entry], ignore_index=True
        )
        st.success(f"Added {name}!")

# --- Display coffee shops on a map ---
st.subheader("📍 Coffee Shops Map")

if not st.session_state.coffee_shops.empty:
    # Create folium map
    avg_lat = st.session_state.coffee_shops["lat"].mean()
    avg_lon = st.session_state.coffee_shops["lon"].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    for _, row in st.session_state.coffee_shops.iterrows():
        color = "blue" if row["status"] == "wishlist" else "green"
        
        popup_html = f"<b>{row['name']}</b><br>Status: {row['status']}"
        if row["review"]:
            popup_html += f"<br><i>{row['review']}</i>"
        if row["pics"]:
            for img in row["pics"]:
                popup_html += f'<br><img src="data:image/png;base64,{img}" width="150">'
        
        folium.Marker(
            [row["lat"], row["lon"]],
            tooltip=row["name"],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color, icon="coffee", prefix="fa")
        ).add_to(m)

    st_folium(m, width=700, height=500)
else:
    st.info("No coffee shops added yet. Add one above!")

# --- List view for quick edits ---
st.subheader("📋 Coffee Shop List")
st.dataframe(st.session_state.coffee_shops[["name", "status", "review"]])
