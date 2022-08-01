from datetime import datetime
import pandas as pd
from geopy.geocoders import Nominatim
import geocoder


#import geopandas as gpd
#import math
#import webbrowser

import folium
from folium import Choropleth, Marker
from folium.plugins import MarkerCluster

from flask import Flask, render_template

def get_day():
    today_date = datetime.now()
    return today_date.strftime('%A')

def get_time():
    today_date = datetime.now()
    return today_date.time().strftime('%H:%M')
    
def get_restaurants():
    # Assign restaurants to the "Honolulu Happy Hour" data
    all_restaurants = pd.read_csv("HonoluluHappyHour.csv", encoding='latin-1')

    day = get_day()
    current_time = get_time()

    # Determine which column to search under based on the day of the week
    if day == "Monday":
        start_time = "Monday_Start"
        end_time = "Monday_End"
    elif day == "Tuesday":
        start_time = "Tuesday_Start"
        end_time = "Tuesday_End"
    elif day == "Wednesday":
        start_time = "Wednesday_Start"
        end_time = "Wednesday_End"
    elif day == "Thursday":
        start_time = "Thursday_Start"
        end_time = "Thursday_End"
    elif day == "Friday":
        start_time = "Friday_Start"
        end_time = "Friday_End"
    elif day == "Saturday":
        start_time = "Saturday_Start"
        end_time = "Saturday_End"
    elif day == "Sunday":
        start_time = "Sunday_Start"
        end_time = "Sunday_End"

    # Drop rows with missing locations and start/end times
    all_restaurants.dropna(subset=['Latitude', 'Longitude', start_time, end_time], inplace=True)

    restaurants = []
    for idx, row in all_restaurants.iterrows():
        if current_time >= row[start_time] and current_time <= row[end_time]:
            restaurants.append(row)
            # print (row["Name"] + "- Start: " + row[start_time] + " End: " + row[end_time])

    #print(restaurants)          
    return restaurants

    
def render_map():
    # Get user's current location
    myloc = geocoder.ip('me')

    # Check to see if user's location is near the Hawaiian Islands
    if myloc.lat < 18 or myloc.lat > 23 or myloc.lng < -161 or myloc.lng > -153:
        loc = [21.277788011986335, -157.82746529215578]
        map_display = folium.Map(location=loc, tiles='cartodbpositron', zoom_start=16) #Also consider 'openstreetmap'
    else:
        loc = [myloc.lat, myloc.lng]
        map_display = folium.Map(location=loc, tiles='cartodbpositron', zoom_start=16) #Also consider 'openstreetmap'

        # Adds user's location to the map
        folium.Marker(location=loc, icon=folium.Icon(color="red")).add_to(map_display)

    all_restaurants = pd.read_csv("HonoluluHappyHour.csv", encoding='latin-1')

    day = get_day()
    current_time = get_time()

    # Determine which column to search under based on the day of the week
    if day == "Monday":
        start_time = "Monday_Start"
        end_time = "Monday_End"
    elif day == "Tuesday":
        start_time = "Tuesday_Start"
        end_time = "Tuesday_End"
    elif day == "Wednesday":
        start_time = "Wednesday_Start"
        end_time = "Wednesday_End"
    elif day == "Thursday":
        start_time = "Thursday_Start"
        end_time = "Thursday_End"
    elif day == "Friday":
        start_time = "Friday_Start"
        end_time = "Friday_End"
    elif day == "Saturday":
        start_time = "Saturday_Start"
        end_time = "Saturday_End"
    elif day == "Sunday":
        start_time = "Sunday_Start"
        end_time = "Sunday_End"

    # Drop rows with missing locations and start/end times
    all_restaurants.dropna(subset=['Latitude', 'Longitude', start_time, end_time], inplace=True)
 
    # Add points to the map in a 
    marker_clusters = MarkerCluster()
    for idx, row in all_restaurants.iterrows():
        if current_time >= row[start_time] and current_time <= row[end_time]:
            # print (row['Name'])
            happy_hour_menu = []
            col = 26 # Sets the initial index to just after "Menu"
            for i in range(col, len(row)):
                if pd.isnull(row[i]):
                    break
                else:
                    happy_hour_menu.append(row[i])

            # Format the popup to display restaurant name, time of HH, address, phone, website, and menu.
            html=f"""
                
                <h3> {row['Name']}</h3>
                <p> {row[start_time]}-{row[end_time]} </p>
                <p> {row['Street']} <br> {row['City']}, {row['State']} {row['Zip']} </p>
                <p> {row['Phone']} </p>
                <p><a href={row['Website']} target="_blank" rel="noopener noreferrer"> {row['Website']} </a></p>
                <p> <u>Menu</u>: 
                """
            
            for i in happy_hour_menu:
                html = html + f"""<br>{i}"""
            iframe = folium.IFrame(html=html, width=400, height=300)
            popup = folium.Popup(iframe)

            """happy_hour_details = ("Name: " + row["Name"],
                                  "Address: " + row["Street"],
                                  "         " + row["City"] + ", " + row["State"] + " " + str(row["Zip"]),
                                  "Phone: " + row["Phone"],
                                  "Website: " + row["Website"],
                                  "Menu: " + str(happy_hour_menu))"""

            marker_clusters.add_child(Marker(
                location = [row['Latitude'], row['Longitude']],
                popup = popup,
                tooltip = row['Name']))
        
    map_display.add_child(marker_clusters)
    map_display.save('templates/map.html')
    return map_display
    
app = Flask(__name__)
@app.route('/')
def home():
    restaurants = get_restaurants()
    map_display = render_map()
    return render_template('home.html')
@app.route('/about/')
def about():
    return render_template('about.html')
@app.route('/map')
def map():
    return render_template('map.html')
if __name__ == '__main__':
    app.run(debug=True)

