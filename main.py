import pandas as pd
import sys
import requests
import numpy as np

FILE = sys.argv[1]  # *.xlsx file path to be GeoCoded
SheetName = sys.argv[2]  # Sheet of *.xlsx File to be used
API_KEY = 'AIzaSyB07eD8KQyzpMuU-_cGF48ax59gWWahTL8'  # Google API Key (Free Trial Key)

xlsx = pd.read_excel(FILE, sheet_name=SheetName)  # Creates DataFrame from *.xlsx file


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
        result = data['results'][0]
        location = result['geometry']['location']
        name = result['formatted_address']
        print("Latitude: " + str(location['lat']) + " Longitude: " + str(location['lng']))

        return location['lng'], location['lat'], name,
    else:
        return


# Verifies found Coordinates
def verifyCoord(file):

    for ind in xlsx.index:
        print(xlsx['PlaceLabel'][ind])
        long, lat, name = getLongLat(xlsx['PlaceLabel'][ind])
        xlsx.at[ind, 'VerifiedLat'] = lat
        xlsx.at[ind, 'VerifiedLong'] = long
        xlsx.at[ind, 'Google Place Name'] = name

        currLat = xlsx.at[ind, 'Latitude']
        currLong = xlsx.at[ind, 'Longitude']

        if np.isnan(currLat):
            xlsx.at[ind, 'Latitude'] = lat

        if np.isnan(currLong):
            xlsx.at[ind, 'Longitude'] = long


# Driving code
verifyCoord(FILE)
print(xlsx)
xlsx.to_excel(FILE, sheet_name=SheetName, index=False)  # Writes DataFrame back to Excel file
xlsx.to_json(r'test.json')
