import grequests
import requests
from pymongo import MongoClient
from random import random

client = MongoClient()
db = client["SQUAD"]

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
		return "you're out"
	return [d['postdata'], "oo"]

def record_answer(username, id1, id2, right):
	d = {}
	d['username'] = username
	d['posts'] = [id1, id2]
	d['correct'] = 1 if right == "correct" else 0
	db.useranswers.insert(d)

def record_comparison(username, id1, id2, answer):
	d = {}
	d['username'] = username
	d['choice'] = answer
	if answer == 'post1':
		vote = 'vote1'
	else:
		vote = 'vote2'
	db.comparisonsdata.update({'posts': [id1, id2]}, {'$push': {'responses': d}, '$push': {'userlist': username}, '$inc': {vote: 1}})

def get_leaders():
	rtn = []
	results = db.userdata.find()
	for user in results:
		right = user['right']
		wrong = user['wrong']
		percentage = round(float(right)/(wrong+right) * 100) if right+wrong != 0 else 0
		rtn.append([user['email'], percentage])
	return rtn

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
		l.append({
			"pic1": i['pic1'], 
			"pic2": i['pic2'], 
			"winningimage": winningimage,
			"votingpercentage": votingpercentage
			})
	return l
