#!/bin/python3
import auth_service
import flask
from flask_cors import CORS
import os
import waitress
from itsdangerous import Signer

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
signer = Signer(os.environ['session_secret'])

@app.route('/login')
def login():
    print("Requesting login")
    return auth.login()

@app.route('/callback')
def callback():
    print("Requesting callback")
    userinfo = auth.callback()
    flask.session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return flask.redirect('/')

@app.route('/logout')
def logout():
    print("Requesting logout")
    flask.session.clear()
    return flask.redirect('/')

#@app.route('/token')
#def token():
#    print("Requesting token")
#    if 'profile' not in flask.session:
#        return flask.make_response(flask.jsonify({"message": "Login Required"}, 400))
#    token = str(signer.sign(flask.session['profile']['user_id']))
#    return flask.make_response(flask.jsonify({"token": token}, 200)

waitress.serve(app, host='0.0.0.0', port=8080, threads=18)

