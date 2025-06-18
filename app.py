
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

VERIFY_TOKEN = "Emi-token-123"
token_file = "access_token.txt"

# Conexión a MongoDB Atlas
MONGO_URI = "mongodb+srv://emilianomottadesouza:1XkGVRmrQYtWvHie@cmd-db.esdo09q.mongodb.net/?retryWrites=true&w=majority&appName=cmd-db"
client = MongoClient(MONGO_URI)
db = client["cmd-db"]
mensajes_collection = db["messages"]

def get_access_token():
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()
    return "TOKEN_POR_DEFECTO"

def set_access_token(new_token):
    with open(token_file, "w") as f:
        f.write(new_token)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Invalid verification token", 403

    if request.method == "POST":
        data = request.get_json()
        if data:
            mensajes_collection.insert_one({
                "data": data,
                "timestamp": datetime.utcnow()
            })
        return "OK", 200

@app.route("/mensajes", methods=["GET"])
def get_mensajes():
    mensajes = list(mensajes_collection.find().sort("timestamp", -1).limit(100))
    for m in mensajes:
        m["_id"] = str(m["_id"])
    return jsonify(mensajes)

@app.route("/set-token", methods=["POST"])
def actualizar_token():
    data = request.get_json()
    if data and "token" in data:
        set_access_token(data["token"])
        return jsonify({"status": "Token actualizado"}), 200
    return jsonify({"error": "Token no enviado"}), 400

@app.route("/", methods=["GET"])
def home():
    return "CMD Backend v17 con MongoDB funcionando", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
