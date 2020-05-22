from constants import (DATABASE_NAME, DRIVERS_TABLE, ORDERS_TABLE, ROUTES_TABLE)
import sqlite3

def get_unassigned_driver_ids():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM {} WHERE route_id is NULL'.format(DRIVERS_TABLE))
        return [tup[0] for tup in c.fetchall()]

def get_unassigned_route_ids():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute('''SELECT DISTINCT(id)
            FROM {}
            WHERE {}.id NOT IN
                (SELECT route_id FROM {} WHERE route_id IS NOT NULL)
        '''.format(ROUTES_TABLE, ROUTES_TABLE, DRIVERS_TABLE))
        return [tup[0] for tup in c.fetchall()]

def get_all_drivers():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM {}'.format(DRIVERS_TABLE))
        return c.fetchall()

def get_num_drivers():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT count(*) FROM {}'.format(DRIVERS_TABLE))
        return c.fetchone()[0]

def get_all_orders():
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM {}'.format(ORDERS_TABLE))
        return c.fetchall()

def get_ordered_route(route_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute('''SELECT google_formatted,google_place_id,lat,lng,action,quantity
                     FROM routes JOIN addresses
                     WHERE routes.address_id=addresses.id
                     AND routes.id='{}'
                     ORDER BY sequence_id ASC'''.format(route_id))
        return c.fetchall()
