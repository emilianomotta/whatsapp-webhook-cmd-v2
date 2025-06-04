from flask import Flask, request
import requests

app = Flask(__name__)

ACCESS_TOKEN = "EAAKGtLKRBjYBOyWrU3xH1iMvVTOocZBBMPOUraJXZC4GHyZBa4PMfxgsVpFAC923OjdZCZB1aR5tSEIMVut7XuwZCPzaTEJtlzmbKkxOjZCYFb5QRZBLHYgxZCgdtdbplTDqx8N1TtFRvMrZCTBatrQbmz3hZAfmfimp67ZCJaoBqLPUEwQilfWFlItfRvL7c2rKiuRqVhzV7GHgM1y2ZCY6uogiOF7c7IyrYSHJzBjPOhA3GP8ZBAMpi55l8ZD"
PHONE_NUMBER_ID = "1204234147922442"

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    print("WhatsApp API response:", response.text)
    return response.status_code

@app.route("/")
def home():
    return "CMD Webhook funcionando"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        verify_token = "Emi-token-123"
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode and token and mode == "subscribe" and token == verify_token:
            return challenge, 200
        else:
            return "Forbidden", 403

    if request.method == "POST":
        data = request.get_json()
        try:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change["value"]
                    if "messages" in value:
                        message = value["messages"][0]
                        text = message.get("text", {}).get("body", "").lower()
                        from_number = message["from"]

                        if any(word in text for word in ["ingreso", "entro", "entré", "entree"]):
                            response_text = "Tu mensaje fue recibido por el CMD de Montevideo. Si luego de 5 minutos no eres contactado el ingreso se considera AUTORIZADO."
                        elif any(word in text for word in ["salida", "salí", "sali", "salgo"]):
                            response_text = "Mensaje recibido por el CMD de Montevideo, gracias por informar la salida."
                        else:
                            response_text = "Mensaje recibido por el CMD de Montevideo."

                        send_whatsapp_message(from_number, response_text)
        except Exception as e:
            print("Error procesando mensaje:", e)

        return "EVENT_RECEIVED", 200