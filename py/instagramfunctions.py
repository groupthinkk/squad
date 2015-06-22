import grequests
import requests
from pymongo import MongoClient
from random import random

from gevent import monkey; monkey.patch_all()

client_id='375701af44384b6da4230f343a528b92'
client_secret='9620d4aef36f4e5b9139731497babcdb'
access_token='2963667.375701a.3eae9d0208074293b2bfe5c0c917f1b1'

#client = MongoClient()
#db = client["SQUAD"]

client = MongoClient("ds061721.mongolab.com", 61721)
db = client["squad"]
db.authenticate("squad", "squadpass")

def create_user_urls(id_list):
	l = []
	for user_id in id_list:
		url = ("https://api.instagram.com/v1/users/%s/media/recent/?access_token=%s") %(user_id, access_token)
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

def pull_accountlist_data(id_list):
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
				p["rnd"] = random()
				inserts.append(p)
	db.accountdata.insert(inserts)
	db.accountdata.ensure_index('rnd')

def update():
	db.accountdata.drop()
	id_list = [(x['id']) for x in db.accountlist.find()]
	pull_accountlist_data(id_list)

def add_username(username):
	if db.collection.find({"name": usenrmae}).limit(1) == None:
		return False
	url = ('https://api.instagram.com/v1/users/search?q=%s&access_token=%s') % (username, access_token)
	j = requests.get(url)
	j = j.json()
	data = j['data'][0]
	if data['username'] == username:
		db.accountlist.insert({'name': username,'id':str(data['id'])})
		pull_accountlist_data([data['id']])
		return True
	else:
		return False
