import requests
from pymongo import MongoClient
from bson import objectid
from random import random
from math import ceil, factorial, pow
from operator import itemgetter

client = MongoClient("ds041841.mongolab.com", 41841)
db = client["heroku_7jhh76p4"]
db.authenticate("squad", "squadpass")

API_URL = "http://localhost:9991/api/v0/instagram/"

#client = MongoClient()
#db = client["SQUAD"]

def get_oo_comparison(username):
	past_comparisons = db.useranswers.find({'username': username})
	call_url = API_URL + "posts/random?api_key=CazMCDN5G2SuFhET3BuXdLIW01PQxisNLwKRIw?exclude="
	comparison_id_string = ','.join([x['comp_id'] for x in past_comparisons])
	request_url = call_url + comparison_id_string
	resp = requests.get(request_url)
	try:
		j = resp.json()
	except ValueError:
		return False
	di = []
	di.append(j['posts'][0][0]['image_url'])
	di.append(j['posts'][0][1]['image_url'])
	di.append('oo')
	di.append(j['id'])
	return di

def get_nn_comparison(username):
	d = db.comparisonsdata.find_one({'userlist': {'$ne': username}})
	if d is not None:
		di = []
		di.append(d['pic1'])
		di.append(d['pic2'])
		di.append('nn')
		di.append(str(d['_id']))
		return di
	else:
		return get_oo_comparison(username)

def get_two(username):
	rand  = random()
	user = db.userdata.find_one({'email': username})
	right = user['right']
	wrong = user['wrong']
	percentage = round(float(right)/(wrong+right) * 100) if right+wrong != 0 else 0
	if rand > .1 and percentage > 0:
		return get_nn_comparison(username)
	else:
		return get_oo_comparison(username)

def get_oo_comp_by_id(id):
	request_url = API_URL + 'posts/random?api_key=CazMCDN5G2SuFhET3BuXdLIW01PQxisNLwKRIw?id=' + id
	return requests.get(request_url).json()

def record_answer(username, right, id, seconds_used):
	d = {}
	d['username'] = username
	d['comp_id'] = id
	d['correct'] = 1 if right == "correct" else 0
	d['seconds_used'] = seconds_used
	db.useranswers.insert(d)

def record_comparison(username, answer, id, seconds_used):
	i = db.userdata.find_one({'email': username})
	right = i['right']
	wrong = i['wrong']
	d = {}
	d['username'] = username
	d['choice'] = answer
	d['percentage'] = round(float(right)/(wrong+right) * 100)
	if answer == 'post1':
		vote = 'vote1'
	else:
		vote = 'vote2'
	db.comparisonsdata.update({'_id': objectid.ObjectId(id)}, {'$push': {'responses': d, 'userlist': username}, '$inc': {vote: 1}})

def get_leaders():
	rtn = []
	results = db.userdata.find()
	for user in results:
		right = user['right']
		wrong = user['wrong']
		percentage = round(float(right)/(wrong+right) * 100) if right+wrong != 0 else 0
		rtn.append([user['email'], percentage])
	return sorted(rtn, key=itemgetter(1), reverse=True)

def insert_test_posts(pic1, pic2, id1, id2, user):
	test = {}
	test['pic1'] = pic1
	test['pic2'] = pic2
	test['id1'] = id1
	test['id2'] = id2
	test['user'] = user
	test['posts'] = [id1, id2]
	test['vote1'] = 0
	test['vote2'] = 0
	test['userlist'] = []
	test['responses'] = []
	db.comparisonsdata.insert(test)

def get_nn_comparisons(user):
	l = []
	r = db.comparisonsdata.find({'user': user})
	for i in r:
		winningimage = "Image 1" if i['vote1'] > i['vote2'] else "Image 2" if i['vote1'] < i['vote2'] else "Tie"
		if i['vote1'] + i['vote2'] != 0:
			votingpercentage = float(i['vote1'])/(i['vote1']+i['vote2'])*100 if i['vote1'] > i['vote2'] else float(i['vote2'])/(i['vote1']+i['vote2'])*100
		else:
			votingpercentage = 0
		juror_percentage = get_jurors_theorem(len(i['responses']), sum([element['percentage'] for element in i['responses']])/len(i['responses'])) if len(i['responses']) != 0 else 0
		l.append({
			"pic1": i['pic1'], 
			"pic2": i['pic2'], 
			"winningimage": winningimage,
			"votingpercentage": votingpercentage,
			"theorempercent": juror_percentage
			})
	return l

def get_jurors_theorem(N, p):
	m = int(ceil(N/2.0-1))+1 if N != 2 else 2
	ans = 0
	for i in range(m, N+1):
		ans = factorial(N)/(factorial(N-i)*factorial(i))*pow(p, i)*pow(1-p, N-i)
	return ans

def get_instagram_accounts():
	r = []
	q = db.accountlist.find()
	for entry in q:
		r.append(entry['name'])
	return r
