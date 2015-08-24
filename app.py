from flask import Flask
from flask import render_template, url_for, redirect
from flask import request, session
from py import *
from flask.ext.basicauth import BasicAuth
from datetime import datetime

from hashlib import sha512

app = Flask(__name__)
app.secret_key = sha512("cybersec").hexdigest()
app.config['BASIC_AUTH_USERNAME'] = 'overlord'
app.config['BASIC_AUTH_PASSWORD'] = 'squad'

env = app.jinja_env
env.line_statement_prefix = '='

basic_auth = BasicAuth(app)

NUM_COMPARISONS = 100

@app.route("/", methods = ["GET", "POST"])
def index():
	if request.method == "GET":
		session["worker_id"] = request.args.get("workerId", "")
		session["assignment_id"] =  request.args.get("assignmentId", "")
		session["amazon_host"] = request.args.get("turkSubmitTo", "") + "/mturk/externalSubmit"
		session["hit_id"] = request.args.get("hitId", "")

		if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
			return "You haven't accepted the HIT yet"
		if dbfunctions.get_worker_id_past_tasks(session['worker_id'], session['hit_id']):
			return "You already did this hit"
		return render_template("landing.html")
	else:
		rw = None
		if 'posttype' in request.form or "post1likes" in session:
			time = datetime.now() - session['time']
			print time
			if 'compid' in request.form:
				comp_id = request.form['compid']
			else:
				comp_id = session['compid']
			if dbfunctions.is_comparison_done(session['worker_id'], session['hit_id'], comp_id):
				return render_new_post(session['worker_id'], session['hit_id'], "back")
			post1likes = session['post1likes']
			post2likes = session['post2likes']
			session.pop('post1likes', None)
			session.pop('post2likes', None)
			session.pop('compid', None)
			if post1likes >= post2likes:
				correct = 'post1'
			else:
				correct = 'post2'
			rw = False
			if correct in request.form or correct + ".x" in request.form and time < datetime.timedelta(seconds=20):
				rw = "correct"
			else:
				rw = "wrong"
			dbfunctions.record_answer(session["worker_id"], session["hit_id"], rw, comp_id, time.seconds + time.microseconds * 1.0 / 1000000)
		session['time'] = datetime.now()
		return render_new_post(session['worker_id'], session['hit_id'], rw)

def render_new_post(worker_id, hit_id, rw = None):
	posts = dbfunctions.get_two(worker_id)
	if posts == False or dbfunctions.get_num_comparisons(worker_id, hit_id) >= NUM_COMPARISONS:
		assignment_id = session['assignment_id']
		worker_id = session['worker_id']
		hit_id = session['hit_id']
		amazon_host = session['amazon_host']
		rater_percentage = dbfunctions.log_finished_worker(worker_id, hit_id)
		session.clear()
		return render_template("ending.html", assignment_id=assignment_id, worker_id=worker_id, hit_id=hit_id, rater_percentage=rater_percentage, amazon_host=amazon_host)
	session['post1likes'] = posts[0]
	session['post2likes'] = posts[1]
	post1image = posts[2]
	post2image = posts[3]
	posttype = posts[4]
	compid = posts[5]
	session['compid'] = compid
	return render_template("home.html", post1image = post1image, post2image = post2image, rw = rw, posttype = posttype, compid=compid)

if __name__ == '__main__':
    app.run(debug=True)