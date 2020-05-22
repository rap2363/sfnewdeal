import argparse
import csv
from client_model import ClientModel

def run(input_csv, output_csv):
    client_models = []
    with open(input_csv, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            client_models.append(ClientModel(row))
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
