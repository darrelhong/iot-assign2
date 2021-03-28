from flask import Blueprint, render_template, request, redirect, url_for

from edge_server.db import query_db, get_db
import paho.mqtt.publish as publish


TOPIC = "/fireeyeofthetiger"

# all routes are prefixed with /api
cloud = Blueprint("cloud", __name__)


@cloud.route("/hello")
def hello():
    return "Hello API"


@cloud.route("/")
def index():
    data = query_db("SELECT * FROM cloud")
    return render_template("index.html", data=data)


@cloud.route("/events", methods=["GET", "POST"])
def events():
    if request.method == "POST":
        if "deactivate" in request.form:
            publish.single(TOPIC, "all reset", hostname="broker.emqx.io")

            with get_db() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO events(station, event_name) VALUES ('all','deactivate global alarm')"
                )
                conn.commit()
            return redirect(url_for("cloud.events"))
        elif "activate" in request.form:
            station_name = request.form["activate"].strip()
            publish.single(TOPIC, f"{station_name} fire", hostname="broker.emqx.io")
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO events(station, event_name) VALUES (?,'activate global alarm')",
                    [station_name],
                )
                conn.commit()
            print(request.form["activate"])

            return redirect(url_for("cloud.events"))
    data = query_db("SELECT * FROM events")
    return render_template("events.html", data=data)


@cloud.route("/api/sensors/add", methods=["POST"])
def add_sensor_data():
    data = request.get_json()
    with get_db() as conn:
        for row in data["rows"]:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO cloud(station, device, temp, light_level, time_recorded) VALUES (?,?,?,?,?)",
                (
                    row["station"],
                    row["device"],
                    row["temp"],
                    row["light_level"],
                    row["time_recorded"],
                ),
            )
            conn.commit()
    return "Success"


@cloud.route("/api/events/add", methods=["POST"])
def add_event():
    data = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events(station, event_name, time_recorded) VALUES (?,?,?)",
            (data["station"], data["event_name"], data["time_recorded"]),
        )
        conn.commit()
    return "Success"
