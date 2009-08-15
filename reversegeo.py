# -*- coding: UTF-8 -*-
import re
TESTS = """

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=42.386951440524854&lng=-83.28460693359375&callback=?
Redford, Michigan
United States

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=39.91605629078665&lng=116.36581420898438&callback=?
Fengsheng, Beijing
China

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=46.80067637163745&lng=7.137722969055176&callback=?
FAILED

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=57.89149735271031&lng=14.23828125&callback=?
Rudu, Jönköping
Sweden

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=57.76865857271793&lng=12.271728515625&callback=?
Lerum, Västra Götaland
Sweden

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=55.7765730186677&lng=-3.603515625&callback=?
Auchengray, Scotland
United Kingdom


http://ws.geonames.org/findNearbyPlaceNameJSON?lat=52.6830427622774&lng=-8.525390625&callback=?
Gilloge Bridge, County Clare
Ireland


http://ws.geonames.org/findNearbyPlaceNameJSON?lat=39.90973623453719&lng=-75.498046875&callback=?
Glen Mills, Pennsylvania
United States

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=39.45316112807393&lng=-81.474609375&callback=?
Oak Grove, Ohio
United States


http://ws.geonames.org/findNearbyPlaceNameJSON?lat=39.50404070558415&lng=-74.5751953125&callback=?
Germania, New Jersey
United States


http://ws.geonames.org/findNearbyPlaceNameJSON?lat=39.14710270770074&lng=-86.5283203125&callback=?
Broadview, Indiana
United States


http://ws.geonames.org/findNearbyPlaceNameJSON?lat=28.998531814051795&lng=-110.91796875&callback=?
La Calera, Sonora
Mexico

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=35.88905007936091&lng=137.28515625&callback=?
Osaka, Gifu
Japan

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=36.31512514748051&lng=127.353515625&callback=?
Ulbawi, Daejeon
South Korea

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=34.59704151614417&lng=119.1796875&callback=?
Xinpu, Jiangsu
China

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=32.99023555965106&lng=114.005126953125&callback=?
Zhumadian, Henan
China

http://ws.geonames.org/findNearbyPlaceNameJSON?lat=26.07652055985697&lng=119.3115234375&callback=?
Fuzhou, Fujian
China

""".strip()

import urllib
import urllib2
import simplejson
from time import sleep, time
from random import randint, shuffle
import cPickle

count = 0
tests = re.split('\n{2,}', TESTS)
shuffle(tests)

YAHOO_KEY = "u1SsEsLV34H1noY4L8gFtZ0yGHjjBkbmlELZfViUoPLwGqIUkHRbQ2dvsMDZTCOUN3J5cMiKfLdt18SGzjX3wg--"
GOOGLE_KEY = "ABQIAAAAnfs7bKE82qgb3Zc2YyS-oBT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSySz_REpPq-4WZA27OwgbtyR3VcA"

from geopy import geocoders
google = geocoders.Google(GOOGLE_KEY)
#print dir(google)
yahoo = geocoders.Yahoo(YAHOO_KEY)
#print dir(yahoo)
geonames = geocoders.GeoNames()
#print dir(geonames)

results = {}


for test in tests:
    geonames_url = test.splitlines()[0]
    result = test.splitlines()[1:]
    
    print repr(geonames_url)
    print result
    lat = float(re.findall('lat=([\d\.-]+)', geonames_url)[0])
    lng = float(re.findall('lng=([\d\.-]+)', geonames_url)[0])
    print (lat, lng)
    
    # TEST GEONAMES JSON
    t0=time()
    geonames_url = geonames_url.replace('&callback=?','')
    json_string = urllib2.urlopen(geonames_url).read()
    r = simplejson.loads(json_string)
    try:
        data = r['geonames'][0]
        name = data['name']
        adminName1 = data['adminName1']
        if adminName1 and adminName1.lower() != name.lower():
            name += ', ' + adminName1
        place = "%s, %s" % (data['name'], data['countryName'])
    except KeyError:
        place = "FAILED"
    print
    t1=time()
    print "geonames json", repr(place), (t1-t0)
    results['geonames_json__%s,%s'%(lat,lng)] = (place, (t1-t0), result)
    sleep(randint(1,3))
    
    # TEST GOOGLE
    t0=time()
    try:
        place, __ = google.reverse((lat, lng))
    except ValueError:
        place = "FAILED"
    t1=time()
    print "google", repr(place), (t1-t0)
    results['google__%s,%s'%(lat,lng)] = (place, (t1-t0), result)
    
    # TEST YAHOO
    #t0=time()
    #place, __ = yahoo.reverse((lat, lng))
    #t1=time()
    #print "yahoo", repr(place), (t1-t0)
    #results['yahoo__%,%s'] = (place, (t1-t0))
    sleep(randint(1,3))
    
    # TEST GeoNames
    t0=time()
    try:
        place, __ = geonames.reverse((lat, lng))
    except ValueError:
        place = "FAILED"
    t1=time()
    print "geonames", repr(place), (t1-t0)
    results['geonames__%s,%s'%(lat,lng)] = (place, (t1-t0), result)
    
    count += 1
    sleep(8)
    
    #if count >= 3:
    #    break
    
    
    
if results:
    import datetime
    f = datetime.datetime.now().strftime('georesults-%H%M%S.pickle')
    cPickle.dump(results, open(f,'wb'))
    print f
    