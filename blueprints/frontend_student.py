from flask import Blueprint, session, redirect, url_for

from .nav import render_template
from ._objs import *
from .frontend_user import require_login

frontend_student = Blueprint("frontend_student", __name__)


@frontend_student.route("/student")
@require_login
def index():
    return render_template("student/index.html")


@frontend_student.route("/student/schedule")
@require_login(prev_endpoint="frontend_student.index")
def schedule_appointment():
    return render_template("student/schedule.html")


@frontend_student.route("/student/walkin")
def walk_in_appointment():
    return render_template("student/walkin.html")


@frontend_student.route("/student/message")
def send_message():
    return render_template("student/message.html")
