import boto3
import flask
import os
import psycopg2

class RequestItem:
    def __init__(self, app):
        self.app = app
        self.uid = ''

    def validate_token(self):
        print("Validating token", flush=True)
        session_interface = flask.sessions.SecureCookieSessionInterface()
        s = session_interface.get_signing_serializer(self.app)
        max_age = int(self.app.permanent_session_lifetime.total_seconds())

        try:
            data = s.loads(self.token, max_age=max_age)
            self.uid = data['profile']['user_id']
            print("Authentication success", flush=True)
            return True
        except:
            print("Authentication failed", flush=True)
            return False

    def validate_arguments(self, *args, **kwargs):
        # Function pointer dictionary for dynamic type casting
        cast = {'int': int, 'float': float, 'str': str}
    
        for arg in args:
            arg_type = self.var_map[arg][0]
            allow_none = self.var_map[arg][1]
            value = self.var_map[arg][2]
    
            # Fail if a value is empty and shouldn't be
            if ( value is None or value == "" ) and not allow_none:
                return False
    
            # Check type casting to the correct value causes an error (all values are passed in as strings)
            try:
                cast[arg_type](value)
            except:
                return False
        return True

class ReportItem(RequestItem):
    def __init__(self, app, data):
        self.app = app
        self.token = data.get('token')
        self.uid = ''
        self.rid = data.get('rid')
        self.name = data.get('name')

        self.var_map = {
            'rid':  [ 'int',   False, self.rid ],
            'name': [ 'str',   True,  self.name ]
        }

    def validate_list(self):
        return True
        
    def validate_delete(self):
        return self.validate_arguments('rid')

    def validate_update(self):
        return self.validate_arguments('rid', 'name')

    def validate_create(self):
        return self.validate_arguments('name')

class ExpenseItem(RequestItem):
    def __init__(self, app, data, file_path = None):
        self.app = app
        self.token = data.get('token')
        self.uid = ''
        self.rid = data.get('rid')
        self.eid = data.get('eid')
        self.date = data.get('date')
        self.description = data.get('description')
        self.category = data.get('category')
        self.amount = data.get('amount')
        self.file_path = file_path

        self.var_map = {
            'rid':         [ 'int',   False, self.rid ],
            'eid':         [ 'int',   False, self.eid ],
            'date':        [ 'str',   False, self.date ],
            'description': [ 'str',   False, self.description ],
            'category':    [ 'str',   True,  self.category ],
            'amount':      [ 'float', False, self.amount ],
            'file_path':   [ 'str',   True,  self.file_path ]
        }

    def validate_list(self):
        return self.validate_arguments('rid')
        
    def validate_delete(self):
        return self.validate_arguments('rid', 'eid')

    def validate_update(self):
        return self.validate_arguments('rid', 'eid', 'date', 'description', 'category', 'amount')

    def validate_create(self):
        return self.validate_arguments('rid', 'date', 'description', 'category', 'amount')

    def validate_upload(self):
        return self.validate_arguments('rid', 'eid', 'file_path')

