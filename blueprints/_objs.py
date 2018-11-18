import os
import pymongo

import data

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])
account_manager = data.account_manager(mongo)
records_manager = data.records_manager(mongo)
student_info_manager = data.student_info_manager(mongo)