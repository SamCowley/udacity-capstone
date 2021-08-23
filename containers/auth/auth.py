#!/bin/python3
import auth_service
import flask
from flask_cors import CORS
import os
import waitress

app = flask.Flask(__name__)
CORS(app)
try: app.secret_key = os.environ['session_secret']
except: raise UnboundLocalError('Missing values: session_secret')
auth = auth_service.Auth0(app)

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

@app.route('/token', methods=["POST"])
def token():
    print("Requesting token")
    data = flask.request.get_json()
    username = data['username']
    password = data['password']

    response = auth.token(username, password)
    print(response)
    print(response.content)
    flask.session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }

    token = flask.session
    return flask.Response(flask.json.jsonify(token), status=200)

waitress.serve(app, host='0.0.0.0', port=8080)
