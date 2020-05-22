from constants import (
    DATABASE_NAME,
    DRIVERS_TABLE,
    ROUTES_TABLE,
    PICKUP,
    DROPOFF
)
import os
import sql_utils
import sqlite3
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_FROM_PHONE_NUMBER = os.environ['TWILIO_FROM_PHONE_NUMBER']
CLIENT = Client(account_sid, auth_token)

BASE_URL='https://www.google.com/maps/dir/?api=1'

def assign_routes_to_drivers():
    '''Go through our drivers table and assign routes to drivers without
       assignments'''
    unassigned_driver_ids = sql_utils.get_unassigned_driver_ids()
    unassigned_route_ids = sql_utils.get_unassigned_route_ids()

    # Assign routes to drivers (we're limited by the drivers)
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        for driver_id, route_id in zip(unassigned_driver_ids, unassigned_route_ids):
            c.execute('''UPDATE {}
                SET route_id='{}'
                WHERE id='{}'
                '''.format(DRIVERS_TABLE, route_id, driver_id))

        conn.commit()

    # Message any drivers we can with the new route
    drivers = sql_utils.get_all_drivers()
    for driver in drivers:
        id, name, phone_number, route_id = driver
        if phone_number is not None:
            route = create_route(route_id)
            message_drivers(phone_number, route)

def create_route(route_id):
    return [
        {
            'address': row[0],
            'place_id': row[1],
            'lat': row[2],
            'lng': row[3],
            'action': row[4],
            'quantity': row[5]
        } for row in sql_utils.get_ordered_route(route_id)]

def message_drivers(driver_phone_number, route):
    message_body = "Thank you for volunteering as a driver with SF New Deal! Here is your route:\n{}"\
       .format(create_messaging_route(route))

    message = CLIENT.messages \
    .create(
         body=message_body,
         from_=TWILIO_FROM_PHONE_NUMBER,
         to=driver_phone_number
    )

def create_messaging_route(route):
    google_route_url = get_directions_url(route)
    message_body = ''
    for step in route:
        if step['action'] == PICKUP:
            message_body += 'Pick up {} meals from {}\n'.format(step['quantity'], step['address'])
        elif step['action'] == DROPOFF:
            message_body += 'Drop off {} meal(s) at {}\n'.format(step['quantity'], step['address'])

    message_body += '\nUse the following link to open up your route in Google Maps: {}'.format(google_route_url)

    return message_body

def get_directions_url(route):
    url = BASE_URL
    if len(route) < 2:
        print('Invalid route! {}'.format(route))
        return None

    origin = "&origin={},{}&origin_place_id={}".format(
        route[0]['lat'], route[0]['lng'], route[0]['place_id']
    )
    destination = "&destination={},{}&destination_place_id={}".format(
        route[-1]['lat'], route[-1]['lng'], route[-1]['place_id']
    )
    waypoints = "&waypoints={}&waypoint_place_ids={}".format(
        '|'.join([str(step['lat'])+','+str(step['lng']) for step in route[1:-1]]),
        '|'.join(step['place_id'] for step in route[1:-1])
    )

    return BASE_URL + origin + destination + waypoints

if __name__ == '__main__':
    assign_routes_to_drivers()
