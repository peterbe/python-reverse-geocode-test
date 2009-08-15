import logging

from urllib import urlencode
from urllib2 import urlopen
import simplejson

import xml

from geopy.geocoders.base import Geocoder
from geopy import Point, Location, util

class GeoNames(Geocoder):
    def __init__(self, format_string='%s', output_format='xml'):
        self.format_string = format_string
        self.output_format = output_format
    
    @property
    def url(self):
        domain = "ws.geonames.org"
        output_format = self.output_format.lower()
        append_formats = {'json': 'JSON'}
	resource = "postalCodeSearch" + append_formats.get(output_format, '')
        return "http://%(domain)s/%(resource)s?%%s" % locals()
    
    @property
    def reverse_url(self):
	domain = "ws.geonames.org"
        output_format = self.output_format.lower()
        append_formats = {'json': 'JSON'}
	resource = "findNearestAddress" + append_formats.get(output_format, '')
	return "http://%(domain)s/%(resource)s?%%s" % locals()
    
    def geocode(self, string, exactly_one=True):
        params = {'placename': string}
        url = self.url % urlencode(params)
        return self.geocode_url(url, exactly_one)
    
    def reverse(self, coord, exactly_one=True):
	(lat,lng) = coord
	params = {'lat':self.format_string % lat,
		  'lng':self.format_string % lng}
	url = self.reverse_url % urlencode(params)
	return self.geocode_url(url, exactly_one, reverse=True)
    
    def geocode_url(self, url, exactly_one=True, reverse=False):
	logging.getLogger().info("Fetching %s..." % url)
        page = urlopen(url)
        dispatch = getattr(self, 'parse_' + self.output_format)
        return dispatch(page, exactly_one, reverse)

    def parse_json(self, page, exactly_one, reverse):
        if not isinstance(page, basestring):
            page = self._decode_page(page)
        json = simplejson.loads(page)
	if reverse:
	    codes = [json.get('address', [])]
	else:
	    codes = json.get('postalCodes', [])
        
        if exactly_one and len(codes) != 1:
            raise ValueError("Didn't find exactly one code! " \
                             "(Found %d.)" % len(codes))
        
        def parse_code(code,reverse):
	    if reverse:
		address = self._join_filter(" ", [code.get("streetNumber"),
						  code.get("street")])
		place = self._join_filter(", ", [address,code.get("placename"),
						 code.get("countryCode")])
		location = self._join_filter(" ", [place,
						   code.get('postalcode')]) or None
	    else:
		place = self._join_filter(", ", [code.get('placeName'),
						 code.get('countryCode')])
		location = self._join_filter(" ", [place,
						   code.get('postalCode')]) or None
	    latitude = code.get('lat')
	    longitude = code.get('lng')
            latitude = latitude and float(latitude)
            longitude = longitude and float(longitude)
            return (location, (latitude, longitude))

        if exactly_one:
            return parse_code(codes[0],reverse)
        else:
            return (parse_code(code,reverse) for code in codes)

    def parse_xml(self, page, exactly_one, reverse):
        if not isinstance(page, basestring):
            page = self._decode_page(page)
        doc = xml.dom.minidom.parseString(page)
	if reverse:
	    codes = doc.getElementsByTagName('address')
	else:
	    codes = doc.getElementsByTagName('code')
        if exactly_one and len(codes) != 1:
            raise ValueError("Didn't find exactly one code! " \
                             "(Found %d.)" % len(codes))

        def parse_code(code,reverse):
	    if reverse:
		street_number = self._get_first_text(code, 'streetNumber')
		street = self._get_first_text(code, 'street')
		place_name = self._get_first_text(code, 'placename')
		country_code = self._get_first_text(code, 'countryCode')
		postal_code = self._get_first_text(code, 'postalcode')
		address = self._join_filter(" ", [street_number, street])
		place = self._join_filter(", ", [address, place_name, country_code])
	    else:
		place_name = self._get_first_text(code, 'name')
		country_code = self._get_first_text(code, 'countryCode')
		postal_code = self._get_first_text(code, 'postalcode')
		place = self._join_filter(", ", [place_name, country_code])
	    location = self._join_filter(" ", [place, postal_code]) or None
	    latitude = self._get_first_text(code, 'lat') or None
	    longitude = self._get_first_text(code, 'lng') or None
	    latitude = latitude and float(latitude)
	    longitude = longitude and float(longitude)
            return (location, (latitude, longitude))
        
        if exactly_one:
            return parse_code(codes[0],reverse)
        else:
            return (parse_code(code,reverse) for code in codes)

