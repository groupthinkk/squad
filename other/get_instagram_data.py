from instagram.client import InstagramAPI
import requests
import csv
from operator import itemgetter
import sys

client_id='375701af44384b6da4230f343a528b92'
client_secret='9620d4aef36f4e5b9139731497babcdb'
access_token='2963667.375701a.3eae9d0208074293b2bfe5c0c917f1b1'

api = InstagramAPI(access_token=access_token, client_secret=client_secret)

def add_username(username):
    url = ('https://api.instagram.com/v1/users/search?q=%s&access_token=%s') % (username, access_token)
    j = requests.get(url)
    j = j.json()
    datalist = j['data']
    for data in datalist:
        if data['username'] == username:
            return str(data['id'])
    return False

def get_posts_from_user_id(user_id, num_times=1):
    media_list, next_ = api.user_recent_media(user_id=user_id, count=40)
    i = 0
    while next_ and i < num_times:
       more_media, next_ = api.user_recent_media(user_id=user_id, count=40, with_next_url=next_)
       media_list.extend(more_media)
       i += 1
    ret_list = []
    for media in media_list:
        if media.type != 'video':
            ret_list.append([media.user.username, media.created_time, media.id, media.like_count, media.comment_count, media.images['standard_resolution'].url])
    return ret_list

def make_csv(data_list):
    csvfile = open(data_list[0][0] + '_ig_data.csv', 'w')
    fieldnames = ["username", "created_time", "post_id", "like_count", "comment_count", "image_url"]
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
    sorted_data_list = sorted(data_list, key=itemgetter(1))
    for entry in sorted_data_list:
        writer.writerow(entry)
    csvfile.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "USAGE: python get_instagram_data.py USERNAME N(*40= # of posts <OPTIONAL>)"
        exit(1)
    user_id = add_username(sys.argv[1])
    if len(sys.argv) == 2:
        data_list = get_posts_from_user_id(user_id)
    else:
        data_list = get_posts_from_user_id(user_id, sys.argv[2])
    make_csv(data_list)
