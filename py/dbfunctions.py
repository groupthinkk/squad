import grequests
import requests
from pymongo import MongoClient
from random import random
from math import ceil, factorial, pow
from operator import itemgetter

client = MongoClient("ds061721.mongolab.com", 61721)
db = client["squad"]
db.authenticate("squad", "squadpass")

#client = MongoClient()
#db = client["SQUAD"]

def get_two(username):
	rand  = random()
	user = db.userdata.find_one({'email': username})
	right = user['right']
	wrong = user['wrong']
	percentage = round(float(right)/(wrong+right) * 100) if right+wrong != 0 else 0
	if rand > .9 and percentage > 50:
		d = db.comparisonsdata.find_one({'userlist': {'$ne': username}})
		if d is not None:
			di = [{}, {}]
			di[0]['image'] = d['pic1']
			di[0]['id'] = d['id1']
			di[1]['image'] = d['pic2']
			di[1]['id'] = d['id2']
			return [di, "nn"]
	rand = random()
	d = db.accountdata.find_one({'userlist': {'$ne': username}, 'rnd': {'$gte': rand}})
	if d is None:
		d = db.accountdata.find_one({'userlist': {'$ne': username}, 'rnd': {'$lte': rand}})
	if d is None:
		return False
	return [d['postdata'], "oo"]

def record_answer(username, id1, id2, right):
	d = {}
	d['username'] = username
	d['posts'] = [id1, id2]
	d['correct'] = 1 if right == "correct" else 0
	db.useranswers.insert(d)

def record_comparison(username, id1, id2, answer):
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
	db.comparisonsdata.update({'posts': [id1, id2]}, {'$push': {'responses': d, 'userlist': username}, '$inc': {vote: 1}})

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

