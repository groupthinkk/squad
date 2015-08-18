import os
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

if os.environ.get("DEV_ENV"):
    HOST = 'mechanicalturk.sandbox.amazonaws.com'
else:
    HOST = 'mechanicalturk.amazonaws.com'

connection = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             host=HOST,
                             debug=1)

url = "https://google.com"
title = "Describe a picture in your own words (COMPLETE THIS TASK ONLY ONCE!)"
description = "COMPLETE THIS TASK ONLY ONCE! All submissions after the first will be rejected"
keywords = ["easy"]
frame_height = 800
amount = 0.05

questionform = ExternalQuestion(url, frame_height)


for _ in xrange(1):
    create_hit_result = connection.create_hit(
        title=title,
        description=description,
        keywords=keywords,
        max_assignments=1,
        question=questionform,
        reward=Price(amount=amount),
        response_groups=('Minimal', 'HITDetail'),  # I don't know what response groups are
    )

# import boto.mturk.connection
 
# sandbox_host = 'mechanicalturk.sandbox.amazonaws.com'
# real_host = 'mechanicalturk.amazonaws.com'
 
# mturk = boto.mturk.connection.MTurkConnection(
#     aws_access_key_id = AWS_ACCESS_KEY_ID,
#     aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
#     host = sandbox_host,
#     debug = 1 # debug = 2 prints out all requests.
# )
 
# print boto.Version # 2.29.1
# print mturk.get_account_balance() # [$10,000.00]