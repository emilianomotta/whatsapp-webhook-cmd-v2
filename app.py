
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if data:
            phone = data.get("from", "sin_numero")
            mensaje = data.get("body", "sin_mensaje")
            nombre = data.get("name", "sin_nombre")
            hora = data.get("timestamp", "sin_hora")

            nuevo = {
                "nombre": nombre,
                "numero": phone,
                "mensaje": mensaje,
                "hora": hora
            }

            if os.path.exists("messages.json"):
                with open("messages.json", "r", encoding="utf-8") as f:
                    mensajes = json.load(f)
            else:
                mensajes = []

            mensajes.append(nuevo)

            with open("messages.json", "w", encoding="utf-8") as f:
                json.dump(mensajes, f, ensure_ascii=False, indent=2)

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/mensajes", methods=["GET"])
def get_mensajes():
    try:
        with open("messages.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify([]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
