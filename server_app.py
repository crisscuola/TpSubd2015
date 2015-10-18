from flask import Flask
from flaskext.mysql import MySQL

import json

import entities.database
import entities.forum
import entities.user
import entities.post
import entities.thread

mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '5425321konsta'
app.config['MYSQL_DATABASE_DB'] = 'DBTest'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()


@app.route('/')
def index():
	return 'Flask is running! TP_DB_2015 v2'
 
@app.route('/authenticate')
def Authenticate():
	# cursor = mysql.connect().cursor()
	# my_query = 'SELECT * from User '
	# cursor.execute(my_query)
	# data = cursor.fetchone()
	# while data is not None:
	# 	print(data)
	# 	data = cursor.fetchone()
	# return json.dumps({"code": 0, "response": "OK"})

	username = request.args.get('UserName')
	password = request.args.get('Password')
	print(username)
	print(password)
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT * from User where UserName='Admin' and password='admin'")
	data = cursor.fetchone()
	if data is None:
		return "Username or Password is wrong"
	else:
		return "Logged in successfully"

   
# @app.route('/clear')
# def clear():


@app.route('/insert')
def insert():	
   # cursor = mysql.connect().cursor()
   print(cursor)
   cursor.execute("INSERT INTO User  VALUES ('4','Test','test')")
   print("2")
   
   # cursor.fetchone()
   conn.commit()
   print("3")
   return "ok"