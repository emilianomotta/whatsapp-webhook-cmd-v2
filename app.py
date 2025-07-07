from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

def cargar_agenda():
    try:
        with open("contacts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    phone = data.get('phone')
    message = data.get('message')

    if not phone or not message:
        return jsonify({'error': 'Datos incompletos'}), 400

    numero = "+{}".format(phone) if not phone.startswith("+") else phone
    numero = numero.replace('@c.us', '').replace('@s.whatsapp.net', '')

    agenda = cargar_agenda()
    nombre = numero
    for contacto in agenda:
        if contacto.get("numero") == numero:
            nombre = contacto.get("nombre", numero)
            break

    mensaje = {
        "id": str(datetime.now().timestamp()),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "numero": numero,
        "contacto": nombre,
        "texto": message
    }

    try:
        if os.path.exists("messages.json"):
            with open("messages.json", "r", encoding="utf-8") as f:
                mensajes = json.load(f)
        else:
            mensajes = []

        mensajes.append(mensaje)
        with open("messages.json", "w", encoding="utf-8") as f:
            json.dump(mensajes, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "guardado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/contacts.json', methods=['GET'])
@app.route('/agenda', methods=['GET'])
def agenda():
    return send_file('contacts.json', mimetype='application/json')

@app.route('/messages.json', methods=['GET'])
@app.route('/mensajes', methods=['GET'])
def mensajes():
    return send_file('messages.json', mimetype='application/json')

    if os.path.exists("deleted.json"):
        return send_file('deleted.json', mimetype='application/json')
    else:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/ocultar", methods=["POST"])
def ocultar():
    try:
        data = request.get_json()
        mensaje_id = data.get("id")
        if not mensaje_id:
            return jsonify({"error": "ID no proporcionado"}), 400

        # Leer papelera.json actual
        papelera_path = os.path.join(os.path.dirname(__file__), "papelera.json")
        if os.path.exists(papelera_path):
            with open(papelera_path, "r", encoding="utf-8") as f:
                papelera = json.load(f)
        else:
            papelera = []

        # Agregar nuevo ID si no está ya en la lista
        if mensaje_id not in papelera:
            papelera.append(mensaje_id)

        # Guardar la nueva papelera
        with open(papelera_path, "w", encoding="utf-8") as f:
            json.dump(papelera, f, indent=2)

        return jsonify({"success": True, "id": mensaje_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/papelera', methods=['GET'])
def papelera():
    try:
        papelera_path = os.path.join(os.path.dirname(__file__), "papelera.json")
        if os.path.exists(papelera_path):
            with open(papelera_path, "r", encoding="utf-8") as f:
                papelera = json.load(f)
        else:
            papelera = []
        return jsonify(papelera)
    except Exception as e:
        return jsonify({"error": str(e)}), 500