from flask import Blueprint

from .nav import render_template
from ._objs import *

frontend_advisor = Blueprint("frontend_advisor", __name__)

@frontend_advisor.route("/advisor")
def index():
    return render_template("advisor/index.html")