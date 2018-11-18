from flask import (
    Blueprint, jsonify, request
)

from ._objs import *

api = Blueprint("api", __name__)

@api.route("/api/accountid-exists", methods=["GET"])
def check_account_id():
    return ""

@api.route("/api/studentid-exists", methods=["GET"])
def check_student_id():
    return ""