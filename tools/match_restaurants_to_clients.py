import argparse
import csv
import json
import os
import requests
import time
from enum import Enum

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


def run(day_of_week, output_csv):


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

        print(day_of_week)

        run(day_of_week, args.output_csv)
