from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "Emi-token-123"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                return challenge, 200
            else:
                return 'Token de verificación incorrecto', 403
    elif request.method == 'POST':
        data = request.get_json()
        print('Evento recibido:', data)
        return 'EVENT_RECEIVED', 200
    return 'Método no permitido', 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
