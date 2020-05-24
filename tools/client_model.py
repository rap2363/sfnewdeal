import re
from enum import Enum

DEFAULT_MEALS_PER_DAY = 3

class MealTime(Enum):
    BREAKFAST = 'Breakfast'
    LUNCH = 'Lunch'
    DINNER = 'Dinner'

class Cuisine(Enum):
    AMERICAN = 'American'
    CHINESE = 'Chinese'
    AMERICAN_SPECIAL_DIET = 'American Special Diet'
    CHINESE_SPECIAL_DIET = 'Chinese Special Diet'
    NO_PREFERENCE = 'No Preference'

def map_to_cuisine(description, is_special):
    if 'AMERICAN' in description.upper():
        return Cuisine.AMERICAN_SPECIAL_DIET if is_special else Cuisine.AMERICAN
    if 'CHINESE' in description.upper():
        return Cuisine.CHINESE_SPECIAL_DIET if is_special else Cuisine.CHINESE
    return Cuisine.NO_PREFERENCE

def map_to_checkbox(desc):
    return 'yes' if 'TRUE' in desc.upper() else 'no'

def map_to_int(desc):
    return 1 if desc == 'yes' else 0

def valid_gp_id(gp_id):
    return len(gp_id) > 1 and gp_id[0].isalpha() and gp_id[1:].isnumeric()

def map_to_meals_on_days(row):
    num_meals_per_day = get_num_meals(row)
    single_day_delivery = 'SINGLE' in row['Delivery Schedule'].upper()
    if single_day_delivery:
        return [num_meals_per_day] * 7
    else:
        return [0, 2 * num_meals_per_day, 0, 2 * num_meals_per_day, 0, 3 * num_meals_per_day, 0]

def get_num_meals(row):
    if row['Total Meals per Day'].isdigit():
        return int(row['Total Meals per Day'])
    return DEFAULT_MEALS_PER_DAY

