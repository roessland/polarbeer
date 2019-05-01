from collections import defaultdict

import pymongo
from pymongo import MongoClient
from utils import load_config

config = load_config("config.yml")
mongoclient = MongoClient(config["mongo_uri"])
db = mongoclient.polarbeer

activities = db.activity.find().sort( "date", pymongo.ASCENDING )
all_steps = []
for activity in activities:
    samples = db.activity_step_samples.find_one({"_id": activity["id"]})["samples"]
    steps = [d.get("steps", 0) for d in samples]
    all_steps.extend(steps)

def cumsum(arr):
    res = [0 for e in arr]
    for i in range(1, len(arr)):
        res[i] = res[i-1] + arr[i]
    return res

for steps in cumsum(all_steps):
    print(steps)

