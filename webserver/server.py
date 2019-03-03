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

@app.route('/log')
def do_admin_log():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def do_admin_login():
    flag = 0
    cursor = g.conn.execute("SELECT user_id, password FROM admin")
    for record in cursor:
      if record[0] == int(request.form['username']) and record[1] == request.form['password']:
        session['logged_in'] = True
        flag = 1
        break;

    if not flag:
      flash("Wrong password")

    return home()

def user_login_page():
  return render_template("user_logged_in.html")

def login_page():
  return render_template("logged_in.html")

@app.route('/enter_database')
def enter_data():
    return render_template("enter_data.html")

@app.route('/get_database')
def get_data():
    return render_template("get_database.html")

@app.route('/get_database_admin')
def get_data_admin():
    return render_template("get_database_admin.html")

@app.route('/get_picture_table')
def get_picture_table():
    cursor = g.conn.execute("SELECT * FROM motion_picture")
    names = []
    for result in cursor:
      names.append(str(result[0]) +', '+str(result[1]) +', '+str(result[2]) +', '+str(result[3]) +', '+str(result[4]) +', '+str(result[5]) +', '+str(result[6]) +', '+str(result[7]) +', '+str(result[8]) +', '+str(result[9]) +', '+str(result[10]))  # can also be accessed using result[0]
    cursor.close()

    context = dict(data = names)

    return render_template("get_picture_table.html", **context)

@app.route('/get_actor_table')
def get_actor_table():
    cursor = g.conn.execute("SELECT * FROM actor")
    names = []
    for result in cursor:
      names.append(str(result[0]) +', '+str(result[1]) +', '+str(result[2]))  # can also be accessed using result[0]
    cursor.close()

    context = dict(data = names)

    return render_template("get_actor_table.html", **context)

@app.route('/get_director_table')
def get_director_table():
    cursor = g.conn.execute("SELECT * FROM director")
    names = []
    for result in cursor:
      names.append(str(result[0]) +', '+str(result[1]) +', '+str(result[2]))  # can also be accessed using result[0]
    cursor.close()

    context = dict(data = names)

    return render_template("get_director_table.html", **context)

@app.route('/get_producer_table')
def get_producer_table():
    cursor = g.conn.execute("SELECT * FROM producer")
    names = []
    for result in cursor:
      names.append(str(result[0]) +', '+str(result[1]) +', '+str(result[2]))  # can also be accessed using result[0]
    cursor.close()

    context = dict(data = names)

    return render_template("get_producer_table.html", **context)

@app.route('/get_award_table')
def get_award_table():
    cursor = g.conn.execute("SELECT A.name, A.year, A.category, M.name FROM award_given as A, motion_picture as M WHERE A.pic_id = M.pic_id")
    names = []
    for result in cursor:
      names.append(str(result[0]) +', '+str(result[1]) +', '+str(result[2])+', '+str(result[3]))  # can also be accessed using result[0]
    cursor.close()

    context = dict(data = names)

    return render_template("get_award_table.html", **context)

@app.route('/get_review_table')
def get_review_table():
    cursor = g.conn.execute("SELECT R.user_id, R.comment, R.rating, M.name FROM review as R, motion_picture as M WHERE R.pic_id = M.pic_id")
    names = []
    for result in cursor:
      names.append(str(result[0]) +', '+str(result[1]) +', '+str(result[2])+', '+str(result[3]))  # can also be accessed using result[0]
    cursor.close()

    context = dict(data = names)

    return render_template("get_review_table.html", **context)

@app.route('/get_user_table')
def get_user_table():
    cursor = g.conn.execute("SELECT * FROM users")
    names = []
    for result in cursor:
      names.append(str(result[0]) +', '+str(result[1]))  # can also be accessed using result[0]
    cursor.close()

    context = dict(data = names)

    return render_template("get_user_table.html", **context)

@app.route('/get_director_producer_table')
def get_director_producer_table():
    cursor = g.conn.execute("SELECT D.name, P.name FROM director as D, producer as P, worked_with as W WHERE D.dir_id = W.dir_id and W.pro_id = P.pro_id")
    names = []
    for result in cursor:
      names.append(str(result[0]) +', '+str(result[1]))  # can also be accessed using result[0]
    cursor.close()

    context = dict(data = names)

    return render_template("get_director_producer_table.html", **context)

@app.route('/actor')
def enter_actor():
    return render_template("actor.html")

