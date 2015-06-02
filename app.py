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
db = client["guesswhich"]

@app.route("/", methods = ["GET", "POST"])
def index():
	if request.method == "GET":
		if 'loggedIn' in session:
			post = instagramfunctions.get_two()
			post1image = post[0]['image']
			post1id = post[0]['id']
			post2image = post[1]['image']
			post2id = post[1]['id']
			return render_template("home.html", post1image = post1image, post1id = post1id, post2image = post2image, post2id = post2id)
		else:
			return redirect(url_for("login"))
	else:
		post1 = db.accountdata.find_one({'id':request.form['post1id']})
		post2 = db.accountdata.find_one({'id':request.form['post2id']})
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
		post = instagramfunctions.get_two()
		post1image = post[0]['image']
		post1id = post[0]['id']
		post2image = post[1]['image']
		post2id = post[1]['id']
		return render_template("home.html", post1image = post1image, post1id = post1id, post2image = post2image, post2id = post2id, rw = rw)

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
		#return redirect(url_for("register"))
		return "no"
	elif password == password2:
		db.userdata.insert({"email": email, "password": password, "right": 0, "wrong": 0})
		return redirect(url_for("index"))
	else:
		#return redirect(url_for("register"))
		return "hi"

@app.route("/add", methods = ["GET", "POST"])
def add():
	if request.method == "GET":
		return render_template("add.html")
	else:
		username = request.form['username']
		instagramfunctions.add_username(username)
		return render_template("add.html", message="Username %s added!" % (username))

@app.route("/logout")
def logout():
	session.pop("loggedIn")
	return redirect(url_for("index"))

@app.route("/updatedata")
def updatedata():
	instagramfunctions.update()
	return redirect(url_for('index'))

if __name__ == "__main__":
	app.run(debug = False)