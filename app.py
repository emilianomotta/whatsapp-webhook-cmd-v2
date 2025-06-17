from flask import Flask, request
from flask_cors import CORS
import os
import pymongo
import requests
from datetime import datetime

# Conexión a MongoDB Atlas para obtener nombres agendados
client = pymongo.MongoClient("mongodb+srv://emilianomottadesouza:1XkGVRmrQYtWvHie@cmd-db.esdo09q.mongodb.net/?retryWrites=true&w=majority&appName=cmd-db")
db = client["cmd"]
agenda_collection = db["agenda"]

def obtener_nombre(numero):
    contacto = agenda_collection.find_one({"telefono": numero})
    return contacto["nombre"] if contacto else None

app = Flask(__name__)
CORS(app)

VERIFY_TOKEN = "Emi-token-123"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAAKGtLKRBjYBO6xvZAZCObOfEZCeIFPOJv8eKZBRFYnqqZANfHCQUrFabY4DSuvfvSvi0XDx64w52LM9sSzt02L6J0ZBahkUo134FbnnRZCexIKq8ZBMupNFZByGp4K8CfkvuGlMfZBCZArIOMA06SUouwdH6sLdFOS1Ez4QpbuUcWZButd9CHFUqpD17k9uLP0MiWJS1zX28gQjNGZCPrQjqlVZBhThSnMki4mc3jZBLubWwDeODhQZAniTAJ4ZD")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://emilianomotta2025:2MurnEOaFb44EIrh@cluster0.oijxuj7.mongodb.net/?retryWrites=true&w=majority&tls=true")
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database("cmd-db")
messages = db.get_collection("messages")

@app.route("/")
def index():
    return "Webhook activo", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    global ACCESS_TOKEN
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
                            text_received = msg.get("text", {}).get("body", "").lower().strip()

                            palabras_ingreso = ["ingreso", "entrada", "entré", "entro", "ingresé"]
                            palabras_salida = ["salida", "salí", "salgo", "me fui", "fuera"]

                            if any(p in text_received for p in palabras_ingreso):
                                respuesta = "Tu mensaje fue recibido por el CMD de Montevideo. Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO."
                            elif any(p in text_received for p in palabras_salida):
                                respuesta = "Tu mensaje fue recibido por el CMD de Montevideo."
                            else:
                                respuesta = "Tu mensaje fue recibido por el CMD de Montevideo."

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

@app.route('/agregar-contacto', methods=['POST'])
def agregar_contacto():
    data = request.get_json()
    telefono = data.get("telefono")
    nombre = data.get("nombre")
    if not telefono or not nombre:
        return {"error": "Faltan datos"}, 400
    if agenda_collection.find_one({"telefono": telefono}):
        return {"mensaje": "El contacto ya existe"}, 200
    agenda_collection.insert_one({"telefono": telefono, "nombre": nombre})
    return {"mensaje": "Contacto agregado correctamente"}, 201

@app.route("/cambiar-token", methods=["POST"])
def cambiar_token():
    global ACCESS_TOKEN
    data = request.get_json()
    if data.get("clave") != "cmd2025":
        return {"error": "Clave incorrecta"}, 403
    nuevo_token = data.get("nuevo_token")
    if not nuevo_token:
        return {"error": "Falta el nuevo token"}, 400
    ACCESS_TOKEN = nuevo_token
    return {"mensaje": "Token actualizado exitosamente"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
