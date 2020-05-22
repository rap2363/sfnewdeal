from constants import (
    ADDRESSES_TABLE,
    DATABASE_NAME,
    DRIVERS_TABLE,
    ORDERS_TABLE,
    RESTAURANT_ADDRESS_ID,
    RESTAURANT_ID,
    RESTAURANTS_TABLE,
    ROUTES_TABLE
)

import os
import sqlite3

# Hard coded for now, but we should figure out how this changes every day
# and code for it in our DB as well (e.g. driver contact information)
NUM_DRIVERS = 10

def initialize_addresses_table():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()

        # Create table if it doesn't already exist
        c.execute('''CREATE TABLE IF NOT EXISTS {}
                     (id TEXT NOT NULL,
                      input_address TEXT,
                      google_place_id TEXT NOT NULL,
                      google_formatted TEXT NOT NULL,
                      lat REAL NOT NULL,
                      lng REAL NOT NULL,
                      PRIMARY KEY (id))'''
                      .format(ADDRESSES_TABLE))

        conn.commit()

def initialize_drivers_table():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()

        # Create table if it doesn't already exist
        c.execute('''CREATE TABLE IF NOT EXISTS {}
                     (id TEXT NOT NULL,
                      name TEXT NOT NULL,
                      phone_number TEXT,
                      route_id TEXT NULLABLE,
                      PRIMARY KEY(id),
                      FOREIGN KEY(route_id) REFERENCES {}(id))'''
                      .format(DRIVERS_TABLE, ROUTES_TABLE))

        # Create and add some fake drivers
        for driver_id in range(NUM_DRIVERS):
            c.execute("INSERT INTO {} VALUES ('{}', '{}', NULL, NULL)"
                .format(
                    DRIVERS_TABLE,
                    'driver ' + str(driver_id),
                    'Driver, ' + str(driver_id))
            )
        conn.commit()

def initialize_orders_table():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()

        # Create table if it doesn't already exist
        c.execute('''CREATE TABLE IF NOT EXISTS {}
                     (id TEXT NOT NULL,
                      client_name TEXT,
                      client_address_id TEXT NOT NULL,
                      supplying_restaurant_id TEXT NOT NULL,
                      delivery_time_window TEXT,
                      assigned_route_id TEXT NULLABLE,
                      PRIMARY KEY(id),
                      FOREIGN KEY(client_address_id) REFERENCES {}(id),
                      FOREIGN KEY(supplying_restaurant_id) REFERENCES {}(id),
                      FOREIGN KEY(assigned_route_id) REFERENCES {}(id))'''
                      .format(
                        ORDERS_TABLE,
                        ADDRESSES_TABLE,
                        RESTAURANTS_TABLE,
                        ROUTES_TABLE))

def initialize_restaurants_table():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()

        # Create table if it doesn't already exist
        c.execute('''CREATE TABLE IF NOT EXISTS {}
                     (id TEXT NOT NULL,
                      name TEXT,
                      address_id TEXT NOT NULL,
                      PRIMARY KEY(id),
                      FOREIGN KEY(address_id) REFERENCES {}(id))'''
                      .format(RESTAURANTS_TABLE, ADDRESSES_TABLE))

        # Insert the resturant
        c.execute('''INSERT INTO {} VALUES (
            '{}',
            '2234 Mission St, San Francisco, CA 94110, USA',
            'ChIJmZN_ljx-j4ARF16HqVQ2vnI',
            '2234 Mission St, San Francisco, CA 94110, USA',
            37.7612,
            -122.4195)'''.format(
                ADDRESSES_TABLE,
                RESTAURANT_ADDRESS_ID
            )
        )
        c.execute('''INSERT INTO {} VALUES ('{}', 'Mission Chinese', '{}')'''
            .format(RESTAURANTS_TABLE, RESTAURANT_ID, RESTAURANT_ADDRESS_ID))

        conn.commit()

def initialize_routes_table():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()

        # Create table if it doesn't already exist
        c.execute('''CREATE TABLE IF NOT EXISTS {}
                     (id TEXT NOT NULL,
                      sequence_id INTEGER NOT NULL,
                      address_id TEXT NOT NULL,
                      restaurant_id TEXT NULLABLE,
                      order_id TEXT NULLABLE,
                      action TEXT NOT NULL,
                      quantity INTEGER NOT NULL,
                      PRIMARY KEY (id, sequence_id),
                      FOREIGN KEY(address_id) REFERENCES {}(id)
                      FOREIGN KEY(restaurant_id) REFERENCES {}(id)
                      FOREIGN KEY(order_id) REFERENCES {}(id))'''
                      .format(
                        ROUTES_TABLE,
                        ADDRESSES_TABLE,
                        RESTAURANTS_TABLE,
                        ORDERS_TABLE
                    ))

        conn.commit()

def remove_existing_db():
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)

def initialize_database():
    remove_existing_db()
    initialize_addresses_table()
    initialize_drivers_table()
    initialize_orders_table()
    initialize_restaurants_table()
    initialize_routes_table()

if __name__ == '__main__':
    initialize_database()
