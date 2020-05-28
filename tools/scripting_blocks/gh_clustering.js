const GRAPH_HOPPER_API_KEY = "${GH_API_KEY}";
const MIN_ORDERS_PER_ROUTE = 5;
const MAX_ORDERS_PER_ROUTE = 20;

const clientsTable = base.getTable('SF New Deal Clients');
const assignmentsTable = base.getTable('Latest Assignments');
const routesTable = base.getTable('Latest Routes');

// Get clients keyed by Great Plate ID
let clientMap = {};
for (const record of (await clientsTable.selectRecordsAsync()).records) {
    clientMap[record.getCellValue('Great Plates ID')] = {
        'Client Name': `${record.getCellValue('First Name')} ${record.getCellValue('Last Name')}`,
        'Client Phone Number': record.getCellValue('Phone Number'),
        'Delivery Instructions': record.getCellValue('Delivery Instructions'),
        'Call Center Notes': record.getCellValue('Call Center Notes'),
        'Orders to Drop Off': record.getCellValue('Requested Meals Per Day'),
        'Google Maps URL': generateDirectionsUrl(record.getCellValue('Latitude'), record.getCellValue('Longitude'), record.getCellValue('Google Place ID'))
    };
}

// First obtain the routes as grouped by the assignments on the restaurant name
let restaurantsToClients = {};
for (const record of (await assignmentsTable.selectRecordsAsync()).records) {
    const key = record.getCellValue('Restaurant Name');
    if (!(key in restaurantsToClients)) {
        restaurantsToClients[key] = [];
    }

    restaurantsToClients[key].push({
        'Restaurant Latitude': record.getCellValue('Restaurant Latitude'),
        'Restaurant Longitude': record.getCellValue('Restaurant Longitude'),
        'Restaurant Street Address': record.getCellValue('Restaurant Street Address'),
        'Great Plates ID': record.getCellValue('Great Plates ID'),
        'Client Latitude': record.getCellValue('Client Latitude'),
        'Client Longitude': record.getCellValue('Client Longitude'),
        'Client Street Address': record.getCellValue('Client Street Address'),
        'Client Zip Code': record.getCellValue('Client Zip Code')
    });
}

// For each restaurant we go through and create routes that group by zip code
let newRecords = [];
for (const restaurantName in restaurantsToClients) {
    const clients = restaurantsToClients[restaurantName];
    // Now we want to find a group of routes to handle this set of orders, so we use the GH Clustering API
    const numRoutes = Math.ceil(clients.length / MAX_ORDERS_PER_ROUTE);

    // Sequence Number = 0 refers to the restaurant
    for (let i = 0; i < numRoutes; i++) {
        newRecords.push({
            fields: {
                'Restaurant Name': restaurantName,
                'Route Number': i,
                'Sequence Number': 0,
                'Great Plates ID': '',
                'Street Address': clients[0]['Restaurant Street Address'],
                'Latitude': clients[0]['Restaurant Latitude'],
                'Longitude': clients[0]['Restaurant Longitude'],
                'Google Maps URL': generateDirectionsUrl(clients[0]['Restaurant Latitude'], clients[0]['Restaurant Longitude'], '')
            }
        });
    }

    const payload = generateClusterRequestPayload(numRoutes, MIN_ORDERS_PER_ROUTE, MAX_ORDERS_PER_ROUTE, clients);
    const clusterApiResponse = await getClusterResponse(payload);

    // For each cluster, add to the route
    for (let routeNumber = 0; routeNumber < clusterApiResponse.clusters.length; routeNumber++) {
        const cluster = clusterApiResponse.clusters[routeNumber];
        const clientsOnRoute = cluster.ids.map(id => clientMap[id]);
        for (let j = 0; j < clientsOnRoute.length; j++) {
            const sequenceNumber = j + 1;
            const client = {...clientsOnRoute[j], ...clientMap[clientsOnRoute[j]['Great Plates ID']]} ;
            newRecords.push({
                fields: {
                    'Restaurant Name': restaurantName,
                    'Route Number': routeNumber,
                    'Sequence Number': sequenceNumber,
                    'Great Plates ID': client['Great Plates ID'],
                    'Street Address': client['Client Street Address'],
                    'Latitude': client['Client Latitude'],
                    'Longitude': client['Client Longitude'],
                    'Client Name': client['Client Name'],
                    'Client Phone Number': client['Client Phone Number'],
                    'Delivery Instructions': client['Delivery Instructions'],
                    'Call Center Notes': client['Call Center Notes'],
                    'Orders to Drop Off': client['Orders to Drop Off'],
                    'Google Maps URL': client['Google Maps URL']
                }
            });
        }
    }
}

