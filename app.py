from flask import Flask
from flask import render_template, url_for, redirect
from flask import request, session, flash
from urlparse import urlparse, urljoin
from py import *
from flask.ext.basicauth import BasicAuth
from datetime import datetime, timedelta
from operator import itemgetter
from itertools import groupby
import random
import logging
import traceback
from pymongo import MongoClient
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask.ext.bcrypt import Bcrypt
from hashlib import sha512
from threading import Lock
from twilio.rest import TwilioRestClient

app = Flask(__name__)
app.secret_key = sha512("cybersec").hexdigest()
app.config['BASIC_AUTH_USERNAME'] = 'overlord'
app.config['BASIC_AUTH_PASSWORD'] = 'squad'

env = app.jinja_env
env.line_statement_prefix = '='

basic_auth = BasicAuth(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

bcrypt = Bcrypt(app)

lock = Lock()

client = MongoClient("ds037713-a0.mongolab.com", 37713)
db = client["turksquad"]
db.authenticate("sweyn", "sweynsquad")

account_sid = "AC92676a683900b40e7ba19d1b9a78a5ef"
auth_token = "4de6b64136ddfcf839562af528f9304e"
twilio_client = TwilioRestClient(account_sid, auth_token)

OVERALL_REWARDS = [50, 20, 15, 10, 10, 5, 5, 5, 5, 5]

WEEKLY_REWARDS = [10, 5, 5, 5, 5]

class User(UserMixin):

    def __init__(self, username, phone_number):
        self.id = username
        self.phone_number = phone_number

@login_manager.user_loader
def load_user(username):
    user_entry = db['users'].find_one({'email':username})
    if user_entry == None:
        return None
    user = User(username, user_entry['phone_number'])
    return user

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

@app.route("/testaction", methods = ["GET"])
@login_required
def test_action():
    session['current_comparison'] = 1000
    return redirect(url_for('queue_doer'))

@app.route("/", methods = ["GET"])
@login_required
def index():
    more_queues = db.users.find_one({'email':current_user.id})['available_queues'] > 0
    return render_template("index.html", more_queues=more_queues)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    email = request.form["email"]
    name = request.form["name"]
    password = request.form["password"]
    password2 = request.form["password2"]
    phone_number = request.form['phone_number'].replace('-', '').replace('(', '').replace(')', '')
    ig_handle = request.form['ig_handle']
    reg_code = request.form['reg_code']
    if db['reg_codes'].find_one({'reg_code':reg_code}) == None:
        return render_template("register.html", message="Registration code is not valid")
    result = db['users'].find_one({"email": email})
    if result is not None:
        return render_template("register.html", message="Email already registered")
    elif password == password2:
        db['users'].insert({"email": email, "name": name, "score": 0, "weekly_score": 0, 'available_queues': 3, "pw_hash": bcrypt.generate_password_hash(password), "phone_number": phone_number, "ig_handle": ig_handle})
        try:
            twilio_client.messages.create(to=phone_number, from_="+19292947687", body="Thank you for registering! We'll be in touch with your first challenge soon. Reply STOP at any time to opt out.")
        except:
            pass
        user = User(email, phone_number)
        login_user(user, remember=True)
        return redirect(url_for('index'))
    else:
        return render_template("register.html", message="Passwords don't match")

@app.route('/login', methods=['GET', 'POST'])
def login():
    next = get_redirect_target()
    if request.method == 'GET':
        return render_template("login.html", next=next)
    email = request.form['email']
    user_entry = db['users'].find_one({'email':email})
    if user_entry != None and bcrypt.check_password_hash(user_entry['pw_hash'], request.form['password']):
        user = User(email, user_entry['phone_number'])
        login_user(user, remember=True)
        flash('Logged in successfully.')
        print 'logged in'
        return redirect_back('index')
    return render_template('login.html', message="Incorrect username and password")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/q", methods = ["GET", "POST"])
@login_required
def queue_doer():
    if request.method == "GET":
        return render_template("landing.html")
    else:
        try:
            rw = None
            if "start" in request.form:
                if 'queue_id' not in session or \
                        'db_hit_id' not in session or \
                        'comparison_queue' not in session or \
                        'current_comparison' not in session or \
                        'correct' not in session or \
                        'contains_target' not in session:
                    if db.users.find_one({'email':current_user.id})['available_queues'] == 0:
                        return redirect(url_for('index'))
                    try:
                        with lock:
                            session['queue_id'] = db.queue_num.find_one()['queue_num']
                            db.queue_num.update({'queue_num':session['queue_id']}, {'$inc':{'queue_num':1}})
                        req = dbfunctions.submit_new_turk(current_user.id, "queue" + str(session['queue_id']), session['queue_id'])
                        if 'messages' in req and ('Hit with this Hit id and Turker already exists.' in req['messages'] or 'Hit with this Turker and Instagram queue already exists.' in req['messages']):
                            if 'queue_id' not in session or \
                                    'db_hit_id' not in session or \
                                    'comparison_queue' not in session or \
                                    'current_comparison' not in session or \
                                    'correct' not in session or \
                                    'contains_target' not in session:
                                return """You already started this queue and navigated away."""
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
                print "hi", db['users'].find_one({'email':current_user.id})
                try:
                    time = datetime.now() - session['time']
                    comp_id = request.form['compid']
                    chosen_post_id = request.form['postid']
                    miliseconds = time.seconds * 1000000 + time.microseconds
                    db_hit_id = session['db_hit_id']
                    ret = dbfunctions.record_comparison(db_hit_id, comp_id, chosen_post_id, miliseconds, "v1")
                    if 'messages' not in ret or 'Instagram prediction with this Hit and Comparison already exists.' not in ret['messages']:
                        if ret["contains_target"]:
                            rw = "correct"
                            session['contains_target'] += 1
                            session['correct'] += 1
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
            current_comparison = session['current_comparison']
            comparison_queue = session['comparison_queue']
            if current_comparison >= len(comparison_queue):
                correct = session['correct']
                add_score = 0
                if correct > 15:
                    add_score = 1
                elif correct > 17:
                    add_score = 3
                elif correct > 20:
                    add_score = 5
                if add_score > 0:
                    db['users'].update({'email':current_user.id}, {'$inc':{'score': add_score}, '$inc':{'weekly_score': add_score}, '$inc':{'available_queues': -1}})
            return render_new_post(rw)
        except:
            return traceback.format_exc()

def render_new_post(rw):
    try:
        current_comparison = session['current_comparison']
        comparison_queue = session['comparison_queue']
        if current_comparison >= len(comparison_queue):
            rater_percentage = round(session['correct'] * 100.0 / (len(comparison_queue)), 1)
            num_right = session['correct']
            all_user_results = list(db['users'].find().sort("score", -1))
            all_users_grouped = groupby(all_user_results, lambda x: x['score'])
            overall_leaderboard_users = []
            rank = 1
            your_index = 0
            for _, user_group in all_users_grouped:
                user_group = list(user_group)
                num_users = len(user_group)
                reward = round(sum(OVERALL_REWARDS[rank-1:rank+num_users-1])/float(num_users), 2) if rank < 11 else ''
                placed_rank = rank
                for user in user_group:
                    if user['email'] == current_user.id:
                        user['current_user'] = 'you'
                    else:
                        user['current_user'] = False
                    user['rank'] = placed_rank
                    if reward == '':
                        user['reward'] = reward
                    elif reward == int(reward):
                        user['reward'] = '$' + str(int(reward))
                    else:
                        user['reward'] = '$' + str(round(reward, 2))
                    if rank < len(OVERALL_REWARDS) + 1:
                        overall_leaderboard_users.append(user)
                    placed_rank = '' if reward != '' else placed_rank
                rank += num_users
            your_index = 0
            for i in xrange(len(all_user_results)):
                if all_user_results[i]['email'] == current_user.id:
                    your_index = i
                    break
            print all_user_results
            if your_index > 2:
                around_me = all_user_results[your_index-2:your_index+3]
            else:
                around_me = all_user_results[:your_index+3]
            if len(set([x['email'] for x in (overall_leaderboard_users + around_me)])) == len(overall_leaderboard_users+around_me):
                overall_leaderboard_users += [{'current_user' : 'break'}] + around_me
            else:
                for user in around_me:
                    if [el for el in overall_leaderboard_users if el['email'] == user['email']] == 0:
                        overall_leaderboard_users.append(user)
            weekly_user_results = list(db['users'].find().sort("weekly_score", -1))
            weekly_users_grouped = groupby(weekly_user_results, lambda x: x['weekly_score'])
            weekly_leaderboard_users = []
            rank = 1
            your_index = 0
            for _, user_group in weekly_users_grouped:
                user_group = list(user_group)
                num_users = len(user_group)
                reward = round(sum(OVERALL_REWARDS[rank-1:rank+num_users-1])/float(num_users), 2) if rank < 11 else ''
                placed_rank = rank
                for user in user_group:
                    if user['email'] == current_user.id:
                        user['current_user'] = 'you'
                    else:
                        user['current_user'] = False
                    user['rank'] = placed_rank
                    if reward == '':
                        user['reward'] = reward
                    elif reward == int(reward):
                        user['reward'] = '$' + str(int(reward))
                    else:
                        user['reward'] = '$' + str(round(reward, 2))
                    if rank < len(WEEKLY_REWARDS) + 1:
                        weekly_leaderboard_users.append(user)
                    placed_rank = '' if reward != '' else placed_rank
                rank += num_users
            your_index = 0
            for i in xrange(len(weekly_user_results)):
                if weekly_user_results[i]['email'] == current_user.id:
                    your_index = i
                    break
            if your_index > 2:
                around_me = weekly_user_results[your_index-2:your_index+3]
            else:
                around_me = weekly_user_results[:your_index+3]
            if len(set([x['email'] for x in (weekly_leaderboard_users + around_me)])) == len(weekly_leaderboard_users+around_me):
                weekly_leaderboard_users += [{'current_user' : 'break'}] + around_me
            else:
                for user in around_me:
                    if [el for el in weekly_leaderboard_users if el['email'] == user['email']] == 0:
                        weekly_leaderboard_users.append(user)
            more_queues = db.users.find_one({'email':current_user.id})['available_queues'] > 0
            session.clear()
            return render_template("ending.html", rater_percentage=rater_percentage, num_right=num_right, overall_leaderboard_users=overall_leaderboard_users, weekly_leaderboard_users=weekly_leaderboard_users, more_queues = more_queues)
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
            correct = session['correct']
            remaining = len(comparison_queue[current_comparison:])
            return render_template("home.html", username=username, profile=profile, \
                                   post1image = post1image, post1id=post1id, post1likes=post1likes, \
                                   post1caption=post1caption, post1timestamp=post1timestamp, \
                                   post2image = post2image, post2id=post2id, post2likes=post2likes, \
                                   post2caption=post2caption, post2timestamp=post2timestamp, \
                                   rw = None, posttype = posttype, compid=compid, correct=correct, remaining=remaining)
    except Exception, e:
        return traceback.format_exc()

if __name__ == '__main__':
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.run(debug=True)
