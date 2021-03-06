from flask import Blueprint, flash, redirect, url_for, request

err = Blueprint("err", __name__)


@err.app_errorhandler(404)
def page_not_found(error):
    flash(f"From {request.referrer} - {error}", category='error')
    return redirect(url_for("frontend.index"))


@err.app_errorhandler(500)
def internal_error(error):
    flash(f"From {request.referrer} - {error}", category='error')
    return redirect(url_for("frontend.index"))


@err.app_errorhandler(400)
def bad_request(error):
    flash(f"(From {request.referrer} - {error})", category='error')
    return redirect(url_for("frontend.index"))
