import datetime
from pymongo import MongoClient

DBNAME = 'weather'


class MongoConnection(object):
    def __init__(self, ip='localhost', port=27015, reinit=False):
        self.connection = MongoClient()

        if DBNAME in self.connection.database_names() and not reinit:
            self.db = self.connection[DBNAME]
        else:
            self.init_db()

    def init_db(self):
        """Initialize the database and collections."""
        self.connection.drop_database(DBNAME)

        # DB
        self.db = self.connection[DBNAME]

        # Collections
        self.db.users.insert_one(
            {
                'username':'rthompson',
                'password':'password'
            }
        )

        #self.db.cache.insert_one(
        #    {
        #        'zip':78665,
        #        'name':'austin',
        #        'state':'texas'
        #    }
        #)

    def get_strftime(self):
        """Converts current time into POSIX time integer."""
        return int(datetime.datetime.now().strftime('%s'))

    def get_location_data(self, latitude, longitude):
        """Gets a location in the DB.  If not present returns None."""
        return self.db.cache.find_one({
            'latitude' :round(latitude, 6),
            'longitude':round(longitude, 6),
        })

    def update_location(self, latitude, longitude):
        """Returns true/false depending on if we need to request
        a new forecast.  True when the time last cached has exceeded
        10 minutes or the location does not exist in the cache.  False
        otherwise."""
        current_time = self.get_strftime()
        result = self.get_location_data(latitude, longitude)

        if result is None:
            return True
        else:
            if (current_time - result['time_updated']) > 10.*60.: # 10 minutes
                print('Time exceeded!')
                return True
            else:
                return False

    def cache_location_data(self, data):
        """Cache the given location to the db"""
        result = self.get_location_data(data['latitude'], data['longitude'])

        data['time_updated'] = self.get_strftime()
        if result is not None:
            print('Updating entry')
            self.db.cache.update({'_id':result['_id']}, data)
        else:
            print('Creating entry')
            self.db.cache.insert_one(data)

    def get_location_name(self, loc_request):
        return self.db.name_cache.find_one({'name':loc_request})

    def cache_location_name(self, loc_request, loc):
        loc['name'] = loc_request
        self.db.name_cache.insert_one(loc)
