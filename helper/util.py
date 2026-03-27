from geopy.distance import geodesic
from datetime import datetime

def calculate_distance(user_location, row):
    lat = row["lat"]
    lng = row["lng"]
    spot_location = (lat,lng)
    dis = geodesic(user_location, spot_location).km
    return round(dis, 2)



def is_open_spot (row):
    current_time = datetime.now().strftime("%H:%M")
    opening_time = row["opening_time"]
    closing_time = row["closing_time"]
    if opening_time <= current_time <= closing_time:
        return "🟢 open"
    else:
        return "🔴close"

icons = ["🏠","🛒","🚚","☕"]
def get_spot_type_icon(spot_type):
      if spot_type == "cafe":
          return "🏠"
      elif spot_type == "cart":
          return "🛒"
      elif spot_type == "truck":
          return "🚚"
      else:
          return "☕"
get_spot_type_icon("home")