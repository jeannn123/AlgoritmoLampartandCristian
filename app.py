from flask import Flask, jsonify, render_template, request

from src.algorithms.cristian import simulate as run_cristian
from src.algorithms.lamport import simulate as run_lamport


app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/lamport/simulate")
def simulate_lamport():
    payload = request.get_json(silent=True) or {}

    try:
        result = run_lamport(payload.get("request_rounds", []))
        return jsonify(result)
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400


@app.post("/api/cristian/simulate")
def simulate_cristian():
    payload = request.get_json(silent=True) or {}

    try:
        result = run_cristian(
            payload.get("server_time", "12:00:00"),
            payload.get("clients", []),
        )
        return jsonify(result)
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
