const DAY_OF_WEEK_CLIENT_MAP = {
    sun: 'Sunday (Number of Meals)',
    mon: 'Monday (Number of Meals)',
    tue: 'Tuesday (Number of Meals)',
    wed: 'Wednesday (Number of Meals)',
    thu: 'Thursday (Number of Meals)',
    fri: 'Friday (Number of Meals)',
    sat: 'Saturday (Number of Meals)'
}

const DAY_OF_WEEK_RESTAURANT_MAP = {
    sun: 'Sunday (Number of Clients)',
    mon: 'Monday (Number of Clients)',
    tue: 'Tuesday (Number of Clients)',
    wed: 'Wednesday (Number of Clients)',
    thu: 'Thursday (Number of Clients)',
    fri: 'Friday (Number of Clients)',
    sat: 'Saturday (Number of Clients)'
}

let dayOfWeekInput = await input.textAsync("Input day of the week (sun, mon, tue, wed, thu, fri, sat, sun)");

if (dayOfWeekInput in DAY_OF_WEEK_RESTAURANT_MAP) {
    const dayOfWeekClient = DAY_OF_WEEK_CLIENT_MAP[dayOfWeekInput];
    const dayOfWeekRestaurant = DAY_OF_WEEK_RESTAURANT_MAP[dayOfWeekInput];
    const clientsTable = base.getTable('SF New Deal Clients');
    const restaurantsTable = base.getTable('Great Plates Restaurants');
    const assignmentsTable = base.getTable('Latest Assignments');
    const unassignableClientsTable = base.getTable('Unassignable Clients');
    let clientsGroupedByZipCodeAndCuisine = {};

    const clients = (await clientsTable.selectRecordsAsync()).records
        .filter(record => Number(record.getCellValue(dayOfWeekClient)) > 0)
        .filter(record => record.getCellValue('Active'))
        .map(client => ({
            lat: client.getCellValue('Latitude'),
            lng: client.getCellValue('Longitude'),
            id: client.getCellValue('Great Plates ID'),
            streetAddress: client.getCellValue('Street Address'),
            cuisine: client.getCellValue('Assigned Cuisine').name,
            zipCode: client.getCellValue('Zip code'),
            originalRow: client
        }));

    const restaurants = (await restaurantsTable.selectRecordsAsync()).records
        .filter(record => Number(record.getCellValue(dayOfWeekRestaurant)) > 0)
        .map(restaurant => ({
            lat: restaurant.getCellValue('Latitude'),
            lng: restaurant.getCellValue('Longitude'),
            name: restaurant.getCellValue('Name'),
            streetAddress: restaurant.getCellValue('Street Address'),
            cuisine: restaurant.getCellValue('Type of Cuisine').name,
            numOrders: restaurant.getCellValue(dayOfWeekRestaurant)
        }));

    for (const client of clients) {
        const key = `${client.zipCode}_${client.cuisine}`;
        if (!(key in clientsGroupedByZipCodeAndCuisine)) {
            clientsGroupedByZipCodeAndCuisine[key] = {
                cuisine: client.cuisine,
                zipCode: client.zipCode,
                centroid: null,
                clients: []
            };
        }

        clientsGroupedByZipCodeAndCuisine[key].clients.push(client);
    }

    // Calculate the centroid of each group
    for (const key in clientsGroupedByZipCodeAndCuisine) {
        let group = clientsGroupedByZipCodeAndCuisine[key];
        group.centroid = calculateCentroid(group.clients);
    }

    let sortedZipCodeCuisineGroups = Array.prototype.slice.call(Object.values(clientsGroupedByZipCodeAndCuisine)).sort((a, b) => {
        if (a.clients.length < b.clients.length) {
            return 1;
        } else if (a.clients.length > b.clients.length) {
            return -1;
        }
        return 0;
    });
    // let sortedZipCodeCuisineGroups = Array.prototype.slice.call(Object.values(clientsGroupedByZipCodeAndCuisine)).sort((a, b) => {
    //     if ((!noPreference(a.cuisine) && !noPreference(b.cuisine)) || (noPreference(a.cuisine) && noPreference(b.cuisine))) {
    //         if (a.clients.length < b.clients.length) {
    //             return 1;
    //         } else if (a.clients.length > b.clients.length) {
    //             return -1;
    //         }
    //     } else if (!noPreference(a.cuisine) && noPreference(b.cuisine)) {
    //         return -1;
    //     } else {
    //         return 1;
    //     }
    //     return 0;
    // });

    let restaurantMap = {};
    for (const restaurant of restaurants) {
        restaurantMap[restaurant.name] = restaurant;
    }

    let newClientRestaurantMatches = [];
    let unassignableClientRows = {};
    const sortedClients = sortedZipCodeCuisineGroups.flatMap(group => group.clients);

    for (const client of sortedClients) {
        let bestScore = Number.POSITIVE_INFINITY;
        let bestRestaurant = null;
        for (const restaurant of restaurants) {
            const score = getScore(client, restaurant, restaurantMap);
            if (score < bestScore) {
                bestScore = score;
                bestRestaurant = restaurant;
            }
        }

        if (bestRestaurant === null) {
            const assignedCuisine = client.cuisine;
            if (!(assignedCuisine in unassignableClientRows)) {
                unassignableClientRows[assignedCuisine] = [];
            }

            let newFieldsObj = {};
            for (const field of unassignableClientsTable.fields) {
                let updateValue = client.originalRow.getCellValue(field.name);
                if (field.type == 'singleSelect') {
                    if (updateValue) {
                        delete updateValue.id; // Remove the original reference for multiselect updates to work
                    }
                } else if (field.type == 'multipleSelects') {
                    if (updateValue) {
                        updateValue = updateValue.map(v => {
                            if (v) {
                                delete v.id;
                            }
                            return v;
                        });
                    }
                }

                newFieldsObj[field.name] = updateValue;
            }

            unassignableClientRows[assignedCuisine].push({
                fields: newFieldsObj
            });

            continue;
        }

        const bestRestaurantName = bestRestaurant.name;
        restaurantMap[bestRestaurant.name].numOrders--;
        newClientRestaurantMatches.push({
            fields: {
                'Great Plates ID': client.id,
                'Restaurant Name': bestRestaurantName,
                'Client Street Address': client.streetAddress,
                'Restaurant Street Address': bestRestaurant.streetAddress,
                'Client Latitude': client.lat,
                'Client Longitude': client.lng,
                'Client Zip Code': client.zipCode,
                'Restaurant Latitude': bestRestaurant.lat,
                'Restaurant Longitude': bestRestaurant.lng
            }
        });
    }

    output.text(`Successfully assigned ${newClientRestaurantMatches.length} clients`);

    // Now upload the matches to the Latest Assignments table

    // First clear the assignments table
    await clearTable(assignmentsTable);
    // A maximum of 50 record creations are allowed at one time, so do it in batches
    while (newClientRestaurantMatches.length > 0) {
        await assignmentsTable.createRecordsAsync(newClientRestaurantMatches.slice(0, 50));
        newClientRestaurantMatches = newClientRestaurantMatches.slice(50);
    }

    // Clear the unassignable clients table
    await clearTable(unassignableClientsTable);

    for (const cuisine in unassignableClientRows) {
        output.text(`Couldn't assign ${unassignableClientRows[cuisine].length} clients who wanted ${cuisine}`);
    }

    for (const restaurantName in restaurantMap) {
        const restaurant = restaurantMap[restaurantName];
        if (restaurant.numOrders === 0) {
            continue;
        }

        output.text(`${restaurantName} has ${restaurant.numOrders} ${restaurant.cuisine} meals left`);
    }

    let unassignableRecords = Object.values(unassignableClientRows).flatMap(v => v);
    // A maximum of 50 record creations are allowed at one time, so do it in batches
    while (unassignableRecords.length > 0) {
        await unassignableClientsTable.createRecordsAsync(unassignableRecords.slice(0, 50));
        unassignableRecords = unassignableRecords.slice(50);
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

function noPreference(cuisine) {
    return cuisine == 'No Preference' || cuisine == 'No Preference Special Diet';
}

function getScore(client, restaurant, restaurantMap) {
    if (restaurantMap[restaurant.name].numOrders <= 0) {
        return Number.POSITIVE_INFINITY;
    }

    if (!cuisinesMatch(restaurant.cuisine, client.cuisine)) {
        return Number.POSITIVE_INFINITY;
    }

    return distance(client, restaurant);
}

function cuisinesMatch(restaurantCuisine, clientCuisine) {
    if (clientCuisine === 'No Preference') {
        return restaurantCuisine === 'American' || restaurantCuisine === 'Chinese';
    } else if (clientCuisine == 'No Preference Special Diet') {
        return restaurantCuisine === 'American Special Diet' || restaurantCuisine === 'Chinese Special Diet';
    }

    return restaurantCuisine === clientCuisine;
}

function sortedByDistance(restaurant, clients) {
    return Array.prototype.slice.call(clients).sort((a,b) => {
        const distanceA = distance(restaurant, a);
        const distanceB = distance(restaurant, b);
        if (distanceA < distanceB) {
            return -1;
        } else if (distanceA > distanceB) {
            return 1;
        }

        return 0;
    })
}

function mapClientCuisine(clientCuisine) {
    if (clientCuisine === 'No Preference') {
        return 'American';
    } else if (clientCuisine == 'No Preference Special Diet') {
        return 'American Special Diet';
    }

    return clientCuisine;
}

function calculateCentroid(objs) {
    return {
        lat: objs.map(o => o.lat).reduce((a, b) => a + b, 0) / objs.length,
        lng: objs.map(o => o.lng).reduce((a, b) => a + b, 0) / objs.length
    };
}

function distance(obj1, obj2) {
    return haversine(obj1.lat, obj1.lng, obj2.lat, obj2.lng);
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
