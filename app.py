
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Ruta para recibir mensajes desde VenomBot
@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    phone = data.get('phone')
    message = data.get('message')

    if not phone or not message:
        return jsonify({'error': 'Datos incompletos'}), 400

    mensaje = {
        "id": f"{datetime.now().timestamp()}",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "numero": phone,
        "contacto": phone,
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
