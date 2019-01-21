from flask import (
    Blueprint
)

from ex import none_if_empty_string
from ._objs import *

api = Blueprint("api", __name__)


@api.route("/api/accountid-exists/<account_id>", methods=["GET"])
@api.route("/api/accountid-exists/", methods=["GET"])
def check_account_id_available(account_id=None):
    account_id = none_if_empty_string(account_id)

    if account_id is None or not(6 <= len(account_id) <= 20):
        return "0"

    return str(int(not account_manager.is_account_id_exists(account_id)))


@api.route("/api/studentid-exists/<student_id>", methods=["GET"])
@api.route("/api/studentid-exists/", methods=["GET"])
def check_student_id_available(student_id=None):
    student_id = none_if_empty_string(student_id)

    if student_id is None or len(student_id) != 9:
        return "0"

    return str(int(not student_info_manager.is_student_id_exists(student_id)))
