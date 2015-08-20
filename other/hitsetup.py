import os
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

if os.environ.get("DEV_PROD"):
    HOST = 'mechanicalturk.amazonaws.com'
else:
    HOST = 'mechanicalturk.sandbox.amazonaws.com'

connection = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             host=HOST,
                             debug=1)

url = "https://squadtest.herokuapp.com/"
title = "This is a test"
description = "COMPLETE THIS TASK ONLY ONCE! All submissions after the first will be rejected"
keywords = ["easy", "survey", "study", "bonus", "image", "images", "compare", "comparisons", "collection", "data", "research", "listings", "simple", "photo", "answer", "opinion", "question"]
frame_height = 800
amount = 1

questionform = ExternalQuestion(url, frame_height)

for _ in xrange(1):
    create_hit_result = connection.create_hit(
        title=title,
        description=description,
        keywords=keywords,
        max_assignments=1,
        question=questionform,
        reward=Price(amount=amount),
        response_groups=('Minimal', 'HITDetail', 'HITQuestion', 'HITAssignmentSummary')
    )