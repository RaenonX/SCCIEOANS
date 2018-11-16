import os
import pymongo

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])