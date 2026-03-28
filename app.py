import os
import threading

from flask import Flask, jsonify

from run_pipeline import run_pipeline

app = Flask(__name__)


def _run_pipeline_with_logs() -> None:
    try:
        run_pipeline()
    except Exception as error:
        print("ERROR:", str(error))


@app.route("/")
def home():
    return "OPENCLAW RUNNING"


@app.route("/run")
def run():
    threading.Thread(target=_run_pipeline_with_logs, daemon=True).start()
    return jsonify({"status": "started"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
