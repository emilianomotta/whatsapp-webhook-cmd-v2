from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

papelera_file = "papelera.json"
mensajes_en_memoria = []
agenda_en_memoria = {}

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
    return "Webhook CMD activo (sin Meta)", 200

@app.route("/mensajes", methods=["GET"])
def obtener_mensajes():
    visibles = [m for m in mensajes_en_memoria if m.get("id") not in mensajes_ocultos]
    return jsonify(visibles), 200

@app.route("/mensajes", methods=["POST"])
def recibir_mensaje():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos"}), 400
    try:
        mensajes_en_memoria.append(data)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.route("/papelera", methods=["GET"])
def get_papelera():
    try:
        with open('papelera.json', 'r', encoding='utf-8') as f:
            papelera = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        papelera = []
    return jsonify(papelera)

@app.route("/contacts.json")
def serve_contacts():
    return send_file('contacts.json', mimetype='application/json')

@app.route("/agenda-archivo", methods=["GET"])
def get_agenda_archivo():
    try:
        with open("contacts.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/agenda-archivo", methods=["POST"])
def update_agenda_archivo():
    try:
        data = request.get_json()
        with open("contacts.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500