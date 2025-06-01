
from flask import Flask, request, jsonify

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
                print('Webhook verificado correctamente')
                return challenge, 200
            else:
                return 'Token de verificación incorrecto', 403

    elif request.method == 'POST':
        data = request.get_json()
        print('Evento recibido:', data)

        if data.get('entry'):
            for entry in data['entry']:
                changes = entry.get('changes', [])
                for change in changes:
                    if change.get('field') == 'messages':
                        value = change.get('value', {})
                        messages = value.get('messages', [])
                        for message in messages:
                            from_number = message.get('from')
                            metadata_phone = value.get('metadata', {}).get('phone_number_id')
                            if from_number == metadata_phone:
                                print('Mensaje echo detectado. Ignorando...')
                                return 'EVENT_RECEIVED', 200

        return 'EVENT_RECEIVED', 200

    else:
        return 'Método no permitido', 405


if __name__ == '__main__':
    app.run(debug=True)
