import grequests
import requests
from pymongo import MongoClient
from random import random

client_id='375701af44384b6da4230f343a528b92'
client_secret='9620d4aef36f4e5b9139731497babcdb'

client = MongoClient()
db = client["guesswhich"]

def create_user_urls(id_list):
	l = []
	for user_id in id_list:
		url = ("https://api.instagram.com/v1/users/%s/media/recent/?client_id=%s") %(user_id, client_id)
		l.append(url)
	return l


def parse_user_data(json_data):
	json_data = json_data.json()
	l = []
	print json_data['data']
	for data in json_data['data']:
		post = {}
		post['likes'] = data['likes']['count']
		post['id'] = data['id']
		post['image'] = data['images']['standard_resolution']['url']
		post['rnd'] = random()
		post['username'] = data['user']['username']
		l.append(post)
	return l

def update():
	db.accountdata.drop()
	id_list = [(x['id']) for x in db.accountlist.find()]
	l = create_user_urls(id_list)
	rs = (grequests.get(i) for i in l)
	data = grequests.map(rs)
	ds = []
	for d in data:
		ds.append(parse_user_data(d))
	for d in ds:
		db.accountdata.insert(d)
	print "done"

def add_username(username):
	url = ('https://api.instagram.com/v1/users/search?q=%s&client_id=%s') % (username, client_id)
	j = requests.get(url).json()
	data = j['data'][0]
	if not data['username'] == username:
		print "nothing happened"
	else:
		db.accountlist.insert({'name': username,'id':str(data['id'])})

def get_two():
	d1 = 0
	d2 = 0
	while (not d1):
		d1 = db.accountdata.find_one({'$query': {'rnd': {'$gte': random()}}, '$orderby': { 'rnd': 1 }})
	while (not d2):
		d2 = db.accountdata.find_one({'$query': {'rnd': {'$gte': random()}, 'id': {'$ne': d1['id']}, 'username': d1['username']}, '$orderby': { 'rnd': 1 }})
	return [d1, d2]