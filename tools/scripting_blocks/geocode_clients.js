const GOOGLE_MAPS_API_KEY = ${API_KEY};

let table = base.getTable("SF New Deal Clients");
let query = await table.selectRecordsAsync();
for (let record of query.records) {
    if (record.getCellValueAsString("Google Place ID") !== '') {
        continue;
    }

    output.text('Updating ' + record.getCellValue('Great Plates ID'));

    let address = (record.getCellValue('Street Address').split(', ')[0].replace(/#|\$|@|!|\./g, '') + ' San Francisco CA').split(' ').join('+');
    let queryUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${address}&key=${GOOGLE_MAPS_API_KEY}`
    let response = await fetch(queryUrl);
    let jsonResponse = await response.json();
    if (jsonResponse.results.length === 0) {
        output.text(`No results for ${queryUrl}`);
        continue;
    }

    let topResult = jsonResponse.results[0];
    table.updateRecordAsync(record, {
        'Google Place ID': topResult.place_id,
        'Latitude': topResult.geometry.location.lat,
        'Longitude': topResult.geometry.location.lng,
        'Google Formatted Address': topResult.formatted_address    
    });
}
