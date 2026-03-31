from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = "dashboard_data.json"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return jsonify(json.load(f))
    return jsonify({})

if __name__ == "__main__":
    app.run(debug=True)
