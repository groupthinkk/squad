from flask import Flask
from flask import render_template, url_for, redirect
from flask import request, session
from py import *
from flask.ext.basicauth import BasicAuth
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

from pymongo import MongoClient
from hashlib import sha512

app = Flask(__name__)
app.secret_key = sha512("cybersec").hexdigest()
app.config['BASIC_AUTH_USERNAME'] = 'overlord'
app.config['BASIC_AUTH_PASSWORD'] = 'squad'

env = app.jinja_env
env.line_statement_prefix = '='

basic_auth = BasicAuth(app)

if os.environ.get("DEV_ENV"):
	AMAZON_HOST = "https://workersandbox.mturk.com/mturk/externalSubmit"
else:
	AMAZON_HOST = "https://www.mturk.com/mturk/externalSubmit"

NUM_COMPARISONS = 1

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
		session["worker_id"] = request.args.get("workerId", "")
		session["assignment_id"] =  request.args.get("assignmentId", "")
		session["amazon_host"] = request.args.get("turkSubmitTo", "") + "/mturk/externalSubmit"
		session["hit_id"] = request.args.get("hitId", "")

		if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
			return "You haven't accepted the HIT yet"
		worker_id = request.args.get("workerId", "")
		if dbfunctions.get_worker_id_past_tasks(session['worker_id'], session['hit_id']):
			return "You already did this hit"
		return render_template("landing.html")
	else:
		rw = None
		if 'posttype' in request.form and request.form['posttype'] == 'oo':
			post1likes = session['post1likes']
			post2likes = session['post2likes']
			session['post1likes'] = ''
			session.pop('post1likes', None)
			session.pop('post2likes', None)
			if post1likes >= post2likes:
				correct = 'post1'
			else:
				correct = 'post2'
			rw = False
			if correct in request.form or correct + ".x" in request.form:
				rw = "correct"
			else:
				rw = "wrong"
			dbfunctions.record_answer(session["worker_id"], session["hit_id"], rw, request.form['compid'], request.form['secondsused'])
		if dbfunctions.get_num_comparisons(session["worker_id"], session['hit_id']) >= NUM_COMPARISONS:
			assignment_id = session['assignment_id']
			worker_id = session['worker_id']
			hit_id = session['hit_id']
			amazon_host = session['amazon_host']
			finish_id = dbfunctions.log_finished_worker(worker_id, hit_id)
			return render_template("ending.html", assignment_id=assignment_id, worker_id=worker_id, hit_id=hit_id, finish_id=finish_id, amazon_host=amazon_host)
		return render_new_post(session['worker_id'], rw)

def render_new_post(worker_id, rw = None):
	posts = dbfunctions.get_two(worker_id)
	session['post1likes'] = posts[0]
	session['post2likes'] = posts[1]
	post1image = posts[2]
	post2image = posts[3]
	posttype = posts[4]
	compid = posts[5]
	return render_template("home.html", post1image = post1image, post2image = post2image, rw = rw, posttype = posttype, compid=compid)

if __name__ == '__main__':
    app.run(debug=True)