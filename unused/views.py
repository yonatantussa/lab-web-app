""" 
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from request import get_all_relay_info, get_relay_state, set_relay_state

views = Blueprint(__name__, "views")

base_url_list = [
    "http://10.10.10.30",
    "http://10.10.10.31",
    "http://10.10.10.32",
    "http://10.10.10.34",
    "http://10.10.10.115",
    "http://10.10.10.111"
]

username = "admin"
password = "1234"

@views.route("/")
def home():
    relay_df = get_all_relay_info(base_url_list, username, password)
    return render_template("index.html", relay_df=relay_df)

@views.route("/change_relay_state", methods=["POST"])
def change_relay_state():
    relay_number = int(request.form.get("relay_number"))
    base_url = request.form.get("base_url")
    username = "admin"
    password = "1234"

    current_state = get_relay_state(base_url, relay_number, username, password)

    ## print(current_state)

    if current_state is not None:
        new_state = not current_state
        ## print("New: ", new_state)
        ## print("Curr:", current_state)
        set_relay_state(base_url, relay_number, new_state, username, password)
        ## print("yes")
    ##else:
        ## print("no")
    
    ## print("test")

    return redirect(url_for("views.home"))

@views.route("/power")
def profile():
    relay_df = get_all_relay_info(base_url_list, username, password)
    return render_template("index.html", relay_df=relay_df)
@views.route("/json")
def get_json():
    return jsonify({'where': '/json', 'a number': 10})

@views.route("/data")
def get_data():
    data = request.json
    return jsonify(data)

@views.route("/go-to-home")
def go_to_home():
    return redirect(url_for("views.home"))
"""