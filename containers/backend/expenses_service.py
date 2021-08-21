import psycopg2
import configparser
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
    def __init__(self, app):
        self.app = app
        self.init_config()
        self.init_db()
        self.s3 = boto3.client('s3')

    def init_config(self):
        missing_values = []
        
        # Get all configuration
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # Add auth0 if it doesn't exist
        if 'expenses' not in self.config: self.config['expenses'] = {}

        # Retrieve all values
        self.s3_bucket = self.config['expenses'].get('s3_bucket')
        if self.s3_bucket in [None, '']:
            missing_values.append('s3_bucket')

        self.s3_timeout = self.config['expenses'].get('s3_timeout')
        if self.s3_timeout in [None, '']:
            missing_values.append('s3_timeout')
            self.s3_timeout = 3600

        self.rds_endpoint = ''
        self.rds_port = ''
        self.rds_user = ''
        self.rds_region = ''

        # Add missing fields and raise an exception
        if len(missing_values) != 0:
            self.config['expenses']['aws_secret'] = None
            self.config['expenses']['s3_bucket'] = str(self.s3_bucket)
            self.config['expenses']['s3_timeout'] = str(self.s3_timeout)
            self.config['expenses']['rds_database'] = str(self.s3_timeout)
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
            raise UnboundLocalError('Missing values: ' + str(missing_values))
        
    def init_db(self):
       def table_exists(name):
           self.rds_cur.execute("SHOW TABLES LIKE %s;", (name,))
           return len(self.rds_cur.fetchall()) > 0

        aws = boto3.Session(profile_name='default')

        rds = aws.client('rds')
        self.rds_token = client.generate_db_auth_token(
            DBHostname=self.rds_endpoint,
            Port=self.rds_port,
            DBUsername=self.rds_user,
            Region=self.rds_region)

        self.rds_conn = psycopg2.connect(
            host=self.rds_endpoint,
            port=self.rds_port,
            database=self.rds_dbname,
            user=self.rds_user,
            password=self.rds_token)

        self.rds_cur = self.rds_conn.cursor()

       # Create Report Table
       if table_exists(self.rds_report_table):
           self.rds_cur.execute("CREATE TABLE %s (uid TEXT, rid INT, name TEXT, PRIMARY KEY (uid, rid));", (self.rds_report_table,))

       # Create Expense Table
       if table_exists(self.rds_expense_table):
           self.rds_cur.execute("CREATE TABLE %s (uid TEXT, rid INT, eid INT, description TEXT, category TEXT, amount INT, image TEXT, PRIMARY KEY (uid, rid, eid));", (self.rds_expense_table,))

    # Reports
    def get_all_reports(self, uid):
        self.rds_cur.execute("SELECT * FROM %s where uid=%s;", (self.rds_report_table, uid))
        try:
            res = []
            for item in self.rds_cur.fetchall():
                res.append(ReportItem(item[0], item[1], item[2]))
            return res
        except:
            return None

    def delete_report(self, uid, rid):
        self.rds_cur.execute("DELETE FROM %s where uid=%s AND rid=%s;", (self.rds_report_table, uid, rid))
        self.rds_cur.execute("DELETE FROM %s where uid=%s and rid=%s;", (self.rds_expense_table, uid, rid))

    def update_report(self, uid, rid, name):
        self.rds_cur.execute("UPDATE SET name = %s FROM %s where uid=%s AND rid=%s;", (name, self.rds_report_table, uid, rid))

    def add_report(self, uid, name):
        self.rds_cur.execute("SELECT MAX(rid) FROM %s where uid=%s", (self.rds_report_table, uid))
        self.rds_cur.execute("INSERT INTO %s (uid, rid, name) VALUES (%s, %s, %s);", (self.rds_report_table, uid, int(rid) + 1, name))

    # Expenses
    def get_expenses(self, uid, rid):
        self.rds_cur.execute("SELECT * FROM %s where uid=%s and rid=%s;", (self.rds_expense_table, uid, rid))
        try:
            res = []
            for item in self.rds_cur.fetchall():
                res.append(ExpenseItem(item[0], item[1], item[2], item[3], item[4], item[5], item[6]))
            return res
        except:
            return None

    def delete_expense(self, uid, rid, eid):
        self.rds_cur.execute("DELETE FROM %s where uid=%s and rid=%s;", (self.rds_expense_table, uid, rid))

    def update_expense(self, uid, rid, eid, description, category, amount, image):
        fields = []
        command = []
        def add(f, c, name, value):
            if value is not None:
                fields.append(value)
                command.append(name + " = %s")
        
        add(fields, command, "description", description)
        add(fields, command, "category", category)
        add(fields, command, "amount", amount)
        add(fields, command, "image", image)

        fields.append(self.rds_expense_table)
        fields.append(uid)
        fields.append(rid)
        fields.append(eid)
            
        self.rds_cur.execute("UPDATE SET " + ", ".join(command) + " FROM %s where uid=%s AND rid=%s AND eid=%s;", tuple(fields))

    def add_expense(self, uid, rid, description = None, category = None, amount = None, image = None):
        self.rds_cur.execute("SELECT MAX(eid) FROM %s where uid=%s and rid=%s", (self.rds_expense_table, uid, rid))

        fields = [self.rds_expense_table, uid, rid, int(eid) + 1]
        command = []
        def add(f, c, name, value):
            if value is not None:
                fields.append(value)
                command.append(name)

        add(fields, command, "description", description)
        add(fields, command, "category", category)
        add(fields, command, "amount", amount)
        add(fields, command, "image", image)

        self.rds_cur.execute("INSERT INTO %s (" + ", ".join(command) ") VALUES (" + ", ".join(["%s"]*len(command)) + ");", tuple(fields))

    # Other
    def upload_image(self, object_name):
        return self.s3.generate_presigned_url(self.s3_bucket, object_name, ExpiresIn=self.s3_timeout)

