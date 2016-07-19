import urllib2
import json
from geopy.geocoders import Nominatim
from mongo_connection import MongoConnection
from api_key import APIKEY

REINIT = False
URL    = 'https://api.forecast.io/forecast'

class ForcastRetriever(object):
    
    def __init__(self):
        self.geolocator = Nominatim()
        self.db = MongoConnection(reinit=REINIT)
        
    def _get_url(self, latitude, longitude):
        return '%s/%s/%f,%f' % (URL, APIKEY, latitude, longitude)

    def _get_location(self, loc_request):
        try:
            loc = self.geolocator.geocode(loc_request)
            return loc
        except:
            raise ValueError('Enter a valid geocode!')

    def set_location(self, loc_request):
        self.current_location = loc_request
        self.current_data     = self.get_forcast(loc_request)
        
    def get_forcast(self, loc_request):
        loc = self._get_location(loc_request)
        
        if self.db.update_location(loc.latitude, loc.longitude):
            print('Refreshing location')
            url = self._get_url(loc.latitude, loc.longitude)
            request = urllib2.urlopen(url).read()
            data = json.loads(request)
            self.db.cache_location(data)
        else:
            print('Getting cached location')
            data = self.db.get_location(loc.latitude, loc.longitude)
            
        return data
