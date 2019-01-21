from flask import session, render_template
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Separator

from ._objs import *

nav = Nav()

nav_items = [
    View("SCC IE Office Appointment Notifying System", "frontend.index"),
    View("Student", "frontend_student.index"),
    View("Advisor", "frontend_advisor.index"),
    View("Staff", "frontend_staff.index")]

_render_template = render_template


def append_dynamic():
    to_append: list = []

    if data.SESSION_LOGIN_KEY in session:
        lgn_key = session[data.SESSION_LOGIN_KEY]
        acc = account_manager.get_account_by_login_key(lgn_key)

        if acc is None:
            to_append.append(View("Login", "frontend_user.login"))
            del session[data.SESSION_LOGIN_KEY]
        else:
            to_append.append(Subgroup("Account Management",
                                      View("My Account Data", "frontend_user.user_summary"),
                                      Separator(),
                                      View("Logout", "frontend_user.logout")))
    else:
        to_append.append(View("Login", "frontend_user.login"))

    return nav_items + to_append


def register_element():
    navitems = append_dynamic()
    return nav.register_element('main', Navbar(*navitems))


def render_template(*args, **kwargs):
    register_element()

    return _render_template(*args, nav=nav.elems, **kwargs)
