from flask import Blueprint

from .nav import render_template
from ._objs import *

frontend = Blueprint("frontend", __name__)

@frontend.route("/")
def index():
    return render_template("index.html")