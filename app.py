
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

CONTACTS_FILE = "contacts.json"
MESSAGES_FILE = "messages.json"

# Cargar contactos
def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return {}
    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Guardar mensajes
def save_messages(messages):
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

# Cargar mensajes existentes
def load_messages():
    if not os.path.exists(MESSAGES_FILE):
        return []
    with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Endpoint para sincronización desde Venom Bot
@app.route("/sync", methods=["POST"])
def sync_messages():
    incoming = request.json
    if not isinstance(incoming, list):
        return jsonify({"error": "El cuerpo debe ser una lista de mensajes"}), 400

    contacts = load_contacts()
    existing = load_messages()
    nuevos = []

    ya_guardados = {(m.get("from"), m.get("body"), m.get("timestamp")) for m in existing}

    for m in incoming:
        key = (m.get("from"), m.get("body"), m.get("timestamp"))
        if key not in ya_guardados:
            nombre = contacts.get(m["from"], m["from"])
            hora = datetime.now().strftime("%H:%M")
            cuerpo = m.get("body", "").lower()

            if "salida" in cuerpo:
                procesado = False
            else:
                procesado = True

            nuevos.append({
                "from": m["from"],
                "body": m["body"],
                "nombre": nombre,
                "hora": hora,
                "procesado": procesado,
                "timestamp": m.get("timestamp")
            })

    todos = existing + nuevos
    save_messages(todos)

    return jsonify({"agregados": len(nuevos), "total": len(todos)})

# Endpoint para que la consola lea mensajes
@app.route("/messages", methods=["GET"])
def get_messages():
    messages = load_messages()
    return jsonify(messages)

if __name__ == "__main__":
    app.run(debug=False, port=5000)
