from flask import Flask
from flask import render_template, url_for, redirect
from flask import request, session
from py import *

from pymongo import MongoClient
from hashlib import sha512

app = Flask(__name__)
app.secret_key = sha512("cybersec").hexdigest()

env = app.jinja_env
env.line_statement_prefix = '='

client = MongoClient()
db = client["SQUAD"]

@app.route("/", methods = ["GET", "POST"])
def index():
	if request.method == "GET":
		if 'loggedIn' in session:
			post = dbfunctions.get_two(session["loggedIn"])
			post1image = post[0]['image']
			post1id = post[0]['id']
			post2image = post[1]['image']
			post2id = post[1]['id']
			return render_template("home.html", post1image = post1image, post1id = post1id, post2image = post2image, post2id = post2id)
		else:
			return redirect(url_for("login"))
	else:
		posts = db.accountdata.find_one({'posts': [request.form['post1id'], request.form['post2id']]})
		post1 = posts['postdata'][0]
		post2 = posts['postdata'][1]
		if post1['likes'] >= post2['likes']:
			correct = 'post1'
		else:
			correct = 'post2'
		rw = False
		if correct in request.form:
			db.userdata.update({'email': session['loggedIn']}, {'$inc': {'right':1}})
			rw = "correct"
		else:
			db.userdata.update({'email': session['loggedIn']}, {'$inc': {'wrong':1}})
			rw = "wrong"
		db.accountdata.update({'posts': [request.form['post1id'], request.form['post2id']]}, {'$push': {'userlist': session["loggedIn"]}})
		dbfunctions.record_answer(session["loggedIn"], request.form['post1id'], request.form['post2id'], rw)
		post = dbfunctions.get_two(session["loggedIn"])
		post1image = post[0]['image']
		post1id = post[0]['id']
		post2image = post[1]['image']
		post2id = post[1]['id']
		return render_template("home.html", post1image = post1image, post1id = post1id, post2image = post2image, post2id = post2id, rw = rw)

@app.route("/leaderboard", methods = ["GET"])
def leaderboard():
	leaders = dbfunctions.get_leaders()
	return render_template("leaderboard.html", leaders=leaders)

@app.route("/stats", methods = ["GET", "POST"])
def stats():
	user = db.userdata.find_one({'email': session['loggedIn']})
	right = user['right']
	wrong = user['wrong']
	percentage = round(float(right)/(wrong+right) * 100)
	print right, wrong, percentage
	return render_template("stats.html", right=right, wrong=wrong, percentage=percentage)

@app.route("/login", methods = ["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")
	else:
		email = request.form["email"]
		password = request.form["password"]
		result = db.userdata.find_one({"email": email})
		if result is not None and password == result["password"]:
			session["loggedIn"] = email
			return redirect(url_for("index"))
		else:
			return redirect(url_for("login"))

@app.route("/register", methods = ["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register.html")

	email = request.form["email"]
	password = request.form["password"]
	password2 = request.form["password2"]

	result = db.userdata.find_one({"email": email})

	if result is not None:
		return redirect(url_for("register"))
	elif password == password2:
		db.userdata.insert({"email": email, "password": password, "right": 0, "wrong": 0})
		return redirect(url_for("index"))
	else:
		return redirect(url_for("register"))

@app.route("/logout")
def logout():
	if "admin" in session:
		session.pop("admin")
		return redirect(url_for("admin"))
	else:
		session.pop("loggedIn")
		return redirect(url_for("index"))

@app.route("/admin", methods = ["GET", "POST"])
def admin():
	if 'admin' not in session:
		return redirect(url_for("adminlogin"))
	if request.method == "GET":
		return render_template("admin.html")
	else:
		username = request.form['username']
		instagramfunctions.add_username(username)
		return render_template("admin.html", message="Username %s added!" % (username))

@app.route("/adminlogin", methods = ["GET", "POST"])
def adminlogin():
	if request.method == "GET":
		return render_template("adminlogin.html")
	else:
		email = request.form["email"]
		password = request.form["password"]
		result = db.admindata.find_one({"email": email})
		if result is not None and password == result["password"]:
			session["admin"] = email
			return redirect(url_for("admin"))
		else:
			return redirect(url_for("adminlogin"))

@app.route("/adminregister", methods = ["GET", "POST"])
def adminregister():
	if request.method == "GET":
		return render_template("adminregister.html")
	else:
		email = request.form["email"]
		password = request.form["password"]
		password2 = request.form["password2"]

		result = db.admindata.find_one({"email": email})

		if result is not None:
			return redirect(url_for("adminregister"))
		elif password == password2:
			db.admindata.insert({"email": email, "password": password})
			return redirect(url_for("adminlogin"))
		else:
			return redirect(url_for("adminregister"))

@app.route("/updatedata")
def updatedata():
	instagramfunctions.update()
	return redirect(url_for('index'))

if __name__ == "__main__":
	app.run(debug = True)