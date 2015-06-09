import grequests
import requests
from pymongo import MongoClient
from random import random

client = MongoClient()
db = client["SQUAD"]

def get_two(username):
	rand = random()
	print rand
	d = db.accountdata.find_one({'userlist': {'$ne': username}, 'rnd': {'$gte': rand}})
	if d is None:
		d = db.accountdata.find_one({'userlist': {'$ne': username}, 'rnd': {'$lte': rand}})
	if d is None:
		return "you're out"
	print d['postdata']
	return d['postdata']

def record_answer(username, id1, id2, right):
	d = {}
	d['username'] = username
	d['posts'] = [id1, id2]
	d['correct'] = 1 if right == "correct" else 0
	db.useranswers.insert(d)

def get_leaders():
	rtn = []
	results = db.userdata.find()
	for user in results:
		right = user['right']
		wrong = user['wrong']
		percentage = round(float(right)/(wrong+right) * 100) if right+wrong != 0 else 0
		rtn.append([user['email'], percentage])
	return rtn
