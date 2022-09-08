import openpyxl
import pandas as pd
import sys

ACCESS_KEY = '7502c7e664797c45bd13bcbef4f9f12c'
FILE = sys.argv[1]
SheetName = sys.argv[2]


def getLongLat(location):
    import http.client, urllib.parse

    conn = http.client.HTTPConnection('api.positionstack.com')

    params = urllib.parse.urlencode({
        'access_key': ACCESS_KEY,
        'query': location,
        'region': 'South Africa',
        'limit': 1,
        'fields': 'results.latitude',
    })



    conn.request('GET', '/v1/forward?{}'.format(params))

    res = conn.getresponse()
    data = res.read()


    print(data.decode('utf-8'))


def getLocationName():
    import http.client, urllib.parse

    conn = http.client.HTTPConnection('api.positionstack.com')

    params = urllib.parse.urlencode({
        'access_key': ACCESS_KEY,
        'query': '51.507822,-0.076702',
    })

    conn.request('GET', '/v1/reverse?{}'.format(params))

    res = conn.getresponse()
    data = res.read()

    print(data.decode('utf-8'))


# getLongLat()
# getLocationName()
def printExcel(file):
    df = pd.read_excel(file, sheet_name=SheetName)
    # pd.head()
    print(df)


# printExcel(FILE)


def parseLocationNames(file):
    xlsx = pd.ExcelFile(file)
    frame1 = xlsx.parse(sheet_name=SheetName, usecols={1})

    #frame10 += frame1.apply(getLongLat())
    for ind in frame1.index:
        getLongLat(frame1['PlaceLabel'][ind])
        #return frame1['PlaceLabel'][ind].latitude

        #for ind in frame10
        #frame10 = xlsx.parse(sheet_name=SheetName, usecols={10})

    #print(frame1)
    #print(frame10)


parseLocationNames(FILE)
