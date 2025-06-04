from flask import Flask, request
import os
import pymongo
import requests
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = "Emi-token-123"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAAKGtLKRBjYBO4ygG1ZAhGZAFHzKkIMdjj0C9awy0ZCKNMZC455Th7epmt6Ac1bbAuNMN6FfqVrhZCgyvhR3ZClHR3ZBbiI2xBO55vWCCDNwEnxe9PHLM01OytWpqTRHpG04UHGyyLHOnwKTTeP5ZBe2eFoKIJJ6rQC6vZBJBCqLltSNX0JZCwEfVQ6fDJ0h3ZCUgAPrDrPVtjTPAFcXfUlckVSJccqkgfKua2JZAYbczFlOojek26g8OwcZD")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://emilianomotta2025:2MurnEOaFb44EIrh@cluster0.oijxuj7.mongodb.net/?retryWrites=true&w=majority&tls=true")
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
            try:
                for entry in data.get("entry", []):
                    for change in entry.get("changes", []):
                        value = change.get("value", {})
                        messages_list = value.get("messages", [])
                        for msg in messages_list:
                            phone_id = value["metadata"]["phone_number_id"]
                            from_number = msg["from"]
                            text = "Mensaje Recibido por el CMD de Montevideo, gracias por informar la salida, saludos."
                            url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
                            headers = {
                                "Authorization": f"Bearer {ACCESS_TOKEN}",
                                "Content-Type": "application/json"
                            }
                            payload = {
                                "messaging_product": "whatsapp",
                                "to": from_number,
                                "text": {"body": text}
                            }
                            requests.post(url, json=payload, headers=headers)
            except Exception as e:
                print("Error al responder:", e)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
