from flask import Blueprint, render_template, redirect, url_for, session, request
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
from functools import wraps
from auth.config import ClientID, ClientSecret
from DB.DB import DB

# Create blueprint
auth = Blueprint('auth', __name__, template_folder='templates')
db = DB()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login')
def login():
    return render_template('login.html', client_id=ClientID)

@auth.route('/google_login')
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
    flow.redirect_uri = url_for('auth.callback', _external=True)
    
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

@auth.route('/callback')
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
    
    flow.redirect_uri = url_for('auth.callback', _external=True)
    
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
    print(f"User ID: {session['user_id']}, Name: {session['name']}, Email: {session['email']}")
    
    if db.check_user(session['user_id']):
        print("User already exists in the database.")
    else:
        db.add_user(session['user_id'], session['name'], session['email'], session['picture'])
        print("New user detected, proceed with registration.")
    
    return redirect(url_for('dashboard'))

@auth.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('home'))
