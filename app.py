from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["cmd-db"]
messages_col = db["messages"]

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == os.environ.get("VERIFY_TOKEN"):
            return request.args.get("hub.challenge"), 200
        return "Unauthorized", 403

    data = request.get_json()
    if data.get("entry"):
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if "messages" in value:
                    msg = value["messages"][0]
                    contact = value["contacts"][0]
                    messages_col.insert_one({
                        "from": msg["from"],
                        "name": contact["profile"]["name"],
                        "message": msg["text"]["body"],
                        "timestamp": msg["timestamp"]
                    })
    return "EVENT_RECEIVED", 200

@app.route('/messages')
def get_messages():
    messages = list(messages_col.find({}, {"_id": 0}))
    return jsonify(messages)

if __name__ == '__main__':
    app.run()