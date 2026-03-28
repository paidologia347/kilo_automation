import os
import threading

from flask import Flask, jsonify

from run_pipeline import run_pipeline

app = Flask(__name__)


@app.route("/")
def home():
    return "APP RUNNING"


@app.route("/run")
def run():
    threading.Thread(target=run_pipeline).start()
    return jsonify({"status": "pipeline started"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
