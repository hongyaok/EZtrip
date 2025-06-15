from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import uuid
import os
from auth.auth import auth, login_needed
from DB.DB import DB
from datetime import datetime
from func.emailfn import mass_email

db = DB() 
app = Flask(__name__, static_folder = 'static', template_folder = 'templates') # set static and template folders

app.secret_key = os.urandom(24) #key for sess
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # use for development

app.register_blueprint(auth, url_prefix='/auth') # register the auth blueprint

@app.route('/') # when href '/' is called in html
def home():
    return render_template('index.html')

@app.route('/create-trip') # when href '/create-trip' is called in html
@login_needed # ensure user is logged in
def create_trip():
    return render_template('create_trip.html', 
                          name=session['name'], 
                          email=session['email'],
                          picture=session['picture'])

@app.route('/dashboard')
@login_needed
def dashboard():
    try:
        # want to check if the user has a trip invitation
        if 'trip_inv' in session:
            db.add_user_to_trip(session['user_id'], session['trip_inv'])  # add user to trip
            print(f"User {session['user_id']} added to trip: ", session['trip_inv'])
            del session['trip_inv']

        trips = db.get_all_trips_for_user(session['user_id'])

        for trip in trips:
            start_date =datetime.fromisoformat(trip['start_date'].replace('Z', '+00:00'))
            end_date =datetime.fromisoformat(trip['end_date'].replace('Z', '+00:00'))
            trip['formatted_start'] = start_date.strftime('%b %d, %Y')
            trip['formatted_end'] = end_date.strftime('%b %d, %Y')
        
        return render_template('dashboard.html',name=session['name'],email=session['email'],picture=session['picture'],trips=trips)
    except Exception as e:
        print(f"Error in dashboard: {e}") # debug
        return render_template('index.html')


@app.route('/join/<trip_id>', methods=['GET','POST'])
def accept_invite(trip_id): # user should be coming from an email link...
    session['trip_inv'] = trip_id
    return redirect('/auth/login') # this should bring user to login -> then dashboard

@app.route('/api/trips', methods=['POST'])
@login_needed
def create_trip_api():
    #extract out the info from the form 
    trip_title=request.form['title']
    trip_destination=request.form['destination']
    trip_theme= request.form['theme']
    trip_start_date=request.form['start_date']
    trip_end_date=request.form['end_date']
    trip_description=request.form['description']
    trip_privacy= request.form['privacy']
    other_friends_emails=request.form['friend_emails']


    #extract info of the person who is creating the trip
    owner_id =session['user_id']
    owner_name =session['name']

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
    
    trip_id=db.add_trip(
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


### BUGGY CODE BELOW - NEEDS TO BE FIXED ###
# @ weng mun plz help fix
@app.route('/trip/<int:trip_id>')
@login_needed
def view_trip(trip_id):
    trip = db.get_trip_by_id(trip_id)
    print(trip)
    if not trip:
        return redirect('/dashboard')
    
    if not db.user_has_access_to_trip(session['user_id'], trip_id):
        return redirect('/dashboard')
    
    start_date = datetime.fromisoformat(trip['start_date'].replace('Z', '+00:00'))
    end_date = datetime.fromisoformat(trip['end_date'].replace('Z', '+00:00'))
    trip['formatted_start'] = start_date.strftime('%b %d, %Y')
    trip['formatted_end'] = end_date.strftime('%b %d, %Y')
    
    locations = db.get_trip_locations(trip_id, session['user_id'])
    
    itinerary = db.get_trip_itinerary(trip_id)
    if not itinerary:
        itinerary = []
    print(itinerary)
    
    return render_template('trips.html',
                         trip=trip,
                         locations=locations,
                         itinerary=itinerary,
                         name=session['name'],
                         email=session['email'],
                         picture=session['picture'])

@app.route('/api/locations', methods=['POST'])
@login_needed
def add_location():
    data = request.get_json()
    
    location_id = db.add_location(
        trip_id=data['trip_id'],
        name=data['name'],
        description=data['description'],
        category=data['category'],
        lat=data['lat'],
        lng=data['lng'],
        address=data['address'],
        suggested_by=session['user_id']
    )
    
    if location_id:
        return jsonify({'success': True, 'location_id': location_id})
    else:
        return jsonify({'success': False, 'message': 'Failed to add location'})

@app.route('/api/vote', methods=['POST'])
@login_needed
def vote_location():
    data = request.get_json()
    
    result = db.vote_on_location(
        location_id=data['location_id'],
        user_id=session['user_id'],
        vote_type=data['vote_type']
    )

    print(result)
    
    if result:
        return jsonify({
            'success': True,
            'upvotes': result['upvotes'],
            'downvotes': result['downvotes'],
            'user_vote': result['user_vote']
        })
    else:
        return jsonify({'success': False})

@app.route('/api/itinerary/add', methods=['POST'])
@login_needed
def add_to_itinerary():
    data =request.get_json()
    
    success =db.add_location_to_itinerary(
        location_id=data['location_id'],
        trip_id=data['trip_id']
    )

    print(success)

    
### END OF BUGGY CODE ###


if __name__ == '__main__':
    app.run(debug=True)
