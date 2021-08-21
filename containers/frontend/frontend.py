#!/bin/python3
import flask
import requests
import waitress
import os

app = flask.Flask(__name__)
try: app.secret_key = os.environ['session_secret']
except: raise UnboundLocalError('Missing values: session_secret')

@app.route('/')
def dashboard():
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
    
    return flask.render_template('index.html', logged_in=logged_in, reports=reports)

@app.route('/<report_id>')
def expenses(rid):
    logged_in = 'profile' in flask.session
    return flask.render_template('report.html', logged_in=logged_in)

waitress.serve(app, host='0.0.0.0', port=8080)
