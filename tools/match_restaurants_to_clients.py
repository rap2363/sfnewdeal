import argparse
import csv
import json
import os
import time
import utils

from client_model import Cuisine
from enum import Enum
from utils import Point

AIR_TABLE_API_KEY = os.environ['AIR_TABLE_API_KEY']

AIR_TABLE_CLIENTS_URL = 'https://api.airtable.com/v0/appkknBvhJoouuyAl/SF%20New%20Deal%20Clients'
AIR_TABLE_RESTAURANTS_URL = 'https://api.airtable.com/v0/appkknBvhJoouuyAl/Great%20Plates%20Restaurants'

class Day(Enum):
    SUNDAY = 'sun'
    MONDAY = 'mon'
    TUESDAY = 'tue'
    WEDNESDAY = 'wed'
    THURSDAY = 'thu'
    FRIDAY = 'fri'
    SATURDAY = 'sat'

class RestaurantModel:
    def __init__(self, name, location, cuisine, num_clients_to_serve):
        self.name = name
        self.location = location
        self.cuisine = cuisine
        self.num_clients_to_serve = num_clients_to_serve

    def __str__(self):
        return '{}: {}, {}, {}'.format(self.name, str(self.location), str(self.cuisine), self.num_clients_to_serve)

class ClientModel:
    def __init__(self, great_plates_id, location, cuisine):
        self.great_plates_id = great_plates_id
        self.location = location
        if cuisine == Cuisine.NO_PREFERENCE:
            self.cuisine = Cuisine.AMERICAN
        else:
            self.cuisine = cuisine

        def __str__(self):
            return '{}: {}, {}'.format(self.great_plates_id, str(self.location), str(self.cuisine))

DAY_TO_FIELD = {
    Day.SUNDAY : 'Sunday (Number of Meals)',
    Day.MONDAY : 'Monday (Number of Meals)',
    Day.TUESDAY : 'Tuesday (Number of Meals)',
    Day.WEDNESDAY : 'Wednesday (Number of Meals)',
    Day.THURSDAY : 'Thursday (Number of Meals)',
    Day.FRIDAY : 'Friday (Number of Meals)',
    Day.SATURDAY : 'Saturday (Number of Meals)',
}

def row_to_client_model(row):
    row_fields = row['fields']
    return ClientModel(
        row_fields['Great Plates ID'],
        Point(float(row_fields['Latitude']), float(row_fields['Longitude'])),
        Cuisine(row_fields['Assigned Cuisine'])
    )

def row_to_restaurant_model_with_day(row, day_of_week):
    row_fields = row['fields']
    return RestaurantModel(
        row_fields['Name'],
        Point(float(row_fields['Latitude']), float(row_fields['Longitude'])),
        Cuisine(row_fields['Type of Cuisine']),
        int(row_fields.get(DAY_TO_FIELD[day_of_week], '') or 0)
    )

def get_restaurants(day_of_week):
    row_to_restaurant_model = lambda row: row_to_restaurant_model_with_day(row, day_of_week)
    rows = utils.get_all_rows(AIR_TABLE_RESTAURANTS_URL, AIR_TABLE_API_KEY)
    return map(row_to_restaurant_model, rows)

def get_clients(day_of_week):
    rows = utils.get_all_rows_with_filter(AIR_TABLE_CLIENTS_URL, AIR_TABLE_API_KEY, filter_string='AND({{{}}} > 0, {{Active}})'.format(DAY_TO_FIELD[day_of_week]))
    return map(row_to_client_model, rows)

def get_score(restaurant, client, restaurant_to_clients):
    if len(restaurant_to_clients[restaurant.name]) >= restaurant.num_clients_to_serve:
        return float('inf')

    return utils.distance(restaurant.location, client.location)

def get_best_assignment(restaurants, client, restaurant_to_clients):
    best_score = float('inf')
    best_restaurant = None
    for restaurant in restaurants:
        score = get_score(restaurant, client, restaurant_to_clients)
        if score < best_score:
            best_score = score
            best_restaurant = restaurant

    return best_restaurant

def match_clients_to_restaurants(restaurants, clients):
    restaurant_to_clients = {r.name: [] for r in restaurants}
    for client in clients:
        best_restaurant = get_best_assignment(restaurants, client, restaurant_to_clients)
        restaurant_to_clients[best_restaurant.name].append(client)

    return restaurant_to_clients

def run(day_of_week, output_csv):
    restaurants = [r for r in get_restaurants(day_of_week) if r.num_clients_to_serve > 0]
    clients = get_clients(day_of_week)
    restaurants_with_clients = match_clients_to_restaurants(restaurants, clients)

    restaurant_name_to_restaurant = {r.name: r for r in restaurants}

    for name,clients in restaurants_with_clients.items():
        print(name)
        print(restaurant_name_to_restaurant[name].location)
        print([c.location for c in clients])
        print()

if __name__ == '__main__':
        parser = argparse.ArgumentParser(
            description='Match the existing clients to the restaurants we have'
        )
        parser.add_argument(
            'day_of_week', help='A day of the week to match for (sun, mon, tue, wed, thu, fri, or sat)'
        )
        parser.add_argument(
            'output_csv', help='A path to the output CSV of matched clients'
        )

        args = parser.parse_args()

        day_of_week = Day(args.day_of_week)

        run(day_of_week, args.output_csv)
