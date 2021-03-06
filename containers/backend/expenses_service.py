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
            'rid':  [ 'int', False, self.rid ],
            'name': [ 'str', False, self.name ]
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
        self.image = data.get('image')

    def validate_list(self):
        self.var_map = {
            'rid': [ 'int', False, self.rid ]
        }
        return self.validate_arguments('rid')
        
    def validate_delete(self):
        self.var_map = {
            'rid': [ 'int',   False, self.rid ],
            'eid': [ 'int',   False, self.eid ]
        }
        return self.validate_arguments('rid', 'eid')

    def validate_update(self):
        self.var_map = {
            'rid':         [ 'int',   False, self.rid ],
            'eid':         [ 'int',   False, self.eid ],
            'date':        [ 'str',   False, self.date ],
            'description': [ 'str',   False, self.description ],
            'category':    [ 'str',   True,  self.category ],
            'amount':      [ 'float', False, self.amount ]
        }
        return self.validate_arguments('rid', 'eid', 'date', 'description', 'category', 'amount')

    def validate_create(self):
        self.var_map = {
            'rid':         [ 'int',   False, self.rid ],
            'date':        [ 'str',   False, self.date ],
            'description': [ 'str',   False, self.description ],
            'category':    [ 'str',   True,  self.category ],
            'amount':      [ 'float', False, self.amount ]
        }
        return self.validate_arguments('rid', 'date', 'description', 'category', 'amount')

    def validate_upload(self):
        self.var_map = {
            'rid':       [ 'int', False, self.rid ],
            'eid':       [ 'int', False, self.eid ],
            'file_path': [ 'str', False, self.file_path ]
        }
        return self.validate_arguments('rid', 'eid', 'file_path')

    def validate_download(self):
        self.var_map = {
            'image': [ 'str', False, self.image ]
        }
        return self.validate_arguments('image')

    def validate_delete_image(self):
        self.var_map = {
            'rid':   [ 'int', False, self.rid ],
            'eid':   [ 'int', False, self.eid ]
        }
        return self.validate_arguments('rid', 'eid')

class Expenses:
    def __init__(self):
        self.init_config()
        self.init_db()
        self.s3 = boto3.resource('s3')

    def init_config(self):
        try: self.s3_bucket = os.environ['s3_bucket']
        except: raise UnboundLocalError('s3_bucket')

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

        # Initialize aws session
        aws = boto3.Session(profile_name='default')

        # Connect to rds instance
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
            # Delete all associated images
            self.rds_cur.execute("SELECT image FROM {} where image is not NULL and uid=%s and rid=%s".format(self.rds_expense_table), (item.uid, item.rid))
            rows = self.rds_cur.fetchall()
            self.rds_conn.commit()
            for row in rows:
                key = row[0].split('.')[0]
                self.s3.meta.client.delete_object(Bucket=self.s3_bucket, Key=key)
            # Delete report
            self.rds_cur.execute("DELETE FROM {} where uid=%s AND rid=%s;".format(self.rds_report_table), (item.uid, item.rid))
            # Delete all associate expenses
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
        key = self.rds_cur.fetchall()
        self.rds_conn.commit()
        if (len(key) > 0 and key[0][0] is not None):
            self.s3.meta.client.delete_object(Bucket=self.s3_bucket, Key=key[0][0])

        self.rds_cur.execute("DELETE FROM {} where uid=%s and rid=%s and eid=%s;".format(self.rds_expense_table), (item.uid, item.rid, item.eid))
        self.rds_conn.commit()

    def update_expense(self, item):
        fields = []

        fields.append(item.date)
        fields.append(item.description)
        fields.append(item.category)
        fields.append(item.amount)
        fields.append(item.uid)
        fields.append(item.rid)
        fields.append(item.eid)
            
        try:
            self.rds_cur.execute("UPDATE {} SET date=%s, description=%s, category=%s, amount=%s where uid=%s AND rid=%s AND eid=%s;".format(self.rds_expense_table), tuple(fields))
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
            # Check if an image exists
            self.rds_cur.execute("SELECT image FROM {} where uid=%s and rid=%s and eid=%s".format(self.rds_expense_table), (item.uid, item.rid, item.eid))
            key = self.rds_cur.fetchall()
            self.rds_conn.commit()
            if (len(key) == 0 or key[0][0] is not None): return (405,)

            # Save image
            self.s3.meta.client.upload_file(item.file_path, self.s3_bucket, item.file_path[5:])
            os.remove(item.file_path)
            self.rds_cur.execute("UPDATE {} SET image=%s where uid=%s AND rid=%s and eid=%s;".format(self.rds_expense_table), (item.file_path[5:], item.uid, item.rid, item.eid))
            self.rds_conn.commit()
            return (200,)
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()
            return (500,)

    def download_image(self, item):
        try:
            # Check if an image exists
            self.rds_cur.execute("SELECT image FROM {} where uid=%s and image=%s".format(self.rds_expense_table), (item.uid, item.image))
            key = self.rds_cur.fetchall()
            self.rds_conn.commit()
            if (len(key) == 0): return (404,)
            mime_type = item.image.split('.')[1]

            # Return image
            self.s3.meta.client.download_file(self.s3_bucket, item.image, '/tmp/' + item.image)
            return (200, '/tmp/' + item.image, mime_type)
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()
            return (500,)

    def delete_image(self, item):
        try:
            # Check if an image exists
            self.rds_cur.execute("SELECT image FROM {} where image is not NULL and uid=%s and rid=%s and eid=%s".format(self.rds_expense_table), (item.uid, item.rid, item.eid))
            key = self.rds_cur.fetchall()
            self.rds_conn.commit()
            if (len(key) == 0): return (404,)

            # Delete image
            self.s3.meta.client.delete_object(Bucket=self.s3_bucket, Key=key[0][0])
            self.rds_cur.execute("UPDATE {} SET image = NULL where uid=%s AND rid=%s and eid=%s;".format(self.rds_expense_table), (item.uid, item.rid, item.eid))
            self.rds_conn.commit()
            return (200,)
        except Exception as e:
            print("ERROR: " + str(e), flush=True)
            self.rds_conn.cancel()
            return (500,)
