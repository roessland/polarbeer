from pymongo import MongoClient
from utils import load_config
import xml.etree.ElementTree as ET
from collections import namedtuple

config = load_config("config.yml")
mongoclient = MongoClient(config["mongo_uri"])
db = mongoclient.polarbeer

Trackpoint = namedtuple("Trackpoint", ["t", "lat", "lng", "alt"])

class Exercise:

    def __init__(self, exercise_dict):
        d = exercise_dict
        self.tcx = d["tcx"]
        self.sport = d["sport"]
        self.device = d["device"]
        self.id = d["id"]
        self.distance = d["id"]
        self.training_load = d["training-load"]
        self.calories = d["calories"]
        self.heart_rate = d["heart-rate"]
        self.transaction_id = d["transaction-id"]
        self.polar_user = d["polar-user"]
        self.start_time = d["start-time"]
        self.has_route = d["has-route"]
        self.detailed_sport_info = d["detailed-sport-info"]
        self.upload_time = d["upload-time"]
        self.duration = d["duration"]
        self._id = d["_id"]

    def track(self):
        root = ET.fromstring(self.tcx)
        bs = root.findall(".//*")
        for b in bs:
            raise NotImplementedError

        return []

def get_exercises():
    exercises = db.exercise.find({"sport": "CYCLING", "has-route": True})
    for exercise in exercises:
        exercise["tcx"] = db.exercise_tcx.find_one({"_id": exercise["_id"]})["data"]
        yield Exercise(exercise)

ex = next(get_exercises())
ex.track()
print("hehe")

"""
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2">
<Activities>
<Activity Sport="Biking">
<Id>2018-03-14T07:57:19.000Z</Id>
<Lap StartTime="2018-03-14T07:57:19.000Z">
<TotalTimeSeconds>2445.0</TotalTimeSeconds>
<DistanceMeters>3942.300048828125</DistanceMeters>
<MaximumSpeed>11.972220738728842</MaximumSpeed>
<Calories>262</Calories>
<AverageHeartRateBpm>
<Value>101</Value>
</AverageHeartRateBpm>
<MaximumHeartRateBpm>
<Value>148</Value>
</MaximumHeartRateBpm>
<Intensity>Active</Intensity>
<TriggerMethod>Manual</TriggerMethod>
<Track>
<Trackpoint>
<Time>2018-03-14T07:57:20.000Z</Time>
<SensorState>Present</SensorState>
</Trackpoint>
"""
