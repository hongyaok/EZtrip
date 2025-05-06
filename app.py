from flask import Flask, render_template, request, jsonify, redirect, url_for
import os

app = Flask(__name__, 
           static_folder='static',
           template_folder='templates')

# sample data
sample_trips = [
    {
        "id": 1,
        "title": "Tokyo Adventure",
        "destination": "Tokyo, Japan",
        "start_date": "2025-06-15",
        "end_date": "2025-06-22",
        "collaborators": 3
    },
    {
        "id": 2,
        "title": "European Tour",
        "destination": "Multiple Cities, Europe",
        "start_date": "2025-07-10",
        "end_date": "2025-07-24", 
        "collaborators": 5
    }
]

@app.route('/')
def home():
    return render_template('index.html', trips=sample_trips)

@app.route('/create-trip')
def create_trip():
    return "Create Trip Form - To be implemented"

@app.route('/login')
def login():
    return "Login Page - To be implemented"

@app.route('/api/trips', methods=['GET'])
def get_trips():
    return jsonify({"trips": sample_trips})

@app.route('/api/trips', methods=['POST'])
def create_trip_api():
    data = request.json
    return jsonify({"message": "Trip created successfully", "trip": data})

if __name__ == '__main__':
    app.run(debug=True)