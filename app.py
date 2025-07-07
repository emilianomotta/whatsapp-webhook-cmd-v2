from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

mensajes_en_memoria = []

@app.route("/receive", methods=["POST"])
def receive():
    data = request.get_json()
    phone = data.get("phone")
    message = data.get("message")

    if not phone or not message:
        return jsonify({"error": "Faltan datos"}), 400

    numero = "+{}".format(phone) if not phone.startswith("+") else phone

    nombre = numero
    try:
        agenda = requests.get("https://whatsapp-webhook-cmd-v2.onrender.com/agenda").json()
        for contacto in agenda:
            if contacto.get("numero") == numero:
                nombre = contacto.get("nombre", numero)
                break
    except:
        pass

    mensaje = {
        "id": str(datetime.now().timestamp()),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "numero": numero,
        "contacto": nombre,
        "texto": message
    }
    mensajes_en_memoria.append(mensaje)
    return jsonify({"status": "ok"})

@app.route("/mensajes", methods=["GET"])
def mensajes():
    return jsonify(mensajes_en_memoria)

@app.route("/agenda", methods=["GET"])
def agenda():
    try:
        with open("contacts.json", "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route("/contacts.json", methods=["GET"])
def contacts_json():
    return send_file("contacts.json", mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
