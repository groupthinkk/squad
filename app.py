from flask import Flask
from flask import render_template, url_for, redirect
from flask import request, session
from py import *
import uuid
import os
from flask import send_from_directory
from flask.ext.basicauth import BasicAuth

from pymongo import MongoClient
from hashlib import sha512
UPLOAD_FOLDER = "comparisons"

app = Flask(__name__)
app.secret_key = sha512("cybersec").hexdigest()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BASIC_AUTH_USERNAME'] = 'overlord'
app.config['BASIC_AUTH_PASSWORD'] = 'squad'

env = app.jinja_env
env.line_statement_prefix = '='

basic_auth = BasicAuth(app)

#client = MongoClient()
#db = client["SQUAD"]

client = MongoClient("ds041841.mongolab.com", 41841)
db = client["heroku_7jhh76p4"]
db.authenticate("squad", "squadpass")

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@app.route("/", methods = ["GET", "POST"])
def index():
	if request.method == "GET":
		if 'loggedIn' in session:
			post = dbfunctions.get_two(session["loggedIn"])
			print post
			post1image = post[0][0]['image']
			post1id = post[0][0]['id']
			post2image = post[0][1]['image']
			post2id = post[0][1]['id']
			posttype = post[1]
			return render_template("home.html", post1image = post1image, post1id = post1id, post2image = post2image, post2id = post2id, posttype = posttype)
		else:
			return redirect(url_for("login"))
	else:
		if request.form['posttype'] == 'oo':
			posts = db.accountdata.find_one({'posts': [request.form['post1id'], request.form['post2id']]})
			if posts == False:
				return render_template("home.html", rw = "nomore", posttype = posttype)
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
		else:
			print 'posttype' + request.form['posttype']
			if 'post1' in request.form:
				answer = 'post1'
			else:
				answer = 'post2'
			rw = "neither"
			dbfunctions.record_comparison(session['loggedIn'], request.form['post1id'], request.form['post2id'], answer)
		post = dbfunctions.get_two(session["loggedIn"])
		print post
		post1image = post[0][0]['image']
		post1id = post[0][0]['id']
		post2image = post[0][1]['image']
		post2id = post[0][1]['id']
		posttype = post[1]
		return render_template("home.html", post1image = post1image, post1id = post1id, post2image = post2image, post2id = post2id, rw = rw, posttype = posttype)

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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],
    							filename)

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
			filename1 = str(uuid.uuid4())
			filename2 = str(uuid.uuid4())
			pic1 = request.files['pic1']
			pic2 = request.files['pic2']
			print pic1
			print pic2
			if pic1 and pic2 and allowed_file(pic1.filename) and allowed_file(pic2.filename):
				path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1 + "." + pic1.filename.rsplit('.', 1)[1])
				path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2 + "." + pic2.filename.rsplit('.', 1)[1])
				pic1.save(path1)
				pic2.save(path2)
				dbfunctions.insert_test_posts("uploads/" + filename1 + "." + pic1.filename.rsplit('.', 1)[1], 
												"uploads/" + filename2 + "." + pic2.filename.rsplit('.', 1)[1],
												filename1,
												filename2,
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