from flask import Blueprint, flash, redirect, url_for, request

from .nav import render_template

err = Blueprint("err", __name__)

@err.app_errorhandler(404)
def page_not_found(error):
    flash("404 - Page Not Found. (From {})".format(request.referrer), category='error')
    return redirect(url_for("frontend.index"))

@err.app_errorhandler(500)
def internal_error(error):
    flash("500 - Server Internal Error (From {})".format(request.referrer), category='error')
    return redirect(url_for("frontend.index"))

@err.app_errorhandler(400)
def bad_request(error):
    return render_template("error/400.html", error=error)