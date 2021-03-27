from flask import Blueprint, render_template

from edge_server.db import query_db, get_db

# all routes are prefixed with /api
cloud = Blueprint("cloud", __name__)


@cloud.route("/hello")
def hello():
    return "Hello API"


@cloud.route("/")
def index():
    data = query_db("SELECT * FROM cloud")
    return render_template("index.html", data=data)


@cloud.route("/events")
def events():
    data = query_db("SELECT * FROM events")
    return render_template("events.html", data=data)
