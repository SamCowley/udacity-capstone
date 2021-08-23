#!/bin/python3
import flask
from flask_cors import CORS
import requests
import waitress
import os

app = flask.Flask(__name__)
CORS(app)
try: app.secret_key = os.environ['session_secret']
except: raise UnboundLocalError('Missing values: session_secret')

@app.route('/')
def dashboard():
    print("Requesting dashboard")
    logged_in = 'profile' in flask.session
    reports = ['a']
    url = flask.request.url_root + "/api/v0/report/list"
    data = ''
    try:
        resp = requests.get(url = url)
        if resp.ok:
            data = resp.json()
    except:
        pass
    
    print("Returning dashboard rendering")
    return flask.render_template('index.html', logged_in=logged_in, reports=reports)

@app.route('/report/<report_id>')
def expenses(report_id):
    print("Requesting report: " + report_id)
    logged_in = 'profile' in flask.session
    print("Rendering report: " + report_id)
    return flask.render_template('report.html', logged_in=logged_in)

waitress.serve(app, host='0.0.0.0', port=8080, threads=18)
