import os
import expenses_service
from functools import wraps
import flask
from flask_cors import CORS
import waitress

app = flask.Flask(__name__)
CORS(app)
try: app.secret_key = os.environ['session_secret']
except: raise UnboundLocalError('Missing values: session_secret')
expenses = expenses_service.Expenses()

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in flask.session:
            return flask.abort('401', 'Login required')
        else:
            f(*args, **kwargs)
    return decorated

def validate_arguments(*args, **kwargs):
    # Function pointer dictionary for dynamic type casting
    cast = {'int': int, 'float': float, 'str': str}

    for arg in args:
        value = arg[0]
        arg_type = arg[1]
        allow_none = arg[2]

        # Continue if value is None and it's allowed
        if value is None and allow_none:
            continue

        # Check type casting to the correct value causes an error (all values are passed in as strings)
        try:
            cast[arg_type](value)
        except:
            return False
    return True

@app.route('/report/list', methods=['POST'])
@requires_auth
def get_all_reports():
    uid = flask.session['profile']['user_id']
    reports = expenses.get_all_reports(uid)

    return flask.Response(flask.json.jsonify(reports), status=200)

@app.route('/report/delete', methods=['POST'])
@requires_auth
def delete_report():
    uid = flask.session['profile']['user_id']
    rid = flask.request.args.get('rid')

    if not validate_arguments((rid, 'int', False)):
        return flask.Response(flask.json.jsonify({"message": "Invalid parameters"}, status=400))

    expenses.delete_report(uid, rid)
    return flask.Response(status=200)

@app.route('/report/update', methods=['POST'])
@requires_auth
def update_report():
    uid = flask.session['profile']['user_id']
    rid = flask.request.args.get('rid')
    name = flask.request.args.get('name')

    if not validate_arguments((rid, 'int', False), (name, 'str', False)):
        return flask.Response(flask.json.jsonify({"message": "Invalid parameters"}, status=400))

    expenses.update_report(uid, rid, name)
    return flask.Response(status=200)

@app.route('/report/create', methods=['POST'])
@requires_auth
def create_report():
    uid = flask.session['profile']['user_id']
    name = flask.request.args.get('name')

    if not validate_arguments((name, 'str', False)):
        return flask.Response(flask.json.jsonify({"message": "Invalid parameters"}, status=400))

    expenses.add_report(uid, name)
    return flask.Response(status=201)

@app.route('/expenses/list', methods=['POST'])
@requires_auth
def get_report_expenses(rid):
    uid = flask.session['profile']['user_id']
    rid = flask.request.args.get('rid')

    if not validate_arguments((rid, 'int', False)):
        return flask.Response(flask.json.jsonify({"message": "Invalid parameters"}, status=400))

    resp = expenses.get_expenses(uid, rid)
    return flask.Response(flask.json.jsonify(resp), status=200)

@app.route('/expenses/delete', methods=['POST'])
@requires_auth
def delete_expense():
    uid = flask.session['profile']['user_id']
    rid = flask.request.args.get('rid')
    eid = flask.request.args.get('eid')

    if not validate_arguments((rid, 'int', False), (eid, 'int', False)):
        return flask.Response(flask.json.jsonify({"message": "Invalid parameters"}, status=400))

    expenses.delete_expense(uid, rid, eid)
    return flask.Response(status=200)

@app.route('/expenses/update', methods=['POST'])
@requires_auth
def update_expense():
    uid = flask.session['profile']['user_id']
    rid = flask.request.args.get('rid')
    eid = flask.request.args.get('eid')
    description = flask.request.args.get('description')
    category = flask.request.args.get('category')
    amount = flask.request.args.get('amount')
    image = flask.request.args.get('image')

    if not validate_arguments((rid, 'int', False),
                              (eid, 'int', False),
                              (description, 'str', False),
                              (category, 'str', True),
                              (amount, 'float', False),
                              (image, 'str', True)):
        return flask.Response(flask.json.jsonify({"message": "Invalid parameters"}, status=400))

    expenses.update_expense(uid, rid, eid, description, category, amount, image)
    return flask.Response(status=200)

@app.route('/expenses/create', methods=['POST'])
@requires_auth
def create_expense():
    uid = flask.session['profile']['user_id']
    rid = flask.request.args.get('rid')
    eid = flask.request.args.get('eid')
    description = flask.request.args.get('description')
    category = flask.request.args.get('category')
    amount = flask.request.args.get('amount')
    image = flask.request.args.get('image')

    if not validate_arguments((rid, 'int', False),
                              (eid, 'int', False),
                              (description, 'str', False),
                              (category, 'str', True),
                              (amount, 'float', False),
                              (image, 'str', True)):
        return flask.Response(flask.json.jsonify({"message": "Invalid parameters"}, status=400))

    expenses.add_expense(uid, rid, eid, description, category, amount, image)
    return flask.Response(status=201)

@app.route('/upload')
@requires_auth
def upload_image():
    return expenses.upload_image()

waitress.serve(app, host='0.0.0.0', port='8080')
