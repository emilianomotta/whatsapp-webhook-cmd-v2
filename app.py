
from flask import Flask, request
from flask_cors import CORS
import os
import requests
import pymongo
from datetime import datetime

app = Flask(__name__)
CORS(app)

VERIFY_TOKEN = "Emi-token-123"
ACCESS_TOKEN = "EAAKGtLKRBjYBO9M5iiHAyvvtdZB6rLgWfSNYb5yparyatagA2Yd755NPz512z3zBMcw4N2KO8aZCZBr34dKLA9TZAU9EFZCPTwHMUI0zt2ZBRloeAZC5fZBiMSV7kJlbMXHk9VPtQuBcY4BXJTE6boRES86CRAZAldpm1u8i8M7LFRm2TiIc7mLUyUT9mLWxhWPRZB1RpFeDumfOfS9PZCzuqsZBGyFKsEzsfpiTbKIIZBnZAWK9rcQurckOcZD"

client = pymongo.MongoClient("mongodb+srv://emilianomottadesouza:2MurnEOaFb44EIrh@cmd-db.esdo09q.mongodb.net/?retryWrites=true&w=majority&appName=cmd-db")
db = client["cmd-db"]
collection = db["mensajes"]

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Token inválido", 403

    data = request.get_json()
    print("EVENTO RECIBIDO:")
    print(data)

    # Guardar en MongoDB
    collection.insert_one({"data": data, "timestamp": datetime.utcnow()})

    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                if messages:
                    for message in messages:
                        telefono = message["from"]
                        texto = message.get("text", {}).get("body", "").lower()

                        if any(palabra in texto for palabra in ["ingreso", "entro", "entré"]):
                            respuesta = (
                                "Tu mensaje fue recibido por el CMD de Montevideo. "
                                "Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO, "
                                "no olvides informar la salida, gracias."
                            )
                        elif any(palabra in texto for palabra in ["salida", "salgo", "me fui"]):
                            respuesta = (
                                "Tu mensaje fue recibido por el CMD de Montevideo. "
                                "Gracias por informar la salida, saludos."
                            )
                        else:
                            respuesta = (
                                "Tu mensaje fue recibido por el CMD de Montevideo. "
                                "En breve será respondido si es necesario. Gracias."
                            )

                        payload = {
                            "messaging_product": "whatsapp",
                            "to": telefono,
                            "text": {"body": respuesta}
                        }

                        headers = {
                            "Authorization": f"Bearer {ACCESS_TOKEN}",
                            "Content-Type": "application/json"
                        }

                        requests.post(
                            "https://graph.facebook.com/v18.0/709855918868317/messages",
                            json=payload,
                            headers=headers
                        )

    return "EVENT_RECEIVED", 200

@app.route("/", methods=["GET"])
def index():
    return "CMD Webhook activo", 200
