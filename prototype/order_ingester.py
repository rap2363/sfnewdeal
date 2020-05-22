import argparse
from constants import (
    ADDRESSES_TABLE,
    DATABASE_NAME,
    ORDERS_TABLE,
    RESTAURANT_ID
)
import csv
from order_model import OrderModel
import json
import sqlite3

def run(filepath, geocoded_addresses):
    order_models = []
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            order_models.append(OrderModel.from_row(row))

    write_orders_to_db(order_models, geocoded_addresses)

def write_orders_to_db(order_models, geocoded_addresses):
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()

        # Insert into the addresses and orders tables
        for order_model in order_models:
            c.execute("INSERT INTO {} VALUES {}"
                .format(
                    ADDRESSES_TABLE,
                    to_address_row(order_model, geocoded_addresses[order_model.client_address_id])))
            c.execute("INSERT INTO {} VALUES {}"
                .format(ORDERS_TABLE, order_model.to_order_row()))

        # Save (commit) the changes
        conn.commit()

def to_address_row(order_model, geocoded_address):
    return "('{}', '{}', '{}', '{}', {}, {})".format(
        order_model.client_address_id,
        order_model.client_address,
        geocoded_address['place_id'],
        geocoded_address['formatted_address'],
        geocoded_address['location']['lat'],
        geocoded_address['location']['lng']
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process a CSV of meal orders'
    )
    parser.add_argument(
        'input_csv', help='A path to the CSV of orders to process'
    )
    parser.add_argument(
        'input_geocoded_address', help='A path to geocoded address points'
    )

    args = parser.parse_args()

    geocoded_addresses = {}
    with open(args.input_geocoded_address, 'r') as f:
        geocoded_addresses = json.load(f)

    run(args.input_csv, geocoded_addresses)
