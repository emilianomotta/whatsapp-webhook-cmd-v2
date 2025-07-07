
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGES_FILE = os.path.join(BASE_DIR, "messages.json")
CONTACTS_FILE = os.path.join(BASE_DIR, "contacts.json")

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route("/mensaje", methods=["POST"])
def recibir_mensaje():
    data = request.get_json()

    numero = data.get("numero")
    mensaje = data.get("mensaje")

    if not numero or not mensaje:
        return jsonify({"error": "Faltan datos"}), 400

    contactos = load_json(CONTACTS_FILE)
    nombre = next((c["nombre"] for c in contactos if c["numero"] == numero), f"Desconocido ({numero})")

    if "salida" in mensaje.lower():
        return jsonify({"estado": "Mensaje de salida ignorado"}), 200

    entrada = {
        "nombre": nombre,
        "numero": numero,
        "mensaje": mensaje,
        "hora": datetime.now().strftime("%H:%M:%S"),
        "fecha": datetime.now().strftime("%Y-%m-%d")
    }

    mensajes = load_json(MESSAGES_FILE)
    mensajes.append(entrada)
    save_json(MESSAGES_FILE, mensajes)

    return jsonify({"estado": "Mensaje guardado"}), 200

@app.route("/mensajes", methods=["GET"])
def obtener_mensajes():
    return send_file(MESSAGES_FILE, mimetype="application/json")

@app.route("/agenda", methods=["GET"])
def obtener_agenda():
    return send_file(CONTACTS_FILE, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
