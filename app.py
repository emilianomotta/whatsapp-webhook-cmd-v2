
from flask import Flask, request, jsonify, send_file
import json
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "Chatbot CMD funcionando"

@app.route("/contacts.json")
def get_contacts():
    try:
        with open("contacts.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # Convertir de lista de objetos a dict plano si tiene nombres
                contacts = {}
                for item in data:
                    number = item.get("phone") or item.get("numero") or item.get("number") or item.get("contact")
                    name = item.get("name") or (
                        (item.get("firstName") or "") + " " + (item.get("lastName") or "")
                    ).strip()
                    if number and name:
                        contacts[number] = name
                return jsonify(contacts)
            elif isinstance(data, dict):
                return jsonify(data)
            else:
                return jsonify({})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
