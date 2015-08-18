from flask import Flask
from flask import render_template, url_for, redirect
from flask import request, session
from py import *
from flask.ext.basicauth import BasicAuth
import cloudinary
import cloudinary.uploader
import cloudinary.api

from pymongo import MongoClient
from hashlib import sha512

app = Flask(__name__)
app.secret_key = sha512("cybersec").hexdigest()
app.config['BASIC_AUTH_USERNAME'] = 'overlord'
app.config['BASIC_AUTH_PASSWORD'] = 'squad'

env = app.jinja_env
env.line_statement_prefix = '='

basic_auth = BasicAuth(app)

#client = MongoClient()
#db = client["SQUAD"]

#client = MongoClient("ds041841.mongolab.com", 41841)
#db = client["heroku_7jhh76p4"]
#db.authenticate("squad", "squadpass")

client = MongoClient("ds031903.mongolab.com", 31903)
db = client["squadtesting"]
db.authenticate("sweyn", "sweynsquad")

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@app.route("/", methods = ["GET", "POST"])
def index():
	if request.method == "GET":
		if 'loggedIn' in session:
			posts = dbfunctions.get_two(session["loggedIn"])
			if posts == False:
				return render_template("home.html", rw = "nomore", posttype = '', compid = 0)
			post1image = posts[0]
			post2image = posts[1]
			posttype = posts[2]
			compid = posts[3]
			return render_template("home.html", post1image = post1image, post2image = post2image, posttype = posttype, compid=compid)
		else:
			return redirect(url_for("login"))
	else:
		if request.form['posttype'] == 'oo':
			posts = dbfunctions.get_oo_comp_by_id(request.form['compid'])
			post1 = posts['posts'][0][0]
			post2 = posts['posts'][0][1]
			if post1['likes_count'] >= post2['likes_count']:
				correct = 'post1'
			else:
				correct = 'post2'
			rw = False
			if correct in request.form or correct + ".x" in request.form:
				db.userdata.update({'email': session['loggedIn']}, {'$inc': {'right':1}})
				rw = "correct"
			else:
				db.userdata.update({'email': session['loggedIn']}, {'$inc': {'wrong':1}})
				rw = "wrong"
			dbfunctions.record_answer(session["loggedIn"], rw, request.form['compid'], request.form['secondsused'])
		else:
			if 'post1' in request.form:
				answer = 'post1'
			else:
				answer = 'post2'
			rw = "neither"
			dbfunctions.record_comparison(session['loggedIn'], answer, request.form['compid'], request.form['secondsused'])
		posts = dbfunctions.get_two(session["loggedIn"])
		if posts == False:
			return render_template("home.html", rw = "nomore", posttype = '', compid = 0)
		post1image = posts[0]
		post2image = posts[1]
		posttype = posts[2]
		compid = posts[3]
		return render_template("home.html", post1image = post1image, post2image = post2image, rw = rw, posttype = posttype, compid=compid)

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
@basic_auth.required
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

def allowed_file(filename):
	return '.' in filename and \
    	filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/admin", methods = ["GET", "POST"])
def admin():
	if 'admin' not in session:
		return redirect(url_for("adminlogin"))
	usernames = dbfunctions.get_instagram_accounts()
	if request.method == "GET":
		comparisons = dbfunctions.get_nn_comparisons(session['admin'])
		return render_template("admin.html", comparisons=comparisons, usernames=usernames)
	else:
		if 'addname' in request.form:
			username = request.form['username']
			result = instagramfunctions.add_username(username)
			if result:
				message = "Username %s added!" % (username)
				t = "Success"
			else:
				message = "Duplicate name or name does not exist"
				t = "Failure"
			usernames = dbfunctions.get_instagram_accounts()
			comparisons = dbfunctions.get_nn_comparisons(session['admin'])
			return render_template("admin.html", message=message,type=t , comparisons=comparisons, usernames=usernames)
		else:
			pic1 = request.files['pic1']
			pic2 = request.files['pic2']
			if pic1 and pic2 and allowed_file(pic1.filename) and allowed_file(pic2.filename):
				pic1response = cloudinary.uploader.upload(pic1)
				pic2response = cloudinary.uploader.upload(pic2)
				dbfunctions.insert_test_posts(pic1response['url'], 
												pic2response['url'],
												pic1response['public_id'],
												pic2response['public_id'],
												session['admin'])
				comparisons = dbfunctions.get_nn_comparisons(session['admin'])
				return render_template("admin.html", comparisonmessage="Comparison added!", comparisons=comparisons, usernames=usernames)

@app.route("/admin/login", methods = ["GET", "POST"])
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

@app.route("/admin/register", methods = ["GET", "POST"])
@basic_auth.required
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