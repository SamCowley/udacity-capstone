#!/bin/python3
import auth_service
import flask
import os
import waitress

app = flask.Flask(__name__)
try: app.secret_key = os.environ['session_secret']
except: raise UnboundLocalError('Missing values: session_secret')
auth = auth_service.Auth0(app)

@app.route('/login')
def login():
    return auth.login()

@app.route('/api/v0/auth/callback')
def callback():
    userinfo = auth.callback()
    flask.session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return flask.redirect('/')

@app.route('/logout')
def logout():
    flask.session.clear()

@app.route('/token', methods=["POST"])
def token():
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

waitress.serve(app, host='127.0.0.1', port=8080)
