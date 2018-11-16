import os
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    flash, redirect, url_for, request, current_app, session
)
from flask_mail import Message
from markupsafe import escape

from .nav import render_template
from ._objs import *

frontend = Blueprint("frontend", __name__)

@frontend.route("/")
def index():
    return render_template("index.html")

@frontend.route("/student")
def student_portal():
    return render_template("student.html")

@frontend.route("/")
def advisor_portal():
    return render_template("advisor.html")

@frontend.route("/")
def staff_portal():
    return render_template("staff.html")