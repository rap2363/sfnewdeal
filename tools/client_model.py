import re
from enum import Enum

HARD_CODED_START_DATE = '5/25/2020'

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

class ClientModel:
    keys = [
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
    ]

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
        'Delivery Instructions',
        'Call Center Notes'
    ]

    def __init__(self, old_csv_row):
        self.great_plates_id = old_csv_row['Great Plates ID'].strip()
        self.first_name = old_csv_row['Client Name'].split(',')[1].strip()
        self.last_name = old_csv_row['Client Name'].split(',')[0].strip()
        self.start_date = HARD_CODED_START_DATE
        self.street_address = old_csv_row['Street Address'].strip()
        self.zip_code = old_csv_row['Zip Code'].strip()
        self.requested_dietary_restrictions = old_csv_row['Dietary Restrictions']
        self.requested_cuisine = old_csv_row['Cuisine Preferences']
        self.assigned_cuisine = map_to_cuisine(self.requested_cuisine, len(old_csv_row.get('choices for 5/22', '').strip()) > 0)
        self.breakfast = map_to_checkbox(old_csv_row['Breakfast'])
        self.lunch = map_to_checkbox(old_csv_row['Lunch'])
        self.dinner = map_to_checkbox(old_csv_row['Dinner'])
        self.requested_meals_per_day = map_to_int(self.breakfast) + map_to_int(self.lunch) + map_to_int(self.dinner)
        self.household_size = int(old_csv_row['Household Size'] or 1)
        self.phone_number = int(re.sub('[^0-9]','', old_csv_row['Phone #']))
        self.language = old_csv_row['Language']
        self.access_to_fridge = map_to_checkbox(old_csv_row['Access to Fridge'])
        self.access_to_microwave = map_to_checkbox(old_csv_row['Access to Microwave'])
        self.delivery_instructions = old_csv_row['Delivery Instructions']
        self.notes = old_csv_row.get('Notes', 'None') or 'None'
        self.active = 'yes'

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
            'Breakfast': self.breakfast,
            'Lunch': self.lunch,
            'Dinner': self.dinner,
            'Household Size': self.household_size,
            'Phone Number': self.phone_number,
            'Language': self.language,
            'Access to Fridge': self.access_to_fridge,
            'Access to Microwave': self.access_to_microwave,
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
