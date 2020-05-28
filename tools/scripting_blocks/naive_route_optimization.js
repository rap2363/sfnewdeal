const MAX_ORDERS_PER_ROUTE = 10;

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
    const numRoutes = Math.ceil(clients.length / MAX_ORDERS_PER_ROUTE);
    const clientsSortedByZipCode = Array.prototype.slice.call(clients).sort((a, b) => {
        if (a['Client Zip Code'] < b['Client Zip Code']) {
            return -1;
        } else if (a['Client Zip Code'] > b['Client Zip Code']) {
            return 1;
        }

        return 0;
    });

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

    // Naive implementation, go through the clients sorted by zip code and assign to a route
    for (let i = 0; i < clientsSortedByZipCode.length; i++) {
        const currentClient = clientsSortedByZipCode[i];
        const routeNumber = Math.floor(i / MAX_ORDERS_PER_ROUTE);
        const sequenceNumber = (i % MAX_ORDERS_PER_ROUTE) + 1;
        const client = {...currentClient, ...clientMap[currentClient['Great Plates ID']]} ;
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
