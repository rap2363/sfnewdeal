import requests
from collections import namedtuple

from math import radians, cos, sin, asin, sqrt

Point = namedtuple('Point', ['latitude', 'longitude'])

def distance(p1, p2):
    return haversine(p1.latitude, p1.longitude, p2.latitude, p2.longitude)

def haversine(lat1, lon1, lat2, lon2):

      R = 6372.8 # this is the Earth's radius in km

      dLat = radians(lat2 - lat1)
      dLon = radians(lon2 - lon1)
      lat1 = radians(lat1)
      lat2 = radians(lat2)

      a = sin(dLat / 2)**2 + cos(lat1) * cos(lat2) * sin(dLon/2)**2
      c = 2 * asin(sqrt(a))

      return R * c

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

def get_all_rows(url, api_key):
    return get_all_rows_with_filter(url, api_key)

def get_all_rows_with_filter(url, api_key, filter_string = None):
    '''We must paginate to obtain all records'''
    all_rows = []
    offset = None
    while True:
        params = {}
        #params = {'maxRecords': 20} # JUST FOR TESTING REMOVE!
        if offset is not None:
            params['offset'] = offset
        if filter_string is not None:
            params['filterByFormula'] = filter_string

        resp = requests.get(url=url, auth=BearerAuth(api_key), params=params).json()
        all_rows.extend(resp['records'])
        if 'offset' not in resp:
            return all_rows
        offset = resp['offset']