@app.route('/actor/add',methods=['POST'])
def actor_add():
    ID = request.form['id']
    name = request.form['name']
    gender = request.form['gender']
    MID = request.form['movieID']
    flag = 0

    cursor = g.conn.execute("SELECT pic_id FROM motion_picture")
    for m_id in cursor:
      if int(m_id[0]) == int(MID):
        flag = 1

    if flag == 0:
      flash("Movie ID doesn't exist")
      return redirect('/actor')


    flag = 0
    cursor = g.conn.execute("SELECT act_id FROM actor")
    for record in cursor:
      if int(record[0]) == int(ID):
        flag = 1
        break;

    if flag:
      flash("Actor ID already exist")
      return redirect('/actor')

    cmd = 'INSERT INTO actor(act_id, name, gender) VALUES (:ID, :name, :gender) '
    g.conn.execute(text(cmd), ID = ID, name = name, gender = gender)

    cmd = 'INSERT INTO acts(act_id, pic_id) VALUES (:ID, :MID) '
    g.conn.execute(text(cmd), ID = ID, MID = MID)

    return render_template("logged_in.html")

@app.route('/director')
def enter_director():
    return render_template("director.html")

@app.route('/director/add',methods=['POST'])
def director_add():
    ID = request.form['id']
    name = request.form['name']
    gender = request.form['gender']

    flag = 0
    cursor = g.conn.execute("SELECT dir_id FROM director")
    for record in cursor:
      if int(record[0]) == int(ID):
        flag = 1
        break;

    if flag:
      flash("director ID already exist")
      return redirect('/director')

    cmd = 'INSERT INTO director(dir_id, name, gender) VALUES (:ID, :name, :gender) '
    g.conn.execute(text(cmd), ID = ID, name = name, gender = gender)

    return render_template("logged_in.html")

@app.route('/producer')
def enter_producer():
    return render_template("producer.html")

@app.route('/producer/add',methods=['POST'])
def producer_add():
    ID = request.form['id']
    name = request.form['name']
    gender = request.form['gender']

    flag = 0
    cursor = g.conn.execute("SELECT pro_id FROM producer")
    for record in cursor:
      if int(record[0]) == int(ID):
        flag = 1
        break;

    if flag:
      flash("producer ID already exist")
      return redirect('/producer')

    cmd = 'INSERT INTO producer(pro_id, name, gender) VALUES (:ID, :name, :gender) '
    g.conn.execute(text(cmd), ID = ID, name = name, gender = gender)

    return render_template("logged_in.html")

@app.route('/admin')
def enter_admin():
    return render_template("admin.html")

@app.route('/admin/add',methods=['POST'])
def admin_add():
    ID = request.form['id']
    password = request.form['password']
    re_password = request.form['re_password']

    if(str(password) != str(re_password)):
      flash("passwords don't match")
      return redirect('/admin')

    flag = 0
    cursor = g.conn.execute("SELECT user_id FROM admin")
    for record in cursor:
      if int(record[0]) == int(ID):
        flag = 1
        break;

    if flag:
      flash("Admin ID already exist")
      return redirect('/admin')

    cmd = 'INSERT INTO admin(user_id, password) VALUES (:ID, :password) '
    g.conn.execute(text(cmd), ID = ID, password = password)

    return render_template("logged_in.html")

@app.route('/awards')
def enter_awards():
    return render_template("awards.html")

@app.route('/awards/add',methods=['POST'])
def awards_add():
    name = request.form['name']
    year = request.form['year']
    category = request.form['category']
    pic_id = request.form['pic_id']

    flag = 0
    cursor = g.conn.execute("SELECT pic_id FROM motion_picture")
    for record in cursor:
      if int(record[0]) == int(pic_id):
        flag = 1
        break;

    if not flag:
      flash("Pic id doesn't exist")
      return redirect('/awards')

    flag = 0
    cursor = g.conn.execute("SELECT name, year, category FROM award_given")
    for record in cursor:
      if str(record[0]) == str(name) and int(record[1]) == int(year) and str(record[2]) == str(category):
        flag = 1
        break;

    if(flag):
      flash("Award already assigned, please re-enter")
      return redirect('/awards')

    cmd = 'INSERT INTO award_given(name, year, category, pic_id) VALUES (:name, :year, :category, :pic_id) '
    g.conn.execute(text(cmd), name = name, year = year, category = category, pic_id = pic_id)

    return render_template("logged_in.html")
