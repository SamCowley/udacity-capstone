#!/bin/python3
import auth_service
import flask
from flask_cors import CORS
import os
import waitress

app = flask.Flask(__name__)
# Allow client side scripts to read the session cookie
app.config['SESSION_COOKIE_HTTPONLY'] = False
# Allow CORS requests
CORS(app)

# Get PSK
try: app.secret_key = os.environ['session_secret']
except: raise UnboundLocalError('Missing values: session_secret')

# Service
auth = auth_service.Auth0(app)

@app.route('/login')
def login():
    print("Requesting login", flush=True)
    return auth.login()

@app.route('/callback')
def callback():
    print("Requesting callback", flush=True)
    userinfo = auth.callback()
    flask.session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return flask.redirect('/')

@app.route('/logout')
def logout():
    print("Requesting logout", flush=True)
    flask.session.clear()
    return flask.redirect('/')

waitress.serve(app, host='0.0.0.0', port=8080, threads=18)

