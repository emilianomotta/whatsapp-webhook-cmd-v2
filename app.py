from flask import Flask, request
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = "Emi-token-123"
ACCESS_TOKEN = "EAAGW...REPLACE_WITH_VALID_TOKEN..."  # Reemplazá por tu token actual
PHONE_NUMBER_ID = "709855918868317"

bienvenida = """Bienvenido, tu mensaje fue recibido por el CMD de Montevideo, procedemos a agendarte en nuestra base de datos.

IMPORTANTE
Favor respetar el formato de texto que tienen que enviar

Ejemplos para ingreso de quienes tienen cel registrado a nombre personal:

Ingreso SB0001 relevamiento                      Salida SB0001
Ingreso ES01 comunicaciones                    Salida ES01
Ingreso MH inspección                                  Salida MH

Para quienes trabajan en los cables y línea:

EST01 a SB0001 reparación                       EST01 a SB0001 Finalizado 
SB0001 a SB0002 ensayos DP y TD          SB0001 a SB0002 Finalizado
ES31 a ES78 verificar traza                        ES31 a ES78 Finalizado
SC602456 a SB4567 LMT poda                 SC602456 a SB4567 Finalizado
SB3456 a SB2745 LMT poda                      SB3456 a SB2745 Finalizado

Para quiénes trabajan en baja tensión:

Ingreso SB0001 Trabajos en BT reparación ...
Salida SB0001

(en caso que corresponda corte o aviso de trabajos finalizados o cualquier otro aviso llamar a la mesa de baja tensión como siempre)

Para quienes tienen Cel compartidos agregar nombre y apellido empresa y la unidad a la que realizan la tarea:

Ingreso SB0001 relevamiento  Juan Perez UTE obras
Salida SB0001 Juan Perez UTE obras	     

En caso de que se equivoquen en algún texto NO mandar otro con la corrección, ELIMINAR PARA TODOS Y VOLVER A ENVIAR EL TEXTO CORRECTAMENTE.

Tampoco enviar el mensaje en partes, es un mensaje para el ingreso y otro para la salida

NO OLVIDAR ENVIAR EL MENSAJE DE SALIDA RECUERDEN QUE ADEMÁS DE SER UN AVISO, ES UN REGISTRO DEL TIEMPO QUE SE ENCUENTRAN EN LAS INSTALACIONES, DE OCURRIR ALGÚN VANDALISMO O ROBO ETC ESTOS REGISTROS SERÁN CONSULTADOS.

Mensaje automático no contestar"""

def enviar_respuesta(telefono_destino, texto):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono_destino,
        "type": "text",
        "text": {"body": texto}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Respuesta enviada:", response.status_code, response.text)

@app.route('/')
def index():
    return 'Webhook activo', 200

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

    elif request.method == 'POST':
        data = request.get_json()
        print("Mensaje recibido:", json.dumps(data, indent=2))

        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    contacts = value.get("contacts", [])

                    for message in messages:
                        texto = message.get("text", {}).get("body", "").lower()
                        telefono = message.get("from")
                        contacto = contacts[0].get("profile", {}).get("name", "Desconocido") if contacts else "Desconocido"

                        if "ingreso" in texto:
                            enviar_respuesta(telefono, "Tu mensaje fue recibido por el CMD de Montevideo. Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO, no olvides informar la salida, gracias.")
                        elif "salida" in texto or "finalizado" in texto:
                            enviar_respuesta(telefono, "Tu mensaje fue recibido por el CMD de Montevideo. Gracias por informar la salida, saludos.")
                        elif contacts and "profile" not in contacts[0]:
                            enviar_respuesta(telefono, bienvenida)
        except Exception as e:
            print("Error procesando el mensaje:", e)

        return "EVENT_RECEIVED", 200