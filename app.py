from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os, time, threading, json

app = Flask(__name__)
CORS(app)

VERIFY_TOKEN = "Emi-token-123"
PAGE_ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN", "EAAKGtLKRBjY...")  # Token largo
MONGO_URI = "mongodb+srv://emilianomottadesouza:1XkGVRmrQYtWvHie@cmd-db.esdo09q.mongodb.net/?retryWrites=true&w=majority&appName=cmd-db"

client = MongoClient(MONGO_URI)
db = client["cmd-db"]
messages_col = db["messages"]

subscribers = []

@app.route('/')
def index():
    return 'Webhook CMD Activo', 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Unauthorized", 403

    if request.method == 'POST':
        data = request.get_json()
        print("Mensaje recibido:", json.dumps(data, indent=2))
        threading.Thread(target=process_message, args=(data,)).start()
        return "EVENT_RECEIVED", 200

def process_message(data):
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return
        msg = messages[0]
        wa_id = msg.get("from")
        text = msg.get("text", {}).get("body", "")
        timestamp = msg.get("timestamp")
        profile = value.get("contacts", [{}])[0].get("profile", {})
        name = profile.get("name", "Sin nombre")

        tipo = detectar_tipo(text)
        registro = {"wa_id": wa_id, "nombre": name, "texto": text, "timestamp": timestamp, "tipo": tipo}
        messages_col.insert_one(registro)

        for sub in subscribers:
            sub.put(json.dumps(registro))

    except Exception as e:
        print("Error al procesar:", e)

def detectar_tipo(text):
    t = text.lower()
    if "ingres" in t:
        return "ingreso"
    elif "salid" in t or "finalizado" in t:
        return "salida"
    return "otro"

import queue

@app.route('/stream')
def stream():
    def event_stream(q):
        while True:
            try:
                msg = q.get()
                yield f"data: {msg}\n\n"
            except:
                break

    q = queue.Queue()
    subscribers.append(q)
    return Response(event_stream(q), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True)