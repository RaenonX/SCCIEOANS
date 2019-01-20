from flask import (
    Blueprint, request, redirect, url_for, session, flash
)

import utils
from ex import none_if_empty_string
from ._objs import *
from .nav import render_template

frontend_user = Blueprint("frontend_user", __name__)


@frontend_user.route("/user/register", methods=["GET"])
@frontend_user.route("/user/register/", methods=["GET"])
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
        student_id = form["studentID"]

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
        
        session[data.SESSION_LOGIN_KEY] = account_manager.create_account_student(account_id, name, student_id, account_pw, recov_email).login_key
    else:
        session[data.SESSION_LOGIN_KEY] = account_manager.create_account_non_student(identity_enum, account_id, name, account_pw, recov_email).login_key

    flash(f"Registration succeed. Welcome, {name}!")

    return redir_portal_by_identity(identity_enum)


@frontend_user.route("/user", methods=["GET"])
@frontend_user.route("/user/", methods=["GET"])
def user_summary():
    if data.SESSION_LOGIN_KEY in session:
        lgn_key = session[data.SESSION_LOGIN_KEY]
        acc = account_manager.get_account_by_login_key(lgn_key)

        if acc is not None:
            redir_portal_by_identity(acc.identity)
        else:
            del session[data.SESSION_LOGIN_KEY]

    return redirect(url_for("frontend_user.login"))


@frontend_user.route("/user/login", methods=["GET"])
@frontend_user.route("/user/login/", methods=["GET"])
def login():
    if data.SESSION_LOGIN_KEY in session:
        idt_type = account_manager.check_key_get_identity(session[data.SESSION_LOGIN_KEY])

        if idt_type is not None:
            return redir_portal_by_identity(idt_type)
        else:
            del session[data.SESSION_LOGIN_KEY]

    return render_template("user/login.html")


@frontend_user.route("/user/login", methods=["POST"])
def login_post():
    form = request.form

    acctID = form["accountID"]
    acctPW = form["accountPW"]

    login_result = account_manager.login(acctID, acctPW)

    if login_result.success:
        session[data.SESSION_LOGIN_KEY] = login_result.acc_entry.login_key
        
        flash(f"Welcome, {login_result.acc_entry.name}!")
        return redir_portal_by_identity(login_result.acc_entry.identity)
    else:
        flash("Either account ID or the password is incorrect.", category="danger")
        return redirect(url_for("frontend_user.login"))


@frontend_user.route("/user/logout", methods=["GET"])
@frontend_user.route("/user/logout/", methods=["GET"])
def logout():
    if data.SESSION_LOGIN_KEY in session:
        del session[data.SESSION_LOGIN_KEY]

    flash("Successfully logged out.")
    return redirect(url_for("frontend.index"))


@frontend_user.route("/user/recover", methods=["GET"])
@frontend_user.route("/user/recover/", methods=["GET"])
def forget_password():
    return render_template("user/forget_pw.html")


@frontend_user.route("/user/recover", methods=["POST"])
def forget_password_issue_token():
    recovery_email = request.form["recovEmail"]

    acc = account_manager.get_account_by_recovery_email(recovery_email)

    if acc is None:
        flash("Account not exists.")
        return redirect(url_for("frontend_user.forget_password"))
    else:
        entry = pw_lost_manager.create_and_get_entry(acc.recovery_email)

        utils.FlaskMail.send_html_mail("Password recovery email from SCCIEOANS",
                                       entry.get_html_content(os.environ["APP_ROOT_URL"] +
                                                              url_for("frontend_user.reset_pw",
                                                                      token=entry.token)),
                                       acc.recovery_email)

        flash(f"Recovery email has been sent.")
        return redirect(url_for("frontend.index"))


@frontend_user.route("/user/pw-reset/<token>", methods=["GET"])
@frontend_user.route("/user/pw-reset/", methods=["GET"])
@frontend_user.route("/user/pw-reset", methods=["GET"])
def reset_pw(token):
    if token is None:
        raise NotImplementedError()
        # TODO: Verify login key to get into this page
    else:
        entry = pw_lost_manager.get_entry(token)

        if entry is None:
            flash("Token is invalid. The password resetting link might expired.")
            return redirect(url_for("frontend.index"))
        else:
            return render_template("user/reset_pw.html",
                                   auid=entry.linked_account_unique_id,
                                   token=entry.token)


@frontend_user.route("/user/pw-reset", methods=["POST"])
def reset_pw_post():
    if account_manager.reset_password(request.form["auid"], request.form["newPassword"]):
        pw_lost_manager.delete_entry(request.form["token"])
        flash("Successfully reset the password.")
        return redirect(url_for("frontend.index"))
    else:
        flash("Fail to reset the password. Try to change your password to a new one.")
        return redirect(url_for("frontend_user.reset_pw", token=request.form["token"]))


def redir_portal_by_identity(identity_enum, err_on_not_recognized=False):
    if identity_enum == data.Identity.STUDENT:
        return redirect(url_for("frontend_student.index"))
    elif identity_enum == data.Identity.ADVISOR:
        return redirect(url_for("frontend_advisor.index"))
    elif identity_enum == data.Identity.STAFF:
        return redirect(url_for("frontend_staff.index"))
    else:
        if err_on_not_recognized:
            raise ValueError(f"Identity type not recognized. {identity_enum}")
        else:
            flash(f"Identity not recognized: {identity_enum}")
            return redirect(url_for("frontend.index"))
