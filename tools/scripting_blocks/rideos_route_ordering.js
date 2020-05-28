const RIDEOS_API_KEY = '${RIDEOS_API_KEY}';
const RIDEOS_GET_PLAN_URL = 'https://api.rideos.ai/fleet/v2/GetPlan';

const routesTable = base.getTable('Latest Routes');

let routes = {};

// Iterate through each route and generate plans so that we can update the route orderings
for (const record of (await routesTable.selectRecordsAsync()).records) {
    const key = record.getCellValue('Restaurant Name') + '_' + record.getCellValue('Route Number');
    if (!(key in routes)) {
        routes[key] = {};
    }

    routes[key][record.getCellValue('Sequence Number')] = {
        latitude: record.getCellValue('Latitude'),
        longitude: record.getCellValue('Longitude'),
        id: record.id
    };
}

let optimalRouteRecordUpdates = [];
for (const routeKey in routes) {
    console.log(`Obtaining routes for ${routeKey}`);

    const route = routes[routeKey];
    const payload = getPlanForRoute(route);
    const response = await fetch(
        RIDEOS_GET_PLAN_URL,
        {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Api-Key': RIDEOS_API_KEY,
                'Rideos-Api-Version': '2020-01-07'
            },
            body: JSON.stringify(payload)
        }
    );

    const jsonResponse = await response.json();
    let sequenceNumber = 1;
    for (const step of jsonResponse.recommendations[0].planRecommendation.assignedSteps) {
        if (step.stepType !== 'DROPOFF') {
            continue;
        }

        optimalRouteRecordUpdates.push({
            id: step.taskId,
            fields: {
                'Sequence Number': sequenceNumber
            }
        });
        sequenceNumber++;
    }
}

// Now update all the rows
output.text(`Updating ${optimalRouteRecordUpdates.length} rows`);
while (optimalRouteRecordUpdates.length > 0) {
    await routesTable.updateRecordsAsync(optimalRouteRecordUpdates.slice(0, 50));
    optimalRouteRecordUpdates = optimalRouteRecordUpdates.slice(50);
}

function getPlanForRoute(route) {
    // MUCH HACK
    route.length = Object.keys(route).length;
    return getPlan(route[0], Array.prototype.slice.call(route, 1));
}

function getPlan(restaurant, clients) {
        return {
            vehicles: generateVehiclesForRestaurant(restaurant),
            tasks: generateTasksForClients(restaurant, clients),
            allowVehicleReassignment: true,
            optimizeFor: 'GOODS',
            includeServicingDropoffStepInPlan: false,
            includeServicingPickupStepInPlan: false
    }
}

function generateVehiclesForRestaurant(restaurant) {
    return {
        'vehicle-0': {
            position: {
                latitude: restaurant.latitude,
                longitude: restaurant.longitude
            },
            resourceCapacity: 1000, // Hack for now to avoid passing a bunch of vars down
            vehicleId: 'vehicle-0'
        }
    };
}

function generateTasksForClients(restaurant, clients) {
    let tasks = {};
    for (const client of clients) {
        tasks[client.id] = {
            resourcesRequired: 1,
            pickupStep: {
                position: {
                    latitude: restaurant.latitude,
                    longitude: restaurant.longitude
                }
            },
            dropoffStep: {
                position: {
                    latitude: client.latitude,
                    longitude: client.longitude
                }
            }
        }
    }

    return tasks;
}
