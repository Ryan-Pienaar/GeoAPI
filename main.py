import pandas as pd
import sys
import requests

FILE = sys.argv[1]
SheetName = sys.argv[2]
API_KEY = 'AIzaSyB07eD8KQyzpMuU-_cGF48ax59gWWahTL8'

def getGeoCoord(address):
    params = {
        'key': API_KEY,
        'address': address.replace(' ', '+')
    }

    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(base_url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        result = data['results'][0]
        location = result['geometry']['location']
        print("Latitude: " + str(location['lat']) + " Longitude: " + str(location['lng']))
        return location['lat'], location['lng']
    else:
        return

def printExcel(file):
    df = pd.read_excel(file, sheet_name=SheetName)
    print(df)

#printExcel(FILE)


def parseLocationNames(file):
    xlsx = pd.read_excel(file)

    for ind in xlsx.index:
        print(xlsx['PlaceLabel'][ind])
        getGeoCoord(xlsx['PlaceLabel'][ind])



parseLocationNames(FILE)
