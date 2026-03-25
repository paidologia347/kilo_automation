from flask import Flask, request, jsonify
from worker import run_workers
from queue import add_tasks

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run():
    prompts = request.json.get("prompts", [])
    add_tasks(prompts)
    run_workers()
    return jsonify({"status":"running"})
