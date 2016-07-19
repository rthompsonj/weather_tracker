import urllib2
import json
from geopy.geocoders import Nominatim
from mongo_connection import MongoConnection
from api_key import APIKEY

REINIT = False
URL = 'https://api.forecast.io/forecast'


class ForecastRetriever(object):
    def __init__(self):
        self.geolocator = Nominatim()
        self.db = MongoConnection(reinit=REINIT)

    def _get_url(self, latitude, longitude):
        return '%s/%s/%f,%f' % (URL, APIKEY, latitude, longitude)

    def _get_location(self, loc_request):
        loc_request = loc_request.lower()
        
        cached_loc = self.db.get_location_name(loc_request)
        if cached_loc is None:
            try:
                loc = self.geolocator.geocode(loc_request)
                self.db.cache_location_name(loc_request, loc.raw)
                print('Caching location name')
                return loc
            except:
                raise ValueError('Enter a valid geocode!')
        else:
            print('Returning cached location name')
            return self.geolocator.parse_code(cached_loc)

    #def set_location(self, loc_request):
    #    self.current_location = loc_request
    #    self.current_data = self.get_forecast(loc_request)

    def get_forecast(self, loc_request):
        loc = self._get_location(loc_request)

        if self.db.update_location(loc.latitude, loc.longitude):
            print('Refreshing location forecast')
            url = self._get_url(loc.latitude, loc.longitude)
            print(url)
            request = urllib2.urlopen(url).read()
            print('after request')
            data = json.loads(request)
            self.db.cache_location_data(data)
        else:
            print('Getting cached location forecast')
            data = self.db.get_location_data(loc.latitude, loc.longitude)

        #import json
        #data['_id'] = None
        #f = open('sample.json','w')
        #f.write(json.dumps(data))
        #f.close()
            
        return data
