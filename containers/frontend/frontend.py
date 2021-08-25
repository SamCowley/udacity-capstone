#!/bin/python3
import flask
from flask_cors import CORS
import requests
import waitress
import os

app = flask.Flask(__name__)
# Allow client side scripts to read the session cookie
app.config['SESSION_COOKIE_HTTPONLY'] = False
# Allow CORS requests
CORS(app)

# Get PSK
try: app.secret_key = os.environ['session_secret']
except: raise UnboundLocalError('Missing values: session_secret')

@app.route('/')
def dashboard():
    print("Requesting dashboard", flush=True)
    logged_in = 'profile' in flask.session
    reports = []
    username = ''
    if logged_in:
        username = flask.session['profile']['name']
    
    print("Returning dashboard rendering", flush=True)
    return flask.render_template(
        'index.html',
        logged_in=logged_in,
        username=username)

@app.route('/report/<report_id>')
def expenses(report_id):
    print("Requesting report: " + report_id, flush=True)
    logged_in = 'profile' in flask.session
    print("Rendering report: " + report_id, flush=True)
    return flask.render_template('report.html', logged_in=logged_in)

waitress.serve(app, host='0.0.0.0', port=8080, threads=18)
