from flask import Flask, jsonify, render_template, request

from src.algorithms.cristian import CristianSimulator
from src.algorithms.lamport import LamportBakerySimulator


app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/lamport/simulate")
def simulate_lamport():
    payload = request.get_json(silent=True) or {}

    try:
        simulator = LamportBakerySimulator(payload.get("request_rounds", []))
        return jsonify(simulator.simulate())
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400


@app.post("/api/cristian/simulate")
def simulate_cristian():
    payload = request.get_json(silent=True) or {}

    try:
        simulator = CristianSimulator(
            server_time=payload.get("server_time", "12:00:00"),
            clients=payload.get("clients", []),
        )
        return jsonify(simulator.simulate())
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
