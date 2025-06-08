
from flask import Flask, request
import os
import pymongo
import requests
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = "Emi-token-123"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAAKGtLKRBjYBO1iG7enDC6uC2ygpkQLIZAup531mvNqixgLkGKur7YFSxoi1PUoWZAnCN8SrTgSTQnTRZBAwd7EFBhumVBgDbh73DFkNgFw9EZBYAYrWN2nWYvA1Xh6N6HJZCW37g6nSBDmmJ7DEkyZAxBWIKngnxt6nXtVxo298XgOxC8MHqNb0nxHj9AetOeLqxifHcNxM9Y46EMI0oI3NsGsajeKpQMXiAI3SNh5KXXyTrjPrgZD")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://emilianomotta2025:2MurnEOaFb44EIrh@cluster0.oijxuj7.mongodb.net/?retryWrites=true&w=majority&tls=true")

client = pymongo.MongoClient(MONGO_URI)
db = client.get_database("cmd-db")
messages = db.get_collection("messages")
agenda = db.get_collection("agenda")

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
                            profile_name = value.get("contacts", [{}])[0].get("profile", {}).get("name", "")
                            text_received = msg.get("text", {}).get("body", "").lower().strip()

                            contacto = agenda.find_one({"telefono": from_number})
                            nombre_consola = contacto["nombre"] if contacto else profile_name
                            nombre_whatsapp = profile_name  # este es el que se responde por WhatsApp

                            palabras_ingreso = ["ingreso", "entrada", "entré", "entro", "ingresé"]
                            palabras_salida = ["salida", "salí", "salgo", "me fui", "fuera"]

                            if any(p in text_received for p in palabras_ingreso):
                                respuesta = f"{nombre_whatsapp}, tu mensaje fue recibido por el CMD de Montevideo. Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO."
                            elif any(p in text_received for p in palabras_salida):
                                respuesta = f"{nombre_whatsapp}, tu mensaje fue recibido por el CMD de Montevideo. Gracias por informar la salida, saludos."
                            else:
                                respuesta = f"{nombre_whatsapp}, tu mensaje fue recibido por el CMD de Montevideo."

                            url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
                            headers = {
                                "Authorization": f"Bearer {ACCESS_TOKEN}",
                                "Content-Type": "application/json"
                            }
                            payload = {
                                "messaging_product": "whatsapp",
                                "to": from_number,
                                "type": "text",
                                "text": {"body": respuesta}
                            }
                            response = requests.post(url, headers=headers, json=payload)
                            print("RESPUESTA WHATSAPP:", response.status_code, response.text)
            except Exception as e:
                print("Error al responder:", e)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
