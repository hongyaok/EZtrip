from flask import Blueprint, render_template, redirect, url_for, session, request
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
from functools import wraps
from auth.config import ClientID, ClientSecret
# from DB.DB import DB

auth = Blueprint('auth', __name__, template_folder='templates') # set template folder for auth blueprint/html
# db = DB() # initialise connection to supabase

def login_required(f): 
    @wraps(f)
    # checks if a user if logged in
    # if yes, continue to stated page
    # else redirect to login page
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs) # calls the original function below where the @ is placed
    return decorated_function

@auth.route('/login') # when href '/login' is called in html
def login():
    return render_template('login.html', client_id=ClientID)

@auth.route('/google_login')
def google_login():
    # set up flow for google auth
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
    
    flow.redirect_uri = url_for('auth.callback', _external=True) # call callback function after auth
    # the will call for /auth/callback
    
    
    authorization_url, state = flow.authorization_url(   # url for request to Google's OAuth 2.0 server
        access_type='offline',
        prompt='select_account',
        include_granted_scopes='true'
    )
    
    session['state'] = state # store info in state
    
    return redirect(authorization_url) #sends the user to the authorization URL (by google)

@auth.route('/callback') # after 'returning' from google auth page
def callback():
    # Retrieve state from session
    state = session['state']
    
    flow = Flow.from_client_config( # create a flow like above
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
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = flow.credentials # get credentials from flow
    
    id_info = id_token.verify_oauth2_token(   # make sure id is valid
        id_token=credentials._id_token,
        request=google_auth_requests.Request(),
        audience=ClientID
    )
    
    # store user info in session
    session['user_id'] = id_info.get('sub')
    session['name'] = id_info.get('name')
    session['email'] = id_info.get('email')
    session['picture'] = id_info.get('picture')
    print(f"User ID: {session['user_id']}, Name: {session['name']}, Email: {session['email']}")
    
    # to add new user to USERS table
    # if db.check_user(session['user_id']):
    #     print("User already exists in the database.")
    # else:
    #     db.add_user(session['user_id'], session['name'], session['email'], session['picture'])
    #     print("New user detected, proceed with registration.")
    
    return redirect(url_for('dashboard'))

@auth.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('home')) # calls home function in app.py
