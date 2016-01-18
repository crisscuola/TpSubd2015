import MySQLdb


DB_HOST = 'localhost'
DB_USER = 'test'
#DB_DATABASE = 'test'
DB_DATABASE = 'perf_highload_db'
DB_PASSWORD = 'test'


class MyDatabase:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connection_cursor()

    def execute_post(self, sql, params=()):
        self.cursor.execute(sql, params)

        self.connection.commit()
           
        return self.cursor.lastrowid

    def execute_get(self, sql, params=()):
        self.cursor.execute(sql, params)

        return self.cursor.fetchall() 

    def connection_cursor(self):
        self.connection = MySQLdb.connect(host=DB_HOST, user=DB_USER, db=DB_DATABASE, passwd=DB_PASSWORD, use_unicode=1, charset='utf8')
        self.cursor = self.connection.cursor()

db = MyDatabase()