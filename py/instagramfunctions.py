import grequests
import requests
from pymongo import MongoClient
from random import random

from gevent import monkey; monkey.patch_all()

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
	for data in json_data['data']:
		post = {}
		post['likes'] = data['likes']['count']
		post['id'] = data['id']
		post['image'] = data['images']['standard_resolution']['url']
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
	inserts = []
	for d in ds:
		print d
		print len(d)
		for x in range(len(d)-1):
			for y in range(x+1, len(d)):
				print x, y
				p = {}
				p["postdata"] = []
				p["postdata"].append(d[x])
				p["postdata"].append(d[y])
				p["posts"] = [d[x]['id'], d[y]['id']]
				p["userlist"] = []
				p['rnd'] = random()
				inserts.append(p)
	db.accountdata.insert(inserts)
	db.accountdata.create_index('rnd')
	print "done"

def add_username(username):
	url = ('https://api.instagram.com/v1/users/search?q=%s&client_id=%s') % (username, client_id)
	j = requests.get(url).json()
	data = j['data'][0]
	if not data['username'] == username:
		print "nothing happened"
	else:
		db.accountlist.insert({'name': username,'id':str(data['id'])})

def get_two(username):
	rand = random()
	print rand
	d = db.accountdata.find_one({'userlist': {'$ne': username}, 'rnd': {'$gte': rand}})
	if d is None:
		d = db.accountdata.find_one({'userlist': {'$ne': username}, 'rnd': {'$lte': rand}})
	if d is None:
		return "you're out"
	return d['postdata']