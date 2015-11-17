from flask import Flask
from flask import render_template, url_for, redirect
from flask import request, session
from py import *
from flask.ext.basicauth import BasicAuth
from datetime import datetime, timedelta
import random
import logging
import traceback

from hashlib import sha512

app = Flask(__name__)
app.secret_key = sha512("cybersec").hexdigest()
app.config['BASIC_AUTH_USERNAME'] = 'overlord'
app.config['BASIC_AUTH_PASSWORD'] = 'squad'

env = app.jinja_env
env.line_statement_prefix = '='

basic_auth = BasicAuth(app)

@app.route("/bigbonus", methods = ["GET"])
def big_bonus():
    try:
        if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
            return "You haven't accepted the HIT yet"
        try:
            if not (("worker_id" in session and session['worker_id'] == request.args.get("workerId")) \
                and ("assignment_id" in session and session['assignment_id'] == request.args.get("assignmentId")) \
                and ("hit_id" in session and session['hit_id'] == request.args.get("hitId"))):
                    session.clear()
                    session["worker_id"] = request.args.get("workerId")
                    session["assignment_id"] =  request.args.get("assignmentId")
                    session["amazon_host"] = request.args.get("turkSubmitTo") + "/mturk/externalSubmit"
                    session["hit_id"] = request.args.get("hitId")
                    if "queueId" in request.form:
                        session["queue_id"] = request.args.get("queueId")
        except:
            return "Initial request was malformed"
        return render_template("big_bonus_landing.html")
    except:
        return traceback.format_exc()

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "GET":
        try:
            if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
                return "You haven't accepted the HIT yet"
            try:
                if not (("worker_id" in session and session['worker_id'] == request.args.get("workerId")) \
                    and ("assignment_id" in session and session['assignment_id'] == request.args.get("assignmentId")) \
                    and ("hit_id" in session and session['hit_id'] == request.args.get("hitId"))):
                        session.clear()
                        session["worker_id"] = request.args.get("workerId")
                        session["assignment_id"] =  request.args.get("assignmentId")
                        session["amazon_host"] = request.args.get("turkSubmitTo") + "/mturk/externalSubmit"
                        session["hit_id"] = request.args.get("hitId")
                        if "queueId" in request.args:
                            session["queue_id"] = request.args.get("queueId")
            except:
                return "Initial request was malformed"
            return render_template("landing.html")
        except:
            return traceback.format_exc()
    else:
        try:
            rw = None
            if "start" in request.form:
                try:
                    if "queue_id" in session:
                        req = dbfunctions.submit_new_turk(session['worker_id'], session['hit_id'], session['queue_id'])
                    else:
                        req = dbfunctions.submit_new_turk(session['worker_id'], session['hit_id'])
                    if 'messages' in req and ('Hit with this Hit id and Turker already exists.' in req['messages'] or 'Hit with this Turker and Instagram queue already exists.' in req['messages']):
                        if 'db_hit_id' not in session \
                            or 'comparison_queue' not in session \
                            or 'current_comparison' not in session \
                            or 'correct' not in session:
                            return """You already started this HIT and then tried to restart with an expired session. Please return this HIT.
                                    Contact the administrator if you think there has been a mistake."""
                    elif 'messages' in req and 'No more queues available for turker_id:' in req['messages']:
                        return "We have no more queues for you. You've done too many HITs of ours for now. Please return this HIT. You're awesome!"
                    else:
                        session['db_hit_id'] = req['id']
                        session['comparison_queue'] = req['instagram_queue']['comparisons']
                        random.shuffle(session['comparison_queue'])
                        session['current_comparison'] = 0
                        session['correct'] = 0
                        session['contains_target'] = 0
                except Exception, e:
                    return traceback.format_exc()
            elif 'posttype' in request.form and request.form['posttype'] == 'oo':
                try:
                    time = datetime.now() - session['time']
                    comp_id = request.form['compid']
                    chosen_post_id = request.form['postid']
                    miliseconds = time.seconds * 1000000 + time.microseconds
                    worker_id = session['worker_id']
                    db_hit_id = session['db_hit_id']
                    ret = dbfunctions.record_comparison(db_hit_id, comp_id, chosen_post_id, miliseconds, "v1")
                    if 'messages' not in ret or 'Instagram prediction with this Hit and Comparison already exists.' not in ret['messages']:
                        if ret["contains_target"]:
                            rw = "correct"
                            session['contains_target'] += 1
                        elif ret["correct"]:
                            rw = "correct"
                            session['correct'] += 1
                        else:
                            rw = "wrong"
                except Exception, e:
                    return traceback.format_exc()
                session['current_comparison'] += 1
            else:
                session['current_comparison'] += 1
            return render_new_post(rw)
        except:
            return traceback.format_exc()

def render_new_post(rw):
    try:
        worker_id = session['worker_id']
        hit_id = session['hit_id']
        current_comparison = session['current_comparison']
        comparison_queue = session['comparison_queue']
        if current_comparison >= len(comparison_queue):
            assignment_id = session['assignment_id']
            worker_id = session['worker_id']
            hit_id = session['hit_id']
            amazon_host = session['amazon_host']
            rater_percentage = round(session['correct'] * 100.0 / (len(comparison_queue) - session['contains_target']), 1)
            return render_template("ending.html", assignment_id=assignment_id, worker_id=worker_id, hit_id=hit_id, rater_percentage=rater_percentage, amazon_host=amazon_host)
        else: 
            res = dbfunctions.get_comparison(comparison_queue[current_comparison])
            username = res['user']['username']
            profile = res['user']['image_url']
            post1image = res["post_a"]["image_url"]
            post1id = res['post_a']['id']
            post1likes = res['post_a']['likes_count']
            post1caption = res['post_a']['caption']
            post1timestamp = res['post_a']['created_datetime']
            post2image = res["post_b"]["image_url"]
            post2id = res['post_b']['id']
            post2likes = res['post_b']['likes_count']
            post2caption = res['post_b']['caption']
            post2timestamp = res['post_b']['created_datetime']
            compid = comparison_queue[current_comparison]
            posttype = 'oo'
            session['time'] = datetime.now()
            return render_template("home.html", username=username, profile=profile, \
                                   post1image = post1image, post1id=post1id, post1likes=post1likes, \
                                   post1caption=post1caption, post1timestamp=post1timestamp, \
                                   post2image = post2image, post2id=post2id, post2likes=post2likes, \
                                   post2caption=post2caption, post2timestamp=post2timestamp, \
                                   rw = None, posttype = posttype, compid=compid)
    except Exception, e:
        return traceback.format_exc()

if __name__ == '__main__':
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.run(debug=True)