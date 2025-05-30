from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import uuid
import os
from auth.auth import auth, login_required
from DB.DB import DB
from datetime import datetime
from func.emailfn import mass_email
from func.misc import allowed_file

db = DB()  # initialise connection to supabase
app = Flask(__name__, static_folder = 'static', template_folder = 'templates') # set static and template folders

app.secret_key = os.urandom(24) #key for sess
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # development only
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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

@app.route('/dashboard')
@login_required
def dashboard():
    # want to check if the user has a trip invitation
    if 'trip_inv' in session:
        db.add_user_to_trip(session['user_id'], session['trip_inv'])  # add user to trip
        print(f"User {session['user_id']} added to trip: ", session['trip_inv'])
        del session['trip_inv']

    trips = db.get_all_trips_for_user(session['user_id'])

    for trip in trips:
        start_date = datetime.fromisoformat(trip['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(trip['end_date'].replace('Z', '+00:00'))
        trip['formatted_start'] = start_date.strftime('%b %d, %Y')
        trip['formatted_end'] = end_date.strftime('%b %d, %Y')
    
    return render_template('dashboard.html', 
                          name=session['name'], 
                          email=session['email'],
                          picture=session['picture'],
                          trips=trips)


@app.route('/join/<trip_id>', methods=['GET','POST'])
def accept_invite(trip_id):
    session['trip_inv'] = trip_id
    return redirect('/auth/login')

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
    print("Description: ", trip_description )
    print("Privacy setting: ", trip_privacy)
    print("Friends to invite: ", other_friends_emails)
    print("Created by: ", owner_name)
    print("Creator ID: ", owner_id)
    
    trip_id = db.add_trip(
        google_id=owner_id,
        trip_name=trip_title,
        dest=trip_destination,
        theme=trip_theme,
        start_date=trip_start_date,
        end_date=trip_end_date,
        desc=trip_description,
        privacy=trip_privacy
    )

    if other_friends_emails:
        mass_email(owner_name, trip_destination, trip_description, other_friends_emails, trip_id)

    #once submitted the form, users will be redirected back to the dashboard
    return redirect('/dashboard')


if __name__ == '__main__':
    app.run(debug=True)
