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
else:
    HOST = 'mechanicalturk.sandbox.amazonaws.com'

connection = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             host=HOST,
                             debug=1)

def send_workers_message(worker_ids, subject, message_text):
    for worker_id in worker_ids:
        response = connection.notify_workers(worker_id, subject, message_text)
        if response != []:
            print response

def set_qualifications(worker_ids, scores, qualification_id):
    results = connection.get_qualifications_for_qualification_type(qualification_id)
    results = [x.SubjectId for x in results]
    for worker_id, score in zip(worker_ids, scores):
        if worker_id not in results:
            result = connection.assign_qualification(qualification_id, worker_id, score)
            if result != []:
                print result
        else:
            result = connection.update_qualification_score(qualification_id, worker_id, score)
            if result != []:
                print result

def give_bonus(worker_ids, assignment_id, bonus, reason):
    for worker_id in worker_ids:
        result = connection.grant_bonus(worker_id, assignment_id, bonus, reason)
        if result != []:
            print result

def create_hit(url=None, title=None, description=None, keywords=None, reward_amount=None, max_assignments=None, duration_in_minutes=None, lifetime_in_days=None, approval_delay_in_days=None, qualification_percent_approved=None, qualification_hits_approved=None):
    url = url or "https://squadtest.herokuapp.com/"
    title = title or "Compare 100 sets of 2 Instagram posts to guess which performed better (<10 minutes)"
    description = description or "This HIT will take at most 15 minutes (usually much less). If you have a problem with the HIT, message us so we can fix it!"
    keywords = keywords or ["easy", "survey", "study", "bonus", "image", "images", "compare", "comparisons", "collection", "data", "research", "listings", "simple", "photo", "answer", "opinion", "question"]
    frame_height = 800
    reward_amount = reward_amount or 1
    max_assignments = max_assignments or 200

    duration_in_minutes = duration_in_minutes or 20
    duration = datetime.timedelta(minutes=duration_in_minutes)

    lifetime_in_days = lifetime_in_days or 3
    lifetime = datetime.timedelta(days=3)

    approval_delay_in_days = approval_delay_in_days or 5
    approval_delay = datetime.timedelta(days=approval_delay_in_days)

    qualification_percent_approved = qualification_percent_approved or 95
    q1 = PercentAssignmentsApprovedRequirement('GreaterThan', qualification_percent_approved)

    qualification_hits_approved = qualification_hits_approved or 500
    q2 = NumberHitsApprovedRequirement('GreaterThan', qualification_hits_approved)
    qualifications = Qualifications([q1, q2])

    questionform = ExternalQuestion(url, frame_height)
    result = connection.create_hit(
        title=title,
        description=description,
        keywords=keywords,
        max_assignments=max_assignments,
        question=questionform,
        reward=Price(amount=reward_amount),
        response_groups=('Minimal', 'HITDetail', 'HITQuestion', 'HITAssignmentSummary'),
        lifetime=lifetime,
        duration=duration, 
        approval_delay=approval_delay,
        qualifications=qualifications
    )
    print result
