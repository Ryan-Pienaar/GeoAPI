import pandas as pd
import sys
import requests
import numpy as np
import json

API_KEY = 'AIzaSyB07eD8KQyzpMuU-_cGF48ax59gWWahTL8'  # Google API Key (Free Trial Key)

def checkLocations(FILE):
    xlsx = pd.read_excel(FILE)
    verifyCoord(xlsx)
# Uses Google API To get the longitude and latitude of a place name
# Returns found longitude and latitude
def getLongLat(address):
    params = {
        'key': API_KEY,
        'address': address.replace(' ', '+')
    }

    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(base_url, params=params)
    data = response.json()
    #print(data)
    if data['status'] == 'OK':
        #print(data);
        result = data['results'][0]
        location = result['geometry']['location']
        name = result['formatted_address']
        print("Latitude: " + str(location['lat']) + " Longitude: " + str(location['lng']))

        return location['lng'], location['lat'], name,
    else:
        return


# Verifies found Coordinates
def verifyCoord(file):

    for ind in file.index:
        print(file['PlaceLabel'][ind])
        long, lat, name = getLongLat(file['PlaceLabel'][ind])
        file.at[ind, 'VerifiedLat'] = lat
        file.at[ind, 'VerifiedLong'] = long
        file.at[ind, 'Google Place Name'] = name

        currLat = file.at[ind, 'Latitude']
        currLong = file.at[ind, 'Longitude']

        if np.isnan(currLat):
            file.at[ind, 'Latitude'] = lat

        if np.isnan(currLong):
            file.at[ind, 'Longitude'] = long



#xlsx.to_excel(FILE, sheet_name=SheetName, index=False)  # Writes DataFrame back to Excel file
#xlsx.to_json(r'test.json')