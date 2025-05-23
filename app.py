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
@login_required
def create_trip_api():
    #extract out the info from the form 
    trip_title = request.form['title']
    trip_destination = request.form['destination']
    trip_theme = request.form['theme']
    trip_start_date = request.form['start_date']
    trip_end_date = request.form['end_date']
    trip_description = request.form['description']
    trip_privacy = request.form['privacy']
    other_friends_emails = request.form['friend_emails']

    #extract info of the person who is creating the trip
    owner_id = session['user_id']
    owner_name = session['name']

    #Check if data is to able to flow from HTML to Flask correctly (testing - can be removed once checked)
    print("New trip has been created")
    print("Trip name: ", trip_title)
    print("Travelling to: ", trip_destination)
    print("Theme of the trip: ", trip_theme)
    print("Starting date: ",trip_start_date)
    print ("Ending date: ", trip_end_date)
    print("Descritption: ", trip_description )
    print("Privacy setting: ", trip_privacy)
    print("Friends to invite: ", other_friends_emails)
    print("Created by: ", owner_name)
    print("Creator ID: ", owner_id)

    #once submitted the form, users will be redirected back to the dashboard
    return redirect('/dashboard')
    # implement logic to create a new trip in the database
    # data = request.json
    # return jsonify({"message": "Trip created successfully", "trip": data})

if __name__ == '__main__':
    app.run(debug=True)
