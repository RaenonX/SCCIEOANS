import os

from flask import Blueprint, current_app

from .nav import render_template
from ._objs import *

import utils

frontend = Blueprint("frontend", __name__)

@frontend.route("/")
def index():
    return render_template("index.html")

@frontend.route("/student")
def student():
    return render_template("student.html")

@frontend.route("/advisor")
def advisor():
    return render_template("advisor.html")

@frontend.route("/staff")
def staff():
    return render_template("staff.html")