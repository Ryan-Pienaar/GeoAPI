import pandas as pd
import requests
import numpy as np
import json
from shapely.geometry import shape, Point
from math import radians, cos, sin, asin, sqrt

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
        postal = None
        suburb = None
        city = None
        province = None
        country = None

        for ind in range(len(result['address_components'])):
            if 'country' in result['address_components'][ind]['types']:
                country = result['address_components'][ind]['long_name']

            if 'postal_code' in result['address_components'][ind]['types']:
                postal = result['address_components'][ind]['long_name']

            if 'administrative_area_level_1' in result['address_components'][ind]['types']:
                province = result['address_components'][ind]['long_name']

            if 'locality' in result['address_components'][ind]['types']:
                city = result['address_components'][ind]['long_name']

            if 'sublocality' in result['address_components'][ind]['types']:
                suburb = result['address_components'][ind]['long_name']

        name = result['formatted_address']
        # print("Latitude: " + str(location['lat']) + " Longitude: " + str(location['lng']))

        return location['lng'], location['lat'], name, postal, suburb, city, province, country,
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
        vlong, vlat, vname, vpostal, vsuburb, vcity, vprovince, vcountry = getLongLat(placeLabel)
        localMun = getLocalMun(vlat, vlong)
        districtMun = getDistrictMun(vlat, vlong)
        file.at[ind, 'Verified Latitude'] = vlat
        file.at[ind, 'Verified Longitude'] = vlong
        file.at[ind, 'Verified Place Name'] = vname
        file.at[ind, 'Verified Postal Code'] = postal
        if vsuburb is None:
            file.at[ind, 'Verified Suburb'] = file.at[ind, 'Suburb']
        else:
            file.at[ind, 'Verified Suburb'] = vsuburb
        file.at[ind, 'Verified City'] = vcity
        file.at[ind, 'Verified Province'] = vprovince
        file.at[ind, 'Verified Country'] = vcountry
        file.at[ind, 'District Municipality'] = districtMun
        file.at[ind, 'Local Municipality'] = localMun

        currLat = file.at[ind, 'Latitude']
        currLong = file.at[ind, 'Longitude']

        currSuburb = file.at[ind, 'Suburb']

        if city == suburb:
            file.at[ind, 'Verified Suburb'] = currSuburb

        if np.isnan(currLat):
            file.at[ind, 'Latitude'] = vlat

        if np.isnan(currLong):
            file.at[ind, 'Longitude'] = vlong

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

def score(FILE):
    xlsx = pd.read_excel(FILE)
    #print(xlsx)
    scoreEntries(xlsx)
    file_name = 'out.xlsx'
    xlsx.to_excel(file_name, index=False)

def scoreEntries(frame):
    for ind in frame.index:
        total = 0.00
        distance = calcDist(frame.at[ind, 'Longitude'], frame.at[ind, 'Latitude'], frame.at[ind, 'Verified Longitude'],
                            frame.at[ind, 'Verified Latitude'])

        #Suburb score counts 20% to total score
        if frame.at[ind, 'Suburb'] == frame.at[ind, 'Verified Suburb']:
            total += 20.00

        #City score counts 10% to total score
        if frame.at[ind, 'City'] == frame.at[ind, 'Verified City']:
            total += 10.00

        #Country score counts 20% to total score
        if frame.at[ind, 'Country'] == frame.at[ind, 'Verified Country']:
            total += 20.00

        #Province score counts 10% to total score
        if frame.at[ind, 'Province'] == frame.at[ind, 'Verified Province']:
            total += 10.00

        #Postal Code score counts 10% to total score
        if frame.at[ind, 'PostalCode'] == frame.at[ind, 'Verified Postal Code']:
            total += 10.00

        #Distance score counts 30% to total score
        if 3 >= distance > 2:
            total += (30.00 * 0.50)
        elif 2>= distance > 1:
            total += (30.00 * 0.75)
        elif 1>= distance:
            total += (30.00 * 1.00)


        print(total)
        frame.at[ind, 'Score'] = total



def calcDist(lon1, lat1, lon2, lat2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return (c * r)


