import requests
from pymongo import MongoClient
from bson import objectid
from random import random
from math import ceil, factorial, pow
from operator import itemgetter

API_KEY = 'CazMCDN5G2SuFhET3BuXdLIW01PQxisNLwKRIw'

def submit_new_turk(turk_id, hit_id):
	API_URL = "http://54.200.77.76/api/v0/predictions/turkers/"
	data = {
	    'api_key': API_KEY,
	    'turker_id': turk_id
	}
	print requests.post(API_URL, data=data).text
	API_URL = "http://54.200.77.76/api/v0/predictions/hits/"
	data = {
	    'api_key': API_KEY,
	    'turker_id': turk_id,
	    'hit_id': hit_id
	}
	req = requests.post(API_URL, data=data)
	print req.text
	return req.json()

def get_comparison(comparison_id):
	API_URL = "http://54.200.77.76/api/v0/instagram/posts/comparisons/"
	data = {
		'api_key': API_KEY,
		'id': comparison_id
	}
	req = requests.get(API_URL, params=data)
	print req
	return req.json()['results'][0]

def record_comparison(turk_id, comparison_id, choice_id, dec_miliseconds, ux_id):
    API_URL = "http://54.200.77.76/api/v0/predictions/instagram/"
    data = {
        'api_key': API_KEY,
        'hit_id': turk_id,
        'comparison_id': comparison_id,
        'choice_id': choice_id,
        'decision_milliseconds': dec_miliseconds,
        'ux_id': ux_id
    }
    req = requests.post(API_URL, data=data)
    return req.json()

if __name__ == '__main__':
	record_comparison("turker_0003", 1, 2605, 11, "1")