import pandas as pd
import requests
import numpy as np
import json
from shapely.geometry import shape, Point

count = 0
total = 11481

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
    global postal, city, province, country, suburb
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
        # print("test")
        # print(result['address_components'][0]['types'])
        # print(len(result['address_components']))

        for ind in range(len(result['address_components'])):
            if 'country' in result['address_components'][ind]['types']:
                country = result['address_components'][ind]

            if 'postal_code' in result['address_components'][ind]['types']:
                postal = result['address_components'][ind]

            if 'administrative_area_level_1' in result['address_components'][ind]['types']:
                province = result['address_components'][ind]

            if 'locality' in result['address_components'][ind]['types']:
                city = result['address_components'][ind]

            if 'sublocality' in result['address_components'][ind]['types']:
                suburb = result['address_components'][ind]['long_name']
            else:
                suburb = ''

        name = result['formatted_address']
        # print("Latitude: " + str(location['lat']) + " Longitude: " + str(location['lng']))

        return location['lng'], location['lat'], name, postal['long_name'], \
               suburb, city['long_name'], province['long_name'], \
               country['long_name'],
    else:
        return


# Verifies found Coordinates
def verifyCoord(file):
    global count, placeLabel
    for ind in file.index:

        # print(file['PlaceLabel'][ind])
        if file['Suburb'][ind] == file['City'][ind]:
            placeLabel = file['Suburb'][ind] + "," + file['Province'][ind] + "," + file['Country'][ind]
        else:
            placeLabel = file['Suburb'][ind] + "," + file['City'][ind] + "," + file['Province'][ind] + "," + \
                         file['Country'][ind]
        print(placeLabel)
        long, lat, name, postal, suburb, city, province, country = getLongLat(placeLabel)
        localMun = getLocalMun(lat, long)
        districtMun = getDistrictMun(lat, long)
        file.at[ind, 'Verified Latitude'] = lat
        file.at[ind, 'Verified Longitude'] = long
        file.at[ind, 'Verified Place Name'] = name
        file.at[ind, 'Verified Postal Code'] = postal
        if suburb == '':
            file.at[ind, 'Verified Suburb'] = city
        else:
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

        count = count + 1
        progress = (count / total) * 100
        print(progress)


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
