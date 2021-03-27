from flask import Blueprint, render_template, request

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
                    row["time_recorded"]
                ),
            )
            conn.commit()
    return "Success"


@cloud.route("/api/events/add", methods=["POST"])
def add_event():
    data = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO events(station, event_name, time_recorded) VALUES (?,?,?)",
        (
            data['station'],
            data['event_name'],
            data['time_recorded']
        ))
        conn.commit()
    return 'Success'

