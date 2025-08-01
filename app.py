from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, abort
from werkzeug.utils import secure_filename
import uuid
import os
from auth.auth import auth, login_needed
from DB.DB import DB
from datetime import datetime
from func.emailfn import mass_email
from func.to_ics import convert_to_ics, clear_all_ics
from func.gemini import GeminiYapper

### init connections ###
db = DB() 
planner = GeminiYapper()
#########################

app = Flask(__name__, static_folder = 'static', template_folder = 'templates') # set static and template folders

### USED FOR AUTH DO NOT DELETE ###
app.secret_key = os.urandom(24)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' 
####################################

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
        # print(trips) # debug

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

@app.route('/api/trips/invite/<trip_id>', methods=['POST'])
@login_needed
def invite_friends(trip_id):
    email_list = request.form['friend_emails']
    mass_email(session['name'], 
               db.get_trip_by_id(trip_id)['dest'], 
               db.get_trip_by_id(trip_id)['desc'], 
               email_list, 
               trip_id)
    return redirect(f'/trip/{trip_id}')

@app.route('/denied') #use directly for debug only
def access_denied():
    return render_template('no_access.html', name=session['name'], email=session['email'], picture=session['picture'])

@app.route('/trip/<int:trip_id>')
@login_needed
def view_trip(trip_id):
    trip = db.get_trip_by_id(trip_id)
    if not trip:
        return redirect('/denied')
    
    if not db.user_has_access_to_trip(session['user_id'], trip_id):
        return redirect('/denied')
    
    start_date = datetime.fromisoformat(trip['start_date'].replace('Z', '+00:00'))
    end_date = datetime.fromisoformat(trip['end_date'].replace('Z', '+00:00'))
    trip['formatted_start'] = start_date.strftime('%b %d, %Y')
    trip['formatted_end'] = end_date.strftime('%b %d, %Y')
    
    locations = db.get_trip_locations(trip_id, session['user_id']) # O(n)
    itinerary = db.get_trip_itinerary(trip_id) # O(n)
    logs = db.get_trip_page_activities(trip_id) # O(n)
    conflicts = db.get_trip_conflicts(trip_id) # O(n^2)
    users = db.get_list_of_users_in_trip(trip_id = trip_id) # O(n)

    # print(f"\ntrip: {trip}, \n\nlocations: {locations}, \n\nitinerary: {itinerary}, \n\nlogs: {logs}, \n\nconflicts: {conflicts}, \n\nusers: {users}")

    try:
        return render_template('trips.html',
                            trip=trip,
                            locations=locations,
                            itinerary=itinerary,
                            logs=logs,
                            conflicts=conflicts,
                            users=users,
                            name=session['name'],
                            email=session['email'],
                            picture=session['picture'])
    except Exception as e:
        print(f"error in viewing trip: {e}")
        return render_template('no_access.html', error_msg = e, name=session['name'], email=session['email'], picture=session['picture'])

@app.route('/api/locations', methods=['POST'])
@login_needed
def add_location():
    try:
        data = request.get_json()

        trip_id = data['trip_id']
        name = data['name']
        category = data['category']
        description = data['description']
        start_date = data['start_date']
        end_date = data['end_date']
        start_time = data['start_time']
        end_time = data['end_time']
        lat = data.get('lat')
        lng = data.get('lng')

        location_id = db.add_location(
            trip_id=trip_id,
            name=name,
            category=category,
            description=description,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            user=session['name'],
            lat=lat,
            lng=lng
        )

        print("Location ID created:", location_id) 

        if location_id:
            email_list = db.get_list_of_users_in_trip(trip_id=trip_id, ver=1)
            action = f"A new location '{name}' has been added to the trip."
            trip = db.get_trip_by_id(trip_id)

            mass_email(session['name'], trip['dest'], trip['desc'], email_list, trip_id, action=action, ver=1)
            
            # Return the location data that the frontend need
            location_data = {
                'id': location_id,
                'name': name,
                'category': category,
                'description': description,
                'start_date': start_date,
                'end_date': end_date,
                'start_time': start_time,
                'end_time': end_time,
                'suggested_by': session['name'],
                'lat': lat,
                'lng': lng,
                'trip_id': trip_id
            }
            
            return jsonify({
                'success': True, 
                'location': location_data,
                'message': 'Location added successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to add location'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})
    
