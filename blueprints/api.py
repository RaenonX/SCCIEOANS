from flask import (
    Blueprint, jsonify, request
)

from ._objs import *

api = Blueprint("api", __name__)

@api.route("/api", methods=["GET"])
def dummy():
    return ""