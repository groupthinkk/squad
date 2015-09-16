import requests
from pymongo import MongoClient
from bson import objectid
from random import random
from math import ceil, factorial, pow
from operator import itemgetter

client = MongoClient("ds031903.mongolab.com", 31903)
db = client["squadtesting"]
db.authenticate("sweyn", "sweynsquad")

API_URL = "http://54.200.77.76/api/v0/instagram/posts/random"
API_KEY = 'CazMCDN5G2SuFhET3BuXdLIW01PQxisNLwKRIw'

def get_worker_id_past_tasks(worker_id, hit_id):
	return db.finishedusersids.find({"worker_id": worker_id,"hit_ids": hit_id}).count() != 0

def get_num_comparisons(worker_id, hit_id):
	return db.useranswers.find({'worker_id': worker_id, 'hit_id': hit_id}).count()

def is_comparison_done(worker_id, hit_id, comp_id):
	return db.useranswers.find({'worker_id': worker_id, 'hit_id': hit_id, "comp_id": comp_id}).count() > 0

def log_finished_worker(worker_id, hit_id):
	q = db.finishedusersids.find_one({'worker_id': worker_id})
	if q != None:
		q['right'] = db.useranswers.find({"worker_id": worker_id, "correct": 1}).count() * 1.0 / db.useranswers.find({"worker_id": worker_id}).count()
		if hit_id not in q['hit_ids']:
			q['hit_ids'].append(hit_id)
		db.finishedusersids.update({'worker_id': worker_id}, q)
	else:
		d = {}
		d['worker_id'] = worker_id
		d['hit_ids'] = [hit_id]
		d['right'] = db.useranswers.find({"worker_id": worker_id, "correct": 1}).count() * 1.0 / db.useranswers.find({"worker_id": worker_id}).count()
		db.finishedusersids.insert(d)
	rater_percentage = db.useranswers.find({"worker_id": worker_id, "hit_id": hit_id, "correct": 1}).count() * 1.0 / db.useranswers.find({"worker_id": worker_id, "hit_id": hit_id}).count()
	return round(rater_percentage, 5) * 100

def get_oo_comparison(username):
	past_comparisons = db.useranswers.find({'worker_id': username})
	calldata = {"api_key" : API_KEY}
	comparison_id_string = ','.join([x['comp_id'] for x in past_comparisons])
	if comparison_id_string != "":
		calldata['exclude'] = comparison_id_string
	resp = requests.post(API_URL,data=calldata)
	try:
		j = resp.json()
	except ValueError:
		return False
	di = []
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
	calldata = {
		"api_key" : API_KEY,
		"id" : id
	}
	return requests.get(API_URL, data=calldata).json()

def record_answer(worker_id, hit_id, right, id, seconds_used):
	d = {}
	d['worker_id'] = worker_id
	d['hit_id'] = hit_id
	d['comp_id'] = id
	d['correct'] = 1 if right == "correct" else 0
	d['seconds_used'] = seconds_used
	db.useranswers.insert(d)

