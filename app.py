from flask import Flask, request
import os
import json

app = Flask(__name__)

VERIFY_TOKEN = "Emi-token-123"

@app.route('/')
def index():
    return 'Webhook activo', 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Unauthorized", 403

    elif request.method == 'POST':
        data = request.get_json()
        print("Mensaje recibido:", json.dumps(data, indent=2))
        return "EVENT_RECEIVED", 200