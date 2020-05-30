const table = base.getTable('SF New Deal Clients');

const fileResult = await input.fileAsync(
    'Upload an Excel (xlsx) spreadsheet of clients',
    {allowedFileTypes: ['.xlsx'], hasHeaderRow: true}
);

const startDate = await input.textAsync(
    'Enter the start date for these clients in the following format: YYYY-MM-DD'
);

const rows = fileResult.parsedContents.Sheet1;

const shouldContinue = await input.buttonsAsync(
    `Import ${rows.length} records from ${fileResult.file.name} into ${table.name}?`,
    [{label: 'Yes', variant: 'primary'}, 'No']) === 'Yes'

if (shouldContinue) {
    let newRecords = rows.map(row => {
        const numberOfMealsPerDay = Number(row['Total Meals per Day']);
        const numberOfMeals = mapToNumberOfMeals(numberOfMealsPerDay, row['Delivery Schedule'].toUpperCase().includes('SINGLE'));
        return {
            fields: {
                'Great Plates ID': row['Great Plates ID'],
                'First Name': row['Client Name'].split(', ')[1],
                'Last Name': row['Client Name'].split(', ')[0],
                'Start Date': startDate,
                'Street Address': row['Street Address'],
                'Zip code': Number(row['Zip Code']),
                'Requested Dietary Restrictions': row['Dietary Restrictions'],
                'Requested Cuisine': row['Cuisine Preferences'],
                'Requested Meals Per Day': numberOfMealsPerDay,
                'Household Size': Number(row['Household Size']),
                'Phone Number': row['Phone #'],
                'Language': row['Language'],
                'Access to Fridge': row['Access to Fridge'],
                'Access to Microwave': row['Access to Microwave'],
                'Sunday (Number of Meals)': numberOfMeals[0],
                'Monday (Number of Meals)': numberOfMeals[1],
                'Tuesday (Number of Meals)': numberOfMeals[2],
                'Wednesday (Number of Meals)': numberOfMeals[3],
                'Thursday (Number of Meals)': numberOfMeals[4],
                'Friday (Number of Meals)': numberOfMeals[5],
                'Saturday (Number of Meals)': numberOfMeals[6],
                'Delivery Instructions': row['Delivery Contact (Detail)'],
                'Call Center Notes': ''
            }
        };
    });

    // A maximum of 50 record creations are allowed at one time, so do it in batches
    while (newRecords.length > 0) {
        await table.createRecordsAsync(newRecords.slice(0, 50));
        newRecords = newRecords.slice(50);
    }

    output.text(`Uploaded ${rows.length} records!`);
}

function mapToNumberOfMeals(numberOfMealsPerDay, isSingleDayDelivery) {
    if (isSingleDayDelivery) {
        return Array(7).fill(numberOfMealsPerDay);
    } else {
        // Deliver meals for Monday, Wednesday, and Friday.
        return [0, 2 * numberOfMealsPerDay, 0, 2 * numberOfMealsPerDay, 0, 3 * numberOfMealsPerDay, 0];
    }
}
