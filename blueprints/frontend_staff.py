from flask import Blueprint

from .nav import render_template

frontend_staff = Blueprint("frontend_staff", __name__)


@frontend_staff.route("/staff")
def index():
    return render_template("staff/index.html")
