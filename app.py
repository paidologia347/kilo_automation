import os
import logging
from pathlib import Path

from flask import Flask, jsonify, request

from queue import add_tasks
from worker import run_workers


logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
Path("log.txt").touch(exist_ok=True)

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route("/", methods=["GET"])
def health():
    try:
        logger.info("Health check called")
        print("GET / -> APP RUNNING")
        return "APP RUNNING"
    except Exception as error:
        logger.exception("Failed processing / request: %s", error)
        print(f"ERROR in / endpoint: {error}")
        return jsonify({"error": "internal server error"}), 500


@app.route("/run", methods=["POST"])
def run():
    try:
        data = request.get_json(silent=True) or {}
        prompts = data.get("prompts", [])
        if not isinstance(prompts, list) or not all(isinstance(item, str) for item in prompts):
            return jsonify({"error": "prompts must be a list of strings"}), 400

        add_tasks(prompts)
        logger.info("Received %s prompts", len(prompts))
        print(f"POST /run received {len(prompts)} prompts")
        run_workers()

        return jsonify({"status": "completed", "queued": len(prompts)})
    except Exception as error:
        logger.exception("Failed processing /run request: %s", error)
        print(f"ERROR in /run endpoint: {error}")
        return jsonify({"error": "internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"Starting Flask server on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
