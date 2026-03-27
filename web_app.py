import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from helper.util import calculate_distance,is_open_spot,get_spot_type_icon

data = pd.read_csv("bhopal_cold_cafe_spot_name.csv")
data_areas =pd.read_csv("bhopal_areas_label.csv")

st.markdown("""
    <style>
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
    }
    </style>
""", unsafe_allow_html=True)


st.set_page_config(page_title="Bhopal Cold Coffee Finder",
                   page_icon="☕",layout="wide")
st.title("☕ Bhopal Cold Coffee Finder")
st.write("Find the nearest cold coffee spots around you in Bhopal.")
st.write("Explore cafes, carts, and trucks based on distance, rating, and availability.")

st.header("📍 Select Your Area")

area_labels = list(data_areas["label"])
# area_labels.insert(0,"Select")

selected_area = st.selectbox("Choose your area...",area_labels)
with st.sidebar:
   st.header("🔍 Search & Filters")
   spot_name = st.text_input("Search by name...",
                             placeholder="eg: Coffee Cart 10No")
   
   st.divider()
   st.header("⚙️ Filters")
   options = list(data["type"].unique())
   options.insert(0,"All")
   spot_type = st.selectbox("Spot Type",options)

   max_distance = st.slider("Max Distance (km)",min_value=1,max_value=20,value=10)
   min_rating = st.slider("Min Rating",min_value=1.0,max_value=5.0,value=3.0,step=0.1)

   show_only_open = st.checkbox("Show only open spots",False)
   sort_by = st.radio("Sort By",["Distance","Rating"])

ss = data_areas[data_areas["label"] == selected_area][["lat","lng"]]
user_location = tuple(ss.iloc[0])

def get_row(row):
   return calculate_distance(user_location,row)

data["distance_km"] = data.apply(get_row,axis=1)
data["is_open"] = data.apply(is_open_spot,axis=1)

df2 = data.copy()


if spot_type != "All":
   data = data[data["type"] == spot_type]

data = data[data["distance_km"] <= max_distance]
data = data[data["rating"] >= min_rating]

if show_only_open:
   data = data[data["is_open"] == "open"]

if sort_by == "Distance":
   data = data.sort_values(by="distance_km")
else:
   data = data.sort_values(by="rating",ascending=False)
   
if spot_name:
   data = data[data["name"].str.contains(spot_name,case=False)]

tab1,tab2,tab3 = st.tabs(["🗺️ Nearby Spots","📊 Analytics","🏆 Leaderboard"])

with tab1:
   st.subheader(f"{len(data)} spot(s) found")
   bhopal_map = folium.Map(location=user_location,zoom_start=13)
   marker_icon = folium.Icon(color="green",icon="user")

   area_marker = folium.Marker(user_location,
                               icon=marker_icon,
                               tooltip=f"Area: {selected_area}")
   area_marker.add_to(bhopal_map)

   for df in data.iterrows():
    row = df[1]
    lat = row['lat']
    lng = row['lng']
    name = row["name"]
    spot_type = row["type"]
    is_open = row["is_open"]
    color = "green"
    if is_open == "closed":
       color = "red"

    spot_location = (lat,lng)
    m_icon = folium.Icon(color=color,icon="coffee",prefix="fa")
    marker = folium.Marker(spot_location,icon=m_icon,tooltip=f"{spot_type}:{name}")
    marker.add_to(bhopal_map)

   st_folium(bhopal_map,height=300,use_container_width=True)
   
   for i in range(0,len(data),2):
       small_data = data.iloc[i:i+2]
       columns = st.columns(2)
       for j in range(len(small_data)):
           with columns[j]:
               with st.container(border = True):
                row = small_data.iloc[j]
                spot_icon = get_spot_type_icon(row["type"])
                st.subheader(f"{spot_icon} {row['name']}")
                col1,col2 = st.columns(2)
                with col1:
                 st.markdown(f"###### Type: {row['type']}")
                 st.markdown(f"###### Distance: {row['distance_km']} km")
                 st.caption(f"⏰ Opens at: {row['opening_time']} - {row['closing_time']}")
                with col2:
                    rating = row["rating"]
                    st.markdown(f"###### Rating: {'⭐' * int(rating)}{(rating)}")
                    st.markdown(f"###### Status: {row['is_open']}")
                 
                   
                  

   #st.dataframe(df)
with tab2:
   st.header("📈 Summary Stats")
   c1,c2,c3,c4 = st.columns(4)
   total_spots = len(df2)
   avg_rating = round(df2["rating"].mean(),2)
   open_spots = len(df2[df2["is_open"] == "🟢 open"])
   sort_data = df2.sort_values(by="distance_km")
   mis_data = sort_data["distance_km"].iloc[0]
   
   c1.metric("Total Spots",total_spots)
   c2.metric("Avg rating",avg_rating)
   c3.metric("Open Now",f"{open_spots}/{total_spots}")
   c4.metric("Nearest Spot",f"{mis_data}km")
   spots_counts = df2["type"].value_counts()
   st.bar_chart(spots_counts)
   
   st.subheader("📊 Rating Distribution")
   grp = df2.groupby('type')["rating"].mean()
   st.bar_chart(grp)

with tab3:
    st.header("Top Rated Spots")
    df_leaderboard = df2.sort_values(by="rating",ascending=False).reset_index(drop=True).head(10)
    df_leaderboard.index = df_leaderboard.index + 1
    st.dataframe(df_leaderboard)
    st.header("Closest Spots")
    df_leaderboard = df2.sort_values(by="distance_km",ascending=False).reset_index(drop=True).tail(10)
    df_leaderboard.index = df_leaderboard.index + 1
    st.dataframe(df_leaderboard)

