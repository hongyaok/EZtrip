from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from config import ClientID, ClientSecret
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests

app = Flask(__name__,
    static_folder='static',
    template_folder='templates')

# Set up session
app.secret_key = os.urandom(24)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html', client_id=ClientID)

@app.route('/google_login')
def google_login():
    # Create flow instance to manage OAuth 2.0 process
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": ClientID,
                "client_secret": ClientSecret,
                "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ]
    )
    
    # Set redirect URI
    flow.redirect_uri = url_for('callback', _external=True)
    
    # Generate URL for request to Google's OAuth 2.0 server
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='select_account',
        include_granted_scopes='true'
    )
    
    # Store state in session
    session['state'] = state
    
    # Redirect to Google's OAuth 2.0 server
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    # Retrieve state from session
    state = session['state']
    
    # Create flow with the same parameters as in google_login
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": ClientID,
                "client_secret": ClientSecret,
                "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ],
        state=state
    )
    
    flow.redirect_uri = url_for('callback', _external=True)
    
    # Use the authorization server's response to fetch tokens
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    # Get credentials and ID token
    credentials = flow.credentials
    
    # Verify ID token
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=google_auth_requests.Request(),
        audience=ClientID
    )
    
    # Store user info in session
    session['user_id'] = id_info.get('sub')
    session['name'] = id_info.get('name')
    session['email'] = id_info.get('email')
    session['picture'] = id_info.get('picture')
    
    # Redirect to dashboard
    return redirect(url_for('dashboard'))

@app.route('/create-trip')
def create_trip():
    return "Create Trip Form - To be implemented"

@app.route('/dashboard')
def dashboard():
    print(session) #debug
    # Check if user is logged in
    if 'name' not in session:
        return redirect(url_for('login'))
    
    # Return dashboard with user info
    return render_template('dashboard.html', 
                          name=session['name'], 
                          email=session['email'],
                          picture=session['picture'])

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('home'))

@app.route('/api/trips', methods=['GET'])
def get_trips():
    return jsonify({"trips": []})

@app.route('/api/trips', methods=['POST'])
def create_trip_api():
    data = request.json
    return jsonify({"message": "Trip created successfully", "trip": data})

if __name__ == '__main__':
    app.run(debug=True)
