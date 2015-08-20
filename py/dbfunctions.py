import requests
from pymongo import MongoClient
from bson import objectid
from random import random
from math import ceil, factorial, pow
from operator import itemgetter

#client = MongoClient("ds041841.mongolab.com", 41841)
#db = client["heroku_7jhh76p4"]
#db.authenticate("squad", "squadpass")

client = MongoClient("ds031903.mongolab.com", 31903)
db = client["squadtesting"]
db.authenticate("sweyn", "sweynsquad")

API_URL = "http://54.200.77.76/api/v0/instagram/"

def get_worker_ids_past_tasks():
	yield db.finishedusersids.find()

def get_num_comparisons(worker_id):
	return db.useranswers.find({'worker_id': worker_id}).count()

def log_finished_worker(worker_id, hash):
	d = {}
	d['worker_id'] = worker_id
	d['hashlist']
	d['right'] = db.useranswers

def get_oo_comparison(username):
	past_comparisons = db.useranswers.find({'worker_id': username})
	call_url = API_URL + "posts/random?api_key=CazMCDN5G2SuFhET3BuXdLIW01PQxisNLwKRIw" 
	comparison_id_string = ','.join([x['comp_id'] for x in past_comparisons])
	if comparison_id_string != "":
		request_url = call_url + "&exclude=" + comparison_id_string
	else:
		request_url = call_url
	print request_url
	resp = requests.get(request_url)
	try:
		j = resp.json()
	except ValueError:
		return False
	di = []
	print j
	di.append(j['posts'][0][0]['likes_count'])
	di.append(j['posts'][0][1]['likes_count'])
	di.append(j['posts'][0][0]['image_url'])
	di.append(j['posts'][0][1]['image_url'])
	di.append('oo')
	di.append(j['id'])
	return di

def get_two(username):
	return get_oo_comparison(username)

def get_oo_comp_by_id(id):
	request_url = API_URL + 'posts/random?api_key=CazMCDN5G2SuFhET3BuXdLIW01PQxisNLwKRIw&id=' + id
	return requests.get(request_url).json()

def record_answer(username, right, id, seconds_used):
	d = {}
	d['worker_id'] = username
	d['comp_id'] = id
	d['correct'] = 1 if right == "correct" else 0
	d['seconds_used'] = seconds_used
	db.useranswers.insert(d)

