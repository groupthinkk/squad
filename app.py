from flask import Flask
from flask import render_template, url_for, redirect
from flask import request, session
from py import *
from flask.ext.basicauth import BasicAuth
from datetime import datetime, timedelta
import random
import logging

from hashlib import sha512

app = Flask(__name__)
app.secret_key = sha512("cybersec").hexdigest()
app.config['BASIC_AUTH_USERNAME'] = 'overlord'
app.config['BASIC_AUTH_PASSWORD'] = 'squad'

env = app.jinja_env
env.line_statement_prefix = '='

basic_auth = BasicAuth(app)

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "GET":
        session["worker_id"] = request.args.get("workerId", "")
        session["assignment_id"] =  request.args.get("assignmentId", "")
        session["amazon_host"] = request.args.get("turkSubmitTo", "") + "/mturk/externalSubmit"
        session["hit_id"] = request.args.get("hitId", "")

        if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
            return "You haven't accepted the HIT yet"
        return render_template("landing.html")
    else:
        rw = None
        if "start" in request.form:
            req = dbfunctions.submit_new_turk(session['worker_id'], session['hit_id'])
            if 'messages' in req and 'Hit with this Hit id and Turker already exists.' in req['messages']:
                if 'db_hit_id' not in session \
                    or 'comparison_queue' not in session \
                    or 'current_comparison' not in session \
                    or 'correct' not in session:
                    return """You already started this HIT and then tried to restart with an expired session. Please return this HIT.
                            Contact the administrator if you think there has been a mistake."""
            else:
                session.clear()
                session['db_hit_id'] = req['id']
                session['comparison_queue'] = req['instagram_queue']['comparisons']
                random.shuffle(session['comparison_queue'])
                session['current_comparison'] = 0
                session['correct'] = 0
        elif 'posttype' in request.form:
            time = datetime.now() - session['time']
            comp_id = request.form['compid']
            chosen_post_id = request.form['postid']
            miliseconds = time.seconds * 1000000 + time.microseconds
            worker_id = session['worker_id']
            db_hit_id = session['db_hit_id']
            ret = dbfunctions.record_comparison(db_hit_id, comp_id, chosen_post_id, miliseconds, "v0")
            print ret
            if 'messages' not in ret or 'Instagram prediction with this Hit and Comparison already exists.' not in ret['messages']:
                if ret["correct"]:
                    rw = "correct"
                    session['correct'] += 1
                else:
                    rw = "wrong"
            session['current_comparison'] += 1
        return render_new_post(rw)

def render_new_post(rw = None):
    worker_id = session['worker_id']
    hit_id = session['hit_id']
    current_comparison = session['current_comparison']
    comparison_queue = session['comparison_queue']
    if current_comparison >= len(comparison_queue):
        assignment_id = session['assignment_id']
        worker_id = session['worker_id']
        hit_id = session['hit_id']
        amazon_host = session['amazon_host']
        rater_percentage = round(session['correct'] * 100.0 / len(comparison_queue), 1)
        session.clear()
        return render_template("ending.html", assignment_id=assignment_id, worker_id=worker_id, hit_id=hit_id, rater_percentage=rater_percentage, amazon_host=amazon_host)
    else: 
        res = dbfunctions.get_comparison(comparison_queue[current_comparison])
        print res
        post1image = res["post_a"]["image_url"]
        post1id = res['post_a']['id']
        post2image = res["post_b"]["image_url"]
        post2id = res['post_b']['id']
        compid = comparison_queue[current_comparison]
        posttype = 'oo'
        session['time'] = datetime.now()
        return render_template("home.html", post1image = post1image, post1id=post1id, post2image = post2image, post2id=post2id, rw = rw, posttype = posttype, compid=compid)

if __name__ == '__main__':
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
    app.run()