from flask import Flask
from flask import render_template, url_for, redirect
from flask import request, session, flash
from urlparse import urlparse, urljoin
from py import *
from flask.ext.basicauth import BasicAuth
from datetime import datetime, timedelta
import random
import logging
import traceback
from pymongo import MongoClient
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask.ext.bcrypt import Bcrypt
from hashlib import sha512
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

client = MongoClient("ds037713-a0.mongolab.com", 37713)
db = client["turksquad"]
db.authenticate("sweyn", "sweynsquad")

account_sid = "AC92676a683900b40e7ba19d1b9a78a5ef"
auth_token = "4de6b64136ddfcf839562af528f9304e"
client = TwilioRestClient(account_sid, auth_token)

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

@app.route("/", methods = ["GET"])
@login_required
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    email = request.form["email"]
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
        db['users'].insert({"email": email, "pw_hash": bcrypt.generate_password_hash(password), "phone_number": phone_number, "ig_handle": ig_handle})
        client.messages.create(to=phone_number, from_="+19292947687", body="Thank you for registering! We'll be in touch with your first challenge soon. Reply STOP at any time to opt out.")
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

@app.route("/q/<int:queue_id>", methods = ["GET", "POST"])
@login_required
def queue_doer(queue_id):
    email = "test"
    if request.method == "GET":
        session["queue_id"] = queue_id
        return render_template("landing.html")
    else:
        try:
            rw = None
            if "start" in request.form:
                try:
                    req = dbfunctions.submit_new_turk(email, email + str(session['queue_id']), session['queue_id'])
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
        current_comparison = session['current_comparison']
        comparison_queue = session['comparison_queue']
        if current_comparison >= len(comparison_queue):
            rater_percentage = round(session['correct'] * 100.0 / (len(comparison_queue) - session['contains_target']), 1)
            return render_template("ending.html", rater_percentage=rater_percentage)
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
