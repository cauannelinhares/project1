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
from flask import Flask, request, render_template, g, redirect, Response
import datetime

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

today = datetime.date.today()
print today

usecheckemail = ""

#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#
DATABASEURI = "postgresql://tt2571:XJWYLH@w4111db.eastus.cloudapp.azure.com/tt2571"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


#
# END SQLITE SETUP CODE
#



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
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name,user_id FROM Users_work")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()


  testfcomid = "Microsoft"
  cursor = g.conn.execute("SELECT com_id FROM Company WHERE name = %s", testfcomid)
  ccccid = []
  for result in cursor:
    ccccid.append(result[0])
  cursor.close()
  print ccccid[0]


  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['text']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/welcome')
def welcome():
  return render_template("welcome.html")

@app.route('/errorpage')
def errorpage():
  return render_template("errorpage.html")

@app.route('/searchop')
def searchop():
  print request.args


  cursor = g.conn.execute("SELECT op.position,op.opp_id,op.paid,op.deadline,op.description,op.location,op.post_date,uw.email FROM Opportunity_Post AS op, Users_work AS uw WHERE op.user_id=uw.user_id")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

  
  commentdic = []
  for test in names:
    cursor = g.conn.execute("SELECT content,comment_date FROM Comment_Left WHERE opp_id = %s", test[1])
    cnames = []
    for result in cursor:
        cnames.append(result)  # can also be accessed using result[0]
    cursor.close()
    commentdic.append(cnames)
    
  context = dict(data = names, comm=commentdic)

  return render_template("searchop.html", **context)





# Example of adding new data to the database
@app.route('/addcomment', methods=['POST'])
def addcomment():
  commenttext = request.form['commenttext']
  print commenttext
 
  global usecheckemail
  cursor = g.conn.execute("SELECT user_id FROM Users_work WHERE email = %s", usecheckemail)
  uuuuserid = []
  for result in cursor:
    uuuuserid.append(result[0])  # can also be accessed using result[0]
  cursor.close()

  cuserid = uuuuserid[0]

  coppid = request.form['coppid']
  print coppid
  cursor = g.conn.execute("SELECT MAX(comid) FROM Comment_Left")
  comidd = []
  for result in cursor:
    comidd.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print comidd[0]
  comidd[0] = comidd[0] + 1
  print comidd[0]
    
  g.conn.execute('INSERT INTO Comment_Left(comid, opp_id, content, comment_date, user_id) VALUES(%s,%s,%s,%s,%s)', (comidd[0], coppid, commenttext, today, cuserid))



  return redirect('/searchop')






@app.route('/singleopp')
def singleopp():
  return render_template("singleopp.html")


@app.route('/register')
def register():
  return render_template("registeruser.html")


@app.route('/student')
def student():
  return render_template("student.html")


@app.route('/alumnus')
def alumnus():
  return render_template("alumnus.html")



@app.route('/updateprofile')
def updateprofile():
  return render_template("updateprofile.html")

                

# Example of adding new data to the database
@app.route('/updateinfo', methods=['POST'])
def updateinfo():

  global usecheckemail
  cursor = g.conn.execute("SELECT user_id FROM Users_work WHERE email = %s", usecheckemail)
  userids = []
  for result in cursor:
    userids.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  upname = request.form['upname']
  upaddress = request.form['upaddress']
  g.conn.execute("UPDATE Users_work SET name = %s, address = %s WHERE user_id = %s", (upname, upaddress, userids[0]))
  print upname
  print upaddress
  print "hahahahahahaah"
  return redirect('/welcome')


              
                 
