import os
import expenses_service
from functools import wraps
import flask
from flask_cors import CORS
import hashlib
import itsdangerous
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
expenses = expenses_service.Expenses()

def authenticate_token(session):
    print("Validating token", flush=True)
    session_interface = flask.sessions.SecureCookieSessionInterface()
    s = session_interface.get_signing_serializer(app)
    max_age = int(app.permanent_session_lifetime.total_seconds())

    try:
        data = s.loads(session, max_age=max_age)
        uid = data['profile']['user_id']
        print("Authentication success", flush=True)
        return uid
    except:
        print("Authentication failed", flush=True)
        return None

def validate_arguments(*args, **kwargs):
    # Function pointer dictionary for dynamic type casting
    cast = {'int': int, 'float': float, 'str': str}

    for arg in args:
        value = arg[0]
        arg_type = arg[1]
        allow_none = arg[2]

        # Continue if value is None and it's allowed
        if ( value is None or value == "" ) and allow_none:
            continue

        # Check type casting to the correct value causes an error (all values are passed in as strings)
        try:
            cast[arg_type](value)
        except:
            return False
    return True

@app.route('/list', methods=['POST'])
def get_all_reports():
    print("Requesting all reports", flush=True)
    data = flask.request.get_json()

    uid = authenticate_token(data["token"])
    if uid is None:
        return flask.make_response(flask.jsonify({"message": "Invalid token"}, 400))

    reports = expenses.get_all_reports(uid)
    return flask.make_response(flask.jsonify({"data": reports}), 200)

@app.route('/delete', methods=['POST'])
def delete_report():
    print("Requesting delete report", flush=True)
    data = flask.request.get_json()

    uid = authenticate_token(data["token"])
    if uid is None:
        return flask.make_response(flask.jsonify({"message": "Invalid token"}, 400))
    rid = data["rid"]

    if not validate_arguments((rid, 'int', False)):
        return flask.make_response(flask.jsonify({"message": "Invalid parameters"}, 400))

    expenses.delete_report(uid, rid)
    return flask.make_response(flask.jsonify({"message": "Success"}), 200)

@app.route('/update', methods=['POST'])
def update_report():
    print("Requesting update report", flush=True)
    data = flask.request.get_json()

    uid = authenticate_token(data["token"])
    if uid is None:
        return flask.make_response(flask.jsonify({"message": "Invalid token"}, 400))

    rid = data["rid"]
    name = data["name"]

    if not validate_arguments((rid, 'int', False), (name, 'str', False)):
        return flask.make_response(flask.jsonify({"message": "Invalid parameters"}, 400))

    expenses.update_report(uid, rid, name)
    return flask.make_response(flask.jsonify({"message": "Success"}), 200)

@app.route('/create', methods=['POST'])
def create_report():
    print("Requesting create report", flush=True)
    data = flask.request.get_json()

    uid = authenticate_token(data["token"])
    if uid is None:
        return flask.make_response(flask.jsonify({"message": "Invalid token"}, 400))
    name = data["name"]

    if not validate_arguments((name, 'str', False)):
        return flask.make_response(flask.jsonify({"message": "Invalid parameters"}, 400))

    expenses.add_report(uid, name)
    return flask.make_response(flask.jsonify({"message": "Success"}), 201)

@app.route('/expenses/list', methods=['POST'])
def get_report_expenses(rid):
    print("Requesting report expenses", flush=True)
    data = flask.request.get_json()

    uid = authenticate_token(data["token"])
    if uid is None:
        return flask.make_response(flask.jsonify({"message": "Invalid token"}, 400))
    rid = data["rid"]

    if not validate_arguments((rid, 'int', False)):
        return flask.make_response(flask.jsonify({"message": "Invalid parameters"}, 400))

    resp = expenses.get_expenses(uid, rid)
    return flask.make_response(flask.jsonify({"data": resp}), 200)

@app.route('/expenses/delete', methods=['POST'])
def delete_expense():
    print("Requesting delete expense", flush=True)
    data = flask.request.get_json()

    uid = authenticate_token(data["token"])
    if uid is None:
        return flask.make_response(flask.jsonify({"message": "Invalid token"}, 400))
    rid = data["rid"]
    eid = data["eid"]

    if not validate_arguments((rid, 'int', False), (eid, 'int', False)):
        return flask.make_response(flask.jsonify({"message": "Invalid parameters"}, 400))

    expenses.delete_expense(uid, rid, eid)
    return flask.make_response(flask.jsonify({"message": "Success"}), 200)

@app.route('/expenses/update', methods=['POST'])
def update_expense():
    print("Requesting update expense", flush=True)
    data = flask.request.get_json()

    uid = authenticate_token(data["token"])
    if uid is None:
        return flask.make_response(flask.jsonify({"message": "Invalid token"}, 400))
    rid = data["rid"]
    eid = data["eid"]
    description = data['description']
    category = data['category']
    amount = data['amount']
    image = data['image']

    if not validate_arguments((rid, 'int', False),
                              (eid, 'int', False),
                              (description, 'str', False),
                              (category, 'str', True),
                              (amount, 'float', False),
                              (image, 'str', True)):
        return flask.make_response(flask.jsonify({"message": "Invalid parameters"}, 400))

    expenses.update_expense(uid, rid, eid, description, category, amount, image)
    return flask.make_response(flask.jsonify({"message": "Success"}), 200)

@app.route('/expenses/create', methods=['POST'])
def create_expense():
    print("Requesting create expense", flush=True)
    data = flask.request.get_json()

    uid = authenticate_token(data["token"])
    if uid is None:
        return flask.make_response(flask.jsonify({"message": "Invalid token"}, 400))
    rid = data['rid']
    eid = data['eid']

    description = data['description']
    category = data['category']
    amount = data['amount']
    image = data['image']

    if not validate_arguments((rid, 'int', False),
                              (eid, 'int', False),
                              (description, 'str', False),
                              (category, 'str', True),
                              (amount, 'float', False),
                              (image, 'str', True)):
        return flask.make_response(flask.jsonify({"message": "Invalid parameters"}, 400))

    expenses.add_expense(uid, rid, eid, description, category, amount, image)
    return flask.make_response(flask.jsonify({"message": "Success"}), 201)

@app.route('/upload')
def upload_image():
    print("Requesting upload image", flush=True)
    data = flask.request.get_json()

    uid = authenticate_token(data["token"])
    if uid is None:
        return flask.make_response(flask.jsonify({"message": "Invalid token"}, 400))

    return expenses.upload_image()

waitress.serve(app, host='0.0.0.0', port='8080')
