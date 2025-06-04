from flask import Flask, request
from flask_cors import CORS
import os
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

VERIFY_TOKEN = "Emi-token-123"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["cmd_montevideo"]
collection = db["mensajes"]

@app.route("/")
def index():
    return "Webhook activo para CMD Montevideo", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Unauthorized", 403
    elif request.method == "POST":
        data = request.get_json()
        print("Mensaje recibido:", data)
        if data and "entry" in data:
            collection.insert_one({
                "timestamp": datetime.utcnow(),
                "data": data
            })
        return "EVENT_RECEIVED", 200
