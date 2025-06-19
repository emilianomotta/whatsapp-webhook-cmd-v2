
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

VERIFY_TOKEN = "Emi-token-123"
token_file = "access_token.txt"
mensajes_file = "mensajes.json"
agenda_file = "contacts.json"

def get_access_token():
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()
    return "TOKEN_POR_DEFECTO"

def guardar_mensaje(fecha, numero, contacto, texto):
    mensajes = []
    if os.path.exists(mensajes_file):
        with open(mensajes_file, "r") as f:
            try:
                mensajes = json.load(f)
            except:
                mensajes = []
    mensajes.append({
        "fecha": fecha,
        "numero": numero,
        "contacto": contacto,
        "texto": texto
    })
    with open(mensajes_file, "w") as f:
        json.dump(mensajes, f)

def cargar_mensajes():
    if os.path.exists(mensajes_file):
        with open(mensajes_file, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def cargar_agenda():
    if os.path.exists(agenda_file):
        with open(agenda_file, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def guardar_agenda(data):
    with open(agenda_file, "w") as f:
        json.dump(data, f)

@app.route("/")
def index():
    return "Webhook CMD activo (v15 compatible)", 200

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
        print("==> MENSAJE RECIBIDO:", data)

        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages_list = value.get("messages", [])
                    for msg in messages_list:
                        phone_id = value["metadata"]["phone_number_id"]
                        from_number = msg["from"]
                        text_received = msg.get("text", {}).get("body", "").strip()
                        agenda = cargar_agenda()
                        contacto = agenda.get(from_number, from_number)
                        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        guardar_mensaje(fecha, from_number, contacto, text_received)

                        palabras_ingreso = ["ingreso", "entrada", "entré", "entro", "ingresé"]
                        palabras_salida = ["salida", "salí", "salgo", "me fui", "fuera"]

                        if any(p in text_received.lower() for p in palabras_ingreso):
                            respuesta = "Tu mensaje fue recibido por el CMD de Montevideo. Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO, no olvides informar la salida, gracias."
                        elif any(p in text_received.lower() for p in palabras_salida):
                            respuesta = "Tu mensaje fue recibido por el CMD de Montevideo, gracias por informar la salida, saludos."
                        else:
                            respuesta = "Mensaje recibido por el CMD de Montevideo."

                        url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
                        headers = {
                            "Authorization": f"Bearer {get_access_token()}",
                            "Content-Type": "application/json"
                        }
                        body = {
                            "messaging_product": "whatsapp",
                            "to": from_number,
                            "text": {"body": respuesta}
                        }
                        print("==> RESPUESTA AUTOMÁTICA:", respuesta)
                        requests.post(url, headers=headers, json=body)
        except Exception as e:
            print("Error al procesar mensaje:", e)

        return "OK", 200

@app.route("/mensajes", methods=["GET"])
def obtener_mensajes():
    return jsonify(cargar_mensajes()), 200

@app.route("/agenda", methods=["GET", "POST"])
def manejar_agenda():
    if request.method == "GET":
        return jsonify(cargar_agenda()), 200
    elif request.method == "POST":
        data = request.get_json()
        guardar_agenda(data)
        return jsonify({"status": "ok"}), 200