
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

def get_access_token():
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()
    return "TOKEN_POR_DEFECTO"

def set_access_token(new_token):
    with open(token_file, "w") as f:
        f.write(new_token)

def guardar_mensaje(data):
    mensajes = []
    if os.path.exists(mensajes_file):
        with open(mensajes_file, "r") as f:
            try:
                mensajes = json.load(f)
            except:
                mensajes = []
    mensajes.append({"data": data, "timestamp": datetime.utcnow().isoformat()})
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

@app.route("/")
def index():
    return "Webhook CMD activo (v14 con almacenamiento en archivo)", 200

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
        guardar_mensaje(data)

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
                            respuesta = "Tu mensaje fue recibido por el CMD de Montevideo. Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO, no olvides informar la salida, gracias."
                        elif any(p in text_received for p in palabras_salida):
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
                        print("==> ENVIANDO A:", from_number)
                        print("==> BODY:", body)
                        print("==> HEADERS:", headers)
                        requests.post(url, headers=headers, json=body)
        except Exception as e:
            print("Error al procesar mensaje:", e)

        return "OK", 200

@app.route("/mensajes", methods=["GET"])
def obtener_mensajes():
    return jsonify(cargar_mensajes()), 200

@app.route("/update-token", methods=["POST"])
def actualizar_token():
    nuevo_token = request.json.get("token")
    if nuevo_token:
        set_access_token(nuevo_token)
        return jsonify({"status": "ok", "message": "Token actualizado"}), 200
    return jsonify({"status": "error", "message": "Falta el token"}), 400
