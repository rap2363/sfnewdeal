import argparse
from constants import RESTAURANT_NAME, RESTAURANT_ADDRESS_ID
import csv
import json
import os
from order_model import OrderModel
import requests

API_KEY=os.environ['GOOGLE_MAPS_API_KEY']
BASE_URL='https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'

'''
This script is to geocode the input addresses once to a file that can be
used as a cache so we can avoid calling Google while testing
'''

def geocode_restaurants(geocoded_addresses):
    geocoded_addresses[RESTAURANT_ADDRESS_ID] = {
        'place_id': 'ChIJmZN_ljx-j4ARF16HqVQ2vnI',
        'location': {'lat': 37.7612,'lng': -122.4195},
        'formatted_address': '2234 Mission St, San Francisco, CA 94110, USA'
    }

    return geocoded_addresses

def geocode_order_model(order_model):
    '''Make a request to Google's Geocoding API'''
    input_address = get_cleaned_input_address(order_model.client_address)
    query_url = BASE_URL.format(input_address, API_KEY)
    response = requests.get(url = query_url).json()
    if (len(response['results']) == 0):
        print('No results for {}'.format(query_url))
    top_result = response['results'][0]

    return {
        'place_id': top_result['place_id'],
        'location': top_result['geometry']['location'],
        'formatted_address': top_result['formatted_address']
    }

def get_cleaned_input_address(input_client_address):
    return '+'.join(input_client_address.translate({ord(i):None for i in '!@#$'}).split(' '))

def geocode_meal_addresses(input_csv, geocoded_addresses):
    order_models = []
    with open(input_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            order_models.append(OrderModel.from_row(row))

    for order_model in order_models:
        geocoded_addresses[order_model.client_address_id] = geocode_order_model(order_model)

    return geocoded_addresses

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Geocode a CSV of meal orders'
    )
    parser.add_argument(
        'input_csv', help='A path to the CSV of orders to process'
    )
    parser.add_argument(
        'output_json', help='A path of where to write a JSON blob of the geocoded addresses'
    )

    args = parser.parse_args()

    geocoded_addresses = {}
    geocoded_addresses = geocode_restaurants(geocoded_addresses)
    geocode_meal_addresses(args.input_csv, geocoded_addresses)

    with open(args.output_json, 'w') as outfile:
        json.dump(geocoded_addresses, outfile, indent=4)
