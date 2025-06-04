from flask import Flask, request
from datetime import datetime
import requests
import pymongo
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "Emi-token-123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "TU_TOKEN_TEMPORAL_AQUI")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://emilianomottadesouza:1XkGVRmrQYtWvHie@cmd-db.esdo09q.mongodb.net/?retryWrites=true&w=majority&appName=cmd-db")

client = pymongo.MongoClient(MONGO_URI)
db = client["whatsapp"]
messages = db["mensajes"]

@app.route("/")
def index():
    return "CMD Webhook Online"

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
                            mensaje = msg.get("text", {}).get("body", "").lower().strip()

                            palabras_ingreso = ["ingreso", "entré", "entre", "entrando", "llegué"]
                            palabras_salida = ["salida", "salí", "me fui", "retirada", "saliendo"]

                            if any(p in mensaje for p in palabras_ingreso):
                                texto_respuesta = "Tu mensaje fue recibido por el CMD de Montevideo. Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO"
                            elif any(p in mensaje for p in palabras_salida):
                                texto_respuesta = "Tu mensaje fue recibido por el CMD de Montevideo."
                            else:
                                texto_respuesta = None

                            if texto_respuesta:
                                url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
                                headers = {
                                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                                    "Content-Type": "application/json"
                                }
                                payload = {
                                    "messaging_product": "whatsapp",
                                    "to": from_number,
                                    "text": {"body": texto_respuesta}
                                }
                                requests.post(url, json=payload, headers=headers)
            except Exception as e:
                print("Error al responder:", e)

        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)