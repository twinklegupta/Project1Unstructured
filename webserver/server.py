#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash, abort

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "sn2786"
DB_PASSWORD = "s788l1bi"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)

USER_IDID = None
# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def home():
    if not session.get('logged_in') and not session.get('user_logged_in'):
        return render_template('main.html')
    elif session.get('logged_in'):
        return login_page()
    else:
        return user_login_page()

@app.route('/user/login', methods=['POST'])
def do_user_login():
    flag = 0
    cursor = g.conn.execute("SELECT user_id, password FROM users")
    global USER_IDID
    for record in cursor:
      if record[0] == int(request.form['id']) and record[1] == request.form['password']:
        USER_IDID = int(record[0])
        session['user_logged_in'] = True
        flag = 1
        break;

    if not flag:
      flash("Wrong password")

    return home()

@app.route('/logout')
def logout():
    session['user_logged_in'] = False
    session['logged_in'] = False
    global USER_IDID
    USER_IDID = None

    return home()

@app.route('/user/new')
def new_user():
    return render_template('user.html')

@app.route('/user/new/add', methods=['POST', 'GET'])
def add_new_user():
    ID = request.form['id']
    password = request.form['password']
    re_password = request.form['re_password']

    if(str(password) != str(re_password)):
      flash("passwords don't match")
      return render_template('user.html')

    flag = 0
    cursor = g.conn.execute("SELECT user_id FROM users")
    for record in cursor:
      if int(record[0]) == int(ID):
        flag = 1
        break;

    if flag:
      flash("user_id already exists")
      return redirect('/')

    cmd = 'INSERT INTO users(user_id, password) VALUES (:ID, :password) '
    g.conn.execute(text(cmd), ID = ID, password = password)

    return redirect('/')
