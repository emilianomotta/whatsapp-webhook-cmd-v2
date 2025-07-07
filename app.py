
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(__file__)
VENOMBOT_MESSAGES_PATH = os.path.join(BASE_DIR, '../VenomBot/messages.json')
CONTACTS_PATH = os.path.join(BASE_DIR, 'contacts.json')
PAPELERA_PATH = os.path.join(BASE_DIR, 'papelera.json')

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_salida(mensaje):
    texto = mensaje.lower()
    return 'salida' in texto or 'sali' in texto or 'egreso' in texto

def is_ingreso(mensaje):
    texto = mensaje.lower()
    return 'ingreso' in texto or 'entro' in texto or 'entrada' in texto

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = load_json(VENOMBOT_MESSAGES_PATH)
    contacts = load_json(CONTACTS_PATH)
    papelera = load_json(PAPELERA_PATH)

    # indexar contactos por número
    contactos_index = {c['numero']: c['nombre'] for c in contacts if 'numero' in c and 'nombre' in c}

    resultados = []
    for m in messages:
        numero = m.get('numero')
        if not numero or numero in papelera:
            continue

        mensaje = m.get('mensaje', '')
        if is_ingreso(mensaje) or is_salida(mensaje):
            continue

        nombre = contactos_index.get(numero, numero)
        hora = m.get('hora') or datetime.now().strftime('%Y-%m-%d %H:%M')

        resultados.append({
            'nombre': nombre,
            'numero': numero,
            'mensaje': mensaje,
            'hora': hora
        })

    return jsonify(resultados)

@app.route('/contacts', methods=['GET'])
def get_contacts():
    return jsonify(load_json(CONTACTS_PATH))

@app.route('/contacts', methods=['POST'])
def update_contacts():
    try:
        nuevos = request.get_json()
        if isinstance(nuevos, list):
            save_json(CONTACTS_PATH, nuevos)
            return jsonify({'status': 'ok'})
        return jsonify({'error': 'Formato inválido'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/papelera', methods=['POST'])
def add_to_papelera():
    try:
        datos = request.get_json()
        numero = datos.get('numero')
        if not numero:
            return jsonify({'error': 'Número faltante'}), 400
        papelera = load_json(PAPELERA_PATH)
        if numero not in papelera:
            papelera.append(numero)
            save_json(PAPELERA_PATH, papelera)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