@app.route('/yourprofile')
def yourprofile():
  global usecheckemail              
  cursor = g.conn.execute("SELECT usertype FROM Users_work WHERE email = %s", usecheckemail)
  unames = []
  for result in cursor:
    unames.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print unames


  cursor = g.conn.execute("SELECT user_id FROM Users_work WHERE email = %s", usecheckemail)
  userids = []
  for result in cursor:
    userids.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print userids
 

  if unames[0] == "student":
        cursor = g.conn.execute("SELECT uw.name, uw.email, uw.address, uw.gender, st.major, st.degree, un.name FROM Users_work AS uw, ISA_Students AS st, From_University AS fu, Universities AS un WHERE uw.user_id = st.user_id AND st.user_id = fu.user_id AND fu.name_uni = un.name AND uw.user_id = %s", userids[0])
        names = []
        for result in cursor:
            names.append(result)  # can also be accessed using result[0]
        cursor.close()
  elif unames[0] == "alumnus":
        cursor = g.conn.execute("SELECT uw.name, uw.email, uw.address, uw.gender, cm.name, cm.industry, un.name FROM Users_work AS uw, Alumnus AS am, From_University AS fu, Universities AS un, Company AS cm WHERE uw.user_id = am.user_id AND am.user_id = fu.user_id AND fu.name_uni = un.name AND cm.com_id=uw.com_id AND uw.user_id = %s", userids[0])
        names = []
        for result in cursor:
            names.append(result)  # can also be accessed using result[0]
        cursor.close()
  else:
        cursor = g.conn.execute("SELECT uw.name, uw.email, uw.address, uw.gender, pf.department, pf.position, un.name FROM Users_work AS uw, Professors AS pf, From_University AS fu, Universities AS un WHERE uw.user_id = pf.user_id AND pf.user_id = fu.user_id AND fu.name_uni = un.name AND uw.user_id = %s", userids[0])
        names = []
        for result in cursor:
            names.append(result)  # can also be accessed using result[0]
        cursor.close()
  
                 
  print names 
  print "hahahahahahahahahahahahaha"
  context = dict(data = names)


  return render_template("yourprofile.html", **context)      



@app.route('/professor')
def professor():
  return render_template("professor.html")




@app.route('/postop')
def postop():

  return render_template("postop.html")



