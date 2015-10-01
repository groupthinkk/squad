import os
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement

import datetime

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

if os.environ.get("DEV_PROD"):
    HOST = 'mechanicalturk.amazonaws.com'
    while(1):
        if raw_input("Type 'yes' to continue:") == "yes":
            break
else:
    HOST = 'mechanicalturk.sandbox.amazonaws.com'

connection = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             host=HOST,
                             debug=1)

url = "https://squadtest.herokuapp.com/"
title = "(Qualifying) Compare sets of 2 Instagram posts to guess which performed better (<15 minutes)"
description = "This HIT will take at most 15 minutes (usually much less). If you encounter an issue, send us a message so we can correct it. If you do 60% or better on this HIT, you will be invited to more, higher-paying HITs"
keywords = ["easy", "survey", "study", "bonus", "image", "images", "compare", "comparisons", "collection", "data", "research", "listings", "simple", "photo", "answer", "opinion", "question"]
frame_height = 850
amount = 1.30

duration = datetime.timedelta(minutes=60)
lifetime = datetime.timedelta(days=5)
approval_delay = datetime.timedelta(days=5)

q1 = PercentAssignmentsApprovedRequirement('GreaterThan', 95)
q2 = NumberHitsApprovedRequirement('GreaterThan', 250)
if os.environ.get("DEV_PROD"):
    qualifications = Qualifications([q1, q2])
else: 
    qualifications = Qualifications()

questionform = ExternalQuestion(url, frame_height)

for _ in xrange(1):
    create_hit_result = connection.create_hit(
        title=title,
        description=description,
        keywords=keywords,
        max_assignments=1750,
        question=questionform,
        reward=Price(amount=amount),
        response_groups=('Minimal', 'HITDetail', 'HITQuestion', 'HITAssignmentSummary'),
        lifetime=lifetime,
        duration=duration, 
        approval_delay=approval_delay,
        qualifications=qualifications
    )