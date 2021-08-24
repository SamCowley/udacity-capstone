import os
import psycopg2
import boto3

class ExpenseItem:
    def __init__(self, uid, rid, eid, description, category, amount, image):
        self.uid = uid
        self.rid = rid
        self.eid = eid
        self.description = description
        self.category = category
        self.amount = amount
        self.image_url = image

class ReportItem:
    def __init__(self, uid, rid, name):
        self.uid = uid
        self.rid = rid
        self.name = name

class Expenses:
    def __init__(self):
        self.init_config()
        self.init_db()
        self.s3 = boto3.client('s3')

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
            self.rds_cur.execute("CREATE TABLE {} (uid TEXT, rid INT, eid INT, description TEXT, category TEXT, amount INT, image TEXT, PRIMARY KEY (uid, rid, eid));".format(self.rds_expense_table))
            self.rds_conn.commit()

    # Reports
    def get_all_reports(self, uid):
        self.rds_cur.execute("SELECT * FROM {} where uid=%s;".format(self.rds_report_table), (uid,))
        try:
            res = []
            for item in self.rds_cur.fetchall():
                res.append(ReportItem(item[0], item[1], item[2]))
            self.rds_conn.commit()
            return res
        except:
            return None

    def delete_report(self, uid, rid):
        self.rds_cur.execute("DELETE FROM {} where uid=%s AND rid=%s;".format(self.rds_report_table), (uid, rid))
        self.rds_cur.execute("DELETE FROM {} where uid=%s and rid=%s;".format(self.rds_expense_table), (uid, rid))
        self.rds_conn.commit()

    def update_report(self, uid, rid, name):
        self.rds_cur.execute("UPDATE SET name = %s FROM {} where uid=%s AND rid=%s;".format(self.rds_report_table), (name, uid, rid))
        self.rds_conn.commit()

    def add_report(self, uid, name):
        try:
            self.rds_cur.execute("SELECT MAX(rid) FROM {} where uid=%s".format(self.rds_report_table), (uid,))
            rid = self.rds_cur.fetchall()[0]
            self.rds_conn.commit()
        except:
            rid = 0
        self.rds_cur.execute("INSERT INTO {} (uid, rid, name) VALUES (%s, %s, %s);".format(self.rds_report_table), (uid, int(rid) + 1, name))
        self.rds_conn.commit()

    # Expenses
    def get_expenses(self, uid, rid):
        self.rds_cur.execute("SELECT * FROM {} where uid=%s and rid=%s;".format(self.rds_expense_table), (uid, rid))
        try:
            res = []
            for item in self.rds_cur.fetchall():
                res.append(ExpenseItem(item[0], item[1], item[2], item[3], item[4], item[5], item[6]))
            self.rds_conn.commit()
            return res
        except:
            return None

    def delete_expense(self, uid, rid, eid):
        self.rds_cur.execute("DELETE FROM {} where uid=%s and rid=%s;".format(self.rds_expense_table), (uid, rid))
        self.rds_conn.commit()

    def update_expense(self, uid, rid, eid, description, category, amount, image):
        fields = []

        fields.append("description")
        fields.append(description)
        fields.append("category")
        fields.append(category)
        fields.append("amount")
        fields.append(amount)
        fields.append("image")
        fields.append(image)
        fields.append(uid)
        fields.append(rid)
        fields.append(eid)
            
        self.rds_cur.execute("UPDATE SET {} FROM {} where uid=%s AND rid=%s AND eid=%s;".format(", ".join(["%s=%s"]*(len(fields) - 3)/2), self.rds_expense_table), tuple(fields))
        self.rds_conn.commit()

    def add_expense(self, uid, rid, description = None, category = None, amount = None, image = None):
        try:
            self.rds_cur.execute("SELECT MAX(eid) FROM {} where uid=%s and rid=%s".format(self.rds_expense_table), (uid, rid))
            eid = self.rds_cur.fetchall()[0]
            self.rds_conn.commit()
        except:
            eid = 0

        fields = [uid, rid, int(eid) + 1]
        fields.append(description)
        fields.append(category)
        fields.append(amount)
        fields.append(image)

        self.rds_cur.execute("INSERT INTO {} (uid, rid, eid, description, category, amount, image) VALUES (%s, %s, %s, %s, %s, %s, %s);".format(self.rds_expense_table), tuple(fields))
        self.rds_conn.commit()

    # Other
    def upload_image(self, object_name):
        return self.s3.generate_presigned_url(self.s3_bucket, object_name, ExpiresIn=self.s3_timeout)

