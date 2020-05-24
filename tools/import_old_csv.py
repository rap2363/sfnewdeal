import argparse
import csv
from client_model import ClientModel

HARD_CODED_START_DATE = '5/25/2020'

'''
Old Keys
    'Great Plates ID',
    'Neighborhood',
    'Client Name',
    'Street Address',
    'Zip Code',
    'Phone #',
    'Client Cannot Meet Driver',
    'choices for 5/22',
    'Dietary Restrictions',
    'Cuisine Preferences',
    'Requested Meals Per Day',
    'Meals for 5/22',
    'Meals for 5/23',
    'Meals for 5/24',
    'Total Meals Delivered on 5/22',
    'Companion',
    'Breakfast',
    'Lunch',
    'Dinner',
    'Cuisine Preference: Other',
    'Language',
    'Language (Other)',
    'Household Size',
    'Gender',
    'Eligibility Determination',
    'Access to Fridge',
    'Access to Microwave',
    'Delivery: 3 Meals at Once',
    'Delivery: Multi-Day Delivery',
    'Delivery Schedule',
    'Days Not Receive',
    'Contact to Start (Drop Down)',
    'Delivery Contact (Detail)',
    'Delivery Text (Yes/No)',
    'Delivery Text (#)',
    'Delivery Instructions',
    'Days Not Receiving',
    'Breakfast Notes',
    'Lunch Notes',
    'Dinner Notes',
    'Assessment Date',
    'Notes'
'''
def run(input_csv, output_csv):
    client_models = []
    with open(input_csv, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = ClientModel.from_old_csv_row(row, HARD_CODED_START_DATE)
            if model is not None:
                client_models.append(model)

    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames = ClientModel.fieldnames)
        writer.writeheader()
        for client_model in client_models:
            writer.writerow(client_model.to_csv_dict_row())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process a CSV of clients'
    )
    parser.add_argument(
        'input_csv', help='A path to the CSV of clients to process'
    )
    parser.add_argument(
        'output_csv', help='A path to the output CSV of processed clients'
    )

    args = parser.parse_args()

    run(args.input_csv, args.output_csv)
