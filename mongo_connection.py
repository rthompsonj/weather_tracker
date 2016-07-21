import datetime
from pymongo import MongoClient
from passlib.hash import bcrypt

DBNAME = 'weather'  # name of the database in Mongo
UPDATE_TIME = 10    # time in minutes to refresh a forecast on request

class MongoConnection(object):
    """Database connection manager.

    Parameters
    ----------
    ip : str, optional
        The IP address of the Mongo server.
    port : int, optional
        The Mongo server port.
    reinit : bool, optional
        If True the database is dropped (if present) and reinitialized
        on instantiation.

    """
    def __init__(self, ip='localhost', port=27015, reinit=False):
        self.connection = MongoClient()

        if DBNAME in self.connection.database_names() and not reinit:
            self.db = self.connection[DBNAME]
        else:
            self._init_db()

    def _init_db(self):
        """Drop, then initialize the database."""
        self.connection.drop_database(DBNAME)
        self.db = self.connection[DBNAME]

    def get_strftime(self):
        """Converts current time into POSIX time integer."""
        return int(datetime.datetime.now().strftime('%s'))

    def get_location_data(self, latitude, longitude):
        """Gets cached location data from the database.  Returns None
        if the location is not present in the database.

        Parameters
        ----------
        latitude : float
            Latitude of the requested location.
        longitude : float
            Longitude of the requested location.

        """
        return self.db.location_data_cache.find_one(
            {
                'latitude' :round(latitude, 6),
                'longitude':round(longitude, 6),
            }
        )

    def update_location(self, latitude, longitude):
        """Returns True/False depending on if we need to request
        a new forecast.  True when the time last cached has exceeded
        UPDATE_TIME or the location does not exist in the cache.  False
        otherwise.

        Parameters
        ----------
        latitude : float
            Latitude of the requested location.
        longitude : float
            Longitude of the requested location.

        """
        current_time = self.get_strftime()
        result = self.get_location_data(latitude, longitude)

        if result is None:
            return True
        else:
            if (current_time - result['time_updated']) > float(UPDATE_TIME)*60.: # in minutes
                print('Time exceeded!')
                return True
            else:
                return False

    def cache_location_data(self, data):
        """Cache location data to the Database.

        Parameters
        ----------
        data : dict
            Json dictionary from the weather API.

        """
        result = self.get_location_data(data['latitude'], data['longitude'])

        data['time_updated'] = self.get_strftime()
        if result is not None:
            print('Updating entry')
            self.db.location_data_cache.update({'_id':result['_id']}, data)
        else:
            print('Creating entry')
            self.db.location_data_cache.insert_one(data)

    def get_location_name(self, loc_request):
        """Gets the requested location name from the cache if exists.

        Parameters
        ----------
        loc_request : str
            The name of the location requested by the client.

        """
        return self.db.location_name_cache.find_one({'name':loc_request})

    def cache_location_name(self, loc_request, loc):
        """Caches the requested location name to the database.

        Parameters
        ----------
        loc_request : str
            The name of the location requested by the client.
        loc : dict
            Raw location dict from geopy.

        """
        loc['name'] = loc_request
        self.db.location_name_cache.insert_one(loc)

    def get_user(self, username):
        """Returns the requested user if present.
        
        Parameters
        ----------
        username : str
            Client's username.

        """
        return self.db.users.find_one({'username':username})

    def add_user(self, username, password):
        """Adds a user to the database.

        Parameters
        ----------
        username : str
            Client's username.
        password : str
            Client's password.

        """
        p = bcrypt.encrypt(password)
        self.db.users.insert_one(
            {
                'username':username,
                'password':p
            }
        )

    def verify_password(self, db_password, entered_password):
        """Verifies client username and password.

        Parameters
        ----------
        db_password : str
            Hashed password from the database.
        entered_password : str
            Client supplied password to check.

        """        
        return bcrypt.verify(entered_password, db_password)        

    def modify_user_location(self, username, location, ADD=True):
        """Modify the client's list of locations.

        Parameters
        ----------
        username : str
            Client's username.
        location : str
            Requested location name.
        ADD : bool, optional
            If set to False the location will be removed from the list
            instead of added.

        """
        if not isinstance(location, str):
            raise Exception('Location must be a string!')
        
        user = self.get_user(username)
        if user is None:
            return

        location = location.lower()
        if 'locations' not in user:
            user['locations'] = []

        if ADD:
            if location in user['locations']:
                print('Loc already present!')
                return
            user['locations'].append(location)
        else:
            if location not in user['locations']:
                print('Loc not present, cannot remove!')
                return
            user['locations'].remove(location)

        self.db.users.replace_one({'_id':user['_id']}, user)

    def remove_location_index(self, username, index):
        """Remove a location from the client's location list by index.

        Parameters
        ----------
        username : str
            Supplied username
        index : int
            Which index to remove from the location list.

        """
        user = self.get_user(username)
        if user is None:
            return

        if 'locations' not in user:
            return

        user['locations'].pop(index)

        self.db.users.replace_one({'_id':user['_id']}, user)
        
        
