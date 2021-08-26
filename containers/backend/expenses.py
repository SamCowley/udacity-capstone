import os
import expenses_service
import flask
from flask_cors import CORS
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

def auth_fail():
    return flask.make_response(flask.jsonify({"message": "Invalid token"}, 400))

def param_fail():
    return flask.make_response(flask.jsonify({"message": "Invalid parameters"}, 400))

@app.route('/list', methods=['POST'])
def get_all_reports():
    print("Requesting all reports", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ReportItem(app, data)
    if not item.validate_token(): return auth_fail()
    if not item.validate_list():  return param_fail()
    reports = expenses.get_all_reports(item)

    return flask.make_response(flask.jsonify({"data": reports}), 200)

@app.route('/delete', methods=['POST'])
def delete_report():
    print("Requesting delete report", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ReportItem(app, data)
    if not item.validate_token():  return auth_fail()
    if not item.validate_delete(): return param_fail()
    expenses.delete_report(item)

    return flask.make_response(flask.jsonify({"message": "Success"}), 200)

@app.route('/update', methods=['POST'])
def update_report():
    print("Requesting update report", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ReportItem(app, data)
    if not item.validate_token():  return auth_fail()
    if not item.validate_update(): return param_fail()
    expenses.update_report(item)

    return flask.make_response(flask.jsonify({"message": "Success"}), 200)

@app.route('/create', methods=['POST'])
def create_report():
    print("Requesting create report", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ReportItem(app, data)
    if not item.validate_token():  return auth_fail()
    if not item.validate_create(): return param_fail()
    expenses.add_report(item)
    return flask.make_response(flask.jsonify({"message": "Success"}), 201)

@app.route('/expenses/list', methods=['POST'])
def get_report_expenses():
    print("Requesting report expenses", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token(): return auth_fail()
    if not item.validate_list():  return param_fail()
    resp = expenses.get_expenses(item)

    return flask.make_response(flask.jsonify({"data": resp}), 200)

@app.route('/expenses/delete', methods=['POST'])
def delete_expense():
    print("Requesting delete expense", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token():  return auth_fail()
    if not item.validate_delete(): return param_fail()
    expenses.delete_expense(item)

    return flask.make_response(flask.jsonify({"message": "Success"}), 200)

@app.route('/expenses/update', methods=['POST'])
def update_expense():
    print("Requesting update expense", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token():  return auth_fail()
    if not item.validate_update(): return param_fail()
    expenses.update_expense(item)

    return flask.make_response(flask.jsonify({"message": "Success"}), 200)

@app.route('/expenses/create', methods=['POST'])
def create_expense():
    print("Requesting create expense", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token():  return auth_fail()
    if not item.validate_create(): return param_fail()
    expenses.add_expense(item)

    return flask.make_response(flask.jsonify({"message": "Success"}), 201)

@app.route('/expenses/upload', methods=['POST'])
def create_expense():
    print("Requesting create expense", flush=True)

    data = flask.args.get('metadata')
    print(str(data))
    files = flask.request.files
    print(files)
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token():  return auth_fail()
    if not item.validate_upload(): return param_fail()
    expenses.upload_expense(item)

    return flask.make_response(flask.jsonify({"message": "Success"}), 201)

waitress.serve(app, host='0.0.0.0', port='8080')
