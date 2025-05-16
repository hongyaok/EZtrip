from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from auth.auth import auth, login_required

app = Flask(__name__, static_folder = 'static', template_folder = 'templates') # set static and template folders

app.secret_key = os.urandom(24) #key for sess
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # development only

app.register_blueprint(auth, url_prefix='/auth') # register the auth blueprint

@app.route('/') # when href '/' is called in html
def home():
    return render_template('index.html')

@app.route('/create-trip') # when href '/create-trip' is called in html
@login_required # ensure user is logged in
def create_trip():
    return render_template('create_trip.html', 
                          name=session['name'], 
                          email=session['email'],
                          picture=session['picture'])

@app.route('/dashboard') # when href '/dashboard' is called in html
@login_required  # ensure user is logged in
def dashboard():
    return render_template('dashboard.html', 
                          name=session['name'], 
                          email=session['email'],
                          picture=session['picture'])

@app.route('/api/trips', methods=['GET'])
def get_trips(): 
    # implement logic to fetch trips from the database
    return jsonify({"trips": []})

@app.route('/api/trips', methods=['POST'])
def create_trip_api():
    # implement logic to create a new trip in the database
    data = request.json
    return jsonify({"message": "Trip created successfully", "trip": data})

if __name__ == '__main__':
    app.run(debug=True)
