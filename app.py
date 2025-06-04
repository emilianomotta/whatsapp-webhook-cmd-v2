from flask import Flask, request
import os
import pymongo
import requests
from datetime import datetime
import re

app = Flask(__name__)

VERIFY_TOKEN = "Emi-token-123"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAAKGtLKRBjYBO4ygG1ZAhGZAFHzKkIMdjj0C9awy0ZCKNMZC455Th7epmt6Ac1bbAuNMN6FfqVrhZCgyvhR3ZClHR3ZBbiI2xBO55vWCCDNwEnxe9PHLM01OytWpqTRHpG04UHGyyLHOnwKTTeP5ZBe2eFoKIJJ6rQC6vZBJBCqLltSNX0JZCwEfVQ6fDJ0h3ZCUgAPrDrPVtjTPAFcXfUlckVSJccqkgfKua2JZAYbczFlOojek26g8OwcZD")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://emilianomotta2025:2MurnEOaFb44EIrh@cluster0.oijxuj7.mongodb.net/?retryWrites=true&w=majority&tls=true")
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database("cmd-db")
messages = db.get_collection("messages")

# Funciones auxiliares
def es_ingreso(texto):
    return bool(re.search(r"\bingreso\b|\bverificar\b|\btrabajos\b|\brelevamiento\b|\ba\s+.*?\s+(reparaci[oó]n|ensayos|poda|verificar|trabajos)", texto, re.IGNORECASE))

def es_salida(texto):
    return bool(re.search(r"\bsalida\b|\bfinalizado\b", texto, re.IGNORECASE))

def enviar_respuesta(phone_id, to, texto):
    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
    headers = {{
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }}
    payload = {{
        "messaging_product": "whatsapp",
        "to": to,
        "text": {{"body": texto}}
    }}
    requests.post(url, json=payload, headers=headers)

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
            now = datetime.utcnow()
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    phone_id = value.get("metadata", {{}}).get("phone_number_id")
                    profile = value.get("contacts", [{{}}])[0].get("profile", {{}})
                    name = profile.get("name", "Desconocido")
                    from_number = value.get("contacts", [{{}}])[0].get("wa_id")
                    messages_list = value.get("messages", [])
                    for msg in messages_list:
                        text = msg.get("text", {{}}).get("body", "")
                        tipo = "otro"
                        respuesta = None

                        if es_ingreso(text):
                            tipo = "ingreso"
                            respuesta = "Tu mensaje fue recibido por el CMD de Montevideo. Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO, no olvides informar la salida, gracias."
                        elif es_salida(text):
                            tipo = "salida"
                            respuesta = "Tu mensaje fue recibido por el CMD de Montevideo. Gracias por informar la salida, saludos."
                        elif name == "Desconocido":
                            respuesta = "Bienvenido, tu mensaje fue recibido por el CMD de Montevideo, procedemos a agendarte en nuestra base de datos.\n\nIMPORTANTE\nFavor respetar el formato de texto que tienen que enviar..."

                        registro = {{
                            "timestamp": now,
                            "from": from_number,
                            "name": name,
                            "text": text,
                            "tipo": tipo
                        }}
                        messages.insert_one(registro)

                        if respuesta:
                            enviar_respuesta(phone_id, from_number, respuesta)
        return "EVENT_RECEIVED", 200
