
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
from datetime import datetime
import os
import requests

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://emilianomottadesouza:1XkGVRmrQYtWvHie@cmd-db.esdo09q.mongodb.net/?retryWrites=true&w=majority&appName=cmd-db")
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database("cmd-db")
collection = db.mensajes
agenda = db.agenda

VERIFY_TOKEN = "Emi-token-123"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAAKGtLKRBjYBOwyTeF0ZBaQR46kzMnR2HFiKVvJ9egJanpZCoP5y6aDd77Wuy1vUWSZC40JPFZCzrVBMnkGHwTsg65stobj4GS6I1gYa9LBey9Qii7vPqQtXcLu3ZBTkVvCv4Llc5BL2Mc94PTBFOJRdXqWwpq0FsH263OSqa0x7MSbKkIY6m2s5bkYqjsL9PUFu6PK1sj8IgibckZCqo8Ur4Cyuc9EsOFmiVtsCB11p400hQ6z5QZD")

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Token de verificación inválido", 403

    data = request.get_json()
    if data and "entry" in data:
        for entry in data["entry"]:
            if "changes" in entry:
                for change in entry["changes"]:
                    value = change["value"]
                    if "messages" in value:
                        mensaje_info = value["messages"][0]
                        telefono = mensaje_info["from"]
                        mensaje = mensaje_info["text"]["body"]
                        contactos = cargar_agenda()

                        if mensaje and telefono:
                            print(f"Mensaje recibido de {telefono}: {mensaje}")

                            if deberia_responder(mensaje):
                                enviar_respuesta_automatica(telefono, mensaje, contactos)
                                if not contiene_palabra_salida(mensaje):
                                    guardar_mensaje(telefono, mensaje, contactos)
    return "OK", 200

@app.route("/mensajes", methods=["GET"])
def obtener_mensajes():
    mensajes = list(collection.find({}, {"_id": 0}))
    return jsonify(mensajes)

@app.route("/guardar-token", methods=["POST"])
def guardar_token():
    data = request.json
    nuevo_token = data.get("token")
    password = data.get("password")
    if password == "cmd2025" and nuevo_token:
        global ACCESS_TOKEN
        ACCESS_TOKEN = nuevo_token
        print("Nuevo token actualizado correctamente")
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Contraseña incorrecta"}), 403

@app.route("/agenda", methods=["GET", "POST", "PUT", "DELETE"])
def contactos_api():
    if request.method == "GET":
        return jsonify(list(agenda.find({}, {"_id": 0})))

    data = request.json
    telefono = data.get("telefono")

    if request.method == "POST":
        nombre = data.get("nombre")
        if telefono and nombre:
            agenda.update_one({"telefono": telefono}, {"$set": {"nombre": nombre}}, upsert=True)
            return jsonify({"status": "guardado"})
        return jsonify({"status": "error", "message": "Faltan campos"}), 400

    if request.method == "PUT":
        nombre = data.get("nombre")
        agenda.update_one({"telefono": telefono}, {"$set": {"nombre": nombre}})
        return jsonify({"status": "modificado"})

    if request.method == "DELETE":
        agenda.delete_one({"telefono": telefono})
        return jsonify({"status": "eliminado"})

def cargar_agenda():
    contactos = {}
    for c in agenda.find():
        contactos[c["telefono"]] = c["nombre"]
    return contactos

def deberia_responder(texto):
    texto = texto.lower()
    return "ingreso" in texto or "entrada" in texto or "salida" in texto or "egreso" in texto

def contiene_palabra_salida(texto):
    texto = texto.lower()
    return any(p in texto for p in ["salida", "egreso", "me fui", "me retiro"])

def enviar_respuesta_automatica(telefono, mensaje, contactos):
    nombre = contactos.get(telefono, "")
    if contiene_palabra_salida(mensaje):
        texto = f"Tu mensaje fue recibido por el CMD de Montevideo. Gracias por informar la salida, saludos."
    elif "ingreso" in mensaje.lower() or "entrada" in mensaje.lower():
        texto = f"Tu mensaje fue recibido por el CMD de Montevideo. Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO, no olvides informar la salida, gracias."
    else:
        texto = f"Tu mensaje fue recibido por el CMD de Montevideo."

    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {"body": texto}
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    response = requests.post("https://graph.facebook.com/v18.0/1204234147922442/messages", headers=headers, json=payload)
    print("RESPUESTA WHATSAPP:", response.status_code, response.text)

def guardar_mensaje(telefono, mensaje, contactos):
    nombre = contactos.get(telefono, "")
    mensaje_data = {
        "telefono": telefono,
        "mensaje": mensaje,
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nombre": nombre
    }
    collection.insert_one(mensaje_data)

if __name__ == "__main__":
    app.run()
