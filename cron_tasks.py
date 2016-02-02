from pymongo import MongoClient
from itertools import groupby
import datetime as dt
from sys import argv

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

client = MongoClient("ds037713-a0.mongolab.com", 37713)
db = client["turksquad"]
db.authenticate("sweyn", "sweynsquad")

WEEKLY_REWARDS = [10, 5, 5, 5, 5]
WEEKLY_POINTS = [200, 150, 100]

def record_and_reset_weekly():
    weekly_user_results = list(db['users'].find().sort("weekly_score", -1))
    weekly_users_grouped = groupby(weekly_user_results, lambda x: x['weekly_score'])
    weekly_leaderboard_users = []
    rank = 1
    for _, user_group in weekly_users_grouped:
        user_group = list(user_group)
        num_users = len(user_group)
        reward = round(sum(WEEKLY_REWARDS[rank-1:rank+num_users-1])/float(num_users), 2) if rank < 11 else ''
        placed_rank = rank
        for user in user_group:
            user['rank'] = placed_rank
            if reward == '':
                user['reward'] = reward
            elif reward == int(reward):
                user['reward'] = '$' + str(int(reward))
            else:
                user['reward'] = '$' + str(round(reward, 2))
            if rank < len(WEEKLY_REWARDS) + 1:
                weekly_leaderboard_users.append(user)
            placed_rank = '' if reward != '' else placed_rank
        rank += num_users
    weekly_leaders = []
    for user in weekly_leaderboard_users:
        weekly_leaders.append({'email': user['email'], 'reward': user['reward'], 'weekly_score': user['weekly_score']})
        if user['rank'] < 4:
            db['users'].update({'email':user['email']}, {'$inc':{'score': WEEKLY_POINTS[user['rank']-1]}})
    db['weekly_leaders'].insert({'winners': weekly_leaders, 'date': dt.datetime.now()})
    db['users'].update(
        {},
        {"$set": {"weekly_score": 0, "num_queues_weekly": 0} },
        multi=True
    )

@sched.scheduled_job('cron', day_of_week='mon', hour=3)
def scheduled_job():
    record_and_reset_weekly()

if __name__ == '__main__':
    if argv[1] == "0":
        record_and_reset_weekly()
    else:
        sched.start()