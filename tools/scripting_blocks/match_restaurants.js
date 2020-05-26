const DAY_OF_WEEK_MAP = {
    sun: 'Sunday (Number of Meals)',
    mon: 'Monday (Number of Meals)',
    tue: 'Tuesday (Number of Meals)',
    wed: 'Wednesday (Number of Meals)',
    thu: 'Thursday (Number of Meals)',
    fri: 'Friday (Number of Meals)',
    sat: 'Saturday (Number of Meals)'
}

let dayOfWeekInput = await input.textAsync("Input day of the week (sun, mon, tue, wed, thu, fri, sat, sun)");

if (dayOfWeekInput in DAY_OF_WEEK_MAP) {
    let dayOfWeek = DAY_OF_WEEK_MAP[dayOfWeekInput]; // Add this as input
    let clientsTable = base.getTable('SF New Deal Clients');
    let restaurantsTable = base.getTable('Great Plates Restaurants');
    let assignmentsTable = base.getTable('Latest Assignments');

    let clients = (await clientsTable.selectRecordsAsync()).records
        .filter(record => record.getCellValue(dayOfWeek) > 0)
        .filter(record => record.getCellValue('Active'));

    let restaurants = (await restaurantsTable.selectRecordsAsync()).records
        .filter(record => record.getCellValue(dayOfWeek) > 0);

    let restaurantsWithCapacities = {};
    for (let restaurant of restaurants) {
        restaurantsWithCapacities[restaurant.getCellValue('Name')] = restaurant.getCellValue(dayOfWeek);
    }

    let newClientRestaurantMatches = [];
    for (let client of clients) {
        let bestScore = Number.POSITIVE_INFINITY;
        let bestRestaurant = null;
        for (let restaurant of restaurants) {
            const score = getScore(client, restaurant, restaurantsWithCapacities);
            if (score < bestScore) {
                bestScore = score;
                bestRestaurant = restaurant;
            }
        }

        if (bestRestaurant === null) {
            output.text(`Couldn't assign ${client.getCellValue('Great Plates ID')} with cuisine preference: ${client.getCellValue('Assigned Cuisine').name}`);
            continue;
        }
        const bestRestaurantName = bestRestaurant.getCellValue('Name');
        restaurantsWithCapacities[bestRestaurant.getCellValue('Name')]--;
        newClientRestaurantMatches.push({
            fields: {
                'Great Plates ID': client.getCellValue('Great Plates ID'),
                'Restaurant Name': bestRestaurantName,
                'Client Street Address': client.getCellValue('Google Formatted Address'),
                'Restaurant Street Address': bestRestaurant.getCellValue('Google Formatted Address'),
                'Client Latitude': client.getCellValue('Latitude'),
                'Client Longitude': client.getCellValue('Longitude'),
                'Restaurant Latitude': bestRestaurant.getCellValue('Latitude'),
                'Restaurant Longitude': bestRestaurant.getCellValue('Longitude'),
            }
        });
    }

    // Now upload the matches to the Latest Assignments table

    // First clear the table
    await clearTable(assignmentsTable);

    // A maximum of 50 record creations are allowed at one time, so do it in batches
    while (newClientRestaurantMatches.length > 0) {
        await assignmentsTable.createRecordsAsync(newClientRestaurantMatches.slice(0, 50));
        newClientRestaurantMatches = newClientRestaurantMatches.slice(50);
    }
} else {
    output.text('Invalid Day of Week! Try again');
}

async function clearTable(table) {
    let recordIds = (await table.selectRecordsAsync()).records.map(record => record.id);
    while (recordIds.length > 0) {
        await table.deleteRecordsAsync(recordIds.slice(0, 50));
        recordIds = recordIds.slice(50);
    }
}

function getScore(client, restaurant, restaurantsWithCapacities) {
    if (restaurantsWithCapacities[restaurant.getCellValue('Name')] <= 0) {
        return Number.POSITIVE_INFINITY;
    }

    let clientCuisine = client.getCellValue('Assigned Cuisine').name;
    if (clientCuisine === 'No Preference') {
        clientCuisine = 'American';
    } else if (clientCuisine == 'No Preference Special Diet') {
        clientCuisine = 'American Special Diet';
    }

    if (restaurant.getCellValue('Type of Cuisine').name !== clientCuisine) {
        return Number.POSITIVE_INFINITY;
    }

    return distance(client, restaurant);
}

function distance(row0, row1) {
    return haversine(row0.getCellValue('Latitude'), row0.getCellValue('Longitude'), row1.getCellValue('Latitude'), row1.getCellValue('Longitude'));
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