class ClientModel:
    fieldnames = [
        'Great Plates ID',
        'First Name',
        'Last Name',
        'Start Date',
        'Street Address',
        'Zip Code',
        'Requested Dietary Restrictions',
        'Requested Cuisine',
        'Assigned Cuisine',
        'Requested Meals Per Day',
        'Breakfast',
        'Lunch',
        'Dinner',
        'Household Size',
        'Phone Number',
        'Language',
        'Access to Fridge',
        'Access to Microwave',
        'Sunday (Number of Meals)',
        'Monday (Number of Meals)',
        'Tuesday (Number of Meals)',
        'Wednesday (Number of Meals)',
        'Thursday (Number of Meals)',
        'Friday (Number of Meals)',
        'Saturday (Number of Meals)',
        'Delivery Instructions',
        'Call Center Notes'
    ]

    def __init__(
        self,
        great_plates_id,
        first_name,
        last_name,
        start_date,
        street_address,
        zip_code,
        requested_dietary_restrictions,
        requested_cuisine,
        assigned_cuisine,
        requested_meals_per_day,
        household_size,
        phone_number,
        language,
        access_to_fridge,
        access_to_microwave,
        delivery_instructions,
        num_meals_per_day,
        notes,
        active
    ):
        self.great_plates_id = great_plates_id
        self.first_name = first_name
        self.last_name = last_name
        self.start_date = start_date
        self.street_address = street_address
        self.zip_code = zip_code
        self.requested_dietary_restrictions = requested_dietary_restrictions
        self.requested_cuisine = requested_cuisine
        self.assigned_cuisine = assigned_cuisine
        self.requested_meals_per_day = requested_meals_per_day
        self.household_size = household_size
        self.phone_number = phone_number
        self.language = language
        self.access_to_fridge = access_to_fridge
        self.access_to_microwave = access_to_microwave
        self.delivery_instructions = delivery_instructions
        self.num_meals_per_day = num_meals_per_day
        self.notes = notes
        self.active = active

    def from_old_csv_row(old_csv_row, start_date):
        great_plates_id = old_csv_row['Great Plates ID'].strip()
        if not valid_gp_id(great_plates_id):
            print('Invalid Great Plates ID: {} for {}'.format(great_plates_id, old_csv_row['Client Name']))
            return None

        return ClientModel(
            great_plates_id,
            old_csv_row['Client Name'].split(',')[1].strip(),
            old_csv_row['Client Name'].split(',')[0].strip(),
            start_date,
            old_csv_row['Street Address'].strip(),
            old_csv_row['Zip Code'].strip(),
            '{};{}'.format(old_csv_row['Dietary Restrictions'], old_csv_row['Dietary Restrictions: Other']),
            old_csv_row['Cuisine Preferences'],
            map_to_cuisine(old_csv_row['Cuisine Preferences'], len(old_csv_row.get('choices for 5/22', '').strip()) > 0),
            get_num_meals(old_csv_row),
            int(old_csv_row['Household Size'] or 1),
            int(re.sub('[^0-9]','', old_csv_row['Phone #'])),
            old_csv_row['Language'],
            map_to_checkbox(old_csv_row['Access to Fridge']),
            map_to_checkbox(old_csv_row['Access to Microwave']),
            old_csv_row['Delivery Instructions'],
            map_to_meals_on_days(old_csv_row),
            old_csv_row.get('Notes', 'None') or 'None',
            'yes'
        )

    '''
    Great Plates ID
    Client Name
    Street Address
    Zip Code
    Phone #
    Language
    Language (Other)
    Household Size
    Gender
    Eligibility Determination
    Companion Case
    IR2 ID
    Dietary Restrictions
    Dietary Restrictions: Other
    Cuisine Preferences
    Cuisine Preferences: Other
    Breakfast
    Lunch
    Dinner
    Total Meals per Day
    Access to Fridge
    Access to Microwave
    Delivery: 3 Meals at Once
    Delivery: Multi-Day Delivery
    Delivery Schedule
    Delivery Schedule Reason
    Days Not Receive
    Contact to Start (Drop Down)
    Delivery Contact (Detail)
    Delivery Text (Yes/No)
    Delivery Text (#)
    Delivery Instructions
    Client Cannot Meet Driver
    '''
    def from_csv_row(csv_row, start_date):
        great_plates_id = csv_row['Great Plates ID'].strip()
        if not valid_gp_id(great_plates_id):
            print('Invalid Great Plates ID: {} for {}'.format(great_plates_id, csv_row['Client Name']))
            return None
        return ClientModel(
            great_plates_id,
            csv_row['Client Name'].split(',')[1].strip(),
            csv_row['Client Name'].split(',')[0].strip(),
            start_date,
            csv_row['Street Address'].strip(),
            csv_row['Zip Code'].strip(),
            '{};{}'.format(csv_row['Dietary Restrictions'], csv_row['Dietary Restrictions: Other']),
            csv_row['Cuisine Preferences'],
            map_to_cuisine(csv_row['Cuisine Preferences'], len(csv_row.get('Cuisine Preferences: Other', '').strip()) > 0),
            get_num_meals(csv_row),
            int(csv_row['Household Size'] or 1),
            int(re.sub('[^0-9]','', csv_row['Phone #'])),
            csv_row['Language'],
            map_to_checkbox(csv_row['Access to Fridge']),
            map_to_checkbox(csv_row['Access to Microwave']),
            csv_row['Delivery Instructions'],
            map_to_meals_on_days(csv_row),
            csv_row.get('Notes', 'None') or 'None',
            'yes'
        )

    def to_csv_dict_row(self):
        return {
            'Great Plates ID': self.great_plates_id,
            'First Name': self.first_name,
            'Last Name': self.last_name,
            'Start Date': self.start_date,
            'Street Address': self.street_address,
            'Zip Code': self.zip_code,
            'Requested Dietary Restrictions': self.requested_dietary_restrictions,
            'Requested Cuisine': self.requested_cuisine,
            'Assigned Cuisine': self.assigned_cuisine.value,
            'Requested Meals Per Day': self.requested_meals_per_day,
            'Breakfast': self.requested_meals_per_day >= 3,
            'Lunch': self.requested_meals_per_day >= 2,
            'Dinner': self.requested_meals_per_day >= 1,
            'Household Size': self.household_size,
            'Phone Number': self.phone_number,
            'Language': self.language,
            'Access to Fridge': self.access_to_fridge,
            'Access to Microwave': self.access_to_microwave,
            'Sunday (Number of Meals)': self.num_meals_per_day[0],
            'Monday (Number of Meals)': self.num_meals_per_day[1],
            'Tuesday (Number of Meals)': self.num_meals_per_day[2],
            'Wednesday (Number of Meals)': self.num_meals_per_day[3],
            'Thursday (Number of Meals)': self.num_meals_per_day[4],
            'Friday (Number of Meals)': self.num_meals_per_day[5],
            'Saturday (Number of Meals)': self.num_meals_per_day[6],
            'Delivery Instructions': self.delivery_instructions,
            'Call Center Notes': self.notes
        }

        return map(lambda v : "'{}'".format(str(v)), [
            self.great_plates_id,
            self.first_name,
            self.last_name,
            self.start_date,
            self.street_address,
            self.zip_code,
            self.requested_dietary_restrictions,
            self.requested_cuisine,
            self.assigned_cuisine.value,
            self.requested_meals_per_day,
            self.breakfast,
            self.lunch,
            self.dinner,
            self.phone_number,
            self.language,
            self.access_to_fridge,
            self.access_to_microwave,
            self.notes
        ])

    def to_csv_row(self):
        return map(lambda v : "'{}'".format(str(v)), [
            self.great_plates_id,
            self.first_name,
            self.last_name,
            self.start_date,
            self.street_address,
            self.zip_code,
            self.requested_dietary_restrictions,
            self.requested_cuisine,
            self.assigned_cuisine.value,
            self.requested_meals_per_day,
            self.breakfast,
            self.lunch,
            self.dinner,
            self.phone_number,
            self.language,
            self.access_to_fridge,
            self.access_to_microwave,
            self.notes
        ])
