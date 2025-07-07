
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

@app.route('/papelera', methods=['GET'])
def papelera():
    if os.path.exists("deleted.json"):
        return send_file('deleted.json', mimetype='application/json')
    else:
        return jsonify([])



@app.route('/eliminar', methods=['POST'])
def eliminar():
    data = request.get_json()
    mensaje_id = data.get("id")

    if not mensaje_id:
        return jsonify({"error": "ID requerido"}), 400

    try:
        # Leer mensajes existentes
        with open("messages.json", "r", encoding="utf-8") as f:
            mensajes = json.load(f)

        # Buscar el mensaje por ID
        mensaje_a_borrar = None
        mensajes_filtrados = []
        for m in mensajes:
            if m["id"] == mensaje_id:
                mensaje_a_borrar = m
            else:
                mensajes_filtrados.append(m)

        if not mensaje_a_borrar:
            return jsonify({"error": "Mensaje no encontrado"}), 404

        # Guardar el mensaje eliminado en papelera.json
        papelera = []
        if os.path.exists("papelera.json"):
            with open("papelera.json", "r", encoding="utf-8") as f:
                papelera = json.load(f)
        papelera.append(mensaje_a_borrar)
        with open("papelera.json", "w", encoding="utf-8") as f:
            json.dump(papelera, f, indent=2, ensure_ascii=False)

        # Reescribir messages.json sin el mensaje borrado
        with open("messages.json", "w", encoding="utf-8") as f:
            json.dump(mensajes_filtrados, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "eliminado"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
