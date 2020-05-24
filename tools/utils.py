import requests

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
        if offset is not None:
            params['offset'] = offset
        if filter_string is not None:
            params['filterByFormula'] = filter_string

        resp = requests.get(url=url, auth=BearerAuth(api_key), params=params).json()
        all_rows.extend(resp['records'])
        if 'offset' not in resp:
            return all_rows
        offset = resp['offset']
