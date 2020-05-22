from constants import (
    DATABASE_NAME,
    ORDERS_TABLE,
    RESTAURANT_ADDRESS_ID,
    RESTAURANT_ID,
    RESTAURANTS_TABLE,
    DRIVERS_TABLE,
    ROUTES_TABLE,
    PICKUP,
    DROPOFF
)
from order_model import OrderModel
from itertools import chain
import sql_utils
import sqlite3

def to_route_row(route):
    return "('{}', '{}', '{}', {}, {}, '{}', '{}')".format(
        route['route_id'],
        route['sequence_id'],
        route['address_id'],
        'NULL' if route['restaurant_id'] is None else "'{}'".format(
            route['restaurant_id']),
        'NULL' if route['order_id'] is None else "'{}'".format(
            route['order_id']),
        route['action'],
        route['quantity']
    )

def process_orders():
    routes = process_orders_and_calculate_routes()
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()

        # Insert into the routes table
        for route in chain(*routes):
            c.execute("INSERT INTO {} VALUES {}"
                .format(ROUTES_TABLE, to_route_row(route)))

        # Save (commit) the changes
        conn.commit()


def process_orders_and_calculate_routes():
    '''Divide up the total number of orders to one of 10 routes'''
    num_drivers = sql_utils.get_num_drivers()
    orders = sql_utils.get_all_orders()

    routes = [
        calculate_route(i, orders[i::num_drivers]) for i in range(num_drivers)
    ]

    return routes

def calculate_route(route_id, orders):
    '''The route starts at the restaurant, and then processes each order
       sequentially'''
    route = []
    route.append({
        'route_id': route_id,
        'sequence_id': 0,
        'address_id': RESTAURANT_ADDRESS_ID,
        'restaurant_id': RESTAURANT_ID,
        'order_id': None,
        'action': PICKUP,
        'quantity': len(orders)
    })

    for i, order in enumerate(orders):
        route.append({
            'route_id': route_id,
            'sequence_id': i + 1,
            'address_id': order[2],
            'restaurant_id': None,
            'order_id': order[0],
            'action': DROPOFF,
            'quantity': 1 # We can include this in the order model later
        })

    return route

if __name__ == '__main__':
    process_orders()
