from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from auth.auth import auth, login_required

app = Flask(__name__,
    static_folder='static',
    template_folder='templates')

# Set secret key for session
app.secret_key = os.urandom(24)
# For development only
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Register the auth blueprint
app.register_blueprint(auth, url_prefix='/auth')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create-trip')
@login_required
def create_trip():
    return render_template('create_trip.html', 
                          name=session['name'], 
                          email=session['email'],
                          picture=session['picture'])

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', 
                          name=session['name'], 
                          email=session['email'],
                          picture=session['picture'])

@app.route('/api/trips', methods=['GET'])
def get_trips():
    return jsonify({"trips": []})

@app.route('/api/trips', methods=['POST'])
def create_trip_api():
    data = request.json
    return jsonify({"message": "Trip created successfully", "trip": data})

if __name__ == '__main__':
    app.run(debug=True)
