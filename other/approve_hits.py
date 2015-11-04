import os
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement

import datetime
import pickle

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

if os.environ.get("DEV_PROD"):
    HOST = 'mechanicalturk.amazonaws.com'
    QUAL = '3R5PEB0CKOM2DLVFJW0IK79PLLFO96'
    while(1):
        if raw_input("Type 'yes' to continue:") == "yes":
            break
else:
    HOST = 'mechanicalturk.sandbox.amazonaws.com'
    QUAL = '3ZNBPLV0N92Q4CDD8ICDTG5RJLD2CJ'

connection = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             host=HOST,
                             debug=1)

#hit_id = "3NI0WFPPI9825YFRRSEDYM13M58603"
#hit_id = "3DTJ4WT8BD73KYEW14A3G9W2KL1EZV"
def approve_hit(hit_id):
    page = 1
    assignments = []
    while (1):
            res = connection.get_assignments(hit_id, page_size=100, page_number=str(page))
            if len(res) > 0:
                assignments.extend(res)
                page += 1
            else:
                break
    for assignment in assignments:
        try:
            connection.approve_assignment(assignment.AssignmentId)
        except:
            print "Already submitted"

def list_turkers_over_x(hit_id, percentage):
    page = 1
    assignments = []
    while (1):
            res = connection.get_assignments(hit_id, page_size=100, page_number=str(page))
            if len(res) > 0:
                assignments.extend(res)
                page += 1
            else:
                break
    over_x = []
    for assignment in assignments:
        turk_id = str(assignment.answers[0][0].fields[0])
        success_rate = float(assignment.answers[0][1].fields[0])
        if success_rate >= percentage:
            over_x.append((turk_id, success_rate))
    print len(over_x)
    print over_x
    return over_x

def assign_qualification(qualification_name, turk_list):
    qualification_type_id = connection.search_qualification_types(qualification_name)[0].QualificationTypeId
    for turk_tuple in turk_list:
        try:
            connection.assign_qualification(qualification_type_id, turk_tuple[0], value=int(turk_tuple[1]), send_notification=True)
        except Exception,  e:
            print e

def give_bonus(worker_ids, hit_id, bonus, reason):
    payment = Price(bonus)
    assignments = []
    page = 1
    while (1):
        res = connection.get_assignments(hit_id, page_size=100, page_number=str(page))
        if len(res) > 0:
            assignments.extend(res)
            page += 1
        else:
            break
    for assignment in assignments:
        if assignment.WorkerId in worker_ids:
            print assignment.WorkerId
            result = connection.grant_bonus(assignment.WorkerId, assignment.AssignmentId, payment, reason)
            if result != []:
                print result

def send_workers_message(worker_ids, subject, message_text):
    for worker_id in worker_ids:
        response = connection.notify_workers(worker_id, subject, message_text)
        if response != []:
            print response

if __name__ == '__main__':
    #list_turkers_over_x(58)
    #print connection.search_qualification_types("squad_rating")[0].QualificationTypeId
    #approve_hit("3FI30CQHVKB3PLI1P8B2I3XMDBEB67")
    turk_tuple_list = list_turkers_over_x("3YCT0L9OMM1ADS5VZBJEA3T8CPISNS", 60)
    #print turk_tuple_list
    worker_id_list = [x[0] for x in turk_tuple_list]
    #output = open('sent_ids.pkl', 'r')
    #already_sent = pickle.load(output)
    #worker_id_list = []
    #for worker_id in worker_id_list1:
        #if worker_id not in already_sent:
            #worker_id_list.append(worker_id)
    #output.close()
    #output = open('sent_ids.pkl', 'w')
    #pickle.dump(worker_id_list + already_sent, output)
    give_bonus(worker_id_list, "3YCT0L9OMM1ADS5VZBJEA3T8CPISNS", 1, "Well done on our HIT rating Instagram posts. You scored over 60% - Market Intelligence")
    #assign_qualification("squad_rating", turk_tuple_list)
    #send_workers_message(worker_id_list, "HIT feedback and pay structure", "We were experimenting with different pay structures during this HIT and realize that as such it paided too little. We will compensate an additional $.80 per response in order to put the pay in line with the $1.30 from our previous HITs. We hope this is satisfactory. We love this community and our goal is aways to do right by it. This payment will go out when all outstanding HITs are completed. In the future, our goal is to pay significantly more for people who successfully attain a high percentage (60%+, 70%). What do you think would be a fair way to go about this in terms of bonus structures? We would love to hear from you.")
