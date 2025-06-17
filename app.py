
from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)
CORS(app)

VERIFY_TOKEN = "Emi-token-123"
FILENAME = "mensajes.json"
DRIVE_FOLDER_NAME = "WebhookCMD_Mensajes"

# Autenticación con cuenta de servicio
def init_drive():
    gauth = GoogleAuth()
    gauth.LoadServiceConfigFile('drive_service_account.json')
    gauth.ServiceAuth()
    return GoogleDrive(gauth)

drive = init_drive()

def get_drive_file():
    file_list = drive.ListFile({'q': f"title='{FILENAME}' and trashed=false"}).GetList()
    return file_list[0] if file_list else None

def guardar_mensaje(data):
    file_drive = get_drive_file()
    mensajes = []

    if file_drive:
        content = file_drive.GetContentString()
        try:
            mensajes = json.loads(content)
        except:
            mensajes = []

    mensajes.append({"data": data, "timestamp": datetime.utcnow().isoformat()})

    if file_drive:
        file_drive.SetContentString(json.dumps(mensajes))
        file_drive.Upload()
    else:
        new_file = drive.CreateFile({'title': FILENAME})
        new_file.SetContentString(json.dumps(mensajes))
        new_file.Upload()

def cargar_mensajes():
    file_drive = get_drive_file()
    if not file_drive:
        return []
    try:
        return json.loads(file_drive.GetContentString())
    except:
        return []

@app.route("/")
def home():
    return "Webhook CMD v15 con Google Drive activo", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Unauthorized", 403

    elif request.method == "POST":
        data = request.get_json()
        print("==> MENSAJE RECIBIDO:", data)
        guardar_mensaje(data)
        return "OK", 200

@app.route("/mensajes", methods=["GET"])
def mensajes():
    return jsonify(cargar_mensajes())

if __name__ == "__main__":
    app.run(debug=True)
