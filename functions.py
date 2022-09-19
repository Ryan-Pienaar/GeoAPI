import pandas as pd
import requests
import numpy as np
import json
from shapely.geometry import shape, Point

API_KEY = 'AIzaSyB07eD8KQyzpMuU-_cGF48ax59gWWahTL8'  # Google API Key (Free Trial Key)

def checkLocations(FILE):
    xlsx = pd.read_excel(FILE)
    print(xlsx)
    verifyCoord(xlsx)
    file_name = 'out.xlsx'
    xlsx.to_excel(file_name, index=False)


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
    print(data)
    if data['status'] == 'OK':
        result = data['results'][0]
        location = result['geometry']['location']
        suburb = result['address_components'][0]
        city = result['address_components'][1]
        province = result['address_components'][3]
        country = result['address_components'][4]
        postal = result['address_components'][5]

        name = result['formatted_address']
        print("Latitude: " + str(location['lat']) + " Longitude: " + str(location['lng']))

        return location['lng'], location['lat'], name, postal['long_name'], \
               suburb['long_name'], city['long_name'], province['long_name'], \
               country['long_name'],
    else:
        return


# Verifies found Coordinates
def verifyCoord(file):

    for ind in file.index:
        print(file['PlaceLabel'][ind])
        long, lat, name, postal, suburb, city, province, country = getLongLat(file['PlaceLabel'][ind])
        localMun = getLocalMun(lat, long)
        districtMun = getDistrictMun(lat, long)
        file.at[ind, 'Verified Latitude'] = lat
        file.at[ind, 'Verified Longitude'] = long
        file.at[ind, 'Verified Place Name'] = name
        file.at[ind, 'Verified Postal Code'] = postal
        file.at[ind, 'Verified Suburb'] = suburb
        file.at[ind, 'Verified City'] = city
        file.at[ind, 'Verified Province'] = province
        file.at[ind, 'Verified Country'] = country
        file.at[ind, 'District Municipality'] = districtMun
        file.at[ind, 'Local Municipality'] = localMun

        currLat = file.at[ind, 'Latitude']
        currLong = file.at[ind, 'Longitude']

        currSuburb = file.at[ind, 'Suburb']

        if city == suburb:
            file.at[ind, 'Verified Suburb'] = currSuburb

        if np.isnan(currLat):
            file.at[ind, 'Latitude'] = lat

        if np.isnan(currLong):
            file.at[ind, 'Longitude'] = long


def getLocalMun(lat, long):
    # load GeoJSON file containing sectors
    with open('GeoJSON/local_mun.geojson') as f:
        js = json.load(f)

    # construct point based on lon/lat returned by geocoder
    point = Point(long, lat)

    # check each polygon to see if it contains the point
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return feature['properties']['MAP_TITLE']

def getDistrictMun(lat, long):
    # load GeoJSON file containing sectors
    with open('GeoJSON/district_mun.geojson') as f:
        js = json.load(f)

    # construct point based on lon/lat returned by geocoder
    point = Point(long, lat)

    # check each polygon to see if it contains the point
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return feature['properties']['MAP_TITLE']


