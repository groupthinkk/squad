import os
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement, Requirement

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
title = "[Experts] Compare sets of 2 Instagram posts to guess which performed better (<15 minutes)"
description = "This HIT will take at most 15 minutes (usually much less). If you encounter an issue, send us a message so we can correct it. If you do 60% or better on this HIT, you will receive a $1 bonus. Anyone who qualifies can take this HIT."
keywords = ["easy", "survey", "study", "bonus", "image", "images", "compare", "comparisons", "collection", "data", "research", "listings", "simple", "photo", "answer", "opinion", "question"]
frame_height = 800
amount = 2

duration = datetime.timedelta(hours=2)
lifetime = datetime.timedelta(days=3)
approval_delay = datetime.timedelta(days=7)

q1 = PercentAssignmentsApprovedRequirement('GreaterThan', 95)
q2 = NumberHitsApprovedRequirement('GreaterThan', 250)
qualification_type_id = connection.search_qualification_types("squad_rating")[0].QualificationTypeId
q3 = Requirement(qualification_type_id, 'GreaterThan', 57)
if os.environ.get("DEV_PROD"):
    qualifications = Qualifications([q1, q2, q3])
else: 
    #qualifications = Qualifications()
    qualifications = Qualifications([q1, q2, q3])

questionform = ExternalQuestion(url, frame_height)

for _ in xrange(1):
    create_hit_result = connection.create_hit(
        title=title,
        description=description,
        keywords=keywords,
        max_assignments=400,
        question=questionform,
        reward=Price(amount=amount),
        response_groups=('Minimal', 'HITDetail', 'HITQuestion', 'HITAssignmentSummary'),
        lifetime=lifetime,
        duration=duration, 
        approval_delay=approval_delay,
        qualifications=qualifications
    )