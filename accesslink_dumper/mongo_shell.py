#!/usr/bin/env python

from __future__ import print_function

from utils import load_config, save_config, pretty_print_json

import time
import requests
from pymongo import MongoClient


try:
    input = raw_input
except NameError:
    pass


CONFIG_FILENAME = "config.yml"


config = load_config(CONFIG_FILENAME)

mongoclient = MongoClient(config["mongo_uri"])
db = mongoclient.polarbeer

print(db.exercise.find())