@app.route('/<int:trip_id>/remove/<int:location_id>', methods=['POST', 'GET'])
@login_needed
def remove_location(trip_id, location_id):
    # print(f"Removing location with ID: {location_id} from trip {trip_id}")
    result = db.remove_location(
        location_id=location_id,
        username=session['name']
    )
    email_list = db.get_list_of_users_in_trip(trip_id=trip_id, ver=1)
    locName = db.get_trip_location_by_id(location_id=location_id)
    action = f"The location '{locName}' has been removed from the trip by {session['name']}."
    trip = db.get_trip_by_id(trip_id)

    if result:
        mass_email(session['name'], trip['dest'], trip['desc'], email_list, trip_id, action=action, ver=1)
        return redirect(f'/trip/{trip_id}') 
    else:
        return jsonify({'success': False, 'message': 'Failed to remove location'})

### not yet functional
@app.route('/<int:trip_id>/vote/<int:location_id>', methods=['POST'])
@login_needed
def vote_location(trip_id, location_id):
    # data = request.get_json()
    
    result = db.upvote_on_location(
        location_id=location_id,
        user_id=session['user_id']
    )

    # print(result)
    
    if result:
        return redirect(f'/trip/{trip_id}')
    else:
        return redirect(f'/trip/{trip_id}')

@app.route('/download/<int:trip_id>', methods=['GET'])
@login_needed
def download_file(trip_id):
    itinerary = db.get_trip_itinerary(trip_id)
    download_fname = convert_to_ics(itinerary, username=session['name'])
    print(f"\n\n\nfname: {download_fname}\n\n\n")
    try:
        return send_file(download_fname, as_attachment=True)
    except Exception as e:
        print(f"Error: {e}")
        abort(404)

@app.route('/<int:trip_id>/leave', methods=['POST'])
@login_needed
def leave_trip(trip_id):
    google_id = session['user_id']
    result = db.remove_user_from_trip(google_id, trip_id)
    return redirect('/dashboard')

### commenting feature

@app.route('/api/activities/<int:loc_id>/comments', methods=['POST'])
@login_needed
def add_comment(loc_id):
    data = request.get_json()
    comment = data['comment']
    username = session['name']

    if not comment:
        return jsonify({'success': False, 'message': 'Comment cannot be empty'})

    result = db.add_comment_to_location(
        location_id=loc_id,
        comment=comment,
        username=username
    )

    if result:
        return jsonify({'success': True, 'message': 'Comment added successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to add comment'})
    
@app.route('/api/activities/<int:loc_id>/comments', methods=['GET'])
@login_needed
def get_comments(loc_id):
    comments = db.get_comments_for_location(loc_id)
    # print(comments)
    # print(jsonify(comments))
    return jsonify(comments)

@app.route('/api/chat/start', methods=['POST'])
@login_needed
def start_chat():
    try:
        data = request.get_json()
        trip_id = data.get('trip_id')
        location = data.get('location', 'your destination')
                
        if 'chat_instances' not in session:
            session['chat_instances'] = {}
        
        welcome_message = planner.start(location)
        
        session['chat_instances'][trip_id] = True
        
        return jsonify({
            'success': True,
            'message': welcome_message
        })
        
    except Exception as e:
        print(f"Error starting chat: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to start chat'
        })

@app.route('/api/chat/reply', methods=['POST'])
@login_needed
def chat_reply():
    try:
        data = request.get_json()
        trip_id = data.get('trip_id')
        location = data.get('location', 'your destination')
        chat_history = data.get('chat_history', [])
                
        response = planner.reply(chat_history, location)
        
        return jsonify({
            'success': True,
            'message': response
        })
        
    except Exception as e:
        print(f"Error in chat reply: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get response'
        })

@app.route('/<int:trip_id>/edit', methods=['GET', 'POST'])
@login_needed
def edit_trip(trip_id):
    trip = db.get_trip_by_id(trip_id)
    if not trip:
        return redirect('/denied')
    if not db.user_has_access_to_trip(session['user_id'], trip_id):
        return redirect('/denied')

    data = request.form
    updated_trip = {
        'dest': data['destination'],
        'theme': data['theme'],
        'start_date': data['start_date'],
        'end_date': data['end_date'],
        'desc': data['description'],
    }

    # print(f"updated_trip: {updated_trip}")
    db.edit_trip(updated_trip, trip_id)

    return redirect(f'/trip/{trip_id}')

if __name__ == '__main__':
    clear_all_ics()
    app.run(debug=True)
