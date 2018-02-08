from collections import defaultdict

from pymongo import MongoClient
from utils import load_config

config = load_config("config.yml")
mongoclient = MongoClient(config["mongo_uri"])
db = mongoclient.polarbeer

exercises = list(db.exercise.find())

print("Total distance per exercise")
exercise_distance = defaultdict(float)
for exercise in exercises:
    exercise_distance[exercise["detailed-sport-info"]] += exercise.get("distance", 0.0)

for exercise, distance in exercise_distance.items():
    print(exercise, distance, "m")
