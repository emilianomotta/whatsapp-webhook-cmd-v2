
from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cargar agenda
def cargar_agenda():
    try:
        with open(os.path.join(BASE_DIR, "contacts.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# Guardar mensaje en messages.json
def guardar_mensaje(mensaje):
    messages_path = os.path.join(BASE_DIR, "messages.json")
    try:
        with open(messages_path, "r", encoding="utf-8") as f:
            mensajes = json.load(f)
    except:
        mensajes = []

    mensajes.append(mensaje)
    with open(messages_path, "w", encoding="utf-8") as f:
        json.dump(mensajes, f, indent=2, ensure_ascii=False)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    numero = data.get("numero")
    texto = data.get("mensaje")

    agenda = cargar_agenda()
    nombre = agenda.get(numero, numero)  # Usar nombre si existe

    mensaje = {
        "id": f"{numero}_{datetime.now().isoformat()}",
        "numero": nombre,
        "mensaje": texto,
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    guardar_mensaje(mensaje)
    return jsonify({"status": "ok"})

@app.route("/contacts", methods=["GET"])
def get_contacts():
    return jsonify(cargar_agenda())

@app.route("/mensajes", methods=["GET"])
def get_mensajes():
    try:
        with open(os.path.join(BASE_DIR, "messages.json"), "r", encoding="utf-8") as f:
            mensajes = json.load(f)
        return jsonify(mensajes)
    except:
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
