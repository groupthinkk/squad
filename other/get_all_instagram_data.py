from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import requests
import csv
from operator import itemgetter
import sys
import datetime

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
    while next_ and datetime.datetime.now() - media_list[-1].created_time < datetime.timedelta(days=14):
       more_media, next_ = api.user_recent_media(user_id=user_id, count=40, with_next_url=next_)
       media_list.extend(more_media)
       i += 1
    ret_list = []
    for media in media_list:
        if media.type != 'video' and datetime.datetime.now() - media.created_time <= datetime.timedelta(days=14):
            ret_list.append([media.user.username, media.created_time, media.id, media.like_count, media.comment_count, media.images['standard_resolution'].url])
    return ret_list

def make_csv(data_list):
    csvfile = open('ig_data.csv', 'w')
    fieldnames = ["username", "created_time", "post_id", "like_count", "comment_count", "image_url"]
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
    sorted_data_list = sorted(data_list, key=itemgetter(0, 1))
    for entry in sorted_data_list:
        writer.writerow(entry)
    csvfile.close()

if __name__ == '__main__':
    f = open(sys.argv[1], "rb")
    csv_file = csv.reader(f)
    data_list = []
    for row in csv_file:
        #print row
        user_id = row[1]
        if not user_id.isdigit():
            continue
        try:
            data_list.extend(get_posts_from_user_id(user_id))
            print row[0]
        except InstagramAPIError as e:
           if (e.status_code == 400):
              print "%s is set to private" % (row[0])
    f.close()
    make_csv(data_list)
