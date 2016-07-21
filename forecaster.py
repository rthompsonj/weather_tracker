import urllib2
import json
from geopy.geocoders import Nominatim
from mongo_connection import MongoConnection
from api_key import APIKEY

REINIT = False
URL = 'https://api.forecast.io/forecast'


class ForecastRetriever(object):
    """Forecast wrapper.  Handle's retrieval and caching of 
    geo locations."""
    def __init__(self):
        self.geolocator = Nominatim()
        self.db = MongoConnection(reinit=REINIT)

    def _get_url(self, latitude, longitude):
        """Get the request uri for the weather API.

        Parameters
        ----------
        latitude : float
            Latitude of the location
        longitude : float
            Longitude of the location

        """
        return '%s/%s/%f,%f' % (URL, APIKEY, latitude, longitude)

    def _get_location(self, loc_request):
        """Get a location via a requested string.  First we check the
        local cache to see if this same location has been requested
        before, if not we request a new via geopy.

        Parameters
        ----------
        loc_request : str
            Can be anything from a zip to a description.

        """
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

    def get_forecast(self, loc_request):
        """Gets a location forecast from the weather API.

        Parameters
        ----------
        loc_request : str
            Requested location, can be anything from a zip code to a
            description.
        
        """
        loc = self._get_location(loc_request)

        if self.db.update_location(loc.latitude, loc.longitude):
            print('Refreshing location forecast')
            url = self._get_url(loc.latitude, loc.longitude)
            request = urllib2.urlopen(url).read()
            data = json.loads(request)
            self.db.cache_location_data(data)
        else:
            print('Getting cached location forecast')
            data = self.db.get_location_data(loc.latitude, loc.longitude)

        #tmp_data = data
        #tmp_data['_id'] = 0
        #f = open('sample.json','w')
        #f.write(json.dumps(tmp_data))
        #f.close()

        return data


    def get_location_list(self, username):
        """Gets a specific user's current location list.

        Parameters
        ----------
        username : str
            Client username.

        """
        locs = []
        user = self.db.get_user(username)
        if user is None or 'locations' not in user:
            return locs

        for loc_str in user['locations']:
            loc = self._get_location(loc_str)
            data = self.get_forecast(loc_str)
            locs.append(
                {
                    'location':loc,
                    'data':data
                }
            )
        return locs
