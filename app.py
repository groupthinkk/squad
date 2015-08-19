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
			if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
				return "You haven't accepted the HIT yet"
			worker_id = request.args.get("workerId", "")
			if worker_id in dbfunctions.get_worker_ids_past_tasks():
				return "You already did this hit"
			else:
				#dbfunctions.log_worker(worker_id)
				pass
			session["worker_id"] = request.args.get("workerId", "")
			session["assignment_id"] =  request.args.get("assignmentId", "")
			session["amazon_host"] = AMAZON_HOST
			session["hit_id"] = request.args.get("hitId", "")
			return render_template("landing.html")
	else:
		rw = None
		if 'posttype' in request.form and request.form['posttype'] == 'oo':
			posts = dbfunctions.get_oo_comp_by_id(request.form['compid'])
			post1 = posts['posts'][0][0]
			post2 = posts['posts'][0][1]
			if post1['likes_count'] >= post2['likes_count']:
				correct = 'post1'
			else:
				correct = 'post2'
			rw = False
			if correct in request.form or correct + ".x" in request.form:
				rw = "correct"
			else:
				rw = "wrong"
			dbfunctions.record_answer(session["worker_id"], rw, request.form['compid'], request.form['secondsused'])
		if dbfunctions.get_num_comparisons(session["worker_id"]) >= NUM_COMPARISONS:
			assignment_id = session['assignment_id']
			worker_id = session['worker_id']
			hit_id = session['hit_id']
			finish_id = 0

			return render_template("ending.html", assignment_id=assignment_id, worker_id=worker_id, hit_id=hit_id, finish_id=finish_id)
		return render_new_post(session['worker_id'], rw)

def render_new_post(worker_id, rw = None):
	posts = dbfunctions.get_two(worker_id)
	post1image = posts[0]
	post2image = posts[1]
	posttype = posts[2]
	compid = posts[3]
	return render_template("home.html", post1image = post1image, post2image = post2image, rw = rw, posttype = posttype, compid=compid)

if __name__ == '__main__':
    app.run(debug=True)