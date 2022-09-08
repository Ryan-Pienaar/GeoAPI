import pandas as pd
import sys
import requests

FILE = sys.argv[1]  # *.xlsx file path to be GeoCoded
SheetName = sys.argv[2]  # Sheet of *.xlsx File to be used
API_KEY = 'AIzaSyB07eD8KQyzpMuU-_cGF48ax59gWWahTL8'  # Ryan Pienaar Google API Key !DO NOT USE!

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

def printExcel(file):
    df = pd.read_excel(file, sheet_name=SheetName)
    print(df)

#printExcel(FILE)


# Verifies found Coordinates
def verifyCoord(file):
    for ind in xlsx.index:
        print(xlsx['PlaceLabel'][ind])
        lat, long, name = getLongLat(xlsx['PlaceLabel'][ind])
        xlsx.at[ind, 'VerifiedLat'] = lat
        xlsx.at[ind, 'VerifiedLong'] = long
        xlsx.at[ind, 'Google Place Name'] = name

# Driving code
verifyCoord(FILE)
print(xlsx)
xlsx.to_excel(FILE, sheet_name=SheetName)  # Writes DataFrame back to Excel file
