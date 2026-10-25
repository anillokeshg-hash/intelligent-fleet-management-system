"""Intelligent Fleet Management System - Flask server."""
from flask import Flask, jsonify, send_from_directory

from fleet import CENTER_LAT, CENTER_LON, Fleet
from model import maintenance_risk, train_model

app = Flask(__name__)

print("Training maintenance-prediction model...")
model = train_model()
fleet = Fleet(n=8)

SPEED_LIMIT = 80      # km/h
LOW_FUEL = 15         # percent
RISK_LIMIT = 0.5      # maintenance probability


def analyse(t):
    """Attach AI risk score, alerts and status to a telemetry dict."""
    t["maintenance_risk"] = maintenance_risk(model, t)
    alerts = []
    if t["speed"] > SPEED_LIMIT:
        alerts.append("Overspeeding")
    if t["fuel"] < LOW_FUEL:
        alerts.append("Low fuel")
    if t["maintenance_risk"] >= RISK_LIMIT:
        alerts.append("Maintenance needed")
    if t["tyre_pressure"] < 28:
        alerts.append("Low tyre pressure")
    t["alerts"] = alerts
    if "Maintenance needed" in alerts:
        t["status"] = "Service"
    elif alerts:
        t["status"] = "Warning"
    else:
        t["status"] = "OK"
    return t


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/fleet")
def get_fleet():
    """Advance the simulation one step and return the analysed fleet."""
    vehicles = [analyse(t) for t in fleet.step()]
    summary = {
        "total": len(vehicles),
        "ok": sum(v["status"] == "OK" for v in vehicles),
        "warning": sum(v["status"] == "Warning" for v in vehicles),
        "service": sum(v["status"] == "Service" for v in vehicles),
        "avg_speed": round(sum(v["speed"] for v in vehicles) / len(vehicles), 1),
    }
    return jsonify({"center": [CENTER_LAT, CENTER_LON], "summary": summary, "vehicles": vehicles})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
