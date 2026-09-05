"""
Flask Web Application for the Python Calculator.
Serves the web UI and handles calculation and history API requests.
"""

import os
from flask import Flask, jsonify, render_template, request, session
from calculator_engine import CalculatorEngine, CalculationError

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.urandom(24)

# In-memory session history storage
SESSION_HISTORIES = {}


def get_history(session_id: str):
    if session_id not in SESSION_HISTORIES:
        SESSION_HISTORIES[session_id] = []
    return SESSION_HISTORIES[session_id]


@app.before_request
def ensure_session():
    if "session_id" not in session:
        session["session_id"] = os.urandom(16).hex()


@app.route("/")
def index():
    """Serves the main calculator interface."""
    return render_template("index.html")


@app.route("/api/calculate", methods=["POST"])
def calculate():
    """
    Evaluates a mathematical expression.
    Expects JSON: { "expression": "2 + 2", "angle_mode": "deg" }
    """
    data = request.get_json(silent=True) or {}
    expression = data.get("expression", "")
    angle_mode = data.get("angle_mode", "deg")

    if not expression or not expression.strip():
        return jsonify({
            "success": False,
            "error": "Expression cannot be empty"
        }), 400

    try:
        engine = CalculatorEngine(angle_mode=angle_mode)
        raw_val, formatted_val = engine.evaluate(expression)

        history_item = {
            "expression": expression.strip(),
            "result": formatted_val,
            "angle_mode": angle_mode
        }

        # Store in session history (capped at 50 entries)
        history = get_history(session["session_id"])
        history.insert(0, history_item)
        if len(history) > 50:
            history.pop()

        return jsonify({
            "success": True,
            "expression": expression.strip(),
            "result": formatted_val,
            "raw_result": raw_val,
            "angle_mode": angle_mode
        })

    except CalculationError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Evaluation error: {str(e)}"
        }), 500


@app.route("/api/history", methods=["GET"])
def history():
    """Returns the calculation history for the current session."""
    hist = get_history(session.get("session_id", ""))
    return jsonify({"history": hist})


@app.route("/api/clear-history", methods=["POST"])
def clear_history():
    """Clears the calculation history for the current session."""
    sid = session.get("session_id")
    if sid in SESSION_HISTORIES:
        SESSION_HISTORIES[sid] = []
    return jsonify({"success": True, "message": "History cleared"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Calculator Web App running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
