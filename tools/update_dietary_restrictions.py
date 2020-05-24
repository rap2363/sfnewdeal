import csv
import json
import os
import requests
import time
import utils

AIR_TABLE_API_KEY = os.environ['AIR_TABLE_API_KEY']
GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']

AIR_TABLE_URL = 'https://api.airtable.com/v0/appkknBvhJoouuyAl/SF%20New%20Deal%20Clients'
GOOGLE_MAPS_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'

BATCH_UPDATE_SIZE = 10


def geocode_row(row):
    row_fields = row['fields']
    print(row_fields)
    '''Make a request to Google's Geocoding API'''
    input_address = get_cleaned_input_address(row_fields['Street Address'])
    query_url = GOOGLE_MAPS_BASE_URL.format(input_address, GOOGLE_MAPS_API_KEY)
    response = requests.get(url = query_url).json()
    if (len(response['results']) == 0):
        print('No results for {}'.format(query_url))
        return None
    top_result = response['results'][0]

    return {
        'id': row['id'],
        'fields': {
            'Google Place ID': top_result['place_id'],
            'Latitude': float(top_result['geometry']['location']['lat']),
            'Longitude': float(top_result['geometry']['location']['lng']),
            'Google Formatted Address': top_result['formatted_address']
        }
    }

def update_rows(rows_to_update):
    print('Number of rows to update: {}'.format(len(rows_to_update)))
    for i in range(0, len(rows_to_update), BATCH_UPDATE_SIZE):
        print('Updating rows {} through {}'.format(i, i + BATCH_UPDATE_SIZE))
        batch_to_update = {'records': rows_to_update[i:(i+BATCH_UPDATE_SIZE)]}
        resp = requests.patch(AIR_TABLE_URL, auth = BearerAuth(AIR_TABLE_API_KEY), json = batch_to_update)

if __name__ == '__main__':
    all_rows = utils.get_all_rows_with_filter(AIR_TABLE_API_KEY, filter_string = "{Assigned Dietary Restrictions} = ''")
    print(len(all_rows))
    # rows_to_update = []
    # for row in all_rows:
    #     if (row['fields'].get('Google Place ID', '') == ''):
    #         geocoded_row = geocode_row(row)
    #         if geocoded_row is not None:
    #             rows_to_update.append(geocoded_row)
    #
    # update_rows(rows_to_update)
