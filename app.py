
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Cargar agenda desde contacts.json
def cargar_agenda():
    try:
        with open("contacts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# Ruta para recibir mensajes desde VenomBot
@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    phone = data.get('phone')
    message = data.get('message')

    if not phone or not message:
        return jsonify({'error': 'Datos incompletos'}), 400

    # Formatear número
    numero = "+{}".format(phone) if not phone.startswith("+") else phone

    # Buscar nombre en agenda
    agenda = cargar_agenda()
    nombre = numero
    for contacto in agenda:
        if contacto.get("numero") == numero:
            nombre = contacto.get("nombre", numero)
            break

    # Crear mensaje
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

# Ruta para la agenda con CORS
@app.route('/contacts.json', methods=['GET'])
def agenda():
    return send_file('contacts.json', mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
