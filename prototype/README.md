# SF New Deal Backend (Prototype)

This is a prototype intended to serve as a proof of concept for the backend.
It only inputs data via a CSV file with some known structure and writes
all the data to a file-based DB called "sfnewdeal.db". You can use the sqlite3
CL to access data after running the order_ingester.py. For example:

$ python3 initialize_db.py
$ python3 order_ingester.py
$ sqlite3 -readonly sfnewdeal.db
$ > SELECT * FROM orders LIMIT 10; // See 10 of the orders
