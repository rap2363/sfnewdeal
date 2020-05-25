import requests
import json
import os
from utils import Point

RIDEOS_GET_PLAN_URL = 'https://api.rideos.ai/fleet/v2/GetPlan'
RIDEOS_API_KEY = os.environ['RIDEOS_API_KEY']

class Vehicle:
    def __init__(self, id, location, capacity):
        self.id = id
        self.location = location
        self.capacity = capacity

    def dict(self):
        return {
            'position': {
                'latitude': self.location.latitude,
                'longitude': self.location.longitude
            },
            'resourceCapacity': self.capacity,
            'vehicleId': self.id
        }

    def __str__(self):
        return str(self.dict())

class Task:
    def __init__(self, id, pickup, dropoff, load):
        self.id = id
        self.pickup = pickup
        self.dropoff = dropoff
        self.load = load

    def dict(self):
        return {
            'resourcesRequired': self.load,
            'pickupStep': {
                'position': {
                    'latitude': self.pickup.latitude,
                    'longitude': self.pickup.longitude
                }
            },
            'dropoffStep': {
                'position': {
                    'latitude': self.dropoff.latitude,
                    'longitude': self.dropoff.longitude
                }
            }
        }

    def __str__(self):
        return json.dumps(self.dict())

class GetPlanRequest:
    def __init__(self, vehicles, tasks):
        self.vehicles = vehicles
        self.tasks = tasks

    def dict(self):
        return {
            'vehicles': {v.id: v.dict() for v in self.vehicles},
            'tasks': {t.id: t.dict() for t in self.tasks},
            'allowVehicleReassignment': True,
            'optimizeFor': 'GOODS',
            'includeServicingDropoffStepInPlan': False,
            'includeServicingPickupStepInPlan': False
        }

    def __str__(self):
        return str(self.dict())

class RideosAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['X-Api-Key'] = self.token
        r.headers['Rideos-Api-Version'] = '2020-01-07'
        return r

def construct_get_plan(restaurant_location, meal_locations, num_drivers):
    vehicle_capacity = int(1.5 * len(meal_locations) / num_drivers)
    # Each restaurant_location becomes a vehicle
    vehicles = [Vehicle('vehicle-{}'.format(i), restaurant_location, vehicle_capacity) for i in range(num_drivers)]
    tasks = [Task('task-{}'.format(i), restaurant_location, meal_location, 1) for i, meal_location in enumerate(meal_locations)]

    return GetPlanRequest(vehicles, tasks)

def get_restaurant_routes(restaurant_location, meal_locations, num_drivers=1):
    get_plan = construct_get_plan(restaurant_location, meal_locations, num_drivers)
    return requests.post(
        url=RIDEOS_GET_PLAN_URL,
        auth=RideosAuth(RIDEOS_API_KEY),
        json=get_plan.dict()
    )

if __name__ == '__main__':
    # Green Heart
    restaurant_location = Point(37.7529787,-122.3923472)

    meal_locations = [
        Point(37.758440, -122.395389),
        Point(37.758372, -122.393519),
        Point(37.731662, -122.492848),
        Point(37.749166, -122.480169),
        Point(37.720347, -122.402678),
        Point(37.709803, -122.444987),
        Point(37.739491, -122.485858),
        Point(37.752958, -122.456620),
        Point(37.738373, -122.476687),
        Point(37.715109, -122.454044),
        Point(37.720882, -122.436084),
        Point(37.749363, -122.493593),
        Point(37.753290, -122.466903),
        Point(37.717582, -122.446126),
        Point(37.727065, -122.404755),
        Point(37.747881, -122.483795),
        Point(37.755630, -122.398565),
        Point(37.726182, -122.470938),
        Point(37.736443, -122.490413),
        Point(37.738516, -122.489459),
        Point(37.736443, -122.490413),
        Point(37.763233, -122.420047),
        Point(37.748285, -122.506355),
        Point(37.740003, -122.506178),
        Point(37.741717, -122.499414),
        Point(37.734143, -122.497624),
        Point(37.752135, -122.490129),
        Point(37.709994, -122.470054),
        Point(37.733916, -122.401839),
        Point(37.746090, -122.504089),
        Point(37.753136, -122.485796),
        Point(37.735408, -122.414107),
        Point(37.736423, -122.495174),
        Point(37.747594, -122.433430),
        Point(37.729230, -122.450151),
        Point(37.746166, -122.504056),
        Point(37.741353, -122.500022),
        Point(37.729699, -122.415202),
        Point(37.709397, -122.444401),
        Point(37.740880, -122.421961)
    ]

    response = get_restaurant_routes(restaurant_location, meal_locations, 5)
    print(response.text)
    json_response = response.json()
    restaurant_recommendations = json_response['recommendations']
    routes = []
    for i,recommendation in enumerate(restaurant_recommendations):
        task_indices = [int(step['taskId'][5:]) for step in recommendation['planRecommendation']['assignedSteps'] if step['stepType']=='DROPOFF']
        route_locations = [restaurant_location] + [meal_locations[t_i] for t_i in task_indices]
        routes.append([[route_location.longitude, route_location.latitude] for route_location in route_locations])

    geojson_multiline_string = {
        'type': 'MultiLineString',
        'coordinates': routes
    }

    print(json.dumps(geojson_multiline_string, indent=4))
