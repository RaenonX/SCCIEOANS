import os

import pymongo

import data

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])
account_manager = data.AccountManager(mongo)
pw_lost_manager = data.PwLostTokenManager(mongo)
records_manager = data.AppointmentsManager(mongo)
student_info_manager = data.StudentInfoManager(mongo)