# Example of adding new data to the database
@app.route('/postopadd', methods=['POST'])
def postopadd():
  position = request.form['position']
  description = request.form['description']
  paid = request.form['paid']
  location = request.form['location']
  deadline = request.form['deadline']
  loctype = request.form['loctype']
  universityname = request.form['universityname']
  universityrank = request.form['universityrank']
  companyname = request.form['companyname']
  companyindustry = request.form['companyindustry']
  
  global usecheckemail
  cursor = g.conn.execute("SELECT user_id FROM Users_work WHERE email = %s", usecheckemail)
  uuuuserid = []
  for result in cursor:
    uuuuserid.append(result[0])  # can also be accessed using result[0]
  cursor.close()

  userid = uuuuserid[0]



  cursor = g.conn.execute("SELECT name FROM Universities")
  uname = []
  for result in cursor:
    uname.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print uname
  
  cursor = g.conn.execute("SELECT name FROM Company")
  cname = []
  for result in cursor:
    cname.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print cname
  
  cursor = g.conn.execute("SELECT MAX(opp_id) FROM Opportunity_Post")
  oppid = []
  for result in cursor:
    oppid.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  oppid[0] = oppid[0] + 1
  print oppid[0]
  print today
  
 
    
  if loctype == "University":
        if universityname in uname:
            if paid == "yes":
                g.conn.execute('INSERT INTO Opportunity_Post(paid, opp_id, deadline, position, description, location, post_date, user_id, name_university) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (True, oppid[0], deadline, position, description, location, today, userid, universityname))
            else:
                g.conn.execute('INSERT INTO Opportunity_Post(paid, opp_id, deadline, position, description, location, post_date, user_id, name_university) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (False, oppid[0], deadline, position, description, location, today, userid, universityname))
        else:
            g.conn.execute('INSERT INTO Universities(name,rating) VALUES(%s,%s)',(universityname, universityrank))
            if paid == "yes":
                g.conn.execute('INSERT INTO Opportunity_Post(paid, opp_id, deadline, position, description, location, post_date, user_id, name_university) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (True, oppid[0], deadline, position, description, location, today, userid, universityname))
            else:
                g.conn.execute('INSERT INTO Opportunity_Post(paid, opp_id, deadline, position, description, location, post_date, user_id, name_university) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (False, oppid[0], deadline, position, description, location, today, userid, universityname))
  else:
        if companyname in cname:
            cursor = g.conn.execute("SELECT com_id FROM Company WHERE name = %s", companyname)
            ccid = []
            for result in cursor:
                ccid.append(result[0])
            cursor.close()
            print ccid[0]
            if paid == "yes":
                g.conn.execute('INSERT INTO Opportunity_Post(paid, opp_id, deadline, position, description, location, post_date, user_id, com_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (True, oppid[0], deadline, position, description, location, today, userid, ccid[0]))
            else:
                g.conn.execute('INSERT INTO Opportunity_Post(paid, opp_id, deadline, position, description, location, post_date, user_id, com_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (False, oppid[0], deadline, position, description, location, today, userid, ccid[0]))
        else:
            cursor = g.conn.execute("SELECT MAX(com_id) FROM Company")
            comid = []
            for result in cursor:
                comid.append(result[0])  # can also be accessed using result[0]
            cursor.close()
            comid[0] = comid[0] + 1
            g.conn.execute('INSERT INTO Company(com_id, name, industry) VALUES(%s,%s,%s)',(comid[0], companyname, companyindustry))
            if paid == "yes":
                g.conn.execute('INSERT INTO Opportunity_Post(paid, opp_id, deadline, position, description, location, post_date, user_id, com_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (True, oppid[0], deadline, position, description, location, today, userid, comid[0]))
            else:
                g.conn.execute('INSERT INTO Opportunity_Post(paid, opp_id, deadline, position, description, location, post_date, user_id, com_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (False, oppid[0], deadline, position, description, location, today, userid, comid[0]))
    



      

  return redirect('/welcome')



# Example of adding new data to the database
@app.route('/addstudent', methods=['POST'])
def addstudent():
  username = request.form['username']
  useremail = request.form['useremail']
  useraddress = request.form['useraddress']
  usergender = request.form['usergender']
  usermajor = request.form['usermajor']
  userdegree = request.form['userdegree']
  usergpa = request.form['usergpa']
  print username + "  " + useremail + "  "+ useraddress + "  "+ usergender + "  "+ usermajor + "  "+ userdegree + "  " + usergpa
  userpassword = request.form['userpassword'] 
  universityname = request.form['universityname']
  universityrating = request.form['universityrating']
  attendsince = request.form['attendsince']
  
  cursor = g.conn.execute("SELECT email FROM Users_work")
  uueremail = []
  for result in cursor:
    uueremail.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  if useremail in uueremail:
        return redirect('/errorpage')  
  cursor = g.conn.execute("SELECT MAX(user_id) FROM Users_work")
  userid = []
  for result in cursor:
    userid.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print userid[0]
  userid[0] = userid[0] + 1
  print userid[0]
  usertype = "student"
  g.conn.execute('INSERT INTO Users_work(user_id, name, email, address, gender,password,usertype) VALUES(%s,%s,%s,%s,%s,%s,%s)', (userid[0], username, useremail, useraddress, usergender,userpassword, usertype))
  g.conn.execute('INSERT INTO ISA_Students(user_id, major, degree, gpa) VALUES(%s,%s,%s,%s)', (userid[0], usermajor, userdegree, usergpa))

  cursor = g.conn.execute("SELECT name FROM Universities")
  uuname = []
  for result in cursor:
    uuname.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print uuname
  if universityname not in uuname:
    g.conn.execute('INSERT INTO Universities(name,rating) VALUES(%s,%s)',(universityname, universityrating))

  g.conn.execute('INSERT INTO From_University(user_id, name_uni, SINCE) VALUES(%s,%s,%s)', (userid[0], universityname, attendsince))
  return redirect('/')




# Example of adding new data to the database
@app.route('/addalumnus', methods=['POST'])
def addalumnus():
  username = request.form['username']
  useremail = request.form['useremail']
  useraddress = request.form['useraddress']
  usergender = request.form['usergender']
  sincework = request.form['sincework']
  typework = request.form['typework']
  companyname = request.form['companyname']
  companyindustry = request.form['companyindustry']
  
  usertype = "alumnus"
  userpassword = request.form['userpassword']
  universityname = request.form['universityname']
  universityrating = request.form['universityrating']
  attendsince = request.form['attendsince']
  
  usermajor = request.form['usermajor']
  userdegree = request.form['userdegree']
  usergpa = request.form['usergpa']
  cursor = g.conn.execute("SELECT email FROM Users_work")
  uueremail = []
  for result in cursor:
    uueremail.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  if useremail in uueremail:
        return redirect('/errorpage')
  cursor = g.conn.execute("SELECT MAX(user_id) FROM Users_work")
  userid = []
  for result in cursor:
    userid.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print userid[0]
  userid[0] = userid[0] + 1
  print userid[0]
  
  cursor = g.conn.execute("SELECT name FROM Company")
  ccname = []
  for result in cursor:
    ccname.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print ccname
  

  if companyname in ccname:
    cursor = g.conn.execute("SELECT com_id FROM Company WHERE name = %s", companyname)
    ccomid = []
    for result in cursor:
        ccomid.append(result[0])
    cursor.close()
    g.conn.execute('INSERT INTO Users_work(user_id, name, email, address, gender, since_work, type_work, com_id,password,usertype) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (userid[0], username, useremail, useraddress, usergender, sincework, typework, ccomid[0], userpassword,usertype))
    g.conn.execute('INSERT INTO Alumnus(user_id, major, degree, gpa) VALUES(%s,%s,%s,%s)', (userid[0], usermajor, userdegree, usergpa))
    
  else:
    cursor = g.conn.execute("SELECT MAX(com_id) FROM Company")
    comcid = []
    for result in cursor:
        comcid.append(result[0])  # can also be accessed using result[0]
    cursor.close()
    comcid[0] = comcid[0] + 1
    g.conn.execute('INSERT INTO Company(com_id, name, industry) VALUES(%s,%s,%s)', (comcid[0], companyname, companyindustry))
    g.conn.execute('INSERT INTO Users_work(user_id, name, email, address, gender, since_work, type_work, com_id,usertype) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (userid[0], username, useremail, useraddress, usergender, sincework, typework, comcid[0],usertype))
    g.conn.execute('INSERT INTO Alumnus(user_id, major, degree, gpa) VALUES(%s,%s,%s,%s)', (userid[0], usermajor, userdegree, usergpa))


  cursor = g.conn.execute("SELECT name FROM Universities")
  uuname = []
  for result in cursor:
    uuname.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print uuname
  if universityname not in uuname:
    g.conn.execute('INSERT INTO Universities(name,rating) VALUES(%s,%s)',(universityname, universityrating))

  g.conn.execute('INSERT INTO From_University(user_id, name_uni, SINCE) VALUES(%s,%s,%s)', (userid[0], universityname, attendsince))


  return redirect('/')



# Example of adding new data to the database
@app.route('/addprofessor', methods=['POST'])
def addprofessor():
  username = request.form['username']
  useremail = request.form['useremail']
  useraddress = request.form['useraddress']
  usergender = request.form['usergender']
  userdepartment = request.form['userdepartment']
  userposition = request.form['userposition']
 
  usertype="professor"
  universityname = request.form['universityname']
  universityrating = request.form['universityrating']
  attendsince = request.form['attendsince']
  userpassword = request.form['userpassword']
  cursor = g.conn.execute("SELECT email FROM Users_work")
  uueremail = []
  for result in cursor:
    uueremail.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  if useremail in uueremail:
        return redirect('/errorpage')
  cursor = g.conn.execute("SELECT MAX(user_id) FROM Users_work")
  userid = []
  for result in cursor:
    userid.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print userid[0]
  userid[0] = userid[0] + 1
  print userid[0]

  g.conn.execute('INSERT INTO Users_work(user_id, name, email, address, gender,password,usertype) VALUES(%s,%s,%s,%s,%s,%s,%s)', (userid[0], username, useremail, useraddress, usergender,userpassword,usertype))
  g.conn.execute('INSERT INTO Professors(user_id, department, position) VALUES(%s,%s,%s)', (userid[0], userdepartment, userposition))

  cursor = g.conn.execute("SELECT name FROM Universities")
  uuname = []
  for result in cursor:
    uuname.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  print uuname
  if universityname not in uuname:
    g.conn.execute('INSERT INTO Universities(name,rating) VALUES(%s,%s)',(universityname, universityrating))
  
  g.conn.execute('INSERT INTO From_University(user_id, name_uni, SINCE) VALUES(%s,%s,%s)', (userid[0], universityname, attendsince))

  return redirect('/')


               

# Example of adding new data to the database
@app.route('/logincheck', methods=['POST'])
def logincheck():
  
  useremail = request.form['useremail']
  userpassword = request.form['userpassword']
  print useremail
  print userpassword
  global usecheckemail  
  usecheckemail = useremail
  cursor = g.conn.execute("SELECT email,password FROM Users_work")
  logininfo = []
  for result in cursor:
    logininfo.append(result)  # can also be accessed using result[0]
  cursor.close()
  print logininfo   
  check = "bo2037@columbia.edu"
  
  for check in logininfo:
        if useremail == check[0]:
                 if userpassword == check[1]:
                        return redirect('/welcome')



  return redirect('/')                 

               
@app.route('/logout')
def logout():
  return redirect('/')  



@app.route('/login')
def login():
  return render_template("login.html")          
                 

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()

