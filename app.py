
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

CONTACTS_FILE = "contacts.json"

@app.route("/contacts", methods=["GET"])
def get_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return jsonify({})
    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route("/contacts", methods=["POST"])
def save_contacts():
    data = request.get_json()
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