await clearTable(routesTable);
await uploadRecordsToTable(routesTable, newRecords);

async function uploadRecordsToTable(table, records) {
    // A maximum of 50 record creations are allowed at one time, so do it in batches
    let recordsToUpload = records.slice();
    while (recordsToUpload.length > 0) {
        await table.createRecordsAsync(recordsToUpload.slice(0, 50));
        recordsToUpload = recordsToUpload.slice(50);
    }
}

async function clearTable(table) {
    let recordIds = (await table.selectRecordsAsync()).records.map(record => record.id);
    while (recordIds.length > 0) {
        await table.deleteRecordsAsync(recordIds.slice(0, 50));
        recordIds = recordIds.slice(50);
    }
}

function generateDirectionsUrl(lat, lng, placeId) {
    return `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}&destination_place_id=${placeId}`;
}

function compareDistance(client0, client1) {
    const distance0 = haversine(client0['Restaurant Latitude'], client0['Restaurant Longitude'], client0['Client Latitude'], client0['Client Longitude']);
    const distance1 = haversine(client1['Restaurant Latitude'], client1['Restaurant Longitude'], client1['Client Latitude'], client1['Client Longitude']);

    if (distance0 < distance1) {
        return -1;
    } else if (distance0 > distance1) {
        return 1;
    }

    return 0;
}


function haversine(lat0, lon0, lat1, lon1) {
    const toRadians = theta => theta * Math.PI / 180.0;

    const R = 6372.8; // This is the Earth's radius in km

    let dLat = toRadians(lat1 - lat0)
    let dLon = toRadians(lon1 - lon0)
    let lat0Radians = toRadians(lat0)
    let lat1Radians = toRadians(lat1)

    const sinDeltaLat = Math.sin(dLat * 0.5);
    const sinDeltaLon = Math.sin(dLon * 0.5);

    const a = (sinDeltaLat * sinDeltaLat) + Math.cos(lat0Radians) * Math.cos(lat1Radians) * sinDeltaLon * sinDeltaLon;
    const c = 2 * Math.asin(Math.sqrt(a))

    return R * c
}

function generateClusterRequestPayload(numClusters, minClusterSize, maxClusterSize, clients) {
    return {
        configuration: {
            response_type: "json",
            routing: {
            profile: "car",
            cost_per_second: 1,
            cost_per_meter: 0
            },
            clustering: {
                num_clusters: numClusters,
                max_quantity: maxClusterSize,
                min_quantity: minClusterSize
            }
        },
        customers: clients.map(client => ({
                id: client.getCellValue("Great Plates ID"),
                address: {
                    lon: client.getCellValue("Client Longitude"),
                    lat: client.getCellValue("Client Latitude"),
                    street_hint: client.getCellValue("Client Street Address")
                },
                quantity: 1
        }))
    };
}

async function getClusterResponse(payload) {
    const apiResponse = await fetch(
        `https://graphhopper.com/api/1/cluster?key=${GRAPH_HOPPER_API_KEY}`,
        {
            method: "POST",
            headers: {
            "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        }
    )

    return await apiResponse.json();
}
