from flask import Blueprint

from .nav import render_template

frontend_student = Blueprint("frontend_student", __name__)


@frontend_student.route("/student")
def index():
    return render_template("student/index.html")


@frontend_student.route("/student/schedule")
def schedule_appointment():
    return render_template("student/schedule.html")


@frontend_student.route("/student/walkin")
def walk_in_appointment():
    return render_template("student/walkin.html")


@frontend_student.route("/student/message")
def send_message():
    return render_template("student/message.html")
