from flask import (
    Blueprint, current_app, request, redirect, url_for, session
)

import utils
from ex import none_if_empty_string

from .nav import render_template
from ._objs import *

frontend_user = Blueprint("frontend_user", __name__)

@frontend_user.route("/user/register", methods=["GET"])
def register():
    return render_template("user/register.html", 
                           langs=data.languages, identityTypes=data.Identity.get_choices(), phone_carriers=utils.phone_carrier_dict.keys())

@frontend_user.route("/user/register", methods=["POST"])
def register_post():
    form = request.form

    identity_enum = data.Identity(int(form["idType_id"]))
    
    account_id = form["accountID"]
    account_pw = form["accountPW"]
    name = form["accountName"]
    recov_email = form["accountEmail"]

    if identity_enum == data.Identity.STUDENT:
        student_id = form["studentId"]

        lang_id = data.languages[int(form["lang_id"]) - 1].id

        notifSMS = bool(int(form["notifSMS"]))
        phone_num = none_if_empty_string(form["phoneNum"])
        carrier = none_if_empty_string(form["carrier"])
        if carrier == "-":
            carrier = None

        notifEmail = bool(int(form["notifEmail"]))
        stu_email = none_if_empty_string(form["studentEmail"])

        notifManual = bool(int(form["notifManual"]))
        pronunciation = none_if_empty_string(form["namePron"])

        student_info_manager.create_student_info_entry(student_id, lang_id, stu_email, phone_num, carrier, pronunciation, notifSMS, notifEmail, notifManual)
        
        session[data.SESSION_LOGIN_KEY] = account_manager.create_account_student(account_id, name, student_id, account_pw, recov_email)
    else:
        session[data.SESSION_LOGIN_KEY] = account_manager.create_account_non_student(identity_enum, account_id, name, account_pw, recov_email)

    flash(f"Registration succeed. Welcome, {name}!")

    if identity_enum == data.Identity.STUDENT:
        return redirect(url_for("frontend_student.index"))
    elif identity_enum == data.Identity.ADVISOR:
        return redirect(url_for("frontend_advisor.index"))
    elif identity_enum == data.Identity.STAFF:
        return redirect(url_for("frontend_staff.index"))
    else:
        return redirect(url_for("frontend.index"))