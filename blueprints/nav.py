from flask import session, render_template, url_for, request
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator, RawTag

nav = Nav()

nav_items = [
    View("SCC IE Office Queue System", "frontend.index"),
    View("Student", "frontend.index")
    #Subgroup("資料查詢",
    #         View("查詢精靈資料", "frontend.pokemon_profile_index"),
    #         Separator(),
    #         View("從精靈查食譜", "frontend.find_recipe_index"),
    #         View("從食譜查精靈", "frontend.find_pokemon_index"),
    #         View("從技能查精靈", "frontend.poke_skill_index")),
    ]

def append_dynamic(navitems):
    to_append = []

    return navitems + to_append

def register_element(nav, navitems):
    navitems = append_dynamic(navitems)
    return nav.register_element('main', Navbar(*navitems))

_render_template = render_template

def render_template(*args, **kwargs):
    register_element(nav, nav_items)

    return _render_template(*args, nav=nav.elems, **kwargs)