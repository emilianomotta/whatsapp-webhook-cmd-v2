
from flask import Flask, request
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = "Emi-token-123"
ACCESS_TOKEN = "EAAKGtLKRBjYBOZCO1fG9gdf5Tiu2WtO3x9cQAx0cVMGHDASRJxYGYQ12CXceFZAqcV8a8JRAGrLXePr1HC0ZBdWdMvZCv7pZBeWs2k1UQyM5rBeOZCsLvq5s3ZBNB50jVdom55ydZBSskZCIVMMFcMCaSB8o3vOImu41STimND5SMSmpTDcb4EaDsfZC7xAdNbj83VafAkQsHgiMPUZAZBSQEsuZCISbSZB7ZAZCNUzzSZC3xToOgkj0uKKAs2x8ZD"

known_contacts = set()

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
        print("Mensaje recibido:", data)

        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    if messages:
                        message = messages[0]
                        texto = message.get("text", {}).get("body", "").lower()
                        numero = message.get("from")
                        telefono_id = value.get("metadata", {}).get("phone_number_id")

                        respuesta = None

                        if any(palabra in texto for palabra in ["ingreso", "ingresó", "ingresando", "entré", "entrada"]):
                            respuesta = "Tu mensaje fue recibido por el CMD de Montevideo. Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO, no olvides informar la salida, gracias."
                        elif any(palabra in texto for palabra in ["salida", "salí", "finalizado", "me fui"]):
                            respuesta = "Tu mensaje fue recibido por el CMD de Montevideo. Gracias por informar la salida, saludos."
                        elif numero not in known_contacts:
                            known_contacts.add(numero)
                            respuesta = "Bienvenido, tu mensaje fue recibido por el CMD de Montevideo, procedemos a agendarte en nuestra base de datos.\n\nIMPORTANTE\nFavor respetar el formato de texto que tienen que enviar\n\nEjemplos para ingreso de quienes tienen cel registrado a nombre personal:\n\nIngreso SB0001 relevamiento                      Salida SB0001\nIngreso ES01 comunicaciones                    Salida ES01\nIngreso MH inspección                                  Salida MH\n\nPara quienes trabajan en los cables y línea:\n\nEST01 a SB0001 reparación                       EST01 a SB0001 Finalizado\nSB0001 a SB0002 ensayos DP y TD          SB0001 a SB0002 Finalizado\nES31 a ES78 verificar traza                        ES31 a ES78 Finalizado\nSC602456 a SB4567 LMT poda                 SC602456 a SB4567 Finalizado\nSB3456 a SB2745 LMT poda                      SB3456 a SB2745 Finalizado\n\nPara quiénes trabajan en baja tensión:\n\nIngreso SB0001 Trabajos en BT reparación ….\nSalida SB0001\n\nPara quienes tienen Cel compartidos agregar nombre y apellido empresa y la unidad a la que realizan la tarea:\n\nIngreso SB0001 relevamiento  Juan Perez UTE obras\nSalida SB0001 Juan Perez UTE obras\n\nNO OLVIDAR ENVIAR EL MENSAJE DE SALIDA.\n\nMensaje automático no contestar"

                        if respuesta:
                            url = f"https://graph.facebook.com/v18.0/{telefono_id}/messages"
                            headers = {
                                "Authorization": f"Bearer {ACCESS_TOKEN}",
                                "Content-Type": "application/json"
                            }
                            payload = {
                                "messaging_product": "whatsapp",
                                "to": numero,
                                "text": {"body": respuesta}
                            }
                            r = requests.post(url, headers=headers, json=payload)
                            print("Respuesta enviada:", r.json())

        except Exception as e:
            print("Error procesando mensaje:", e)

        return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
