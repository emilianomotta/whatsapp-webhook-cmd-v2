
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

VERIFY_TOKEN = "Emi-token-123"
token_file = "access_token.txt"
papelera_file = "papelera.json"

mensajes_en_memoria = []
agenda_en_memoria = {}

def get_access_token():
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()
    return "TOKEN_POR_DEFECTO"

def cargar_papelera():
    if os.path.exists(papelera_file):
        with open(papelera_file, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def guardar_papelera(papelera):
    with open(papelera_file, "w", encoding="utf-8") as f:
        json.dump(list(papelera), f, ensure_ascii=False, indent=2)

mensajes_ocultos = cargar_papelera()

@app.route("/")
def index():
    return "Webhook CMD activo (papelera por ID)", 200

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
                        msg_id = msg.get("id")
                        if not msg_id or msg_id in mensajes_ocultos:
                            continue  # Ignorar mensajes ocultos

                        phone_id = value["metadata"]["phone_number_id"]
                        from_number = msg["from"]
                        text_received = msg.get("text", {}).get("body", "").strip()
                        contacto = agenda_en_memoria.get(from_number, from_number)
                        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        mensajes_en_memoria.append({
                            "id": msg_id,
                            "fecha": fecha,
                            "numero": from_number,
                            "contacto": contacto,
                            "texto": text_received
                        })

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

@app.route("/agenda", methods=["GET", "POST"])
def manejar_agenda():
    global agenda_en_memoria
    if request.method == "GET":
        return jsonify(agenda_en_memoria), 200
    elif request.method == "POST":
        agenda_en_memoria = request.get_json()
        return jsonify({"status": "ok"}), 200

@app.route("/ocultar", methods=["POST"])
def ocultar_mensaje():
    global mensajes_ocultos
    data = request.get_json()
    msg_id = data.get("id")
    if msg_id:
        mensajes_ocultos.add(msg_id)
        guardar_papelera(mensajes_ocultos)
    return jsonify({"status": "ok"}), 200

@app.route("/mensajes", methods=["GET"])
def obtener_mensajes():
    visibles = [m for m in mensajes_en_memoria if m.get("id") not in mensajes_ocultos]
    return jsonify(visibles), 200
