from flask import jsonify
from app import app




@app.route('/')
def home():
    return "Siriwat says 'Hello world!'"




@app.route('/phonebook')
def index():
    return app.send_static_file('phonebook.html')




# This route serves the dictionary d at the route /data
@app.route("/api/data")
def data():
    # define some data
    d = {
        "Alice": "(708) 727-2377",
        "Siriwat": "08-8553-1558"
    }
    return jsonify(d)  # convert your data to JSON and return
