from constants import RESTAURANT_ID
from uuid import uuid4

# Hard coded for now
ALL_DAY_TIME_WINDOW = '[6,18]'

class OrderModel:
    order_count = 0

    def __init__(
        self,
        id,
        client_name,
        client_address_id,
        client_address,
        restaurant_id,
        time_window
    ):
        self.id = id
        self.client_name = client_name
        self.client_address_id = client_address_id
        self.client_address = client_address
        self.restaurant_id = restaurant_id
        self.time_window = time_window

    def from_row(row):
        order_count = OrderModel.order_count
        OrderModel.order_count += 1
        return OrderModel(
            uuid4().hex,
            row['Client Name'],
            'client_addr_{}'.format(order_count),
            row['Street Address'] + ', ' + row['Zip Code'],
            RESTAURANT_ID,
            ALL_DAY_TIME_WINDOW
        )

    def to_order_row(self):
        return "('{}', '{}', '{}', '{}', '{}', NULL)".format(
            self.id,
            self.client_name,
            self.client_address_id,
            self.restaurant_id,
            self.time_window
        )
