from flask_cors import CORS
import expenses_service
import flask
import json
import os
import uuid
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

def return_status(code, message = None):
    if code == 200:
        if message is None: message = "Success"
        return flask.make_response(flask.jsonify({"message": message}), 200)
    if code == 201:
        if message is None: message = "Created"
        return flask.make_response(flask.jsonify({"message": message}), 201)
    if code == 400:
        if message is None: message = "Invalid parameters"
        return flask.make_response(flask.jsonify({"message": message}), 400)
    if code == 401:
        if message is None: message = "Invalid token"
        return flask.make_response(flask.jsonify({"message": message}), 401)
    if code == 404:
        if message is None: message = "Not found"
        return flask.make_response(flask.jsonify({"message": message}), 404)
    if code == 405:
        if message is None: message = "Method not allowed"
        return flask.make_response(flask.jsonify({"message": message}), 405)
    if code == 500:
        if message is None: message = "Internal server error"
        return flask.make_response(flask.jsonify({"message": message}), 405)

@app.route('/list', methods=['POST'])
def get_all_reports():
    print("Requesting all reports", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ReportItem(app, data)
    if not item.validate_token(): return return_status(401)
    if not item.validate_list():  return return_status(400)
    reports = expenses.get_all_reports(item)

    return flask.make_response(flask.jsonify({"data": reports}), 200)

@app.route('/delete', methods=['POST'])
def delete_report():
    print("Requesting delete report", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ReportItem(app, data)
    if not item.validate_token():  return return_status(401)
    if not item.validate_delete(): return return_status(400)
    expenses.delete_report(item)

    return return_status(200)

@app.route('/update', methods=['POST'])
def update_report():
    print("Requesting update report", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ReportItem(app, data)
    if not item.validate_token():  return return_status(401)
    if not item.validate_update(): return return_status(400)
    expenses.update_report(item)

    return return_status(200)

@app.route('/create', methods=['POST'])
def create_report():
    print("Requesting create report", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ReportItem(app, data)
    if not item.validate_token():  return return_status(401)
    if not item.validate_create(): return return_status(400)
    expenses.add_report(item)

    return return_status(201)

@app.route('/expenses/list', methods=['POST'])
def get_report_expenses():
    print("Requesting report expenses", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token(): return return_status(401)
    if not item.validate_list():  return return_status(400)
    resp = expenses.get_expenses(item)

    return flask.make_response(flask.jsonify({"data": resp}), 200)

@app.route('/expenses/delete', methods=['POST'])
def delete_expense():
    print("Requesting delete expense", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token():  return return_status(401)
    if not item.validate_delete(): return return_status(400)
    expenses.delete_expense(item)

    return return_status(200)

@app.route('/expenses/update', methods=['POST'])
def update_expense():
    print("Requesting update expense", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token():  return return_status(401)
    if not item.validate_update(): return return_status(400)
    expenses.update_expense(item)

    return return_status(200)

@app.route('/expenses/create', methods=['POST'])
def create_expense():
    print("Requesting create expense", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token():  return return_status(401)
    if not item.validate_create(): return return_status(400)
    expenses.add_expense(item)

    return return_status(201)

@app.route('/file/upload', methods=['POST'])
def upload_image():
    print("Requesting create expense", flush=True)

    data = json.loads(flask.request.form.get('metadata'))
    file = flask.request.files['file']
    file_path = '/tmp/' + uuid.uuid4().hex + '.' + file.content_type.replace('/', ':')
    file.save(file_path)
    item = expenses_service.ExpenseItem(app, data, file_path)
    if not item.validate_token():  return return_status(401)
    if not item.validate_upload(): return return_status(400)
    rc = expenses.upload_image(item)

    return return_status(rc[0])

@app.route('/file/download', methods=['POST'])
def download_image():
    print("Requesting download image", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token():    return return_status(401)
    if not item.validate_download(): return return_status(400)
    rc = expenses.download_image(item)

    if (rc[0] == 200):
        @flask.after_this_request
        def remove_file(response):
            try:
                os.remove(rc[1])
            except:
                pass
            return response

        download_name = item.image + '.img'
        if ':' in rc[2]:
            download_name = item.image + '.' + rc[2].split(':')[1]
        
        return flask.send_file(rc[1], rc[2].replace(':', '/'), True, download_name)
    return return_status(rc[0])

@app.route('/file/delete', methods=['POST'])
def delete_image():
    print("Requesting download image", flush=True)

    data = flask.request.get_json()
    item = expenses_service.ExpenseItem(app, data)
    if not item.validate_token():        return return_status(401)
    if not item.validate_delete_image(): return return_status(400)
    rc = expenses.delete_image(item)

    return return_status(rc[0])

waitress.serve(app, host='0.0.0.0', port='8080')
