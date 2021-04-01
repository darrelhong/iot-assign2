from flask import Blueprint, render_template

from edge_server.db import query_db, get_db

# all routes are prefixed with /api
edge = Blueprint("edge", __name__)


@edge.route("/hello")
def hello():
    return "Hello API"


@edge.route("/")
def index():
    data = query_db("SELECT * FROM edge ORDER BY time_recorded DESC")
    return render_template("index.html", data=data)


@edge.route("/events")
def events():
    data = query_db("SELECT * FROM events ORDER BY time_recorded DESC")
    return render_template("events.html", data=data)
