from flask import Flask, request
import os
import pymongo
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = "Emi-token-123"
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://emilianomottadesouza:1XkGVRmrQYtWvHie@cmd-db.esdo09q.mongodb.net/?retryWrites=true&w=majority&appName=cmd-db")
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database("cmd-db")
messages = db.get_collection("messages")

@app.route("/")
def index():
    return "Webhook activo", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Unauthorized", 403
    elif request.method == "POST":
        data = request.get_json()
        if data:
            messages.insert_one({"data": data, "timestamp": datetime.utcnow()})
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
