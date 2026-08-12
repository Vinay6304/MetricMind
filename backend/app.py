import os
import requests
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from scripts.analytics import get_dashboard_data

app = Flask(__name__)
CORS(app)


@app.route("/api/dashboard")
def dashboard():
    data = get_dashboard_data()
    return jsonify(data)


@app.route("/")
def home():
    return "MetricMind API is running!"

@app.route("/dashboard")
def dashboard_page():
    return send_from_directory(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend"),
    "index.html"
)

@app.route("/api/cube-dashboard")
def cube_dashboard():

    query = {
        "measures": [
            "Orders.total_orders",
            "Orders.total_revenue",
            "Orders.total_cost",
            "Orders.total_profit"
        ]
    }

    response = requests.get(
        "http://localhost:4000/cubejs-api/v1/load",
        params={"query": __import__("json").dumps(query)}
    )

    response.raise_for_status()

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True)