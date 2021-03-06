from functools import wraps
from urllib.parse import urlparse, urljoin

from flask import (
    Blueprint, request, redirect, url_for, session, flash
)

import utils
from ex import none_if_empty_string
from ._objs import *
from .nav import render_template

frontend_user = Blueprint("frontend_user", __name__)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def require_login(_func=None, *, prev_endpoint=None, **kwargs_url):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(*args):
            if data.SESSION_LOGIN_KEY in session:
                return func(*args)
            else:
                if prev_endpoint is None:
                    return redirect(url_for("frontend_user.login"))
                else:
                    return redirect(url_for("frontend_user.login", prev=url_for(prev_endpoint, **kwargs_url)))

        return func_wrapper

    if _func is not None:
        return func_decorator(_func)

    return func_decorator


@frontend_user.route("/user/login", methods=["GET"])
@frontend_user.route("/user/login/", methods=["GET"])
def login():
    prev = request.args.get('prev')

    if data.SESSION_LOGIN_KEY in session:
        idt_type = account_manager.check_key_get_identity(session[data.SESSION_LOGIN_KEY])

        if idt_type is not None:
            return redir_portal_by_identity(idt_type)
        else:
            del session[data.SESSION_LOGIN_KEY]

    return render_template("user/login.html",
                           prev_url=prev if is_safe_url(prev) and prev != "" else url_for("frontend.index"))


@frontend_user.route("/user/login", methods=["POST"])
def login_post():
    form = request.form

    prev_url = form.get("prevUrl")

    acct_id = form["accountID"]
    acct_pw = form["accountPW"]

    login_result = account_manager.login(acct_id, acct_pw)

    if login_result.success:
        session[data.SESSION_LOGIN_KEY] = login_result.account_entry.login_key

        if prev_url is None or none_if_empty_string(prev_url) is None:
            flash(f"Welcome, {login_result.account_entry.name}!")
            return redir_portal_by_identity(login_result.account_entry.identity)
        else:
            return redirect(prev_url)
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


@frontend_user.route("/user/register", methods=["GET"])
@frontend_user.route("/user/register/", methods=["GET"])
def register():
    return render_template("user/register.html",
                           langs=data.languages,
                           identityTypes=data.Identity.get_choices(),
                           phone_carriers=utils.PhoneCarriersManager.get_carrier_generator())


@frontend_user.route("/user/register", methods=["POST"])
def register_post():
    form = request.form

    identity_enum: data.Identity = data.Identity(int(form["idType_id"]))

    account_id = form["accountID"]
    account_pw = form["accountPW"]
    name = form["accountName"]
    recov_email = form["accountEmail"]

    if identity_enum == data.Identity.STUDENT:
        student_id = int(form["studentID"])

        lang_id = data.languages[int(form["lang_id"]) - 1].id

        notif_sms = bool(int(form["notifSMS"]))
        phone_num = none_if_empty_string(form["phoneNum"])
        carrier = none_if_empty_string(form["carrier"])
        if carrier == "-":
            carrier = None

        notif_email = bool(int(form["notifEmail"]))
        stu_email = none_if_empty_string(form["studentEmail"])

        notif_manual = bool(int(form["notifManual"]))
        pronunciation = none_if_empty_string(form["namePron"])

        student_info_manager.create_student_info_entry(
            student_id, [lang_id], stu_email, phone_num, carrier, pronunciation, notif_sms, notif_email, notif_manual)

        session[data.SESSION_LOGIN_KEY] = account_manager.create_account_student(
            account_id, name, student_id, account_pw, recov_email).login_key
    else:
        session[data.SESSION_LOGIN_KEY] = account_manager.create_account_non_student(
            identity_enum, account_id, name, account_pw, recov_email).login_key

    flash(f"Registration succeed. Welcome, {name}!")

    return redir_portal_by_identity(identity_enum)


@frontend_user.route("/user", methods=["GET"])
@frontend_user.route("/user/", methods=["GET"])
def user_summary():
    if data.SESSION_LOGIN_KEY in session:
        lgn_key = session[data.SESSION_LOGIN_KEY]
        idt = account_manager.check_key_get_identity(lgn_key)

        if idt is not None:
            return redir_portal_by_identity(idt)
        else:
            del session[data.SESSION_LOGIN_KEY]

    flash("You must login first.")
    return redirect(url_for("frontend_user.login"))


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
        entry = pw_lost_manager.create_and_get_entry_by_recov_email(acc.recovery_email)

        utils.FlaskMail.send_html_mail(
            "Password recovery email from SCCIEOANS",
            entry.get_html_content(os.environ["APP_ROOT_URL"] + url_for("frontend_user.reset_pw",
                                                                        token=entry.token)),
            acc.recovery_email)

        flash(f"Recovery email has been sent.")
        return redirect(url_for("frontend.index"))


@frontend_user.route("/user/pw-reset/<token>", methods=["GET"])
@frontend_user.route("/user/pw-reset/", methods=["GET"])
@frontend_user.route("/user/pw-reset", methods=["GET"])
def reset_pw(token=None):
    if token is None:
        return render_reset_pw_login()
    else:
        entry = pw_lost_manager.get_entry(token)

        if entry is None:
            flash("Token is invalid. The password resetting link might expired.")
            return redirect(url_for("frontend.index"))
        else:
            return render_reset_pw(entry)


@frontend_user.route("/user/pw-reset", methods=["POST"])
def reset_pw_post():
    if account_manager.reset_password(request.form["auid"], request.form["newPassword"]):
        pw_lost_manager.delete_entry(request.form["token"])
        flash("Successfully reset the password.")
        return redirect(url_for("frontend.index"))
    else:
        flash("Fail to reset the password. Try to change your password to a new one.")
        return redirect(url_for("frontend_user.reset_pw", token=request.form["token"]))


def redir_portal_by_identity(identity_enum: data.Identity, err_on_not_recognized=False):
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


@require_login(prev_endpoint="frontend_user.reset_pw")
def render_reset_pw_login():
    lgn_key = session[data.SESSION_LOGIN_KEY]
    acct = account_manager.get_account_by_login_key(lgn_key)
    entry = pw_lost_manager.create_and_get_entry_by_acct(acct)

    return render_reset_pw(entry)


def render_reset_pw(pw_lost_entry: data.PwLostTokenEntry):
    return render_template("user/reset_pw.html",
                           auid=pw_lost_entry.linked_account_unique_id,
                           token=pw_lost_entry.token)