class Expenses:
    def __init__(self):
        self.init_config()
        self.init_db()
        self.s3 = boto3.resource('s3')

    def init_config(self):
        try: self.s3_bucket = os.environ['s3_bucket']
        except: raise UnboundLocalError('s3_bucket')

        try: self.s3_timeout = os.environ['s3_timeout']
        except: raise UnboundLocalError('s3_timeout')

        try: self.rds_endpoint = os.environ['rds_endpoint']
        except: raise UnboundLocalError('rds_endpoint')

        try: self.rds_port = os.environ['rds_port']
        except: raise UnboundLocalError('rds_port')

        try: self.rds_user = os.environ['rds_user']
        except: raise UnboundLocalError('rds_user')

        try: self.rds_pass = os.environ['rds_pass']
        except: raise UnboundLocalError('rds_pass')

        try: self.rds_region = os.environ['rds_region']
        except: raise UnboundLocalError('rds_region')

        try: self.rds_db = os.environ['rds_db']
        except: raise UnboundLocalError('rds_db')

        self.rds_report_table = "reports"
        self.rds_expense_table = "expenses"
        
    def init_db(self):
        def table_exists(name):
            self.rds_cur.execute("SELECT relname FROM pg_class WHERE relkind='r' AND relname = %s;", (name,))
            return len(self.rds_cur.fetchall()) > 0

        aws = boto3.Session(profile_name='default')

        self.rds_conn = psycopg2.connect(
            host=self.rds_endpoint,
            port=self.rds_port,
            database=self.rds_db,
            user=self.rds_user,
            password=self.rds_pass)

        self.rds_cur = self.rds_conn.cursor()

        # Create Report Table
        if not table_exists(self.rds_report_table):
            self.rds_cur.execute("CREATE TABLE {} (uid TEXT, rid INT, name TEXT, PRIMARY KEY (uid, rid));".format(self.rds_report_table))
            self.rds_conn.commit()

        # Create Expense Table
        if not table_exists(self.rds_expense_table):
            self.rds_cur.execute("CREATE TABLE {} (uid TEXT, rid INT, eid INT, date DATE, description TEXT, category TEXT, amount REAL, image TEXT, PRIMARY KEY (uid, rid, eid));".format(self.rds_expense_table))
            self.rds_conn.commit()

    # Reports
    def get_all_reports(self, item):
        try:
            self.rds_cur.execute("SELECT * FROM {} where uid=%s;".format(self.rds_report_table), (item.uid,))
            res = []
            for row in self.rds_cur.fetchall():
                res.append(row)
            self.rds_conn.commit()
            return res
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()
            return None

    def delete_report(self, item):
        try:
            self.rds_cur.execute("DELETE FROM {} where uid=%s AND rid=%s;".format(self.rds_report_table), (item.uid, item.rid))
            self.rds_cur.execute("DELETE FROM {} where uid=%s and rid=%s;".format(self.rds_expense_table), (item.uid, item.rid))
            self.rds_conn.commit()
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()

    def update_report(self, item):
        try:
            self.rds_cur.execute("UPDATE {} SET name=%s where uid=%s AND rid=%s;".format(self.rds_report_table), (item.name, item.uid, item.rid))
            self.rds_conn.commit()
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()

    def add_report(self, item):
        try:
            self.rds_cur.execute("SELECT MAX(rid) FROM {} where uid=%s".format(self.rds_report_table), (item.uid,))
            rid = self.rds_cur.fetchall()[0][0]
            self.rds_conn.commit()
            if rid is None:
                rid = 0

            self.rds_cur.execute("INSERT INTO {} (uid, rid, name) VALUES (%s, %s, %s);".format(self.rds_report_table), (item.uid, int(rid) + 1, item.name))
            self.rds_conn.commit()
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()

    # Expenses
    def get_expenses(self, item):
        try:
            self.rds_cur.execute("SELECT * FROM {} where uid=%s and rid=%s;".format(self.rds_expense_table), (item.uid, item.rid))
            res = []
            for row in self.rds_cur.fetchall():
                res.append(row)
            self.rds_conn.commit()
            return res
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()
            return None

    def delete_expense(self, item):
        self.rds_cur.execute("SELECT image FROM {} where uid=%s and rid=%s and eid=%s".format(self.rds_expense_table), (item.uid, item.rid, item.eid))
        key = self.rds_cur.fetchall()[0][0]
        self.rds_conn.commit()
        if (expense is not None or expense != ""):
            self.s3.meta.client.delete_object(Bucket=self.s3_bucket, Key=key)

        self.rds_cur.execute("DELETE FROM {} where uid=%s and rid=%s and eid=%s;".format(self.rds_expense_table), (item.uid, item.rid, item.eid))
        self.rds_conn.commit()

    def update_expense(self, item):
        fields = []

        fields.append(item.date)
        fields.append(item.description)
        fields.append(item.category)
        fields.append(item.amount)
        fields.append(item.image)
        fields.append(item.uid)
        fields.append(item.rid)
        fields.append(item.eid)
            
        try:
            self.rds_cur.execute("UPDATE {} SET date=%s, description=%s, category=%s, amount=%s, image=%s where uid=%s AND rid=%s AND eid=%s;".format(self.rds_expense_table), tuple(fields))
            self.rds_conn.commit()
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()

    def add_expense(self, item):
        try:
            self.rds_cur.execute("SELECT MAX(eid) FROM {} where uid=%s and rid=%s".format(self.rds_expense_table), (item.uid, item.rid))
            eid = self.rds_cur.fetchall()[0][0]
            self.rds_conn.commit()
            if eid is None:
                eid = 0

            fields = [item.uid, item.rid, int(eid) + 1]
            fields.append(item.date)
            fields.append(item.description)
            fields.append(item.category)
            fields.append(item.amount)
            fields.append(item.image)

            self.rds_cur.execute("INSERT INTO {} (uid, rid, eid, date, description, category, amount, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);".format(self.rds_expense_table), tuple(fields))
            self.rds_conn.commit()
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()

    # Other
    def upload_image(self, item):
        try:
            self.s3.meta.client.upload_file(item.file_path, self.s3_bucket, item.file_path.split('/')[2])
            os.remove(item.file_path)
            self.rds_cur.execute("UPDATE {} SET image=%s where uid=%s AND rid=%s;".format(self.rds_expense_table), (item.file_path.split('/')[2], item.uid, item.rid))
            self.rds_conn.commit()
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()

    def get_image(self, item):
        try:
            self.rds_cur.execute("SELECT image FROM {} where uid=%s and rid=%s and eid=%s".format(self.rds_expense_table), (item.uid, item.rid, item.eid))
            key = self.rds_cur.fetchall()[0][0]
            self.rds_conn.commit()
            file_object = self.s3.meta.client.get_object(Bucket=self.s3_bucket, Key=key)
            return file_object
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()

